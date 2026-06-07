#!/usr/bin/env python3
"""Garante 1 link no writen_content de cada pilar para cada satélite do cluster."""

from __future__ import annotations

import html
import importlib.util
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGIONS_FILE = ROOT / "scripts" / "service-regions.json"
REGIONAL_FILE = ROOT / "scripts" / "regional-services.json"
REGIONAL_LINKS_SCRIPT = ROOT / "scripts" / "add-service-content-regional-links.py"

ARTICLE_BLOCK = re.compile(
    r'(<article class="col-lg-(?:8|12)[^"]*">)(.*?)(</article>)',
    re.DOTALL,
)
WRITTEN_CONTENT_BLOCK = re.compile(
    r'(<div class="writen_content">)(.*?)(</div>\s*</div>)(?=\s*(?:<nav|<aside|</article|$))',
    re.DOTALL,
)
HREF_PATTERN = re.compile(r'href="([^"]+)"')
CLUSTER_MARKER = 'aria-label="Satélites do cluster regional"'
EXTERNAL_CLUSTER_NAV = re.compile(
    rf'<nav[^>]*{re.escape(CLUSTER_MARKER)}[^>]*>.*?</nav>\s*',
    re.DOTALL | re.IGNORECASE,
)
CLUSTER_SECTION = re.compile(
    rf'<section[^>]*{re.escape(CLUSTER_MARKER)}[^>]*>.*?</section>\s*',
    re.DOTALL | re.IGNORECASE,
)
GEO_H2_KEYWORDS = (
    "bairro",
    "cidade",
    "município",
    "municipio",
    "localidade",
    "hub de reboque",
    "micro-regi",
)
UL_BLOCK = re.compile(r"(<ul>)(.*?)(</ul>)", re.DOTALL)
SATELLITE_LINK = re.compile(
    r'<a\s+href="\.\./([^"/]+)/"[^>]*>(.*?)</a>',
    re.DOTALL | re.IGNORECASE,
)


@dataclass(frozen=True)
class SatellitePage:
    slug: str
    title: str


