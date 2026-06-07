#!/usr/bin/env python3
"""Fase 4: JSON-LD, aria-labels, imagens decorativas e alinhamento semântico."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

JSON_LD_PATTERN = re.compile(
    r'(<script type="application/ld\+json">)(.*?)(</script>)',
    re.DOTALL,
)
TITLE_PATTERN = re.compile(r"<title>([^<]+)</title>")
META_DESC_PATTERN = re.compile(
    r'<meta name="description" content="([^"]*)"',
)
H1_PATTERN = re.compile(r"<h1[^>]*>([^<]+)</h1>", re.IGNORECASE)
BREADCRUMB_PATTERN = re.compile(
    r'<ol class="breadcrumb"[^>]*>(.*?)</ol>',
    re.DOTALL,
)
BREADCRUMB_ITEM_PATTERN = re.compile(
    r'<li class="breadcrumb-item[^"]*"[^>]*>\s*'
    r'<a[^>]*title="([^"]*)"[^>]*href="([^"]*)"',
    re.DOTALL,
)
IMG_TAG_PATTERN = re.compile(r"<img[^>]+>", re.IGNORECASE)

NAV_MAIN = '<nav class="navbar navbar-expand-md navbar-light">'
NAV_MAIN_LABELED = (
    '<nav class="navbar navbar-expand-md navbar-light" aria-label="Menu principal">'
)
NAV_MOBILE = '<nav id="mobile-nav" class="mobile-nav" aria-hidden="true">'
NAV_MOBILE_LABELED = (
    '<nav id="mobile-nav" class="mobile-nav" aria-label="Menu mobile" '
    'aria-hidden="true">'
)
NAV_SIDEBAR = '<nav class="widget-area" id="secondary">'
NAV_SIDEBAR_LABELED = (
    '<nav class="widget-area" id="secondary" aria-label="Serviços relacionados">'
)

WEBPAGE_SUBTYPES = frozenset(
    {
        "WebPage",
        "AboutPage",
        "ContactPage",
        "CollectionPage",
        "SearchResultsPage",
        "FAQPage",
    }
)

REFERENCE_JSON_LD = ROOT / "servico" / "reboque-zona-oeste" / "index.html"


def iter_html_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(ROOT.rglob("*.html")):
        if "wp-content" in path.parts:
            continue
        if path.name == "_downloads.html":
            continue
        files.append(path)
    return files


def root_prefix(path: Path) -> str:
    depth = len(path.relative_to(ROOT).parts) - 1
    return "../" * depth if depth else "./"


def extract_breadcrumb(html: str) -> list[dict[str, Any]]:
    main = html[html.find("<main") : html.find("</main>")]
    match = BREADCRUMB_PATTERN.search(main)
    if not match:
        return []

    items: list[dict[str, Any]] = []
    for position, (name, href) in enumerate(
        BREADCRUMB_ITEM_PATTERN.findall(match.group(1)),
        start=1,
    ):
        items.append(
            {
                "@type": "ListItem",
                "position": position,
                "name": name,
                "item": href,
            }
        )
    return items


def load_reference_provider(prefix: str) -> dict[str, Any]:
    text = REFERENCE_JSON_LD.read_text(encoding="utf-8")
    match = JSON_LD_PATTERN.search(text)
    if not match:
        raise RuntimeError("JSON-LD de referência não encontrado.")

    data = json.loads(match.group(2))
    provider = copy.deepcopy(data["provider"])

    def fix_urls(value: Any) -> Any:
        if isinstance(value, str):
            return value.replace("../../", prefix)
        if isinstance(value, dict):
            return {key: fix_urls(item) for key, item in value.items()}
        if isinstance(value, list):
            return [fix_urls(item) for item in value]
        return value

    return fix_urls(provider)


def build_service_json_ld(html: str, path: Path) -> dict[str, Any]:
    prefix = root_prefix(path)
    h1_match = H1_PATTERN.search(html)
    desc_match = META_DESC_PATTERN.search(html)
    name = h1_match.group(1).strip() if h1_match else path.parent.name
    description = desc_match.group(1).strip() if desc_match else name
    breadcrumb_items = extract_breadcrumb(html)

    webpage: dict[str, Any] = {
        "@type": "WebPage",
        "@id": "#webpage/",
        "name": name,
        "url": "",
        "description": description,
        "mainEntity": {"@id": "#service/"},
    }
    if breadcrumb_items:
        webpage["breadcrumb"] = {
            "@type": "BreadcrumbList",
            "itemListElement": breadcrumb_items,
        }

    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Service",
                "@id": "#service/",
                "name": name,
                "description": description,
                "url": "",
                "image": f"{prefix}wp-content/uploads/2025/08/guinchorj-rio-de-janeiro.webp/",
                "provider": load_reference_provider(prefix),
                "offers": {
                    "@type": "Offer",
                    "priceCurrency": "BRL",
                    "availability": "https://schema.org/InStock",
                    "seller": {"@id": f"{prefix}#localbusiness/"},
                },
                "mainEntityOfPage": {"@id": "#webpage/"},
            },
            webpage,
        ],
    }


def entity_primary_type(entity_type: Any) -> str:
    if isinstance(entity_type, list):
        return str(entity_type[0])
    return str(entity_type)


def align_json_ld(data: dict[str, Any]) -> dict[str, Any]:
    if "@graph" in data:
        return normalize_graph(data)

    entity = copy.deepcopy(data)
    primary_type = entity_primary_type(entity.get("@type"))

    if primary_type in WEBPAGE_SUBTYPES:
        return entity

    webpage_data = entity.pop("mainEntityOfPage", None)
    entity_id = entity.get("@id") or "#main-entity/"
    entity["@id"] = entity_id

    webpage: dict[str, Any]
    if isinstance(webpage_data, dict):
        webpage = copy.deepcopy(webpage_data)
    else:
        webpage = {
            "@type": "WebPage",
            "name": entity.get("name") or entity.get("headline") or "",
            "url": entity.get("url", ""),
            "description": entity.get("description", ""),
        }

    webpage.setdefault("@type", "WebPage")
    webpage.setdefault("@id", "#webpage/")
    webpage["mainEntity"] = {"@id": entity_id}
    entity["mainEntityOfPage"] = {"@id": webpage["@id"]}

    if "name" not in webpage:
        webpage["name"] = entity.get("name") or entity.get("headline") or ""
    if "description" not in webpage and entity.get("description"):
        webpage["description"] = entity["description"]

    return {
        "@context": "https://schema.org",
        "@graph": [entity, webpage],
    }


def normalize_graph(data: dict[str, Any]) -> dict[str, Any]:
    graph = copy.deepcopy(data.get("@graph", []))
    if not graph:
        return data

    entity = next(
        (
            node
            for node in graph
            if entity_primary_type(node.get("@type")) not in WEBPAGE_SUBTYPES
        ),
        None,
    )
    webpage = next(
        (
            node
            for node in graph
            if entity_primary_type(node.get("@type")) in WEBPAGE_SUBTYPES
        ),
        None,
    )

    if not entity or not webpage:
        return data

    entity_id = entity.get("@id") or "#main-entity/"
    webpage_id = webpage.get("@id") or "#webpage/"
    entity["@id"] = entity_id
    webpage["@id"] = webpage_id
    webpage["mainEntity"] = {"@id": entity_id}
    entity["mainEntityOfPage"] = {"@id": webpage_id}

    return {
        "@context": data.get("@context", "https://schema.org"),
        "@graph": graph,
    }


def serialize_json_ld(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def apply_json_ld(html: str, path: Path) -> str:
    match = JSON_LD_PATTERN.search(html)
    if not match:
        return html

    payload = match.group(2).strip()
    if not payload:
        rel = path.relative_to(ROOT)
        if len(rel.parts) >= 2 and rel.parts[0] == "servico":
            data = build_service_json_ld(html, path)
        else:
            return html
    else:
        data = json.loads(payload)
        data = align_json_ld(data)

    replacement = f"{match.group(1)}{serialize_json_ld(data)}{match.group(3)}"
    return html[: match.start()] + replacement + html[match.end() :]


def apply_nav_labels(html: str) -> str:
    updated = html
    if NAV_MAIN in updated and 'aria-label="Menu principal"' not in updated:
        updated = updated.replace(NAV_MAIN, NAV_MAIN_LABELED, 1)
    if NAV_MOBILE in updated and 'aria-label="Menu mobile"' not in updated:
        updated = updated.replace(NAV_MOBILE, NAV_MOBILE_LABELED, 1)
    if NAV_SIDEBAR in updated and 'aria-label="Serviços relacionados"' not in updated:
        updated = updated.replace(NAV_SIDEBAR, NAV_SIDEBAR_LABELED, 1)
    return updated


def fix_logo_alt(html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        if "logo" not in tag:
            return tag
        if 'alt=""' in tag:
            return tag
        if re.search(r'\salt="[^"]*"', tag):
            return re.sub(r'\salt="[^"]*"', ' alt=""', tag, count=1)
        return tag.replace("<img", '<img alt=""', 1)

    return IMG_TAG_PATTERN.sub(repl, html)


def apply_phase4(html: str, path: Path) -> tuple[str, bool]:
    if "<body" not in html:
        return html, False

    updated = html
    updated = apply_nav_labels(updated)
    updated = fix_logo_alt(updated)
    updated = apply_json_ld(updated, path)
    return updated, True


def main() -> None:
    changed = 0
    skipped = 0

    for path in iter_html_files():
        original = path.read_text(encoding="utf-8")
        updated, ok = apply_phase4(original, path)
        if not ok:
            skipped += 1
            continue
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed += 1

    print(f"Páginas atualizadas: {changed}")
    if skipped:
        print(f"Páginas ignoradas: {skipped}")


if __name__ == "__main__":
    main()
