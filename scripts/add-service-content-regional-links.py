#!/usr/bin/env python3
"""Garante links naturais entre páginas satélite do mesmo cluster no conteúdo."""

from __future__ import annotations

import html
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGIONS_FILE = ROOT / "scripts" / "service-regions.json"
MIN_CLUSTER_CONTENT_LINKS = 2

ARTICLE_BLOCK = re.compile(
    r'(<article class="col-lg-(?:8|12)[^"]*">)(.*?)(</article>)',
    re.DOTALL,
)
HREF_PATTERN = re.compile(r'href="([^"]+)"')
LI_ITEM = re.compile(r"(<li>)((?:(?!</li>).)*?)(</li>)", re.DOTALL)
VEHICLE_KEYWORDS: dict[str, tuple[str, ...]] = {
    "reboque-caminhao-rj": ("caminhão", "caminhões", "Caminhão", "Caminhões"),
    "reboque-onibus-rj": ("ônibus", "Ônibus", "onibus", "micro-ônibus"),
    "reboque-embarcacao-rj": ("embarcação", "Embarcação", "embarcacoes", "barco", "lancha"),
    "reboque-de-moto-no-rj": ("motocicleta", "Motocicleta", "moto ", " moto", "motos"),
}


@dataclass(frozen=True)
class TargetPage:
    slug: str
    title: str
    phrases: tuple[str, ...]


def iter_html_files() -> list[Path]:
    return sorted((ROOT / "servico").glob("*/index.html"))


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFD", value)
    value = "".join(char for char in value if unicodedata.category(char) != "Mn")
    return re.sub(r"\s+", " ", value.strip().lower())


def load_regions() -> tuple[dict[str, list[str]], dict[str, str], set[str]]:
    regions: dict[str, list[str]] = json.loads(
        REGIONS_FILE.read_text(encoding="utf-8")
    )
    page_to_region: dict[str, str] = {}
    for region, slugs in regions.items():
        for slug in slugs:
            page_to_region[slug] = region
    all_slugs = {path.parent.name for path in iter_html_files()}
    return regions, page_to_region, all_slugs


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


def extract_location_phrases(slug: str, title: str) -> list[str]:
    phrases: list[str] = []
    match = re.search(
        r"Reboque\s+(?:em|na|no|de)\s+(.+?)(?:\s+24|\s+no RJ|\||$)",
        title,
        re.IGNORECASE,
    )
    if match:
        phrases.append(match.group(1).strip(" ?"))

    if slug in VEHICLE_KEYWORDS:
        phrases.extend(VEHICLE_KEYWORDS[slug])

    deduped: list[str] = []
    seen: set[str] = set()
    for phrase in sorted(set(phrases), key=len, reverse=True):
        key = normalize_text(phrase)
        if len(key) < 4 or key in seen:
            continue
        seen.add(key)
        deduped.append(phrase)
    return deduped


def build_targets(
    allowed_slugs: list[str],
    cache: dict[str, TargetPage],
) -> list[TargetPage]:
    targets: list[TargetPage] = []
    for slug in allowed_slugs:
        if slug not in cache:
            page = ROOT / "servico" / slug / "index.html"
            content = page.read_text(encoding="utf-8")
            h1_match = re.search(r"<h1[^>]*>([^<]+)</h1>", content)
            title = html.unescape(h1_match.group(1).strip()) if h1_match else slug
            cache[slug] = TargetPage(
                slug=slug,
                title=title,
                phrases=tuple(extract_location_phrases(slug, title)),
            )
        targets.append(cache[slug])
    return sorted(
        targets,
        key=lambda item: max((len(p) for p in item.phrases), default=0),
        reverse=True,
    )


def existing_in_region_links(
    content: str,
    allowed: set[str],
    all_slugs: set[str],
) -> set[str]:
    found: set[str] = set()
    for href in HREF_PATTERN.findall(content):
        slug = slug_from_href(href, all_slugs)
        if slug and slug in allowed:
            found.add(slug)
    return found


def is_bairro_list_item(text: str) -> bool:
    clean = re.sub(r"<[^>]+>", "", text).strip()
    if not clean or len(clean) > 45:
        return False
    if clean[0].islower():
        return False
    if ";" in clean or ":" in clean:
        return False
    return len(clean.split()) <= 5


def match_target(text: str, targets: list[TargetPage]) -> TargetPage | None:
    normalized = normalize_text(text)
    for target in targets:
        for phrase in target.phrases:
            if normalized == normalize_text(phrase):
                return target
    return None


