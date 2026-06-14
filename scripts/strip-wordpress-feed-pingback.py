#!/usr/bin/env python3
"""Remove tags legadas do WordPress: <link rel=pingback> (xmlrpc) e <link rel=alternate rss+xml> (feeds).
NAO apaga nenhum arquivo. So edita o HTML, removendo as duas tags do <head>.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Tags-alvo (qualquer href). Removemos a tag e, se a linha ficar so com espacos, a linha toda.
PINGBACK = re.compile(r'[ \t]*<link[^>]*\brel="pingback"[^>]*>[ \t]*\n?', re.I)
RSSFEED  = re.compile(r'[ \t]*<link[^>]*\btype="application/rss\+xml"[^>]*>[ \t]*\n?', re.I)

def main():
    changed = 0
    total_ping = 0
    total_feed = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if "node_modules" in dirpath or "/.git" in dirpath:
            continue
        for fn in filenames:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            with open(path, encoding="utf-8", errors="ignore") as fh:
                content = fh.read()
            new, n_ping = PINGBACK.subn("", content)
            new, n_feed = RSSFEED.subn("", new)
            if n_ping or n_feed:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(new)
                changed += 1
                total_ping += n_ping
                total_feed += n_feed
                rel = os.path.relpath(path, ROOT)
                print(f"  {rel}: pingback={n_ping} feed={n_feed}")
    print(f"\nArquivos alterados: {changed} | pingbacks removidos: {total_ping} | feeds removidos: {total_feed}")

if __name__ == "__main__":
    main()
