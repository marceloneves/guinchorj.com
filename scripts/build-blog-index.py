#!/usr/bin/env python3
"""Reconstrói blog/index.html com bolhas de filtro e todos os artigos estáticos."""

from __future__ import annotations

import html
import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG_INDEX = ROOT / "blog/index.html"
SOURCE_INDEX = ROOT / "blog/index.html"

# Carrega funções do gerador de posts
_spec = importlib.util.spec_from_file_location(
    "gen_posts", ROOT / "scripts/generate-blog-posts-json.py"
)
_gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_gen)

PILLS = [
    ("all", "Todos"),
    ("manual-do-motorista", "Manual do Motorista"),
    ("reboque-e-guincho", "Reboque e Guincho"),
    ("blog", "Artigos gerais"),
]

ASSETS_HEAD = (
    '<link rel="stylesheet" href="blog-pills.css">'
    '<style>#blog-posts-grid&gt;[class*="col-"].blog-card-hidden{display:none!important;'
    'flex:0 0 0!important;width:0!important;max-width:0!important;padding:0!important;'
    'margin:0!important;overflow:hidden!important;visibility:hidden!important;'
    'pointer-events:none!important}</style>'
)
ASSETS_BODY = ""


def load_posts() -> list[dict[str, str]]:
    posts = [
        _gen.extract_post(path)
        for path in sorted((ROOT / "blog").rglob("index.html"))
        if _gen.is_post(path)
    ]
    posts.sort(key=lambda item: item.get("date") or "", reverse=True)
    return posts


def render_pills() -> str:
    buttons = []
    for slug, label in PILLS:
        active = " is-active" if slug == "all" else ""
        pressed = "true" if slug == "all" else "false"
        buttons.append(
            f'<button type="button" class="blog-pill{active}" data-filter="{slug}" '
            f'aria-pressed="{pressed}" '
            f"onclick=\"return window.blogFilterClick('{slug}', this);\">"
            f"{html.escape(label)}</button>"
        )
    return (
        '<div class="blog-pills-wrap">'
        '<div class="blog-pills" role="group" aria-label="Filtrar artigos por categoria">'
        + "".join(buttons)
        + '</div><p class="blog-pills-count" id="blog-pills-count"></p></div>'
    )


def render_empty_message() -> str:
    return '<p class="blog-pills-empty" id="blog-pills-empty">Nenhum artigo nesta categoria.</p>'


def render_card(post: dict[str, str]) -> str:
    title = html.escape(post["title"])
    url = html.escape(post["url"])
    excerpt = html.escape(post["excerpt"])
    category = html.escape(post["category"])

    return (
        f'<article class="col-lg-6 col-md-6" data-category="{category}">'
        f'<div class="single-blog"><div class="image">'
        f'<a href="{url}" title="{title}"> '
        f'<figure class="box-image-post" style="display:flex;align-items:center;justify-content:center;height:401px;">'
        f'<i class="fa fa-file-image-o" aria-hidden="true"></i></figure> '
        f"</a></div><div class=\"content\">"
        f'<h2 class="entry-title" style="text-align:center;height:113px;display:flex;align-items:center;justify-content:center;">'
        f'<a href="{url}" title="{title}">{title}</a></h2>'
        f"<p>{excerpt}</p>"
        f'<div class="blog-btn" style="display:flex;align-items:center;justify-content:center;">'
        f'<a href="{url}" title="{title}" rel="nofollow" class="default-btn">Saiba mais <span></span></a>'
        f"</div></div></div></article>"
    )


def strip_old_nav(html_content: str) -> str:
    html_content = re.sub(
        r'<link rel="stylesheet" href="blog-category-tabs\.css">',
        "",
        html_content,
    )
    html_content = re.sub(
        r"<nav class=\"blog-category-tabs\".*?</nav>",
        "",
        html_content,
        flags=re.DOTALL,
    )
    html_content = re.sub(
        r'<link rel="stylesheet" href="blog-filter\.css">.*?<script src="blog-filter\.js" defer></script>',
        "",
        html_content,
    )
    return html_content


