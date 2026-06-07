#!/usr/bin/env python3
"""Garante 1 link no writen_content de cada pilar para cada satélite do cluster."""

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
CLUSTER_UL = re.compile(
    rf'(<section[^>]*{re.escape(CLUSTER_MARKER)}[^>]*>.*?<ul class="pillar-cluster-links">)(.*?)(</ul>)',
    re.DOTALL | re.IGNORECASE,
)
EXTERNAL_CLUSTER_UL = re.compile(
    rf'(<nav[^>]*{re.escape(CLUSTER_MARKER)}[^>]*>.*?<ul class="pillar-cluster-links">)(.*?)(</ul>)',
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


def extract_written_content(article_inner: str) -> str | None:
    match = WRITTEN_CONTENT_BLOCK.search(article_inner)
    if not match:
        return None
    return match.group(2)


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


def build_cluster_section(region: str, satellites: list[SatellitePage]) -> str:
    heading = REGION_HEADINGS.get(region, "Reboque por localidade")
    items = "".join(make_list_item(item) for item in satellites)
    safe_heading = html.escape(heading)
    return (
        f'<section class="pillar-cluster-links-section" {CLUSTER_MARKER}>'
        f"<h2>{safe_heading}</h2>"
        f'<ul class="pillar-cluster-links">{items}</ul>'
        f"</section>"
    )


def append_to_cluster_list(content: str, satellites: list[SatellitePage]) -> str:
    items = "".join(make_list_item(item) for item in satellites)
    for pattern in (CLUSTER_UL, EXTERNAL_CLUSTER_UL):
        match = pattern.search(content)
        if match:
            return content[: match.end(2)] + items + content[match.end(2) :]
    return content


def remove_external_cluster_nav(article_inner: str) -> str:
    return EXTERNAL_CLUSTER_NAV.sub("", article_inner)


def enrich_written_content(
    written_body: str,
    region: str,
    satellites: list[SatellitePage],
    all_slugs: set[str],
) -> tuple[str, int]:
    if not satellites:
        return written_body, 0

    linked = satellite_links_in_content(written_body, all_slugs)
    missing = [item for item in satellites if item.slug not in linked]
    if not missing:
        return written_body, 0

    if CLUSTER_MARKER in written_body:
        updated = append_to_cluster_list(written_body, missing)
        return updated, len(missing)

    section_html = build_cluster_section(region, missing)
    return written_body.rstrip() + section_html, len(missing)


def process_pillar(
    region: str,
    pillar_slug: str,
    regions: dict[str, list[str]],
    all_slugs: set[str],
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
    satellites = [load_satellite(slug) for slug in satellite_slugs]
    satellites.sort(key=lambda item: item.title.lower())

    updated_body, added = enrich_written_content(
        written_match.group(2),
        region,
        satellites,
        all_slugs,
    )

    updated_written = (
        written_match.group(1) + updated_body + written_match.group(3)
    )
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


def main() -> None:
    regions, pillars, _, all_slugs = load_data()
    total_links = 0
    changed = 0

    for region, pillar_slug in sorted(pillars.items()):
        added = process_pillar(region, pillar_slug, regions, all_slugs)
        if added:
            changed += 1
            total_links += added
            print(f"  {pillar_slug}: +{added} link(s) no writen_content")

    print(f"\nPilares alterados: {changed}")
    print(f"Links adicionados: {total_links}")


if __name__ == "__main__":
    main()
