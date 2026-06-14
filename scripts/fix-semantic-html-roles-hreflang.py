#!/usr/bin/env python3
"""Corrige as falhas do validador de HTML semantico em todas as paginas:
  1) <header>  -> <header role="banner">   (so o header do site, nao o page-title-area)
  2) <footer class="footer-area pt-100 pb-70"> -> + role="contentinfo"
  3) hreflang: ajusta o href dos <link rel="alternate" ... hreflang> para o canonical da propria pagina.
NAO apaga arquivos. Relata o que mudou em cada um.
"""
import os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = [p for p in glob.glob(os.path.join(ROOT, "**", "index.html"), recursive=True)
         if "node_modules" not in p]

HEADER_OLD = "<header>"
HEADER_NEW = '<header role="banner">'
FOOTER_OLD = '<footer class="footer-area pt-100 pb-70">'
FOOTER_NEW = '<footer class="footer-area pt-100 pb-70" role="contentinfo">'

CANON_RE = re.compile(r'<link rel="canonical" href="([^"]+)"')
# href dentro de um <link rel="alternate" href="..." hreflang="...">
ALT_RE = re.compile(r'(<link rel="alternate" href=")([^"]*)("\s+hreflang=")')

def main():
    tot_h = tot_f = tot_hl = 0
    changed = 0
    for p in PAGES:
        s = open(p, encoding="utf-8", errors="ignore").read()
        orig = s
        nh = nf = nhl = 0
        if HEADER_OLD in s:
            s, nh = s.replace(HEADER_OLD, HEADER_NEW, 1), 1
        if FOOTER_OLD in s:
            s, nf = s.replace(FOOTER_OLD, FOOTER_NEW, 1), 1
        m = CANON_RE.search(s)
        if m:
            canon = m.group(1)
            def repl(mm):
                return mm.group(1) + canon + mm.group(3)
            s, nhl = ALT_RE.subn(repl, s)
        if s != orig:
            open(p, "w", encoding="utf-8").write(s)
            changed += 1
            tot_h += nh; tot_f += nf; tot_hl += nhl
    print(f"Arquivos alterados: {changed}/{len(PAGES)}")
    print(f"  header role=banner adicionados: {tot_h}")
    print(f"  footer role=contentinfo adicionados: {tot_f}")
    print(f"  hrefs de hreflang normalizados p/ canonical: {tot_hl}")

if __name__ == "__main__":
    main()
