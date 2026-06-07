#!/usr/bin/env python3
"""Fase 5: acessibilidade, landmarks, headings, figure, FAQ e JSON-LD de listagens."""

from __future__ import annotations

import copy
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

JSON_LD_PATTERN = re.compile(
    r'(<script type="application/ld\+json">)(.*?)(</script>)',
    re.DOTALL,
)
H1_HEADER_PATTERN = re.compile(
    r'<header class="page-title-area[^"]*"[^>]*>.*?<h1[^>]*>(.*?)</h1>',
    re.DOTALL | re.IGNORECASE,
)
H1_PATTERN = re.compile(r"<h1[^>]*>(.*?)</h1>", re.DOTALL | re.IGNORECASE)
POST_DATES_PATTERN = re.compile(
    r'(<p class="post-dates">)\s*Publicado em:\s*(\d{2}/\d{2}/\d{4})'
    r'(?:\s*-\s*Atualizado em:\s*(\d{2}/\d{2}/\d{4}))?',
    re.IGNORECASE,
)
FAQ_NUMBERED_H2 = re.compile(
    r"(<section class=\"faq-guincho-rj\"[^>]*>.*?)(</section>)",
    re.DOTALL,
)
WRITEN_FIRST_H2 = re.compile(
    r'(<(?:div|article) class="writen_content">\s*)<h2([^>]*)>(.*?)</h2>',
    re.DOTALL | re.IGNORECASE,
)
SERVICE_IMAGE_OPEN = re.compile(
    r'(<div class="services-details-desc">.*?)(<div class="image"[^>]*>)',
    re.DOTALL,
)
LEAD_CSS = ".writen_content h2 {"
LEAD_CSS_EXTENDED = ".writen_content h2,.writen_content p.lead {"


def iter_html_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(ROOT.rglob("*.html")):
        if "wp-content" in path.parts:
            continue
        if path.name == "_downloads.html":
            continue
        files.append(path)
    return files


