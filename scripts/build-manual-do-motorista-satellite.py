#!/usr/bin/env python3
"""Gera artigos satélite do cluster Manual do Motorista."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "blog/reboque-e-guincho/o-que-e-reboque-e-como-funciona/index.html"
CONTENT_DIR = ROOT / "scripts/content/manual-do-motorista"
CLUSTER_SLUG = "manual-do-motorista"
CLUSTER_TITLE = "Manual do Motorista"
CATEGORY = "Manual do Motorista"
DATE = "2026-06-07"
DATETIME = "2026-06-07T12:00:00-03:00"

SERVICE_CTA = """
<h2>Precisa de reboque ou guincho no Rio de Janeiro?</h2>
<p>A Guincho RJ atua 24 horas no Rio de Janeiro, Niterói e região metropolitana. Veja nossos principais serviços:</p>
<ul>
<li><a href="../../servico/reboque-na-zona-sul-no-rj/" title="Reboque Zona Sul">Reboque Zona Sul</a></li>
<li><a href="../../servico/reboque-zona-oeste/" title="Reboque Zona Oeste">Reboque Zona Oeste</a></li>
<li><a href="../../servico/reboque-zona-norte-rj/" title="Reboque Zona Norte">Reboque Zona Norte</a></li>
<li><a href="../../servico/reboque-em-niteroi/" title="Reboque Niterói">Reboque Niterói</a></li>
<li><a href="../../servico/reboque-linha-vermelha-rj/" title="Reboque Linha Vermelha">Reboque Linha Vermelha</a></li>
<li><a href="../../servico/reboque-linha-amarela-rj/" title="Reboque Linha Amarela">Reboque Linha Amarela</a></li>
<li><a href="../../servico/reboque-avenida-brasil-rj/" title="Reboque Avenida Brasil">Reboque Avenida Brasil</a></li>
<li><a href="../../servico/reboque-dutra-rj/" title="Reboque Dutra">Reboque Dutra</a></li>
</ul>
<p>Telefone/WhatsApp: <a href="tel:+5521959543043"><strong>(21) 95954-3043</strong></a></p>
"""

COMPANY_FOOTER = """
<h2>Dados oficiais da Guincho RJ</h2>
<p><strong>Empresa:</strong> Guincho RJ</p>
<p><strong>Atuação:</strong> desde 1995</p>
<p><strong>Endereço:</strong> Avenida Presidente Vargas, 1120 — Centro, Rio de Janeiro – RJ, CEP 20071-002</p>
<p><strong>E-mail:</strong> <a href="mailto:contato@guinchorj.com">contato@guinchorj.com</a></p>
<p><strong>Telefone/WhatsApp:</strong> <a href="tel:+5521959543043">(21) 95954-3043</a></p>
<p><strong>Site:</strong> <a href="../../">guinchorj.com</a></p>
"""


def format_tables(html: str) -> str:
    def wrap_table(match: re.Match[str]) -> str:
        table_html = match.group(0)
        table_html = table_html.replace(
            "<table>",
            '<table class="table table-bordered artigo-table">',
            1,
        )
        return f'<div class="table-responsive">{table_html}</div>'

    return re.sub(r"<table>.*?</table>", wrap_table, html, flags=re.DOTALL)


def inject_assets(html: str) -> str:
    assets = '<link rel="stylesheet" href="../article-tables.css">'
    if "article-tables.css" in html:
        return html
    return html.replace("</head>", assets + "</head>", 1)


def fix_paths(html: str) -> str:
    return html.replace("../../../", "../../")


def fix_cross_article_links(html: str) -> str:
    """Em /blog/{slug}/, links ./outro-slug/ devem ser ../outro-slug/."""
    return re.sub(r'href="\./([^"/][^"]*)/"', r'href="../\1/"', html)


def fix_nav_blog_link(html: str) -> str:
    """Artigos em /blog/{slug}/ devem apontar o menu Blog para /blog/, não para a home."""
    return html.replace(
        '<a href="../../" class="nav-link">Blog</a>',
        '<a href="../" class="nav-link">Blog</a>',
    )


def build_body(title: str, body_path: Path, closing_heading: str) -> str:
    raw = body_path.read_text(encoding="utf-8").strip()
    raw = re.sub(r"<h1>.*?</h1>\s*", "", raw, count=1, flags=re.DOTALL)
    raw = fix_cross_article_links(raw)
    raw = format_tables(raw)
    closing_marker = f"<h2>{closing_heading}</h2>"
    if closing_marker not in raw:
        raise SystemExit(
            f'Seção final não encontrada: {closing_marker}\n'
            "Defina um título específico (ex.: Quando Procurar Assistência Especializada). "
            "Não use o subtítulo Conclusão."
        )
    raw = raw.replace(closing_marker, SERVICE_CTA + closing_marker, 1)
    raw += COMPANY_FOOTER
    return (
        f'<p class="lead" style="text-align:center">{title}</p>'
        f'<p class="post-dates">Publicado em: <time datetime="{DATE}">07/06/2026</time> '
        f"- Atualizado em: <time datetime=\"{DATE}\">07/06/2026</time></p>"
        f'<article class="artigo-manual-do-motorista">{raw}</article>'
    )


def build_section(title: str, body_html: str) -> str:
    return (
        f'<section class="services-details-area ptb-100">'
        f'<h2 class="skip-link">{title}</h2>'
        f'<div class="container"> <div class="row"> '
        f'<article class="col-lg-12 col-md-12">'
        f'<h2 class="skip-link">{title}</h2>'
        f'<div class="services-details-desc"> '
        f'<div class="image" style="display:flex;align-items:center;justify-content:center;"> </div> '
        f'<div class="writen_content"> {body_html} </article> </div> </article> </div> </div> </section>'
    )


def replace_head(html: str, title: str, description: str, canonical: str) -> str:
    html = re.sub(r"<title>[^<]+</title>", f"<title>{title}</title>", html, count=1)
    html = re.sub(
        r'name="description" content="[^"]*"',
        f'name="description" content="{description}"',
        html,
        count=1,
    )
    html = re.sub(
        r'<link rel="canonical" href="[^"]+"',
        f'<link rel="canonical" href="{canonical}"',
        html,
        count=1,
    )
    html = re.sub(
        r'property="og:title" content="[^"]+"',
        f'property="og:title" content="{title}"',
        html,
        count=1,
    )
    html = re.sub(
        r'property="og:description" content="[^"]+"',
        f'property="og:description" content="{description}"',
        html,
        count=1,
    )
    html = re.sub(
        r'property="og:url" content="[^"]+"',
        f'property="og:url" content="{canonical}"',
        html,
        count=1,
    )
    html = re.sub(
        r'name="twitter:title" content="[^"]+"',
        f'name="twitter:title" content="{title}"',
        html,
        count=1,
    )
    html = re.sub(
        r'name="twitter:description" content="[^"]+"',
        f'name="twitter:description" content="{description}"',
        html,
        count=1,
    )
    html = re.sub(
        r'property="og:updated_time" content="[^"]+"',
        f'property="og:updated_time" content="{DATETIME}"',
        html,
        count=1,
    )
    return html


def replace_page_title(main: str, title: str, short_title: str) -> str:
    breadcrumb = (
        '<ol class="breadcrumb" style="display:flex;align-items:center;justify-content:center;">'
        '<li class="breadcrumb-item"><a title="Guincho e Reboque Rio de Janeiro" href="../../">'
        "<span>Guincho e Reboque Rio de Janeiro</span></a></li>"
        '<li class="breadcrumb-item"><a title="Blog" href="../"><span>Blog</span></a></li>'
        f'<li class="breadcrumb-item"><a title="{CLUSTER_TITLE}" href="../manual-do-motorista/">'
        f"<span>{CLUSTER_TITLE}</span></a></li>"
        f'<li class="breadcrumb-item active" aria-current="page">'
        f'<a title="{short_title}" href="./"><span>{short_title}</span></a></li>'
        "</ol>"
    )
    header = (
        f'<header class="page-title-area item-bg-1"><div class="d-table"><div class="d-table-cell">'
        f'<div class="container"><div class="page-title-content"><h1>{title}</h1>'
        f'<nav aria-label="Trilha de navegação">{breadcrumb}</nav>'
        f"</div></div></div></div></header>"
    )
    return re.sub(
        r'<header class="page-title-area item-bg-1">.*?</header>',
        header,
        main,
        count=1,
        flags=re.DOTALL,
    )


def replace_section(main: str, section: str) -> str:
    return re.sub(
        r'<section class="services-details-area ptb-100">.*?</section>',
        section,
        main,
        count=1,
        flags=re.DOTALL,
    )


def replace_schema(html: str, title: str, description: str, canonical: str, short_title: str) -> str:
    def repl(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)

        graph = data.get("@graph", [data])
        for node in graph:
            if node.get("@type") == "BlogPosting":
                node["headline"] = title
                node["description"] = description
                node["datePublished"] = DATETIME
                node["dateModified"] = DATETIME
                node["url"] = canonical
                node["articleSection"] = CATEGORY
            if node.get("@type") == "BreadcrumbList":
                node["itemListElement"] = [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Home",
                        "item": "https://guinchorj.com/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "Blog",
                        "item": "https://guinchorj.com/blog/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": CLUSTER_TITLE,
                        "item": f"https://guinchorj.com/blog/{CLUSTER_SLUG}/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 4,
                        "name": short_title,
                        "item": canonical,
                    },
                ]
        return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False, separators=(",", ":"))}</script>'

    return re.sub(
        r'<script type="application/ld\+json">(\{.*?\})</script>',
        repl,
        html,
        count=1,
        flags=re.DOTALL,
    )


def build_article(
    slug: str,
    title: str,
    description: str,
    closing_heading: str,
    short_title: str | None = None,
) -> Path:
    short_title = short_title or title.split(":")[0].strip()
    body_path = CONTENT_DIR / f"{slug}-body.html"
    if not body_path.exists():
        raise SystemExit(f"Conteúdo não encontrado: {body_path}")

    output = ROOT / f"blog/{slug}/index.html"
    canonical = f"https://guinchorj.com/blog/{slug}/"

    html = fix_nav_blog_link(fix_paths(TEMPLATE.read_text(encoding="utf-8")))
    html = replace_head(html, title, description, canonical)
    html = replace_schema(html, title, description, canonical, short_title)
    html = inject_assets(html)

    main_match = re.search(r"(<main[^>]*>)(.*?)(</main>)", html, re.DOTALL)
    if not main_match:
        raise SystemExit("main não encontrado no template")

    body_html = build_body(title, body_path, closing_heading)
    main_inner = replace_page_title(main_match.group(2), title, short_title)
    main_inner = replace_section(main_inner, build_section(title, body_html))
    html = html[: main_match.start()] + main_match.group(1) + main_inner + main_match.group(3) + html[main_match.end() :]

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(html, encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera satélite do Manual do Motorista")
    parser.add_argument("slug", help="Slug do artigo, ex.: bateria-descarregada")
    parser.add_argument("title", help="Título completo do artigo")
    parser.add_argument("description", help="Meta description")
    parser.add_argument(
        "--closing-heading",
        required=True,
        help='Título da seção final (ex.: "Quando Procurar Assistência Especializada")',
    )
    parser.add_argument("--short-title", help="Título curto para breadcrumb")
    args = parser.parse_args()

    output = build_article(
        args.slug,
        args.title,
        args.description,
        args.closing_heading,
        args.short_title,
    )
    print(f"Gerado: {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
