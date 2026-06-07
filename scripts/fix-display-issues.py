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


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = original.replace(BROKEN_FLATICON_RULE, FIXED_FLATICON_RULE)
    updated = updated.replace(".webpwebp", ".webp")

    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = sum(process_file(path) for path in ROOT.rglob("*.html"))
    print(f"Corrigidos: {changed} arquivos")


if __name__ == "__main__":
    main()