def phrase_pattern(phrase: str) -> re.Pattern[str]:
    escaped = re.escape(phrase)
    return re.compile(
        rf"(?<![\wÀ-ÿ-]){escaped}(?![\wÀ-ÿ-])",
        re.IGNORECASE,
    )


def make_link(target: TargetPage, anchor: str) -> str:
    safe_title = html.escape(target.title, quote=True)
    return (
        f'<a href="../{target.slug}/" title="{safe_title}">'
        f"{html.escape(anchor)}</a>"
    )


def link_list_items(
    content: str,
    targets: list[TargetPage],
    *,
    limit: int,
    exclude: set[str],
) -> tuple[str, int]:
    added = 0
    available = [target for target in targets if target.slug not in exclude]

    def repl(match: re.Match[str]) -> str:
        nonlocal added
        if added >= limit:
            return match.group(0)
        item_html = match.group(2)
        if "<a " in item_html or "<a>" in item_html:
            return match.group(0)
        item_text = re.sub(r"<[^>]+>", "", item_html).strip()
        if not is_bairro_list_item(item_text):
            return match.group(0)
        target = match_target(item_text, available)
        if not target or target.slug in exclude:
            return match.group(0)
        added += 1
        exclude.add(target.slug)
        return f"{match.group(1)}{make_link(target, item_text)}{match.group(3)}"

    updated = LI_ITEM.sub(repl, content)
    return updated, added


def split_html_parts(fragment: str) -> list[str]:
    return re.split(r"(<[^>]+>)", fragment)


def link_plain_text_once(
    content: str,
    targets: list[TargetPage],
    *,
    skip_phrases: set[str],
    exclude: set[str],
) -> tuple[str, int]:
    parts = split_html_parts(content)
    in_anchor = False
    available = [target for target in targets if target.slug not in exclude]

    for index, part in enumerate(parts):
        if part.startswith("<a ") or part.startswith("<a>"):
            in_anchor = True
            continue
        if part.startswith("</a>"):
            in_anchor = False
            continue
        if part.startswith("<") or in_anchor or not part.strip():
            continue

        for target in available:
            for phrase in target.phrases:
                if normalize_text(phrase) in skip_phrases:
                    continue
                if len(normalize_text(phrase)) < 6 and " " not in phrase:
                    continue
                match = phrase_pattern(phrase).search(part)
                if not match:
                    continue
                matched = match.group(0)
                linked = make_link(target, matched)
                parts[index] = part[: match.start()] + linked + part[match.end() :]
                return "".join(parts), 1

    return content, 0


def pick_neighbor_targets(
    current_slug: str,
    region_slugs: list[str],
    targets: list[TargetPage],
    *,
    exclude: set[str],
    count: int,
) -> list[TargetPage]:
    picked: list[TargetPage] = []
    try:
        start = region_slugs.index(current_slug)
    except ValueError:
        start = 0

    for offset in range(1, len(region_slugs) + 1):
        candidate = region_slugs[(start + offset) % len(region_slugs)]
        if candidate in exclude or candidate == current_slug:
            continue
        for target in targets:
            if target.slug == candidate:
                picked.append(target)
                exclude.add(candidate)
                break
        if len(picked) >= count:
            break

    for target in targets:
        if len(picked) >= count:
            break
        if target.slug in exclude:
            continue
        picked.append(target)
        exclude.add(target.slug)

    return picked


def anchor_for_target(target: TargetPage) -> str:
    anchor = target.phrases[0] if target.phrases else target.title
    if target.phrases and not anchor.lower().startswith(("reboque", "guincho")):
        return f"reboque em {anchor}"
    return anchor