def rebuild_blog_layout(html_content: str, posts: list[dict[str, str]]) -> str:
    cards = "".join(render_card(post) for post in posts)
    pills_bar = f'<div class="blog-pills-top"><div class="container">{render_pills()}</div></div>'
    blog_section = (
        f'<section class="blog-area ptb-100"><div class="container">'
        f"{render_empty_message()}"
        f'<div class="row" id="blog-posts-grid">{cards}</div>'
        f"</div></section>"
    )

    html_content = re.sub(r'<div class="blog-pills-top">.*?</div>\s*(?=<section class="blog-area)', "", html_content, flags=re.DOTALL)
    html_content = re.sub(r'<div class="blog-pills-wrap">.*?</div>\s*(?=</div></div></div></div></header>)', "", html_content, flags=re.DOTALL)
    html_content = re.sub(
        r'<section class="blog-area ptb-100">.*?</section>',
        blog_section,
        html_content,
        count=1,
        flags=re.DOTALL,
    )

    marker = '</div></div></div></div></header><section class="blog-area ptb-100">'
    if pills_bar not in html_content:
        html_content = html_content.replace(
            marker,
            f"</div></div></div></div></header>{pills_bar}<section class=\"blog-area ptb-100\">",
            1,
        )

    return html_content


def clean_head(html_content: str) -> str:
    html_content = re.sub(r'\s*<link rel="next" href="[^"]+"\s*>', "", html_content)
    html_content = html_content.replace(
        '<link rel="stylesheet" href="blog-category-tabs.css">', ""
    )
    html_content = re.sub(
        r'<link rel="stylesheet" href="blog-pills\.css">',
        "",
        html_content,
    )
    html_content = re.sub(
        r'<script src="blog-pills\.js"( defer)?></script>',
        "",
        html_content,
    )
    if ASSETS_HEAD not in html_content:
        html_content = html_content.replace("</head>", ASSETS_HEAD + "</head>", 1)
    return html_content


def inject_head_script(html_content: str) -> str:
    script_path = ROOT / "blog/blog-pills.js"
    script_content = script_path.read_text(encoding="utf-8")
    inline_script = f"<script>{script_content}</script>"

    html_content = re.sub(
        r"<script>\(function \(\) \{\s*\"use strict\";.*?</script>\s*(?=</main>)",
        "",
        html_content,
        flags=re.DOTALL,
    )
    html_content = re.sub(r'<script src="blog-pills\.js"( defer)?></script>\s*', "", html_content)
    html_content = re.sub(
        r"<script>window\.blogFilterClick=function\(f,b\).*?</script>",
        "",
        html_content,
    )
    html_content = re.sub(
        r"<script>\(function \(\) \{\s*\"use strict\";\s*var pendingFilter.*?</script>",
        "",
        html_content,
        flags=re.DOTALL,
    )

    if inline_script in html_content:
        return html_content

    css_marker = '<style>.blog-card-hidden{display:none!important}</style>'
    if css_marker in html_content:
        return html_content.replace(css_marker, css_marker + inline_script, 1)

    return html_content.replace("</head>", inline_script + "</head>", 1)


def inject_body_script(html_content: str) -> str:
    return html_content


def hide_pagination(html_content: str) -> str:
    return re.sub(
        r'(<div class="col-lg-12 col-md-12" style="display: flex; align-items: center; justify-content: center;">'
        r'<div><nav aria-label="Paginação".*?</nav></div></div>)',
        "",
        html_content,
        count=1,
        flags=re.DOTALL,
    )


def main() -> None:
    posts = load_posts()
    html_content = BLOG_INDEX.read_text(encoding="utf-8")
    html_content = strip_old_nav(html_content)
    html_content = rebuild_blog_layout(html_content, posts)
    html_content = hide_pagination(html_content)
    html_content = clean_head(html_content)
    html_content = inject_head_script(html_content)
    html_content = inject_body_script(html_content)
    BLOG_INDEX.write_text(html_content, encoding="utf-8")
    print(f"blog/index.html reconstruído com {len(posts)} artigos e filtro por bolhas.")


if __name__ == "__main__":
    main()
