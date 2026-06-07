#!/usr/bin/env python3
"""Remove barra final incorreta em URLs de arquivos estáticos."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXT_GROUP = r"(webp|png|jpg|jpeg|gif|svg|ico|js|css|woff2?|eot|ttf|rss|xml|pdf)"
PATTERN = re.compile(
    rf'((?:href|content|src|data-src|data-lazy-src)="[^"]+\.{EXT_GROUP})/(")(?=[\s>])',
    re.IGNORECASE,
)


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = PATTERN.sub(r"\1\2", original)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = sum(process_file(path) for path in ROOT.rglob("*.html"))
    print(f"Corrigidos: {changed} arquivos")


if __name__ == "__main__":
    main()
