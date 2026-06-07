#!/usr/bin/env python3
"""Reduz links do rodapé 'Serviços' para silo regional em todo o site."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = Path(__file__).resolve().parent / "regional-services.json"
REFERENCE = ROOT / "index.html"
ANCHOR_SLUG = "reboque-zona-oeste"

FOOTER_BLOCK = re.compile(
    r"(<h3>Serviços</h3><ul class=\"quick-links\">)(.*?)(</ul></div></div><div class=\"col-lg-3 col-md-6\"><div class=\"single-footer-widget\"><h3>Contato</h3>)",
    re.DOTALL,
)
METADATA_ITEM = re.compile(
    r'<li><a href="(?:\.\./)*servico/([^/]+)/" title="([^"]*)">([^<]*)</a></li>'
)


def metadata_from_service_page(path: Path) -> tuple[str, str]:
    content = path.read_text(encoding="utf-8")
    h1_match = re.search(r"<h1[^>]*>([^<]+)</h1>", content)
    title_match = re.search(r"<title>([^<|]+)", content)
    label = html.unescape((h1_match or title_match).group(1).strip())
    return label, label


def load_metadata() -> dict[str, tuple[str, str]]:
    content = REFERENCE.read_text(encoding="utf-8")
    items = METADATA_ITEM.findall(content)
    metadata = {slug: (title, text) for slug, title, text in items}

    for path in sorted((ROOT / "servico").glob("*/index.html")):
        slug = path.parent.name
        if slug not in metadata:
            metadata[slug] = metadata_from_service_page(path)

    return metadata


def detect_href_prefix(html: str) -> str | None:
    match = re.search(
        rf'<h3>Serviços</h3><ul class="quick-links">.*?href="([^"]*{re.escape(ANCHOR_SLUG)}/)"',
        html,
        re.DOTALL,
    )
    if not match:
        return None
    return match.group(1).replace(f"{ANCHOR_SLUG}/", "")


def build_links_html(slugs: list[str], metadata: dict[str, tuple[str, str]], href_prefix: str) -> str:
    parts: list[str] = []
    for slug in slugs:
        title, text = metadata[slug]
        parts.append(
            f'<li><a href="{href_prefix}{slug}/" title="{title}">{text}</a></li>'
        )
    return "".join(parts)


def update_file(path: Path, slugs: list[str], metadata: dict[str, tuple[str, str]]) -> bool:
    content = path.read_text(encoding="utf-8")
    match = FOOTER_BLOCK.search(content)
    if not match:
        return False

    href_prefix = detect_href_prefix(content)
    if href_prefix is None:
        return False

    new_items = build_links_html(slugs, metadata, href_prefix)
    updated = FOOTER_BLOCK.sub(rf"\1{new_items}\3", content, count=1)

    if updated != content:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def iter_pages() -> list[Path]:
    pages: list[Path] = []
    for path in sorted(ROOT.rglob("index.html")):
        if "wp-content" in path.parts:
            continue
        pages.append(path)
    return pages


def main() -> None:
    slugs = json.loads(CONFIG.read_text(encoding="utf-8"))
    metadata = load_metadata()

    missing = [slug for slug in slugs if slug not in metadata]
    if missing:
        raise SystemExit(f"Metadados ausentes para: {', '.join(missing)}")

    changed = 0
    skipped = 0
    for path in iter_pages():
        if update_file(path, slugs, metadata):
            changed += 1
        elif FOOTER_BLOCK.search(path.read_text(encoding="utf-8")):
            skipped += 1

    print(f"Páginas atualizadas: {changed}")
    if skipped:
        print(f"Páginas com rodapé não alteradas: {skipped}")
    print(f"Links regionais no rodapé: {len(slugs)}")


if __name__ == "__main__":
    main()