def load_regional_links_module():
    spec = importlib.util.spec_from_file_location(
        "regional_links",
        REGIONAL_LINKS_SCRIPT,
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


REGIONAL_LINKS = load_regional_links_module()


def load_data() -> tuple[dict[str, list[str]], dict[str, str], set[str]]:
    regions: dict[str, list[str]] = json.loads(
        REGIONS_FILE.read_text(encoding="utf-8")
    )
    hubs: set[str] = set(json.loads(REGIONAL_FILE.read_text(encoding="utf-8")))
    pillars: dict[str, str] = {}
    for region, slugs in regions.items():
        if region in {"rio-geral", "tipos-veiculo"}:
            continue
        pillar = next((slug for slug in slugs if slug in hubs), None)
        if pillar:
            pillars[region] = pillar
    all_slugs = {path.parent.name for path in (ROOT / "servico").glob("*/index.html")}
    return regions, pillars, all_slugs


def slug_from_href(href: str, all_slugs: set[str]) -> str | None:
    href = href.split("#")[0].split("?")[0].strip()
    if not href or href.startswith(
        ("tel:", "mailto:", "javascript:", "http://", "https://")
    ):
        return None
    for pattern in (
        r"(?:^|/)servico/([^/]+)/?$",
        r"\.\./([^/]+)/?$",
        r"\.\./(?:\.\./)*servico/([^/]+)/?$",
    ):
        match = re.search(pattern, href)
        if match and match.group(1) in all_slugs:
            return match.group(1)
    return None


def satellite_links_in_content(
    content: str,
    satellite_slugs: set[str],
    all_slugs: set[str],
) -> set[str]:
    found: set[str] = set()
    for href in HREF_PATTERN.findall(content):
        slug = slug_from_href(href, all_slugs)
        if slug and slug in satellite_slugs:
            found.add(slug)
    return found


def load_satellite(slug: str) -> SatellitePage:
    page = ROOT / "servico" / slug / "index.html"
    text = page.read_text(encoding="utf-8")
    h1_match = re.search(r"<h1[^>]*>([^<]+)</h1>", text)
    title = html.unescape(h1_match.group(1).strip()) if h1_match else slug
    return SatellitePage(slug=slug, title=title)


def make_list_item(satellite: SatellitePage) -> str:
    safe_title = html.escape(satellite.title, quote=True)
    label = html.escape(satellite.title)
    return (
        f'<li><a href="../{satellite.slug}/" title="{safe_title}">{label}</a></li>'
    )


def strip_cluster_blocks(content: str) -> str:
    content = EXTERNAL_CLUSTER_NAV.sub("", content)
    content = CLUSTER_SECTION.sub("", content)
    return content


def find_geographic_section_bounds(content: str) -> tuple[int, int] | None:
    for match in re.finditer(r"<h2[^>]*>(.*?)</h2>", content, re.DOTALL):
        heading = REGIONAL_LINKS.normalize_text(re.sub(r"<[^>]+>", "", match.group(1)))
        if not any(keyword in heading for keyword in GEO_H2_KEYWORDS):
            continue
        start = match.end()
        next_heading = re.search(r"<h2\b", content[start:])
        end = start + next_heading.start() if next_heading else len(content)
        return start, end
    return None


def append_items_to_geographic_uls(section: str, items: list[str]) -> str:
    if not items:
        return section

    matches = list(UL_BLOCK.finditer(section))
    targets = [
        match
        for match in matches
        if "../reboque" in match.group(2) or "../guincho" in match.group(2)
    ]
    if not targets:
        targets = matches
    if not targets:
        return section.rstrip() + f"<ul>{''.join(items)}</ul>"

    groups: list[list[str]] = [[] for _ in targets]
    for index, item in enumerate(items):
        groups[index % len(targets)].append(item)

    updated = section
    for match, group in reversed(list(zip(targets, groups))):
        if not group:
            continue
        inner = match.group(2) + "".join(group)
        replacement = match.group(1) + inner + match.group(3)
        updated = updated[: match.start()] + replacement + updated[match.end() :]
    return updated


def satellite_slugs_in_range(
    content: str,
    start: int,
    end: int,
    allowed: set[str],
    all_slugs: set[str],
) -> set[str]:
    section = content[start:end]
    return satellite_links_in_content(section, allowed, all_slugs)


def find_outside_geographic_links(
    content: str,
    bounds: tuple[int, int],
    allowed: set[str],
    all_slugs: set[str],
) -> set[str]:
    start, end = bounds
    in_geo = satellite_slugs_in_range(content, start, end, allowed, all_slugs)
    outside: set[str] = set()
    for match in SATELLITE_LINK.finditer(content):
        slug = match.group(1)
        if slug not in allowed:
            continue
        if match.start() < start or match.start() >= end:
            outside.add(slug)
    return outside - in_geo


def unwrap_duplicate_links(
    content: str,
    bounds: tuple[int, int],
    slugs_in_geo: set[str],
) -> tuple[str, int]:
    start, end = bounds
    removed = 0
    updated = content

    for slug in slugs_in_geo:
        pattern = re.compile(
            rf'<a\s+href="\.\./{re.escape(slug)}/"[^>]*>(.*?)</a>',
            re.DOTALL | re.IGNORECASE,
        )
        for match in reversed(list(pattern.finditer(updated))):
            if start <= match.start() < end:
                continue
            updated = updated[: match.start()] + match.group(1) + updated[match.end() :]
            removed += 1

    return updated, removed


def dedupe_geographic_list_items(
    content: str,
    bounds: tuple[int, int],
) -> tuple[str, int]:
    start, end = bounds
    section = content[start:end]
    removed = 0
    seen_hrefs: set[str] = set()

    def repl(match: re.Match[str]) -> str:
        nonlocal removed
        inner = match.group(2)
        kept_items: list[str] = []
        for item_match in re.finditer(
            r"(<li>)((?:(?!</li>).)*?)(</li>)",
            inner,
            re.DOTALL,
        ):
            item_html = item_match.group(2)
            href_match = re.search(r'href="\.\./([^"/]+)/"', item_html)
            if not href_match:
                kept_items.append(item_match.group(0))
                continue
            slug = href_match.group(1)
            if slug in seen_hrefs:
                removed += 1
                continue
            seen_hrefs.add(slug)
            kept_items.append(item_match.group(0))

        if removed == 0:
            return match.group(0)
        return match.group(1) + "".join(kept_items) + match.group(3)

    updated_section = UL_BLOCK.sub(repl, section)
    if updated_section == section:
        return content, 0
    return content[:start] + updated_section + content[end:], removed


def distribute_missing_to_geographic_lists(
    content: str,
    missing: list[SatellitePage],
) -> tuple[str, int]:
    if not missing:
        return content, 0

    bounds = find_geographic_section_bounds(content)
    if not bounds:
        return content, 0

    start, end = bounds
    section = content[start:end]
    items = [make_list_item(satellite) for satellite in missing]
    updated_section = append_items_to_geographic_uls(section, items)
    if updated_section == section:
        return content, 0

    return content[:start] + updated_section + content[end:], len(missing)


def consolidate_satellite_links_in_geo_section(
    content: str,
    *,
    satellite_slugs: list[str],
    all_slugs: set[str],
) -> tuple[str, int]:
    allowed = set(satellite_slugs)
    bounds = find_geographic_section_bounds(content)
    if not bounds:
        return content, 0

    start, end = bounds
    in_geo = satellite_slugs_in_range(content, start, end, allowed, all_slugs)
    outside_only = find_outside_geographic_links(content, bounds, allowed, all_slugs)
    all_linked = satellite_links_in_content(content, allowed, all_slugs)
    missing_slugs = [slug for slug in satellite_slugs if slug not in all_linked]
    to_add_slugs = sorted(
        (set(missing_slugs) | outside_only) - in_geo,
        key=str.lower,
    )
    if not to_add_slugs:
        updated, removed = unwrap_duplicate_links(content, bounds, in_geo)
        updated, deduped = dedupe_geographic_list_items(updated, bounds)
        return updated, removed + deduped

    missing_pages = [load_satellite(slug) for slug in to_add_slugs]
    updated, added = distribute_missing_to_geographic_lists(content, missing_pages)
    if added == 0:
        return content, 0

    new_bounds = find_geographic_section_bounds(updated)
    if new_bounds:
        updated, deduped = dedupe_geographic_list_items(updated, new_bounds)
        new_in_geo = satellite_slugs_in_range(
            updated,
            new_bounds[0],
            new_bounds[1],
            allowed,
            all_slugs,
        )
        updated, removed = unwrap_duplicate_links(updated, new_bounds, new_in_geo)
        return updated, added + removed + deduped

    return updated, added


def enrich_written_content(
    written_body: str,
    *,
    pillar_slug: str,
    satellite_slugs: list[str],
    all_slugs: set[str],
    target_cache: dict[str, REGIONAL_LINKS.TargetPage],
) -> tuple[str, int]:
    updated = strip_cluster_blocks(written_body)
    allowed = set(satellite_slugs)
    targets = REGIONAL_LINKS.build_targets(satellite_slugs, target_cache)
    total_added = 0

    page_content = (ROOT / "servico" / pillar_slug / "index.html").read_text(
        encoding="utf-8"
    )
    h1_match = re.search(r"<h1[^>]*>([^<]+)</h1>", page_content)
    current_title = (
        html.unescape(h1_match.group(1).strip()) if h1_match else pillar_slug
    )
    skip_phrases = {
        REGIONAL_LINKS.normalize_text(phrase)
        for phrase in REGIONAL_LINKS.extract_location_phrases(
            pillar_slug,
            current_title,
        )
    }

    while True:
        linked = satellite_links_in_content(updated, allowed, all_slugs)
        missing_slugs = [slug for slug in satellite_slugs if slug not in linked]
        if not missing_slugs:
            break

        progress = 0
        exclude = set(linked)

        updated, added = REGIONAL_LINKS.link_list_items(
            updated,
            targets,
            limit=len(missing_slugs),
            exclude=exclude,
        )
        progress += added
        linked = satellite_links_in_content(updated, allowed, all_slugs)
        exclude = set(linked)
        missing_slugs = [slug for slug in satellite_slugs if slug not in linked]

        while missing_slugs:
            updated, added = REGIONAL_LINKS.link_plain_text_once(
                updated,
                targets,
                skip_phrases=skip_phrases,
                exclude=exclude,
            )
            if added == 0:
                break
            progress += added
            linked = satellite_links_in_content(updated, allowed, all_slugs)
            exclude = set(linked)
            missing_slugs = [slug for slug in satellite_slugs if slug not in linked]

        missing_pages = [load_satellite(slug) for slug in missing_slugs]
        missing_pages.sort(key=lambda item: item.title.lower())
        updated, added = distribute_missing_to_geographic_lists(updated, missing_pages)
        progress += added

        total_added += progress
        if progress == 0:
            break

    updated, consolidated = consolidate_satellite_links_in_geo_section(
        updated,
        satellite_slugs=satellite_slugs,
        all_slugs=all_slugs,
    )
    total_added += consolidated

    return updated, total_added


def process_pillar(
    region: str,
    pillar_slug: str,
    regions: dict[str, list[str]],
    all_slugs: set[str],
    target_cache: dict[str, REGIONAL_LINKS.TargetPage],
) -> int:
    path = ROOT / "servico" / pillar_slug / "index.html"
    html_content = path.read_text(encoding="utf-8")
    article_match = ARTICLE_BLOCK.search(html_content)
    if not article_match:
        return 0

    article_inner = article_match.group(2)
    cleaned_article = remove_external_cluster_nav(article_inner)

    written_match = WRITTEN_CONTENT_BLOCK.search(cleaned_article)
    if not written_match:
        return 0

    satellite_slugs = [slug for slug in regions[region] if slug != pillar_slug]
    updated_body, added = enrich_written_content(
        written_match.group(2),
        pillar_slug=pillar_slug,
        satellite_slugs=satellite_slugs,
        all_slugs=all_slugs,
        target_cache=target_cache,
    )

    updated_written = written_match.group(1) + updated_body + written_match.group(3)
    updated_article = (
        cleaned_article[: written_match.start()]
        + updated_written
        + cleaned_article[written_match.end() :]
    )

    if updated_article == article_inner:
        return 0

    path.write_text(
        html_content[: article_match.start()]
        + article_match.group(1)
        + updated_article
        + article_match.group(3)
        + html_content[article_match.end() :],
        encoding="utf-8",
    )
    return added if added else 1


def remove_external_cluster_nav(article_inner: str) -> str:
    return EXTERNAL_CLUSTER_NAV.sub("", article_inner)


def main() -> None:
    regions, pillars, all_slugs = load_data()
    target_cache: dict[str, REGIONAL_LINKS.TargetPage] = {}
    total_links = 0
    changed = 0

    for region, pillar_slug in sorted(pillars.items()):
        added = process_pillar(
            region,
            pillar_slug,
            regions,
            all_slugs,
            target_cache,
        )
        if added:
            changed += 1
            total_links += added
            print(f"  {pillar_slug}: +{added} link(s) no writen_content")

    print(f"\nPilares alterados: {changed}")
    print(f"Links adicionados: {total_links}")


if __name__ == "__main__":
    main()
