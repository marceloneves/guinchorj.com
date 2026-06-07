#!/usr/bin/env python3
"""Garante 1 link no conteúdo de cada pilar regional para cada satélite do cluster."""

from __future__ import annotations

import html
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGIONS_FILE = ROOT / "scripts" / "service-regions.json"
REGIONAL_FILE = ROOT / "scripts" / "regional-services.json"

ARTICLE_BLOCK = re.compile(
    r'(<article class="col-lg-(?:8|12)[^"]*">)(.*?)(</article>)',
    re.DOTALL,
)
HREF_PATTERN = re.compile(r'href="([^"]+)"')
NAV_MARKER = 'aria-label="Satélites do cluster regional"'
NAV_UL = re.compile(
    rf'<nav[^>]*{re.escape(NAV_MARKER)}[^>]*>.*?<ul class="pillar-cluster-links">(.*?)</ul>',
    re.DOTALL | re.IGNORECASE,
)

REGION_HEADINGS = {
    "zona-sul": "Reboque na Zona Sul por bairro e via",
    "zona-norte": "Reboque na Zona Norte por bairro e via",
    "zona-oeste": "Reboque na Zona Oeste por bairro e via",
    "centro": "Reboque no Centro por bairro e via",
    "baixada-fluminense": "Reboque na Baixada Fluminense por cidade",
    "regiao-oceanica": "Reboque na Região Oceânica por cidade",
    "regiao-serrana": "Reboque na Região Serrana por cidade",
    "costa-verde": "Reboque na Costa Verde por cidade",
    "litoral-lagos": "Reboque no Litoral Lagos por cidade",
}


@dataclass(frozen=True)
class SatellitePage:
    slug: str
    title: str


def load_data() -> tuple[dict[str, list[str]], dict[str, str], dict[str, str], set[str]]:
    regions: dict[str, list[str]] = json.loads(
        REGIONS_FILE.read_text(encoding="utf-8")
    )
    hubs: set[str] = set(json.loads(REGIONAL_FILE.read_text(encoding="utf-8")))
    pillars: dict[str, str] = {}
    page_to_region: dict[str, str] = {}
    for region, slugs in regions.items():
        for slug in slugs:
            page_to_region[slug] = region
        if region in {"rio-geral", "tipos-veiculo"}:
            continue
        pillar = next((slug for slug in slugs if slug in hubs), None)
        if pillar:
            pillars[region] = pillar
    all_slugs = {path.parent.name for path in (ROOT / "servico").glob("*/index.html")}
    return regions, pillars, page_to_region, all_slugs


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


def satellite_links_in_content(content: str, all_slugs: set[str]) -> set[str]:
    found: set[str] = set()
    for href in HREF_PATTERN.findall(content):
        slug = slug_from_href(href, all_slugs)
        if slug:
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


def build_nav_block(region: str, satellites: list[SatellitePage]) -> str:
    heading = REGION_HEADINGS.get(region, "Reboque por localidade")
    items = "".join(make_list_item(item) for item in satellites)
    safe_heading = html.escape(heading)
    return (
        f'<nav aria-label="Satélites do cluster regional">'
        f"<h2>{safe_heading}</h2>"
        f'<ul class="pillar-cluster-links">{items}</ul>'
        f"</nav>"
    )


def append_to_nav(content: str, satellites: list[SatellitePage]) -> str:
    items = "".join(make_list_item(item) for item in satellites)
    nav_match = NAV_UL.search(content)
    if not nav_match:
        return content
    insert_at = nav_match.end(1)
    inner_start = nav_match.start(1)
    return content[:insert_at] + items + content[insert_at:]


def enrich_pillar_content(
    content: str,
    region: str,
    satellites: list[SatellitePage],
    all_slugs: set[str],
) -> tuple[str, int]:
    if not satellites:
        return content, 0

    linked = satellite_links_in_content(content, all_slugs)
    missing = [item for item in satellites if item.slug not in linked]
    if not missing:
        return content, 0

    if NAV_MARKER in content:
        updated = append_to_nav(content, missing)
        return updated, len(missing)

    nav_html = build_nav_block(region, missing)
    return content.rstrip() + nav_html, len(missing)


def process_pillar(
    region: str,
    pillar_slug: str,
    regions: dict[str, list[str]],
    all_slugs: set[str],
) -> int:
    path = ROOT / "servico" / pillar_slug / "index.html"
    html_content = path.read_text(encoding="utf-8")
    match = ARTICLE_BLOCK.search(html_content)
    if not match:
        return 0

    satellite_slugs = [slug for slug in regions[region] if slug != pillar_slug]
    satellites = [load_satellite(slug) for slug in satellite_slugs]
    satellites.sort(key=lambda item: item.title.lower())

    updated_content, added = enrich_pillar_content(
        match.group(2),
        region,
        satellites,
        all_slugs,
    )
    if added == 0:
        return 0

    path.write_text(
        html_content[: match.start()]
        + match.group(1)
        + updated_content
        + match.group(3)
        + html_content[match.end() :],
        encoding="utf-8",
    )
    return added


def main() -> None:
    regions, pillars, _, all_slugs = load_data()
    total_links = 0
    changed = 0

    for region, pillar_slug in sorted(pillars.items()):
        added = process_pillar(region, pillar_slug, regions, all_slugs)
        if added:
            changed += 1
            total_links += added
            print(f"  {pillar_slug}: +{added} link(s) a satélites")

    print(f"\nPilares alterados: {changed}")
    print(f"Links adicionados: {total_links}")


if __name__ == "__main__":
    main()
