#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Padroniza o menu lateral do silo Sul Fluminense: toda pagina lista o hub e
todas as cidades da regiao (menos ela mesma)."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SILO = [
    ('reboque-sul-fluminense', 'Reboque no Sul Fluminense'),
    ('reboque-em-volta-redonda', 'Reboque em Volta Redonda'),
    ('reboque-em-barra-mansa', 'Reboque em Barra Mansa'),
    ('reboque-em-resende', 'Reboque em Resende'),
    ('reboque-em-itatiaia', 'Reboque em Itatiaia'),
    ('reboque-em-penedo', 'Reboque em Penedo'),
    ('reboque-em-porto-real', 'Reboque em Porto Real'),
    ('reboque-em-quatis', 'Reboque em Quatis'),
    ('reboque-em-barra-do-pirai', 'Reboque em Barra do Piraí'),
    ('reboque-em-pirai', 'Reboque em Piraí'),
    ('reboque-em-pinheiral', 'Reboque em Pinheiral'),
    ('reboque-em-rio-claro-rj', 'Reboque em Rio Claro'),
    ('reboque-em-valenca', 'Reboque em Valença'),
    ('reboque-em-rio-das-flores', 'Reboque em Rio das Flores'),
    ('reboque-em-angra-dos-reis', 'Reboque em Angra dos Reis'),
    ('reboque-em-paraty', 'Reboque em Paraty'),
]

# paginas que recebem o menu (Angra e Paraty ficam no silo da Costa Verde)
TARGETS = [s for s, _ in SILO if s not in ('reboque-em-angra-dos-reis', 'reboque-em-paraty')]


def main():
    for slug in TARGETS:
        p = os.path.join(ROOT, 'servico', slug, 'index.html')
        h = open(p, encoding='utf-8').read()
        m = re.search(r'(<h2 class="widget-title">Serviços</h2> <ul>)(.*?)(</ul>)', h, re.S)
        if not m:
            print('  aviso: widget nao encontrado em %s' % slug)
            continue
        itens = ''.join(
            '<li><a href="../%s/" title="%s">%s</a></li>' % (s, label, label)
            for s, label in SILO if s != slug)
        h = h[:m.start(2)] + itens + h[m.end(2):]
        open(p, 'w', encoding='utf-8').write(h)
        print('%-28s menu lateral com %d links' % (slug, len(SILO) - 1))


if __name__ == '__main__':
    main()
