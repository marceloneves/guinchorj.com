#!/usr/bin/env python3
"""Reduz cards de serviços na home para silo regional."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = Path(__file__).resolve().parent / "regional-services.json"
HOME = ROOT / "index.html"

SERVICES_SECTION = re.compile(
    r'(<section class="blog-area services-section pt-70 pb-70"><div class="container">'
    r'<div class="section-title"><h2>Serviços</h2></div><div class="row">)(.*?)(</div></div></section>)',
    re.DOTALL,
)
CARD = re.compile(
    r'<div class="col-lg-4 col-md-6"><div class="blog-item">.*?</div></div></div>',
    re.DOTALL,
)
SLUG_FROM_CARD = re.compile(r'href="(?:\.\./)*servico/([^/]+)/"')


def extract_cards(section_html: str) -> dict[str, str]:
    cards: dict[str, str] = {}
    for card in CARD.findall(section_html):
        match = SLUG_FROM_CARD.search(card)
        if match:
            cards[match.group(1)] = card
    return cards


def build_card_html(slug: str) -> str:
    path = ROOT / "servico" / slug / "index.html"
    content = path.read_text(encoding="utf-8")
    title_match = re.search(r"<title>([^<|]+)", content)
    h1_match = re.search(r"<h1[^>]*>([^<]+)</h1>", content)
    label = (h1_match or title_match).group(1).strip()
    label = label.replace("&#8211;", "–")
    image = "wp-content/uploads/2025/08/guinchorj-rio-de-janeiro-670x441.webp"
    img_match = re.search(r'src="(\.\./\.\/)?(wp-content/uploads/[^"]+\.(?:webp|jpg|png))"', content)
    if img_match:
        image = img_match.group(2)
    return (
        f'<div class="col-lg-4 col-md-6"><div class="blog-item"><div class="image">'
        f'<a href="servico/{slug}/" title="{label}" rel="nofollow">'
        f'<img width="392" height="205" src="{image}" class="lazyload wp-post-image" '
        f'alt="{label}" title="{label}" loading="lazy" decoding="async" ></a></div>'
        f'<div class="content"><h3><a href="servico/{slug}/" title="{label}">{label}</a></h3>'
        f"</div></div></div>"
    )


def update_home() -> None:
    slugs = json.loads(CONFIG.read_text(encoding="utf-8"))
    content = HOME.read_text(encoding="utf-8")
    match = SERVICES_SECTION.search(content)
    if not match:
        raise SystemExit("Seção de serviços não encontrada na home.")

    cards = extract_cards(match.group(2))
    for slug in slugs:
        if slug not in cards:
            cards[slug] = build_card_html(slug)

    new_row = "".join(cards[slug] for slug in slugs)
    updated = SERVICES_SECTION.sub(rf"\1{new_row}\3", content, count=1)

    if updated == content:
        print("Home já estava com cards regionais.")
        return

    HOME.write_text(updated, encoding="utf-8")
    print(f"Home atualizada: {len(slugs)} cards regionais.")


if __name__ == "__main__":
    update_home()
