#!/usr/bin/env python3
"""Garante 2 links ao pilar regional de cada satélite dentro do conteúdo."""

from __future__ import annotations

import html
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGIONS_FILE = ROOT / "scripts" / "service-regions.json"
HUBS_FILE = ROOT / "scripts" / "regional-services.json"
MIN_PILLAR_CONTENT_LINKS = 2

ARTICLE_BLOCK = re.compile(
    r'(<article class="col-lg-(?:8|12)[^"]*">)(.*?)(</article>)',
    re.DOTALL,
)

REGION_PHRASES: dict[str, tuple[str, ...]] = {
    "zona-sul": ("Zona Sul do RJ", "Zona Sul", "zona sul"),
    "zona-norte": ("Zona Norte do RJ", "Zona Norte", "zona norte"),
    "zona-oeste": ("Zona Oeste do RJ", "Zona Oeste", "zona oeste"),
    "centro": ("Centro do RJ", "no Centro", "região central"),
    "baixada-fluminense": ("Baixada Fluminense", "Baixada Fluminense do RJ", "Baixada"),
    "regiao-oceanica": ("Região Oceânica do RJ", "Região Oceânica"),
    "regiao-serrana": ("Região Serrana do RJ", "Região Serrana"),
    "costa-verde": ("Costa Verde do RJ", "Costa Verde"),
    "litoral-lagos": ("Litoral Lagos", "Litoral de Lagos", "Região dos Lagos"),
}


@dataclass(frozen=True)
class RegionalPillar:
    region: str
    slug: str
    title: str
    phrases: tuple[str, ...]


def iter_html_files() -> list[Path]:
    return sorted((ROOT / "servico").glob("*/index.html"))


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFD", value)
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    return re.sub(r"\s+", " ", value.strip().lower())


def load_data() -> tuple[dict[str, list[str]], dict[str, str], dict[str, RegionalPillar]]:
    regions: dict[str, list[str]] = json.loads(
        REGIONS_FILE.read_text(encoding="utf-8")
    )
    hubs: set[str] = set(json.loads(HUBS_FILE.read_text(encoding="utf-8")))
    page_to_region: dict[str, str] = {}
    pillars: dict[str, RegionalPillar] = {}

    for region, slugs in regions.items():
        for slug in slugs:
            page_to_region[slug] = region

        if region in {"rio-geral", "tipos-veiculo"}:
            continue

        pillar_slug = next((slug for slug in slugs if slug in hubs), None)
        if not pillar_slug:
            continue

        page = ROOT / "servico" / pillar_slug / "index.html"
        content = page.read_text(encoding="utf-8")
        h1_match = re.search(r"<h1[^>]*>([^<]+)</h1>", content)
        title = html.unescape(h1_match.group(1).strip()) if h1_match else pillar_slug
        configured = REGION_PHRASES.get(region, ())
        phrases: list[str] = []
        seen: set[str] = set()
        for phrase in (*configured, title):
            key = normalize_text(phrase)
            if key and key not in seen:
                seen.add(key)
                phrases.append(phrase)
        pillars[region] = RegionalPillar(
            region=region,
            slug=pillar_slug,
            title=title,
            phrases=tuple(sorted(phrases, key=len, reverse=True)),
        )

    return regions, page_to_region, pillars


def count_pillar_links(content: str, pillar_slug: str) -> int:
    return len(re.findall(rf'href="\.\./{re.escape(pillar_slug)}/"', content))


def make_link(pillar: RegionalPillar, anchor: str) -> str:
    safe_title = html.escape(pillar.title, quote=True)
    return (
        f'<a href="../{pillar.slug}/" title="{safe_title}">'
        f"{html.escape(anchor)}</a>"
    )


def phrase_pattern(phrase: str) -> re.Pattern[str]:
    if phrase.startswith("no Centro"):
        return re.compile(r"(?<![\wÀ-ÿ-])no Centro(?![\wÀ-ÿ-])", re.IGNORECASE)
    if phrase == "Baixada":
        return re.compile(r"(?<![\wÀ-ÿ-])Baixada(?!\s+Fluminense)", re.IGNORECASE)
    escaped = re.escape(phrase)
    return re.compile(rf"(?<![\wÀ-ÿ-]){escaped}(?![\wÀ-ÿ-])", re.IGNORECASE)