def load_phase4():
    spec = importlib.util.spec_from_file_location(
        "phase4",
        ROOT / "scripts" / "update-semantic-html-phase4.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PHASE4 = load_phase4()


def normalize_heading(text: str) -> str:
    clean = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", clean.strip().lower())


def br_date_to_iso(value: str) -> str:
    day, month, year = value.split("/")
    return f"{year}-{month}-{day}"


def is_blog_post(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if rel.parts[0] != "blog" or rel.name != "index.html":
        return False
    if len(rel.parts) <= 2:
        return False
    if "page" in rel.parts:
        return False
    if len(rel.parts) == 3 and rel.parts[1] == "reboque-e-guincho":
        return False
    return True


def is_blog_listing(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel in {"blog/index.html", "blog/reboque-e-guincho/index.html"}:
        return True
    if re.fullmatch(r"blog/page/\d+/index\.html", rel):
        return True
    return bool(re.fullmatch(r"blog/reboque-e-guincho/page/\d+/index\.html", rel))


def is_service_page(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return len(rel.parts) >= 2 and rel.parts[0] == "servico"


def extract_h1(html: str) -> str | None:
    header_match = H1_HEADER_PATTERN.search(html)
    if header_match:
        return header_match.group(1)
    any_match = H1_PATTERN.search(html)
    return any_match.group(1) if any_match else None


def headings_match(h1_text: str, h2_text: str) -> bool:
    h1_norm = normalize_heading(h1_text)
    h2_norm = normalize_heading(h2_text)
    if not h1_norm or not h2_norm:
        return False
    if h1_norm == h2_norm:
        return True
    if len(h1_norm) < 12:
        return False
    return h1_norm in h2_norm or h2_norm in h1_norm


def apply_post_dates(html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        published = match.group(2)
        updated = match.group(3)
        pub_iso = br_date_to_iso(published)
        pub_tag = f'<time datetime="{pub_iso}">{published}</time>'
        if updated:
            upd_iso = br_date_to_iso(updated)
            upd_tag = f'<time datetime="{upd_iso}">{updated}</time>'
            body = f"Publicado em: {pub_tag} - Atualizado em: {upd_tag}"
        else:
            body = f"Publicado em: {pub_tag}"
        return f"{match.group(1)}{body}"

    return POST_DATES_PATTERN.sub(repl, html)


def replace_duplicate_content_h2(html: str) -> str:
    h1_text = extract_h1(html)
    if not h1_text:
        return html

    def repl(match: re.Match[str]) -> str:
        h2_text = match.group(3)
        if 'class="sr-only"' in match.group(2):
            return match.group(0)
        if not headings_match(h1_text, h2_text):
            return match.group(0)
        attrs = match.group(2)
        if 'class="' in attrs:
            attrs = re.sub(
                r'class="[^"]*"',
                'class="lead"',
                attrs,
                count=1,
            )
        elif attrs.strip():
            attrs = f' class="lead"{attrs}'
        else:
            attrs = ' class="lead"'
        return f"{match.group(1)}<p{attrs}>{h2_text}</p>"

    return WRITEN_FIRST_H2.sub(repl, html, count=1)


def apply_lead_styles(html: str) -> str:
    if LEAD_CSS_EXTENDED in html or LEAD_CSS not in html:
        return html
    return html.replace(LEAD_CSS, LEAD_CSS_EXTENDED, 1)


def apply_home_landmarks(html: str, path: Path) -> str:
    if path.relative_to(ROOT).as_posix() != "index.html":
        return html

    updated = html
    if '<section class="about-area pb-100">' in updated:
        updated = updated.replace(
            '<section class="about-area pb-100">',
            '<section class="about-area pb-100" aria-labelledby="about-titulo">',
            1,
        )
        updated = updated.replace(
            '<div class="about-content"><h3>',
            '<div class="about-content"><h3 id="about-titulo">',
            1,
        )

    for marker in (
        '<section class="solution-area">',
        '<section class="solution-area pb-70">',
    ):
        if marker in updated and 'aria-label="Solicite um orçamento"' not in updated:
            updated = updated.replace(
                marker,
                marker[:-1] + ' aria-label="Solicite um orçamento">',
                1,
            )

    blog_section = '<section class="blog-area pt-70 pb-70">'
    if blog_section in updated:
        updated = updated.replace(
            blog_section,
            '<section class="blog-area pt-70 pb-70" aria-labelledby="blog-titulo">',
            1,
        )
        updated = updated.replace(
            '<div class="section-title"><h2>Blog</h2></div>',
            '<div class="section-title"><h2 id="blog-titulo">Blog</h2></div>',
            1,
        )

    banner_match = re.search(r'<div class="(main-banner-area[^"]*)"', updated)
    if banner_match and "hero-titulo" not in updated:
        updated = updated.replace(
            banner_match.group(0),
            f'<section class="{banner_match.group(1)}" '
            f'aria-labelledby="hero-titulo"',
            1,
        )
        updated = updated.replace(
            '<h2 style="font-size:55px;color:#ffffff;font-weight:700;">',
            '<h2 id="hero-titulo" style="font-size:55px;color:#ffffff;font-weight:700;">',
            1,
        )
        next_section = updated.find(
            '<section class="blog-area services-section',
            updated.find('<section class="main-banner-area'),
        )
        if next_section > 0:
            prefix = updated[:next_section].rstrip()
            if prefix.endswith("</header>"):
                prefix = prefix[:-9].rstrip().removesuffix("</div>") + "</section>"
            elif prefix.endswith("</div>"):
                prefix = prefix.removesuffix("</div>") + "</section>"
            updated = prefix + updated[next_section:]

    updated = updated.replace(
        "</div></nav></div></div></section></header>",
        "</div></nav></div></div></div></header>",
        1,
    )
    updated = updated.replace(
        '</div></div></div></div></div></header><section class="blog-area services-section',
        '</div></div></div></div></div></section><section class="blog-area services-section',
        1,
    )

    return updated


def apply_solution_area_label(html: str, path: Path) -> str:
    if path.relative_to(ROOT).as_posix() == "index.html":
        return html

    updated = html
    for marker in (
        '<section class="solution-area pb-70">',
        '<section class="solution-area">',
    ):
        if marker not in updated:
            continue
        if 'aria-label="Solicite um orçamento"' in updated:
            return updated
        updated = updated.replace(
            marker,
            marker[:-1] + ' aria-label="Solicite um orçamento">',
            1,
        )
    return updated


def apply_footer_nav(html: str) -> str:
    updated = html
    for title in ("Institucional", "Serviços"):
        open_marker = f'<h3>{title}</h3><ul class="quick-links">'
        nav_open = f'<h3>{title}</h3><nav aria-label="{title}"><ul class="quick-links">'
        if open_marker in updated and nav_open not in updated:
            updated = updated.replace(open_marker, nav_open, 1)
            close_marker = nav_open
            start = updated.find(close_marker)
            if start < 0:
                continue
            ul_end = updated.find("</ul>", start)
            if ul_end < 0:
                continue
            updated = updated[: ul_end + 5] + "</nav>" + updated[ul_end + 5 :]
    return updated


def apply_service_figure(html: str) -> str:
    match = SERVICE_IMAGE_OPEN.search(html)
    if not match:
        return html

    prefix = match.group(1)
    image_open = match.group(2).replace("<div", "<figure", 1)
    start = match.start(2)
    end = html.find('<div class="writen_content">', start)
    if end < 0:
        return html

    close_idx = html.rfind("</div>", start, end)
    if close_idx < 0:
        return html

    return (
        html[: match.start()]
        + prefix
        + image_open
        + html[match.end(2) : close_idx]
        + "</figure>"
        + html[close_idx + 6 :]
    )


def apply_faq_semantics(html: str, path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel != "perguntas-frequentes-sobre-guincho-e-reboque-no-rj/index.html":
        return html

    updated = html
    if 'aria-labelledby="faq-titulo"' not in updated:
        updated = updated.replace(
            '<section class="faq-guincho-rj">',
            '<section class="faq-guincho-rj" aria-labelledby="faq-titulo">',
            1,
        )
        updated = updated.replace(
            '<h2 class="sr-only">',
            '<h2 id="faq-titulo" class="sr-only">',
            1,
        )

    updated = updated.replace(
        '<section class="faq-guincho-rj" aria-labelledby="faq-titulo">Reunimos',
        '<section class="faq-guincho-rj" aria-labelledby="faq-titulo"><p>Reunimos',
        1,
    )

    def demote_questions(match: re.Match[str]) -> str:
        chunk = match.group(1)
        chunk = re.sub(
            r"<h2>",
            "<h3>",
            chunk,
        )
        chunk = chunk.replace("</h2>", "</h3>")
        return chunk + match.group(2)

    updated = FAQ_NUMBERED_H2.sub(demote_questions, updated, count=1)
    return updated


def upgrade_blog_listing_json_ld(html: str) -> str:
    match = JSON_LD_PATTERN.search(html)
    if not match:
        return html

    payload = match.group(2).strip()
    if not payload:
        return html

    data = json.loads(payload)
    if "@graph" in data:
        return html

    if data.get("@type") != "WebPage":
        return html

    collection = copy.deepcopy(data)
    collection["@type"] = "CollectionPage"
    website = collection.pop("isPartOf", None)

    graph: list[dict] = [collection]
    if isinstance(website, dict):
        graph.append(website)

    aligned = {
        "@context": data.get("@context", "https://schema.org"),
        "@graph": graph,
    }
    replacement = (
        f"{match.group(1)}{PHASE4.serialize_json_ld(aligned)}{match.group(3)}"
    )
    return html[: match.start()] + replacement + html[match.end() :]


def apply_phase5(html: str, path: Path) -> str:
    if "<body" not in html:
        return html

    updated = html
    if is_blog_post(path):
        updated = apply_post_dates(updated)

    updated = replace_duplicate_content_h2(updated)
    updated = apply_lead_styles(updated)
    updated = apply_home_landmarks(updated, path)
    updated = apply_solution_area_label(updated, path)
    updated = apply_footer_nav(updated)

    if is_service_page(path):
        updated = apply_service_figure(updated)

    updated = apply_faq_semantics(updated, path)

    if is_blog_listing(path):
        updated = upgrade_blog_listing_json_ld(updated)

    return updated


def main() -> None:
    changed = 0
    for path in iter_html_files():
        original = path.read_text(encoding="utf-8")
        updated = apply_phase5(original, path)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1

    print(f"Páginas atualizadas: {changed}")


if __name__ == "__main__":
    main()
