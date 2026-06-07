#!/usr/bin/env python3
"""Corrige ícones Flaticon e URLs de assets corrompidas."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BROKEN_FLATICON_RULE = (
    '[class*=" flaticon-"]:before,[class^=flaticon-]:after,[class*=" flaticon-"]:after'
    "{font-family:Flaticon;font-style:normal}"
)
FIXED_FLATICON_RULE = (
    '[class*=" flaticon-"]:before,[class^=flaticon-]:before,[class^=flaticon-]:after,'
    '[class*=" flaticon-"]:after{font-family:Flaticon;font-style:normal}'
)


BROKEN_IMAGE_META_REPLACEMENTS = (
    (".webp >", ".webp\">"),
    (".jpg >", ".jpg\">"),
    (".jpeg >", ".jpeg\">"),
    (".png >", ".png\">"),
    (".webp \">", ".webp\">"),
    (".jpg \">", ".jpg\">"),
    (".jpeg \">", ".jpeg\">"),
    (".png \">", ".png\">"),
)


def fix_broken_image_meta_quotes(html: str) -> str:
    """Corrige meta og:image com aspas faltando (ex.: content=\"...webp >)."""
    updated = html
    for broken, fixed in BROKEN_IMAGE_META_REPLACEMENTS:
        updated = updated.replace(broken, fixed)
    return updated


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = original.replace(BROKEN_FLATICON_RULE, FIXED_FLATICON_RULE)
    updated = updated.replace(".webpwebp", ".webp")
    updated = updated.replace(".pngpng >", '.png">')
    updated = updated.replace(".jpgjpg >", '.jpg">')
    updated = fix_broken_image_meta_quotes(updated)

    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = sum(process_file(path) for path in ROOT.rglob("*.html"))
    print(f"Corrigidos: {changed} arquivos")


if __name__ == "__main__":
    main()