def split_html_parts(fragment: str) -> list[str]:
    return re.split(r"(<[^>]+>)", fragment)


def link_pillar_phrase_once(content: str, pillar: RegionalPillar) -> tuple[str, int]:
    parts = split_html_parts(content)
    in_anchor = False

    for index, part in enumerate(parts):
        if part.startswith("<a ") or part.startswith("<a>"):
            in_anchor = True
            continue
        if part.startswith("</a>"):
            in_anchor = False
            continue
        if part.startswith("<") or in_anchor or not part.strip():
            continue

        for phrase in pillar.phrases:
            match = phrase_pattern(phrase).search(part)
            if not match:
                continue
            matched = match.group(0)
            linked = make_link(pillar, matched)
            parts[index] = part[: match.start()] + linked + part[match.end() :]
            return "".join(parts), 1

    return content, 0


def pillar_anchor_label(pillar: RegionalPillar) -> str:
    for phrase in pillar.phrases:
        if len(normalize_text(phrase)) >= 8:
            return phrase
    return pillar.phrases[0] if pillar.phrases else pillar.title


def append_pillar_sentence(
    content: str,
    pillar: RegionalPillar,
    *,
    variant: int,
) -> tuple[str, int]:
    marker = '<div class="writen_content">'
    start = content.find(marker)
    search_from = start + len(marker) if start >= 0 else 0
    paragraphs = list(
        re.finditer(r"(<p[^>]*>.*?</p>)", content[search_from:], re.DOTALL)
    )
    if not paragraphs:
        return content, 0

    label = pillar_anchor_label(pillar)
    link = make_link(pillar, label)
    templates = (
        f" Atendemos toda a {link} com cobertura 24 horas.",
        f" Confira também nosso serviço de reboque na {link}.",
    )
    insertion = templates[variant % len(templates)]

    for offset, paragraph in enumerate(paragraphs):
        if offset < variant:
            continue
        original = paragraph.group(1)
        if link in original or "Também atendemos" in original:
            continue
        updated = original.replace("</p>", f"{insertion}</p>", 1)
        absolute_start = search_from + paragraph.start()
        absolute_end = search_from + paragraph.end()
        return (
            content[:absolute_start] + updated + content[absolute_end:],
            1,
        )

    return content, 0


def enrich_content(content: str, pillar: RegionalPillar) -> tuple[str, int]:
    updated = content
    total_added = 0
    fallback_variant = 0

    while count_pillar_links(updated, pillar.slug) < MIN_PILLAR_CONTENT_LINKS:
        updated, added = link_pillar_phrase_once(updated, pillar)
        if added:
            total_added += added
            continue

        updated, added = append_pillar_sentence(
            updated,
            pillar,
            variant=fallback_variant,
        )
        fallback_variant += 1
        if added:
            total_added += added
            continue

        break

    return updated, total_added


def process_page(
    path: Path,
    page_to_region: dict[str, str],
    pillars: dict[str, RegionalPillar],
) -> int:
    slug = path.parent.name
    region = page_to_region.get(slug)
    if not region or region in {"rio-geral", "tipos-veiculo"}:
        return 0

    pillar = pillars.get(region)
    if not pillar or slug == pillar.slug:
        return 0

    html_content = path.read_text(encoding="utf-8")
    match = ARTICLE_BLOCK.search(html_content)
    if not match:
        return 0

    if count_pillar_links(match.group(2), pillar.slug) >= MIN_PILLAR_CONTENT_LINKS:
        return 0

    updated_content, added = enrich_content(match.group(2), pillar)
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
    _, page_to_region, pillars = load_data()

    changed_pages = 0
    added_links = 0
    for path in iter_html_files():
        count = process_page(path, page_to_region, pillars)
        if count:
            changed_pages += 1
            added_links += count
            print(f"  {path.parent.name}: +{count} link(s) ao pilar")

    print(f"\nPáginas alteradas: {changed_pages}")
    print(f"Links ao pilar adicionados: {added_links}")


if __name__ == "__main__":
    main()
