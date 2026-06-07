#!/usr/bin/env python3
"""Remove links de serviço fora da região no conteúdo das páginas /servico/."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGIONS_FILE = ROOT / "scripts" / "service-regions.json"

ARTICLE_BLOCK = re.compile(
    r'(<article class="col-lg-(?:8|12)[^"]*">)(.*?)(</article>)',
    re.DOTALL,
)
A_TAG = re.compile(r"<a\b([^>]*)>(.*?)</a>", re.IGNORECASE | re.DOTALL)
HREF_ATTR = re.compile(r'\bhref="([^"]+)"', re.IGNORECASE)


def load_page_to_region() -> tuple[dict[str, str], dict[str, list[str]], set[str]]:
    regions: dict[str, list[str]] = json.loads(
        REGIONS_FILE.read_text(encoding="utf-8")
    )
    page_to_region: dict[str, str] = {}
    for region, slugs in regions.items():
        for slug in slugs:
            page_to_region[slug] = region

    all_slugs = {
        path.parent.name for path in (ROOT / "servico").glob("*/index.html")
    }
    return page_to_region, regions, all_slugs


def slug_from_href(href: str, all_slugs: set[str]) -> str | None:
    href = href.split("#")[0].split("?")[0].strip()
    if not href or href.startswith(
        ("tel:", "mailto:", "javascript:", "http://", "https://")
    ):
        return None

    patterns = (
        r"(?:^|/)servico/([^/]+)/?$",
        r"\.\./([^/]+)/?$",
        r"\.\./(?:\.\./)*servico/([^/]+)/?$",
    )
    for pattern in patterns:
        match = re.search(pattern, href)
        if match and match.group(1) in all_slugs:
            return match.group(1)
    return None


def allowed_content_slugs(
    slug: str,
    region: str,
    regions: dict[str, list[str]],
) -> set[str] | None:
    if region == "rio-geral":
        return None
    return set(regions[region]) - {slug}


def unwrap_out_of_region_links(
    content_html: str,
    allowed: set[str],
    all_slugs: set[str],
) -> tuple[str, int]:
    removed = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal removed
        attrs = match.group(1)
        inner = match.group(2)
        href_match = HREF_ATTR.search(attrs)
        if not href_match:
            return match.group(0)

        target = slug_from_href(href_match.group(1), all_slugs)
        if target is None or target in allowed:
            return match.group(0)

        removed += 1
        return inner

    return A_TAG.sub(repl, content_html), removed


def process_page(
    path: Path,
    page_to_region: dict[str, str],
    regions: dict[str, list[str]],
    all_slugs: set[str],
) -> int:
    slug = path.parent.name
    region = page_to_region[slug]
    allowed = allowed_content_slugs(slug, region, regions)
    if allowed is None:
        return 0

    html = path.read_text(encoding="utf-8")
    match = ARTICLE_BLOCK.search(html)
    if not match:
        return 0

    updated_content, removed = unwrap_out_of_region_links(
        match.group(2),
        allowed,
        all_slugs,
    )
    if removed == 0:
        return 0

    updated = (
        html[: match.start()]
        + match.group(1)
        + updated_content
        + match.group(3)
        + html[match.end() :]
    )
    path.write_text(updated, encoding="utf-8")
    return removed


def main() -> None:
    page_to_region, regions, all_slugs = load_page_to_region()

    changed_pages = 0
    removed_links = 0
    for path in sorted((ROOT / "servico").glob("*/index.html")):
        count = process_page(path, page_to_region, regions, all_slugs)
        if count:
            changed_pages += 1
            removed_links += count
            print(f"  {path.parent.name}: {count} link(s)")

    print(f"\nPáginas alteradas: {changed_pages}")
    print(f"Links removidos: {removed_links}")


if __name__ == "__main__":
    main()
