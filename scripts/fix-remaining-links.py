#!/usr/bin/env python3
"""Corrige os 2 ultimos grupos de links quebrados:
  Item 2: slug errado do Jardim Botanico na pagina da Zona Sul.
  Item 3: 2 e-mails ofuscados do Cloudflare (sem decoder) -> mailto real.
Aborta se algum trecho-alvo nao for encontrado.
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JOBS = [
    ("servico/reboque-na-zona-sul-no-rj/index.html", [
        ('<a href="../reboque-no-jardim-botanico-rj/">Reboque no Jardim Botânico</a>',
         '<a href="../reboque-no-jardim-botanico/" title="Reboque no Jardim Botânico">Reboque no Jardim Botânico</a>'),
    ]),
    ("perguntas-frequentes-sobre-guincho-e-reboque-no-rj/index.html", [
        ('<a href="../cdn-cgi/l/email-protection#f4979b9a8095809bb493819d9a979c9b869eda979b99/"><strong><span class="__cf_email__" data-cfemail="680b07061c091c07280f1d01060b00071a02460b0705">[email&#160;protected]</span></strong></a>',
         '<a href="mailto:contato@guinchorj.com"><strong>contato@guinchorj.com</strong></a>'),
        ('<a href="../cdn-cgi/l/email-protection#dfbcb0b1abbeabb09fb8aab6b1bcb7b0adb5f1bcb0b2/"><strong><span class="__cf_email__" data-cfemail="93f0fcfde7f2e7fcd3f4e6fafdf0fbfce1f9bdf0fcfe">[email&#160;protected]</span></strong></a>',
         '<a href="mailto:contato@guinchorj.com"><strong>contato@guinchorj.com</strong></a>'),
    ]),
]

def main():
    for rel, repls in JOBS:
        path = os.path.join(ROOT, rel)
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        for old, _new in repls:
            if old not in content:
                print(f"ABORTADO em {rel}: trecho nao encontrado:\n    {old[:80]}...")
                return 1
        for old, new in repls:
            content = content.replace(old, new, 1)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)
        print(f"OK {rel}: {len(repls)} ajuste(s)")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
