#!/usr/bin/env python3
"""Correções pós-migração: assets, JSON-LD e meta tags."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSET_EXTENSIONS = (
    ".webp",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".js",
    ".css",
    ".woff",
    ".woff2",
    ".eot",
    ".ttf",
    ".rss",
    ".xml",
    ".pdf",
)


def is_asset_path(path: str) -> bool:
    lower = path.lower().split("?", 1)[0].split("#", 1)[0]
    return any(lower.endswith(ext) for ext in ASSET_EXTENSIONS)


def strip_asset_trailing_slash(content: str) -> str:
    pattern = re.compile(
        r'((?:href|content|src|data-src|data-lazy-src)="'
        r'(?:\.?/?(?:\.\./)*wp-content/[^"]+?)(/))(")',
        re.IGNORECASE,
    )

    def repl(match: re.Match[str]) -> str:
        prefix, slash, suffix = match.groups()
        if is_asset_path(prefix.split('"', 1)[1]):
            return prefix + suffix
        return match.group(0)

    return pattern.sub(repl, content)


def fix_json_ld_paths(content: str) -> str:
    def repl(match: re.Match[str]) -> str:
        value = match.group(1)
        if "wp-content/" in value or "cdn-cgi/" in value:
            return match.group(0)
        if value.endswith("/index.html"):
            return f'"{value[:-len("index.html")]}"'
        if value.endswith("index.html"):
            cleaned = value[: -len("index.html")]
            if not cleaned.endswith("/"):
                cleaned += "/"
            return f'"{cleaned}"'
        return match.group(0)

    return re.sub(r'"([^"]*index\.html[^"]*)"', repl, content)


def fix_homepage_og_image(content: str, path: Path) -> str:
    if path != ROOT / "index.html":
        return content

    if 'property="og:image" content="./"' not in content:
        return content

    return content.replace(
        'property="og:image" content="./"',
        'property="og:image" content="wp-content/uploads/2025/10/Guincho_1.webp"',
        1,
    )


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = original
    updated = strip_asset_trailing_slash(updated)
    updated = fix_json_ld_paths(updated)
    updated = fix_homepage_og_image(updated, path)

    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    for file_path in sorted(ROOT.rglob("*.html")):
        if process_file(file_path):
            changed += 1
    print(f"Corrigidos: {changed} arquivos")


if __name__ == "__main__":
    main()
