#!/usr/bin/env python3
"""Substitui e-mails ofuscados do Cloudflare por endereços legíveis."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EMAIL_PATTERN = re.compile(
    r'<a([^>]*?)href="[^"]*?/l/email-protection#[^"]+"([^>]*?)>'
    r'<span class="__cf_email__" data-cfemail="([a-f0-9]+)">[^<]*</span></a>',
    re.IGNORECASE,
)


def decode_cfemail(encoded: str) -> str:
    key = int(encoded[:2], 16)
    return "".join(chr(int(encoded[index : index + 2], 16) ^ key) for index in range(2, len(encoded), 2))


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")

    def repl(match: re.Match[str]) -> str:
        before, after, encoded = match.groups()
        email = decode_cfemail(encoded)
        attrs = f"{before}{after}".strip()
        if "href=" in attrs:
            attrs = re.sub(r'href="[^"]*"', "", attrs)
        attrs = attrs.strip()
        attr_prefix = f" {attrs}" if attrs else ""
        return f'<a{attr_prefix} href="mailto:{email}">{email}</a>'

    updated = EMAIL_PATTERN.sub(repl, original)
    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = sum(process_file(path) for path in ROOT.rglob("*.html"))
    print(f"E-mails corrigidos em {changed} arquivos")


if __name__ == "__main__":
    main()
