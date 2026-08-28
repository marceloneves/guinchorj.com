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

# Angra e Paraty sao Sul Fluminense e litoral: recebem o menu do silo e
# mantem, no topo, o hub e os vizinhos da Costa Verde.
COSTA_VERDE = [
    ('reboque-costa-verde', 'Reboque na Costa Verde'),
    ('reboque-em-mangaratiba', 'Reboque em Mangaratiba'),
    ('reboque-em-itaguai', 'Reboque em Itaguaí'),
]
EXTRA = {'reboque-em-angra-dos-reis': COSTA_VERDE, 'reboque-em-paraty': COSTA_VERDE}

TARGETS = [s for s, _ in SILO]


def main():
    for slug in TARGETS:
        p = os.path.join(ROOT, 'servico', slug, 'index.html')
        h = open(p, encoding='utf-8').read()
        m = re.search(r'(<h2 class="widget-title">Serviços</h2> <ul>)(.*?)(</ul>)', h, re.S)
        if not m:
            print('  aviso: widget nao encontrado em %s' % slug)
            continue
        lista = EXTRA.get(slug, []) + SILO
        vistos = set()
        itens = ''
        for s, label in lista:
            if s == slug or s in vistos:
                continue
            vistos.add(s)
            itens += '<li><a href="../%s/" title="%s">%s</a></li>' % (s, label, label)
        h = h[:m.start(2)] + itens + h[m.end(2):]
        open(p, 'w', encoding='utf-8').write(h)
        print('%-28s menu lateral com %d links' % (slug, len(vistos)))


if __name__ == '__main__':
    main()
