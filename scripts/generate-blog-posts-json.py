#!/usr/bin/env python3
"""Gera blog/posts.json com todos os artigos e categorias para o filtro do blog."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOG = ROOT / "blog"
OUTPUT = BLOG / "posts.json"

CATEGORIES = [
    {"id": "all", "label": "Todos os artigos"},
    {"id": "manual-do-motorista", "label": "Manual do Motorista"},
    {"id": "reboque-e-guincho", "label": "Reboque e Guincho"},
    {"id": "blog", "label": "Artigos gerais"},
]

CATEGORY_LABELS = {item["id"]: item["label"] for item in CATEGORIES if item["id"] != "all"}


def is_post(path: Path) -> bool:
    rel = path.relative_to(BLOG).as_posix()
    if rel == "index.html":
        return False
    parts = rel.split("/")
    if "page" in parts:
        return False
    if parts[-1] != "index.html":
        return False
    if len(parts) == 2 and parts[0] in CATEGORY_LABELS and parts[0] != "manual-do-motorista":
        return False
    if len(parts) not in (2, 3):
        return False
    return True


SECTION_TO_CATEGORY = {
    "Manual do Motorista": "manual-do-motorista",
    "Reboque e Guincho": "reboque-e-guincho",
}


def category_from_html(html: str) -> str | None:
    match = re.search(r'"articleSection"\s*:\s*"([^"]+)"', html)
    if not match:
        return None
    return SECTION_TO_CATEGORY.get(match.group(1))


def post_category(parts: list[str], html: str) -> str:
    from_schema = category_from_html(html)
    if from_schema:
        return from_schema
    if len(parts) == 3:
        return parts[0]
    if len(parts) == 2 and parts[0] in CATEGORY_LABELS:
        return parts[0]
    return "blog"


def extract_field(html: str, *patterns: str) -> str:
    for pattern in patterns:
        match = re.search(pattern, html, re.DOTALL)
        if match:
            return match.group(1).strip()
    return ""


def extract_post(path: Path) -> dict[str, str]:
    html = path.read_text(encoding="utf-8", errors="replace")
    parts = path.relative_to(BLOG).as_posix().split("/")
    category = post_category(parts, html)

    if len(parts) == 3:
        url = f"{parts[0]}/{parts[1]}/"
    else:
        url = f"{parts[0]}/"

    title = extract_field(
        html,
        r'"headline"\s*:\s*"([^"]+)"',
        r'property="og:title"\s+content="([^"]+)"',
        r"<title>([^<]+)</title>",
    )
    title = re.sub(r"\s*[-|].*Guincho.*$", "", title).strip()

    excerpt = extract_field(
        html,
        r'name="description"\s+content="([^"]+)"',
        r'"description"\s*:\s*"([^"]+)"',
    )
    if len(excerpt) > 220:
        excerpt = excerpt[:217].rstrip() + "..."

    date = extract_field(
        html,
        r'"dateModified"\s*:\s*"([^"]+)"',
        r'"datePublished"\s*:\s*"([^"]+)"',
    )

    return {
        "title": title,
        "url": url,
        "category": category,
        "categoryLabel": CATEGORY_LABELS[category],
        "excerpt": excerpt,
        "date": date,
    }


def main() -> None:
    posts = [extract_post(path) for path in sorted(BLOG.rglob("index.html")) if is_post(path)]
    posts.sort(key=lambda item: item.get("date") or "", reverse=True)

    payload = {"categories": CATEGORIES, "posts": posts}
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Gerado {OUTPUT.relative_to(ROOT)} com {len(posts)} artigos.")


if __name__ == "__main__":
    main()
