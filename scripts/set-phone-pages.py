#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Troca o telefone/WhatsApp de paginas especificas.

Substitui todas as ocorrencias do numero central pelo numero local informado:
links tel:, links do WhatsApp (botao flutuante, topo, sidebar, corpo, rodape),
texto exibido e os campos telephone/contactPoint do JSON-LD.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OLD = {'digits': '5521959543043', 'display': '(21) 95954-3043'}
NEW = {'digits': '5524974037983', 'display': '(24) 97403-7983'}

SLUGS = [
    'reboque-em-barra-mansa',
    'reboque-em-barra-do-pirai',
    'reboque-em-pirai',
    'reboque-em-pinheiral',
    'reboque-em-porto-real',
    'reboque-em-quatis',
    'reboque-em-rio-claro-rj',
    'reboque-em-rio-das-flores',
    'reboque-em-valenca',
    'reboque-em-niteroi',
    # silo Sul Fluminense completo: hub + municipais antigas
    'reboque-sul-fluminense',
    'reboque-em-volta-redonda',
    'reboque-em-resende',
    'reboque-em-itatiaia',
    'reboque-em-penedo',
]


def main():
    total = 0
    for slug in SLUGS:
        p = os.path.join(ROOT, 'servico', slug, 'index.html')
        if not os.path.exists(p):
            sys.exit('ERRO: %s nao existe' % p)
        h = open(p, encoding='utf-8').read()
        n = h.count(OLD['digits']) + h.count(OLD['display'])
        if n == 0:
            print('%-28s ja estava com o numero novo' % slug)
            continue
        h = h.replace(OLD['digits'], NEW['digits']).replace(OLD['display'], NEW['display'])
        resto = OLD['digits'] in h or OLD['display'] in h
        assert not resto, slug
        open(p, 'w', encoding='utf-8').write(h)
        total += n
        print('%-28s %2d ocorrencias trocadas' % (slug, n))
    print('total: %d' % total)


if __name__ == '__main__':
    main()
