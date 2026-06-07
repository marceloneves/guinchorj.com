#!/usr/bin/env python3
"""Fase 1: landmarks globais (header, main, footer, skip link)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SKIP_LINK = (
    '<a class="skip-link" href="#conteudo">Ir para o conteúdo</a>'
)
SKIP_CSS = (
    ".skip-link{position:absolute;left:-9999px;z-index:99999;padding:8px 16px;"
    "background:#1e73be;color:#fff;text-decoration:none;font-weight:600}"
    ".skip-link:focus{left:16px;top:16px;width:auto;height:auto;overflow:visible}"
)

MAIN_PATTERN = re.compile(
    r"(</div></nav></div></div></div>)((?:<style>.*?</style>)?)<main(?![^>]*\bid=)([^>]*)>",
    re.DOTALL,
)
MAIN_REPLACEMENT = r'\1</header>\2<main id="conteudo" role="main"\3>'
MAIN_ALREADY = re.compile(
    r"(</div></nav></div></div></div>)((?:<style>.*?</style>)?)<main[^>]*\bid=\"conteudo\"",
    re.DOTALL,
)


def inject_skip_css(html: str) -> str:
    if ".skip-link:focus" in html:
        return html
    marker = "/* Force absolute URLs for icon webfonts"
    if marker in html:
        return html.replace(marker, f"{SKIP_CSS} {marker}", 1)
    return html.replace("<style>", f"<style>{SKIP_CSS}", 1)


def apply_phase1(html: str) -> tuple[str, bool]:
    if '<body>' not in html or "<main" not in html:
        return html, False

    if 'class="skip-link"' not in html:
        if "<header role=\"banner\">" not in html:
            html = html.replace(
                "<body>",
                f'<body>{SKIP_LINK}<header role="banner">',
                1,
            )

    if 'id="conteudo"' not in html:
        if MAIN_ALREADY.search(html):
            pass
        elif MAIN_PATTERN.search(html):
            html = MAIN_PATTERN.sub(MAIN_REPLACEMENT, html, count=1)
        else:
            return html, False

    if 'role="contentinfo"' not in html and '<footer class="footer-area' in html:
        html = html.replace(
            '<footer class="footer-area',
            '<footer role="contentinfo" class="footer-area',
            1,
        )

    html = inject_skip_css(html)
    return html, True


def iter_html_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(ROOT.rglob("*.html")):
        if "wp-content" in path.parts:
            continue
        files.append(path)
    return files


def main() -> None:
    changed = 0
    skipped = 0
    failed: list[str] = []

    for path in iter_html_files():
        original = path.read_text(encoding="utf-8")
        updated, ok = apply_phase1(original)
        if not ok:
            skipped += 1
            failed.append(str(path.relative_to(ROOT)))
            continue
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1

    print(f"Páginas atualizadas: {changed}")
    if skipped:
        print(f"Páginas ignoradas (sem padrão): {skipped}")
        for item in failed:
            print(f"  - {item}")


if __name__ == "__main__":
    main()
