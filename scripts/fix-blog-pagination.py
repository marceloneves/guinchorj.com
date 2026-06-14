#!/usr/bin/env python3
"""Corrige a paginacao quebrada da categoria blog/reboque-e-guincho.
So existem as paginas 1-4; remove/ajusta os links para 5,6,8 (sobra do WordPress).
Aborta se algum trecho-alvo nao for encontrado (nada e alterado nesse arquivo).
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "blog", "reboque-e-guincho")

# (arquivo, [(old, new), ...])
JOBS = [
    ("index.html", [
        ('<a class="page-numbers" href="page/8/" title="8">8</a>',
         '<a class="page-numbers" href="page/4/" title="4">4</a>'),
    ]),
    ("page/2/index.html", [
        ('<a class="page-numbers" href="../8/" title="8">8</a>', ''),
    ]),
    ("page/3/index.html", [
        ('<a class="page-numbers" href="../5/" title="5">5</a>', ''),
        ('<a class="page-numbers" href="../8/" title="8">8</a>', ''),
    ]),
    ("page/4/index.html", [
        ('<a class="page-numbers" href="../5/" title="5">5</a>', ''),
        ('<a class="page-numbers" href="../6/" title="6">6</a>', ''),
        ('<a class="page-numbers" href="../8/" title="8">8</a>', ''),
        ('<a href="../5/" >Próxima página &raquo;</a>', ''),
    ]),
]

def main():
    for rel, repls in JOBS:
        path = os.path.join(BASE, rel)
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        # valida tudo antes de gravar
        for old, _new in repls:
            if old not in content:
                print(f"ABORTADO em {rel}: trecho nao encontrado:\n    {old}")
                return 1
        for old, new in repls:
            content = content.replace(old, new, 1)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"OK {rel}: {len(repls)} ajuste(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