def append_contextual_links(
    content: str,
    *,
    current_slug: str,
    region_slugs: list[str],
    targets: list[TargetPage],
    exclude: set[str],
    needed: int,
) -> tuple[str, int]:
    if needed <= 0:
        return content, 0

    neighbors = pick_neighbor_targets(
        current_slug,
        region_slugs,
        targets,
        exclude=exclude,
        count=needed,
    )
    if not neighbors:
        return content, 0

    marker = '<div class="writen_content">'
    start = content.find(marker)
    search_from = start + len(marker) if start >= 0 else 0
    paragraphs = list(
        re.finditer(r"(<p[^>]*>.*?</p>)", content[search_from:], re.DOTALL)
    )
    if not paragraphs:
        return content, 0

    for paragraph in paragraphs:
        original = paragraph.group(1)
        if "Também atendemos" in original:
            continue
        if sum(1 for target in neighbors if make_link(target, anchor_for_target(target)) in original) >= needed:
            continue

        if len(neighbors) == 1:
            target = neighbors[0]
            insertion = (
                f" Também atendemos {make_link(target, anchor_for_target(target))} "
                "na mesma região."
            )
        else:
            first = make_link(neighbors[0], anchor_for_target(neighbors[0]))
            second = make_link(neighbors[1], anchor_for_target(neighbors[1]))
            insertion = f" Também atendemos {first} e {second} na mesma região."

        updated_paragraph = original.replace("</p>", f"{insertion}</p>", 1)
        absolute_start = search_from + paragraph.start()
        absolute_end = search_from + paragraph.end()
        return (
            content[:absolute_start] + updated_paragraph + content[absolute_end:],
            len(neighbors),
        )

    return content, 0


def enrich_content(
    content: str,
    *,
    current_slug: str,
    region_slugs: list[str],
    targets: list[TargetPage],
    all_slugs: set[str],
) -> tuple[str, int]:
    allowed = {target.slug for target in targets}
    updated = content
    total_added = 0

    page_content = (ROOT / "servico" / current_slug / "index.html").read_text(
        encoding="utf-8"
    )
    h1_match = re.search(r"<h1[^>]*>([^<]+)</h1>", page_content)
    current_title = html.unescape(h1_match.group(1).strip()) if h1_match else current_slug
    skip_phrases = {
        normalize_text(phrase)
        for phrase in extract_location_phrases(current_slug, current_title)
    }

    while True:
        linked = existing_in_region_links(updated, allowed, all_slugs)
        if len(linked) >= MIN_CLUSTER_CONTENT_LINKS:
            break

        needed = MIN_CLUSTER_CONTENT_LINKS - len(linked)
        exclude = set(linked)
        progress = 0

        updated, added = link_list_items(
            updated,
            targets,
            limit=needed,
            exclude=exclude,
        )
        progress += added
        linked = existing_in_region_links(updated, allowed, all_slugs)
        exclude = set(linked)
        needed = MIN_CLUSTER_CONTENT_LINKS - len(linked)

        while needed > 0:
            updated, added = link_plain_text_once(
                updated,
                targets,
                skip_phrases=skip_phrases,
                exclude=exclude,
            )
            if added == 0:
                break
            progress += added
            linked = existing_in_region_links(updated, allowed, all_slugs)
            exclude = set(linked)
            needed = MIN_CLUSTER_CONTENT_LINKS - len(linked)

        linked = existing_in_region_links(updated, allowed, all_slugs)
        needed = MIN_CLUSTER_CONTENT_LINKS - len(linked)
        if needed > 0:
            updated, added = append_contextual_links(
                updated,
                current_slug=current_slug,
                region_slugs=region_slugs,
                targets=targets,
                exclude=set(linked),
                needed=needed,
            )
            progress += added

        total_added += progress
        if progress == 0:
            break

    return updated, total_added


def process_page(
    path: Path,
    regions: dict[str, list[str]],
    page_to_region: dict[str, str],
    all_slugs: set[str],
    cache: dict[str, TargetPage],
) -> int:
    slug = path.parent.name
    region = page_to_region[slug]
    if region == "rio-geral":
        return 0

    region_slugs = regions[region]
    allowed = [item for item in region_slugs if item != slug]
    if len(allowed) < MIN_CLUSTER_CONTENT_LINKS:
        return 0

    html_content = path.read_text(encoding="utf-8")
    match = ARTICLE_BLOCK.search(html_content)
    if not match:
        return 0

    updated_content, added = enrich_content(
        match.group(2),
        current_slug=slug,
        region_slugs=region_slugs,
        targets=build_targets(allowed, cache),
        all_slugs=all_slugs,
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
    regions, page_to_region, all_slugs = load_regions()
    cache: dict[str, TargetPage] = {}

    changed_pages = 0
    added_links = 0
    for path in iter_html_files():
        count = process_page(path, regions, page_to_region, all_slugs, cache)
        if count:
            changed_pages += 1
            added_links += count
            print(f"  {path.parent.name}: +{count} link(s)")

    print(f"\nPáginas alteradas: {changed_pages}")
    print(f"Links adicionados: {added_links}")


if __name__ == "__main__":
    main()
