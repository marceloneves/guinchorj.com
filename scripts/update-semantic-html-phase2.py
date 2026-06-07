#!/usr/bin/env python3
"""Fase 2: HTML semântico nas páginas de serviço (/servico/*/index.html)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SERVICE_DIR = ROOT / "servico"

COL8_OPEN = '<div class="col-lg-8 col-md-12 order-first order-md-1">'
ARTICLE_OPEN = '<article class="col-lg-8 col-md-12 order-first order-md-1">'
SOLUTION_MARKER = '<section class="solution-area'
PAGE_TITLE_CLOSE = (
    "</div></div></div></div></div><section class=\"services-details-area"
)
PAGE_TITLE_CLOSE_HEADER = (
    "</div></div></div></div></header><section class=\"services-details-area"
)
SIDEBAR_OPEN = (
    '<div class="col-lg-4 col-md-12"> <nav class="widget-area" id="secondary">'
)
SIDEBAR_OPEN_SEMANTIC = (
    '<div class="col-lg-4 col-md-12">'
    '<aside aria-label="Serviços relacionados">'
    '<nav class="widget-area" id="secondary">'
)
SIDEBAR_TO_ARTICLE = (
    '</nav> </div> <div class="col-lg-8 col-md-12 order-first order-md-1">'
)
SIDEBAR_TO_ARTICLE_SEMANTIC = (
    '</nav></aside></div><article class="col-lg-8 col-md-12 order-first order-md-1">'
)

BREADCRUMB_PATTERN = re.compile(
    r'<ul class="breadcrumb"([^>]*)>(.*?)</ul>',
    re.DOTALL,
)
BREADCRUMB_REPLACEMENT = (
    r'<nav aria-label="Trilha de navegação">'
    r'<ol class="breadcrumb"\1>\2</ol></nav>'
)


def close_article_tag(html: str) -> str:
    """Substitui o </div> que fecha col-lg-8/article por </article>."""
    start = html.find(ARTICLE_OPEN)
    if start < 0:
        return html

    end_limit = html.find(SOLUTION_MARKER, start)
    if end_limit < 0:
        end_limit = len(html)

    depth = 0
    i = start
    while i < end_limit:
        if html.startswith("<article", i):
            depth += 1
            i = html.find(">", i) + 1
            continue
        if html.startswith("<div", i) and not html.startswith("<div/", i):
            depth += 1
            i = html.find(">", i) + 1
            continue
        if html.startswith("</article>", i):
            depth -= 1
            i += len("</article>")
            continue
        if html.startswith("</div>", i):
            depth -= 1
            if depth == 0:
                return html[:i] + "</article>" + html[i + len("</div>") :]
            i += len("</div>")
            continue
        i += 1

    return html


def fix_duplicate_h1(html: str) -> str:
    if html.lower().count("<h1") <= 1:
        return html

    first_close = html.lower().find("</h1>")
    if first_close < 0:
        return html

    tail_start = first_close + len("</h1>")
    tail = html[tail_start:]
    tail = re.sub(r"<h1([^>]*)>", r"<h2\1>", tail, count=1, flags=re.IGNORECASE)
    tail = re.sub(r"</h1>", r"</h2>", tail, count=1, flags=re.IGNORECASE)
    return html[:tail_start] + tail


def apply_phase2(html: str) -> tuple[str, bool]:
    if "services-details-area" not in html or "page-title-area" not in html:
        return html, False

    if COL8_OPEN not in html and ARTICLE_OPEN not in html:
        return html, False

    updated = html

    if '<header class="page-title-area' not in updated:
        if PAGE_TITLE_CLOSE not in updated:
            return html, False
        updated = updated.replace(
            '<div class="page-title-area',
            '<header class="page-title-area',
            1,
        )
        updated = updated.replace(PAGE_TITLE_CLOSE, PAGE_TITLE_CLOSE_HEADER, 1)

    if 'aria-label="Trilha de navegação"' not in updated:
        if not BREADCRUMB_PATTERN.search(updated):
            return html, False
        updated = BREADCRUMB_PATTERN.sub(BREADCRUMB_REPLACEMENT, updated, count=1)

    if '<aside aria-label="Serviços relacionados">' not in updated:
        if SIDEBAR_OPEN not in updated or SIDEBAR_TO_ARTICLE not in updated:
            return html, False
        updated = updated.replace(SIDEBAR_OPEN, SIDEBAR_OPEN_SEMANTIC, 1)
        updated = updated.replace(SIDEBAR_TO_ARTICLE, SIDEBAR_TO_ARTICLE_SEMANTIC, 1)
        updated = close_article_tag(updated)

    updated = fix_duplicate_h1(updated)

    if updated == html and '<aside aria-label="Serviços relacionados">' in html:
        return html, True

    return updated, True


def iter_service_pages() -> list[Path]:
    return sorted(SERVICE_DIR.glob("*/index.html"))


def validate_page(html: str) -> list[str]:
    errors: list[str] = []
    if '<header class="page-title-area' not in html:
        errors.append("sem header.page-title-area")
    if 'aria-label="Trilha de navegação"' not in html:
        errors.append("breadcrumb sem nav")
    if "<ol" not in html or 'class="breadcrumb"' not in html:
        errors.append("breadcrumb sem ol")
    if ARTICLE_OPEN not in html:
        errors.append("sem article")
    if '<aside aria-label="Serviços relacionados">' not in html:
        errors.append("sem aside")
    if html.lower().count("<h1") != 1:
        errors.append(f"h1={html.lower().count('<h1')}")
    return errors


def main() -> None:
    changed = 0
    skipped = 0
    failed: list[str] = []
    validation_errors: list[str] = []

    for path in iter_service_pages():
        original = path.read_text(encoding="utf-8")
        updated, ok = apply_phase2(original)
        if not ok:
            skipped += 1
            failed.append(str(path.relative_to(ROOT)))
            continue

        errors = validate_page(updated)
        if errors:
            validation_errors.append(f"{path.relative_to(ROOT)}: {', '.join(errors)}")
            continue

        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1

    print(f"Páginas atualizadas: {changed}")
    if skipped:
        print(f"Páginas ignoradas (sem padrão): {skipped}")
        for item in failed:
            print(f"  - {item}")
    if validation_errors:
        print(f"Falhas de validação: {len(validation_errors)}")
        for item in validation_errors[:20]:
            print(f"  - {item}")


if __name__ == "__main__":
    main()
