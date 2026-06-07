#!/usr/bin/env python3
"""Converte links internos para URLs relativas sem extensão .html."""

from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_PREFIX = "https://guinchorj.com"
HTML_SUFFIX = "/index.html"

SKIP_URL_PREFIXES = (
    "http://",
    "https://",
    "mailto:",
    "tel:",
    "javascript:",
    "data:",
    "#",
    "api.whatsapp.com",
)


def page_dir(path: Path) -> Path:
    if path.name == "index.html":
        return path.parent
    return path.parent


def site_path_from_file(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    if not rel.endswith("/"):
        rel += "/"
    return "/" + rel


def relative_site_path(from_dir: Path, target_site_path: str) -> str:
    if target_site_path == "/":
        target_parts: list[str] = []
    else:
        target_parts = [p for p in target_site_path.strip("/").split("/") if p]

    from_parts = [] if from_dir == ROOT else [p for p in from_dir.relative_to(ROOT).as_posix().split("/") if p]

    common = 0
    for left, right in zip(from_parts, target_parts):
        if left != right:
            break
        common += 1

    ups = [".."] * (len(from_parts) - common)
    down = target_parts[common:]
    parts = ups + down

    if not parts:
        return "./"

    rel = "/".join(parts)
    if target_site_path.endswith("/") or target_site_path == "/":
        rel += "/"
    return rel


def clean_index_html_url(url: str) -> str | None:
    if any(url.startswith(prefix) for prefix in SKIP_URL_PREFIXES):
        return None
    if "wp-content/" in url or "cdn-cgi/" in url:
        return None

    if url == "index.html":
        return "./"

    if url.endswith("/index.html"):
        return url[: -len("index.html")]

    if url.endswith("index.html"):
        prefix = url[: -len("index.html")]
        if prefix.endswith("/"):
            return prefix
        return prefix + "/"

    return None


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


def absolutize_guinchorj(url: str) -> str | None:
    if not url.startswith(SITE_PREFIX):
        return None

    parsed = url[len(SITE_PREFIX) :]
    if not parsed or parsed == "/":
        return "/"
    if parsed.endswith("/index.html"):
        parsed = parsed[: -len("index.html")]
    elif parsed.endswith("index.html"):
        parsed = parsed[: -len("index.html")]
        if not parsed.endswith("/"):
            parsed += "/"

    if is_asset_path(parsed):
        return parsed

    if not parsed.endswith("/"):
        parsed += "/"
    return parsed


def replace_attr_urls(content: str, from_dir: Path, attr: str) -> str:
    pattern = re.compile(rf'({attr}=")([^"]+)(")', re.IGNORECASE)

    def repl(match: re.Match[str]) -> str:
        prefix, url, suffix = match.groups()

        if attr == "content" and "wp-content/" in url and is_asset_path(url):
            site_path = absolutize_guinchorj(url) if url.startswith(SITE_PREFIX) else None
            if site_path is not None:
                rel = site_path.lstrip("/")
                depth = 0 if from_dir == ROOT else len(from_dir.relative_to(ROOT).parts)
                return prefix + ("../" * depth + rel if depth else rel) + suffix
            return match.group(0)

        site_path = absolutize_guinchorj(url)
        if site_path is not None:
            if is_asset_path(site_path):
                rel = site_path.lstrip("/")
                depth = 0 if from_dir == ROOT else len(from_dir.relative_to(ROOT).parts)
                return prefix + ("../" * depth + rel if depth else rel) + suffix
            return prefix + relative_site_path(from_dir, site_path) + suffix

        cleaned = clean_index_html_url(url)
        if cleaned is not None:
            return prefix + cleaned + suffix

        return match.group(0)

    return pattern.sub(repl, content)


def replace_canonical_and_og_url(content: str, from_dir: Path) -> str:
    patterns = [
        re.compile(r'(rel="canonical"\s+href=")([^"]+)(")', re.IGNORECASE),
        re.compile(r'(property="og:url"\s+content=")([^"]+)(")', re.IGNORECASE),
    ]

    def normalize(url: str) -> str:
        site_path = absolutize_guinchorj(url)
        if site_path is not None and not is_asset_path(site_path):
            return relative_site_path(from_dir, site_path)
        cleaned = clean_index_html_url(url)
        if cleaned is not None:
            return cleaned
        return url

    for pattern in patterns:
        def repl(match: re.Match[str]) -> str:
            return match.group(1) + normalize(match.group(2)) + match.group(3)

        content = pattern.sub(repl, content)

    return content


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


def replace_json_ld_urls(content: str, from_dir: Path) -> str:
    pattern = re.compile(re.escape(SITE_PREFIX) + r"/?[^\"\\]*")

    def repl(match: re.Match[str]) -> str:
        raw = match.group(0)
        site_path = absolutize_guinchorj(raw.rstrip("\\"))
        if site_path is None:
            return raw
        rel = relative_site_path(from_dir, site_path)
        if rel.startswith("./"):
            return rel[2:]
        return rel

    return pattern.sub(repl, content)


def process_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    from_dir = page_dir(path)

    updated = original
    for attr in ("href", "action"):
        updated = replace_attr_urls(updated, from_dir, attr)

    updated = replace_canonical_and_og_url(updated, from_dir)
    updated = replace_json_ld_urls(updated, from_dir)
    updated = fix_json_ld_paths(updated)

    if updated != original:
        path.write_text(updated, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed = 0
    total = 0

    for file_path in sorted(ROOT.rglob("*.html")):
        if file_path.name.startswith("."):
            continue
        total += 1
        if process_file(file_path):
            changed += 1

    print(f"Processados: {total} arquivos")
    print(f"Alterados: {changed} arquivos")


if __name__ == "__main__":
    main()
