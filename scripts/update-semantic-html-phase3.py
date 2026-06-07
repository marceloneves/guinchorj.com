#!/usr/bin/env python3
"""Fase 3: HTML semântico em home, blog, listagens e páginas institucionais."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

HOME_H1 = "Guincho e Reboque barato e 24 horas no Rio de Janeiro"
HOME_H1_TAG = f'<h1 class="sr-only">{HOME_H1}</h1>'
MAIN_OPEN = '<main id="conteudo" role="main">'
MAIN_OPEN_WITH_H1 = f'{MAIN_OPEN}{HOME_H1_TAG}'

SERVICES_SECTION_OPEN = '<section class="blog-area services-section pt-70 pb-70">'
SERVICES_SECTION_SEMANTIC = (
    '<section class="blog-area services-section pt-70 pb-70" '
    'aria-labelledby="servicos-titulo">'
)
SERVICES_TITLE = (
    '<div class="section-title"><h2>Serviços</h2></div>'
)
SERVICES_TITLE_SEMANTIC = (
    '<div class="section-title"><h2 id="servicos-titulo">Serviços</h2></div>'
)

COL12_OPEN = '<div class="col-lg-12 col-md-12"> <div class="services-details-desc">'
COL12_ARTICLE_OPEN = (
    '<article class="col-lg-12 col-md-12"><div class="services-details-desc">'
)
WRITEN_OPEN = '<div class="writen_content">'
WRITEN_ARTICLE_OPEN = '<article class="writen_content">'
BLOG_ITEM_OPEN = '<div class="blog-item">'
BLOG_ITEM_ARTICLE_OPEN = '<article class="blog-item">'

CONTACT_ROW = (
    '<div class="section-title"> <h2>Fale conosco</h2> </div> <div class="row">'
)
CONTACT_ROW_ARTICLE = (
    '<div class="section-title"> <h2>Fale conosco</h2> </div> '
    '<article class="contact-content"><div class="row">'
)
CONTACT_CLOSE = (
    '</div> </div> </div> </div> </div> </section></main>'
)
CONTACT_CLOSE_ARTICLE = (
    '</div> </div> </div> </div></article> </div> </section></main>'
)

PAGE_TITLE_CLOSE = re.compile(
    r"</div></div></div></div></div>(<section class=\")",
)
BREADCRUMB_PATTERN = re.compile(
    r'<ul class="breadcrumb"([^>]*)>(.*?)</ul>',
    re.DOTALL,
)
BREADCRUMB_REPLACEMENT = (
    r'<nav aria-label="Trilha de navegação">'
    r'<ol class="breadcrumb"\1>\2</ol></nav>'
)
PAGINATION_PATTERN = re.compile(
    r'<div class="pagination-area">(.*?)</div>',
    re.DOTALL,
)
PAGINATION_REPLACEMENT = (
    r'<nav aria-label="Paginação" class="pagination-area">\1</nav>'
)


def load_phase2():
    spec = importlib.util.spec_from_file_location(
        "phase2",
        ROOT / "scripts" / "update-semantic-html-phase2.py",
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PHASE2 = load_phase2()


def wrap_block(
    html: str,
    *,
    open_marker: str,
    open_replacement: str,
    close_replacement: str,
    end_limit: str | None = None,
) -> str:
    if open_marker not in html:
        return html
    if open_replacement in html and open_marker not in html:
        return html

    start = html.find(open_marker)
    html = html[:start] + open_replacement + html[start + len(open_marker) :]

    root_tag = open_replacement.lstrip("<").split()[0]
    start = html.find(open_replacement)
    end = html.find(end_limit, start) if end_limit else len(html)
    if end < 0:
        end = len(html)

    depth = 0
    i = start
    while i < end:
        if html.startswith(f"<{root_tag}", i) or (
            html.startswith("<div", i) and not html.startswith("<div/", i)
        ):
            depth += 1
            i = html.find(">", i) + 1
            continue
        if html.startswith(f"</{root_tag}>", i):
            depth -= 1
            i += len(f"</{root_tag}>")
            continue
        if html.startswith("</div>", i):
            depth -= 1
            if depth == 0:
                return html[:i] + close_replacement + html[i + len("</div>") :]
            i += len("</div>")
            continue
        i += 1

    return html


def replace_all_blocks(
    html: str,
    *,
    open_marker: str,
    open_replacement: str,
    close_replacement: str,
    end_limit: str | None = None,
) -> str:
    while open_marker in html:
        updated = wrap_block(
            html,
            open_marker=open_marker,
            open_replacement=open_replacement,
            close_replacement=close_replacement,
            end_limit=end_limit,
        )
        if updated == html:
            break
        html = updated
    return html


def apply_page_title_header(html: str) -> str:
    if "page-title-area" not in html:
        return html
    if '<header class="page-title-area' in html:
        return html

    updated = html.replace(
        '<div class="page-title-area',
        '<header class="page-title-area',
        1,
    )
    return PAGE_TITLE_CLOSE.sub(
        r"</div></div></div></div></header>\1",
        updated,
        count=1,
    )


def apply_breadcrumb(html: str) -> str:
    if 'aria-label="Trilha de navegação"' in html:
        return html
    if '<ul class="breadcrumb"' not in html:
        return html
    return BREADCRUMB_PATTERN.sub(BREADCRUMB_REPLACEMENT, html, count=1)


def apply_home_h1(html: str) -> str:
    if MAIN_OPEN_WITH_H1 in html:
        return html
    if HOME_H1_TAG not in html or MAIN_OPEN not in html:
        return html

    updated = html.replace(HOME_H1_TAG, "", 1)
    return updated.replace(MAIN_OPEN, MAIN_OPEN_WITH_H1, 1)


def apply_services_section_aria(html: str) -> str:
    updated = html
    if SERVICES_SECTION_OPEN in updated and 'aria-labelledby="servicos-titulo"' not in updated:
        updated = updated.replace(SERVICES_SECTION_OPEN, SERVICES_SECTION_SEMANTIC, 1)
    if SERVICES_TITLE in updated and 'id="servicos-titulo"' not in updated:
        updated = updated.replace(SERVICES_TITLE, SERVICES_TITLE_SEMANTIC, 1)
    return updated


def apply_blog_items(html: str) -> str:
    return replace_all_blocks(
        html,
        open_marker=BLOG_ITEM_OPEN,
        open_replacement=BLOG_ITEM_ARTICLE_OPEN,
        close_replacement="</article>",
        end_limit="</main>",
    )


def apply_blog_post_article(html: str) -> str:
    if "services-details-area" not in html or COL12_OPEN not in html:
        return html
    return wrap_block(
        html,
        open_marker=COL12_OPEN,
        open_replacement=COL12_ARTICLE_OPEN,
        close_replacement="</article>",
        end_limit=PHASE2.SOLUTION_MARKER,
    )


def apply_institutional_article(html: str) -> str:
    if "services-details-area" in html:
        return html
    if WRITEN_OPEN not in html or WRITEN_ARTICLE_OPEN in html:
        return html
    return wrap_block(
        html,
        open_marker=WRITEN_OPEN,
        open_replacement=WRITEN_ARTICLE_OPEN,
        close_replacement="</article>",
        end_limit="</main>",
    )


def revert_writen_article_in_blog_posts(html: str) -> str:
    marker = '<article class="writen_content">'
    if "services-details-area" not in html or marker not in html:
        return html
    return wrap_block(
        html,
        open_marker=marker,
        open_replacement=WRITEN_OPEN,
        close_replacement="</div>",
        end_limit=PHASE2.SOLUTION_MARKER,
    )


def apply_contact_article(html: str) -> str:
    if "contact-area" not in html:
        return html
    if '<article class="contact-content">' in html:
        return html
    if CONTACT_ROW not in html:
        return html

    updated = html.replace(CONTACT_ROW, CONTACT_ROW_ARTICLE, 1)
    if CONTACT_CLOSE in updated:
        return updated.replace(CONTACT_CLOSE, CONTACT_CLOSE_ARTICLE, 1)
    return updated


def apply_pagination(html: str) -> str:
    if 'aria-label="Paginação"' in html:
        return html
    if '<div class="pagination-area">' not in html:
        return html
    return PAGINATION_PATTERN.sub(PAGINATION_REPLACEMENT, html, count=1)


def apply_service_layout(html: str) -> str:
    if PHASE2.COL8_OPEN not in html and PHASE2.ARTICLE_OPEN not in html:
        return html
    updated, _ok = PHASE2.apply_phase2(html)
    return updated


def iter_phase3_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(ROOT.rglob("*.html")):
        if "wp-content" in path.parts:
            continue
        if path.name == "_downloads.html":
            continue
        rel = path.relative_to(ROOT)
        if len(rel.parts) >= 2 and rel.parts[0] == "servico":
            continue
        files.append(path)
    return files


def apply_phase3(html: str, path: Path) -> tuple[str, bool]:
    if "<main" not in html:
        return html, False

    updated = html
    rel = path.relative_to(ROOT)

    if rel.as_posix() == "index.html":
        updated = apply_home_h1(updated)

    updated = apply_page_title_header(updated)
    updated = apply_breadcrumb(updated)
    updated = apply_service_layout(updated)
    updated = apply_blog_post_article(updated)
    updated = revert_writen_article_in_blog_posts(updated)
    updated = apply_institutional_article(updated)
    updated = apply_contact_article(updated)
    updated = apply_services_section_aria(updated)
    updated = apply_blog_items(updated)
    updated = apply_pagination(updated)

    return updated, True


def validate_page(html: str, path: Path) -> list[str]:
    errors: list[str] = []
    rel = path.relative_to(ROOT).as_posix()

    if rel == "index.html":
        if HOME_H1_TAG not in html:
            errors.append("home sem h1 no main")
        if MAIN_OPEN_WITH_H1 not in html.replace("\n", ""):
            if html.count(HOME_H1_TAG) != 1:
                errors.append("home h1 inconsistente")

    if (
        ('<div class="page-title-area' in html or '<header class="page-title-area' in html)
        and '<header class="page-title-area' not in html
    ):
        errors.append("page-title sem header")

    if '<ul class="breadcrumb"' in html:
        errors.append("breadcrumb ainda em ul")

    if BLOG_ITEM_OPEN in html:
        errors.append("blog-item ainda em div")

    if (
        "services-details-area" in html
        and COL12_OPEN in html
        and COL12_ARTICLE_OPEN not in html
    ):
        errors.append("post sem article col-lg-12")

    if (
        "about-area" in html
        and 'class="writen_content"' in html
        and '<article class="writen_content">' not in html
        and "services-details-area" not in html
    ):
        errors.append("institucional sem article")

    if (
        rel == "contato/index.html"
        and '<article class="contact-content">' not in html
    ):
        errors.append("contato sem article")

    if (
        '<div class="pagination-area">' in html
        and 'aria-label="Paginação"' not in html
    ):
        errors.append("paginação sem nav")

    if SERVICES_SECTION_OPEN in html and 'aria-labelledby="servicos-titulo"' not in html:
        errors.append("seção serviços sem aria-labelledby")

    return errors


def main() -> None:
    changed = 0
    skipped = 0
    failed: list[str] = []
    validation_errors: list[str] = []

    for path in iter_phase3_files():
        original = path.read_text(encoding="utf-8")
        updated, ok = apply_phase3(original, path)
        if not ok:
            skipped += 1
            failed.append(str(path.relative_to(ROOT)))
            continue

        errors = validate_page(updated, path)
        if errors:
            validation_errors.append(
                f"{path.relative_to(ROOT)}: {', '.join(errors)}"
            )
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
