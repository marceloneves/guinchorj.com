#!/usr/bin/env python3
"""Atualiza sidebar de páginas /servico/ para silo regional."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGIONS_FILE = Path(__file__).resolve().parent / "service-regions.json"
REGIONAL_FILE = Path(__file__).resolve().parent / "regional-services.json"
REFERENCE = ROOT / "servico/reboque-em-copacabana/index.html"

SIDEBAR = re.compile(
    r'(<section class="widget widget_categories">\s*'
    r'<h2 class="widget-title">Serviços</h2>\s*<ul>)(.*?)(</ul>\s*</section>)',
    re.DOTALL,
)
LINK_ITEM = re.compile(
    r'<li><a href="\.\./([^/]+)/" title="([^"]*)">([^<]*)</a></li>'
)


def metadata_from_service_page(path: Path) -> tuple[str, str]:
    content = path.read_text(encoding="utf-8")
    h1_match = re.search(r"<h1[^>]*>([^<]+)</h1>", content)
    title_match = re.search(r"<title>([^<|]+)", content)
    label = html.unescape((h1_match or title_match).group(1).strip())
    return label, label


def load_metadata() -> dict[str, tuple[str, str]]:
    metadata: dict[str, tuple[str, str]] = {}

    content = REFERENCE.read_text(encoding="utf-8")
    match = SIDEBAR.search(content)
    if match:
        metadata.update(
            {slug: (title, text) for slug, title, text in LINK_ITEM.findall(match.group(2))}
        )

    for path in sorted((ROOT / "servico").glob("*/index.html")):
        slug = path.parent.name
        if slug not in metadata:
            metadata[slug] = metadata_from_service_page(path)

    return metadata


def load_region_map() -> dict[str, str]:
    regions = json.loads(REGIONS_FILE.read_text(encoding="utf-8"))
    page_to_region: dict[str, str] = {}
    duplicates: dict[str, list[str]] = {}

    for region, slugs in regions.items():
        for slug in slugs:
            if slug in page_to_region:
                duplicates.setdefault(slug, [page_to_region[slug]]).append(region)
            page_to_region[slug] = region

    if duplicates:
        details = ", ".join(f"{slug}: {regs}" for slug, regs in duplicates.items())
        raise SystemExit(f"Slugs em mais de uma região: {details}")

    all_slugs = {path.parent.name for path in (ROOT / "servico").glob("*/index.html")}
    missing = sorted(all_slugs - set(page_to_region))
    extra = sorted(set(page_to_region) - all_slugs)
    if missing:
        raise SystemExit(f"Páginas sem região ({len(missing)}): {', '.join(missing)}")
    if extra:
        raise SystemExit(f"Slugs de região inexistentes: {', '.join(extra)}")

    return page_to_region


def load_region_slugs() -> dict[str, list[str]]:
    return json.loads(REGIONS_FILE.read_text(encoding="utf-8"))


def build_sidebar_links(
    current_slug: str,
    region: str,
    region_slugs: dict[str, list[str]],
    metadata: dict[str, tuple[str, str]],
) -> str:
    if region == "rio-geral":
        slugs = json.loads(REGIONAL_FILE.read_text(encoding="utf-8"))
    else:
        slugs = region_slugs[region]

    parts: list[str] = []
    for slug in slugs:
        if slug == current_slug:
            continue
        title, text = metadata[slug]
        parts.append(
            f'<li><a href="../{slug}/" title="{title}">{text}</a></li>'
        )
    return "".join(parts)


def update_file(
    path: Path,
    page_to_region: dict[str, str],
    region_slugs: dict[str, list[str]],
    metadata: dict[str, tuple[str, str]],
) -> bool:
    content = path.read_text(encoding="utf-8")
    match = SIDEBAR.search(content)
    if not match:
        return False

    current_slug = path.parent.name
    region = page_to_region[current_slug]
    new_items = build_sidebar_links(current_slug, region, region_slugs, metadata)
    updated = SIDEBAR.sub(rf"\1{new_items}\3", content, count=1)

    if updated != content:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    page_to_region = load_region_map()
    region_slugs = load_region_slugs()
    metadata = load_metadata()

    changed = 0
    counts: dict[str, int] = {}
    for path in sorted((ROOT / "servico").glob("*/index.html")):
        region = page_to_region[path.parent.name]
        if update_file(path, page_to_region, region_slugs, metadata):
            changed += 1
            counts[region] = counts.get(region, 0) + 1

    print(f"Páginas atualizadas: {changed}")
    for region in sorted(counts):
        print(f"  {region}: {counts[region]} páginas")


if __name__ == "__main__":
    main()
