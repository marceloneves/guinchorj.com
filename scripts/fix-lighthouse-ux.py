#!/usr/bin/env python3
"""Corrige avisos de UX/Performance do Lighthouse (logo, scripts, imagens, terceiros)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CLOUDFLARE_EMAIL_DECODE = re.compile(
    r'<script\s+data-cfasync="false"\s+src="(?:\.\./)*cdn-cgi/scripts/[^"]+/email-decode\.min\.js"></script>',
    re.IGNORECASE,
)

CLOUDFLARE_BEACON = re.compile(
    r'<script defer src="https://static\.cloudflareinsights\.com/beacon\.min\.js/[^"]+"'
    r"\s+data-cf-beacon='[^']*'></script>",
    re.IGNORECASE,
)

PRECONNECT_NOISE = re.compile(
    r'<link\s+rel="preconnect"\s+href="(?:\./|\.\./|https://(?:stats\.g\.doubleclick\.net|www\.google(?:\.com(?:\.br)?|-analytics\.com)))"[^>]*>\s*',
    re.IGNORECASE,
)

BROKEN_SPECULATION_RULES = re.compile(
    r'<script\s*>\{"prefetch"',
    re.IGNORECASE,
)

THEME_SCRIPT = re.compile(
    r'<script(?![^>]*\bdefer\b)(?![^>]*\basync\b)(\s+src="(?:\.\./)*wp-content/themes/leadv/assets/js/'
    r'(?:jquery|bootstrap|main)[^"]+\.js")',
    re.IGNORECASE,
)

LOGO_SRC = re.compile(
    r'src="((?:\.?/?(?:\.\./)*)wp-content/uploads/2025/08/)logo-guincho-rj\.webp"(?=\s+class="logo)',
    re.IGNORECASE,
)

OVERSIZED_CARD_IMAGE = re.compile(
    r'(<img width="392" height="205" src=")((?:\.?/?(?:\.\./)*)wp-content/uploads/2025/08/)'
    r'guinchorj-rio-de-janeiro-670x441\.webp"(\s+class="[^"]*wp-post-image")',
    re.IGNORECASE,
)

BROKEN_CARD_SRCSET = re.compile(
    r'srcset="((?:\.?/?(?:\.\./)*)wp-content/uploads/2025/08/)guinchorj-rio-de-janeiro-392x262\.webp 392w, '
    r'(?:\.?/?(?:\.\./)*)wp-content/uploads/2025/08/guinchorj-rio-de-janeiro-670x441\.webp 670w" '
    r'sizes="\(max-width: 576px\) 100vw, \(max-width: 992px\) 50vw, 392px""',
    re.IGNORECASE,
)

BROKEN_SIZES_QUOTE = re.compile(
    r'sizes="\(max-width: 576px\) 100vw, \(max-width: 992px\) 50vw, 392px""',
    re.IGNORECASE,
)

CARD_SRCSET_670 = re.compile(
    r'srcset="((?:\.?/?(?:\.\./)*)wp-content/uploads/2025/08/)guinchorj-rio-de-janeiro-392x262\.webp 392w, '
    r'(?:\.?/?(?:\.\./)*)wp-content/uploads/2025/08/guinchorj-rio-de-janeiro-670x441\.webp 670w"',
    re.IGNORECASE,
)


def fix_speculation_rules(html: str) -> str:
    return BROKEN_SPECULATION_RULES.sub(
        '<script type="speculationrules">{"prefetch"',
        html,
    )


def remove_cloudflare_email_decode(html: str) -> str:
    return CLOUDFLARE_EMAIL_DECODE.sub("", html)


def add_logo_srcset(html: str) -> str:
    if "logo-guincho-rj@2x.webp" in html:
        return html

    def repl(match: re.Match[str]) -> str:
        base = match.group(1)
        return (
            f'src="{base}logo-guincho-rj.webp" '
            f'srcset="{base}logo-guincho-rj.webp 1x, {base}logo-guincho-rj@2x.webp 2x"'
        )

    return LOGO_SRC.sub(repl, html)


def remove_cloudflare_beacon(html: str) -> str:
    return CLOUDFLARE_BEACON.sub("", html)


def remove_noisy_preconnects(html: str) -> str:
    return PRECONNECT_NOISE.sub("", html)


def defer_theme_scripts(html: str) -> str:
    return THEME_SCRIPT.sub(r"<script defer\1", html)


def fix_logo_loading(html: str) -> str:
    return re.sub(
        r'(<img[^>]*class="[^"]*\blogo\b[^"]*"[^>]*)\sloading="lazy"',
        r'\1 loading="eager"',
        html,
        flags=re.IGNORECASE,
    )


def card_srcset_markup(base: str) -> str:
    src392 = f"{base}guinchorj-rio-de-janeiro-392x262.webp"
    src540 = f"{base}guinchorj-rio-de-janeiro-540x354.webp"
    return (
        f'srcset="{src392} 392w, {src540} 540w" '
        f'sizes="(max-width: 576px) 100vw, (max-width: 992px) 50vw, 392px"'
    )


def fix_broken_card_srcset(html: str) -> str:
    html = BROKEN_SIZES_QUOTE.sub(
        'sizes="(max-width: 576px) 100vw, (max-width: 992px) 50vw, 392px"',
        html,
    )

    def repl670(match: re.Match[str]) -> str:
        return card_srcset_markup(match.group(1))

    html = CARD_SRCSET_670.sub(repl670, html)

    def repl(match: re.Match[str]) -> str:
        return card_srcset_markup(match.group(1))

    return BROKEN_CARD_SRCSET.sub(repl, html)


def fix_oversized_card_images(html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix, base, suffix = match.groups()
        src392 = f"{base}guinchorj-rio-de-janeiro-392x262.webp"
        return f'{prefix}{src392}" {card_srcset_markup(base)}{suffix}'

    return OVERSIZED_CARD_IMAGE.sub(repl, html)


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    updated = fix_speculation_rules(original)
    updated = remove_cloudflare_email_decode(updated)
    updated = remove_cloudflare_beacon(updated)
    updated = remove_noisy_preconnects(updated)
    updated = defer_theme_scripts(updated)
    updated = add_logo_srcset(updated)
    updated = fix_logo_loading(updated)
    updated = fix_broken_card_srcset(updated)
    updated = fix_oversized_card_images(updated)

    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    total = 0

    for file_path in sorted(ROOT.rglob("*.html")):
        if "wp-content" in file_path.parts or file_path.name.startswith("."):
            continue
        total += 1
        if process_file(file_path):
            changed += 1

    print(f"Processados: {total} arquivos")
    print(f"Alterados: {changed} arquivos")


if __name__ == "__main__":
    main()
