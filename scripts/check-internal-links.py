#!/usr/bin/env python3
"""Verifica links internos quebrados no site estatico guinchorj.com."""
import os
import re
import sys
from urllib.parse import urldefrag, unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_DOMAIN = "guinchorj.com"

# Extensoes/recursos que tratamos como arquivos diretos
ASSET_EXTS = {".html", ".css", ".js", ".webp", ".png", ".jpg", ".jpeg", ".gif",
              ".svg", ".ico", ".woff", ".woff2", ".ttf", ".eot", ".pdf", ".xml",
              ".txt", ".kml", ".json", ".webmanifest", ".mp4", ".avif"}

def collect_html_files():
    files = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if "node_modules" in dirpath or "/.git" in dirpath:
            continue
        for fn in filenames:
            if fn.endswith(".html"):
                files.append(os.path.join(dirpath, fn))
    return files

def resolve_target(link, source_file):
    """Retorna caminho absoluto no disco que o link deveria apontar, ou None se externo/ignorar."""
    link = link.strip()
    if not link:
        return None
    # Ignora esquemas nao-http
    if re.match(r"^(mailto:|tel:|javascript:|data:|whatsapp:|sms:|#)", link, re.I):
        return None
    # Remove fragmento
    link, _frag = urldefrag(link)
    if not link:
        return None
    parsed = urlparse(link)
    if parsed.scheme in ("http", "https"):
        # So consideramos interno se for o proprio dominio
        if SITE_DOMAIN not in parsed.netloc:
            return None
        path = parsed.path
        base = ROOT
    elif parsed.scheme:
        return None  # outro esquema
    else:
        path = parsed.path
        if path.startswith("/"):
            base = ROOT
        else:
            base = os.path.dirname(source_file)
    if not path:
        return None
    path = unquote(path)
    # Monta caminho no disco
    if path.startswith("/"):
        candidate = os.path.join(ROOT, path.lstrip("/"))
    else:
        candidate = os.path.normpath(os.path.join(base, path))
    return candidate

def exists_on_disk(candidate):
    if os.path.isfile(candidate):
        return True
    if os.path.isdir(candidate):
        # URL limpa -> precisa de index.html
        return os.path.isfile(os.path.join(candidate, "index.html"))
    # Sem barra final mas pode ser pasta com index.html
    if os.path.isfile(candidate + "/index.html") or os.path.isdir(candidate):
        return os.path.isfile(os.path.join(candidate, "index.html"))
    return False

def main():
    html_files = collect_html_files()
    broken = {}
    href_re = re.compile(r'(?:href|src)\s*=\s*"([^"]*)"', re.I)
    for f in html_files:
        with open(f, encoding="utf-8", errors="ignore") as fh:
            content = fh.read()
        rel_source = os.path.relpath(f, ROOT)
        for m in href_re.finditer(content):
            link = m.group(1)
            candidate = resolve_target(link, f)
            if candidate is None:
                continue
            if not exists_on_disk(candidate):
                broken.setdefault(rel_source, []).append(link)

    total = sum(len(v) for v in broken.values())
    if total == 0:
        print(f"OK - nenhum link interno quebrado em {len(html_files)} arquivos HTML.")
        return 0
    print(f"ENCONTRADOS {total} links internos quebrados em {len(broken)} arquivos:\n")
    for src in sorted(broken):
        uniq = sorted(set(broken[src]))
        print(f"  {src}  ({len(broken[src])} ocorrencias, {len(uniq)} unicos)")
        for link in uniq:
            print(f"      -> {link}")
    return 1

if __name__ == "__main__":
    sys.exit(main())
