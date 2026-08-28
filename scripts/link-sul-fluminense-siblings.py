#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Atualiza o interlinking do silo Sul Fluminense depois da criacao das paginas
municipais: linka mencoes em texto puro nas paginas irmas e corrige o FAQ do hub."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LINKS = {
    'Barra Mansa': 'reboque-em-barra-mansa',
    'Rio Claro': 'reboque-em-rio-claro-rj',
    'Piraí': 'reboque-em-pirai',
    'Pinheiral': 'reboque-em-pinheiral',
    'Porto Real': 'reboque-em-porto-real',
    'Quatis': 'reboque-em-quatis',
    'Valença': 'reboque-em-valenca',
}

# (pagina, trecho original, trecho com link)
PATCHES = [
    ('reboque-em-volta-redonda',
     'ao limite com Barra Mansa e Rio Claro',
     'ao limite com <a href="../reboque-em-barra-mansa/" title="Reboque em Barra Mansa">Barra Mansa</a> e <a href="../reboque-em-rio-claro-rj/" title="Reboque em Rio Claro">Rio Claro</a>'),
    ('reboque-em-volta-redonda',
     'também atendemos Barra Mansa, <a href="../reboque-em-resende/"',
     'também atendemos <a href="../reboque-em-barra-mansa/" title="Reboque em Barra Mansa">Barra Mansa</a>, <a href="../reboque-em-pinheiral/" title="Reboque em Pinheiral">Pinheiral</a>, <a href="../reboque-em-resende/"'),
    ('reboque-em-volta-redonda',
     'esse trecho da Dutra (em Piraí) exige',
     'esse trecho da Dutra (em <a href="../reboque-em-pirai/" title="Reboque em Piraí">Piraí</a>) exige'),
    ('reboque-em-resende',
     'esse trecho da Dutra (em Piraí) exige',
     'esse trecho da Dutra (em <a href="../reboque-em-pirai/" title="Reboque em Piraí">Piraí</a>) exige'),
    ('reboque-sul-fluminense',
     '(em Piraí) é um trecho clássico',
     '(em <a href="../reboque-em-pirai/" title="Reboque em Piraí">Piraí</a>) é um trecho clássico'),
    ('reboque-sul-fluminense',
     'Volta Redonda, Resende e Itatiaia têm páginas próprias; também cobrimos Barra Mansa, Porto Real, Quatis e Barra do Piraí em todo o Médio Paraíba.',
     'Todos os 14 municípios da região têm página própria: Volta Redonda, Barra Mansa, Resende, Itatiaia, Porto Real, Barra do Piraí, Piraí, Pinheiral, Quatis, Rio Claro, Rio das Flores, Valença, Angra dos Reis e Paraty — além do distrito de Penedo.'),
    ('reboque-sul-fluminense',
     'Atendemos Volta Redonda, Resende e Itatiaia, com páginas próprias, além de Barra Mansa, Porto Real, Quatis e Barra do Piraí, em toda a região do Médio Paraíba, conforme distância e disponibilidade.',
     'Atendemos os 14 municípios do Sul Fluminense, todos com página própria: Volta Redonda, Barra Mansa, Resende, Itatiaia, Porto Real, Barra do Piraí, Piraí, Pinheiral, Quatis, Rio Claro, Rio das Flores, Valença, Angra dos Reis e Paraty, além do distrito de Penedo.'),
]

# links extras no sidebar das paginas ja existentes do silo
SIDEBAR_EXTRA = {
    'reboque-em-volta-redonda': [('reboque-em-barra-mansa', 'Reboque em Barra Mansa'),
                                 ('reboque-em-pinheiral', 'Reboque em Pinheiral')],
    'reboque-em-resende': [('reboque-em-porto-real', 'Reboque em Porto Real'),
                           ('reboque-em-quatis', 'Reboque em Quatis')],
    'reboque-em-itatiaia': [('reboque-em-porto-real', 'Reboque em Porto Real')],
    'reboque-em-penedo': [('reboque-em-barra-mansa', 'Reboque em Barra Mansa')],
    'reboque-sul-fluminense': [('reboque-em-barra-mansa', 'Reboque em Barra Mansa'),
                               ('reboque-em-valenca', 'Reboque em Valença')],
}


def path(slug):
    return os.path.join(ROOT, 'servico', slug, 'index.html')


def main():
    touched = {}
    for slug, old, new in PATCHES:
        p = path(slug)
        h = open(p, encoding='utf-8').read()
        if old not in h:
            print('  aviso: trecho nao encontrado em %s: %.50s...' % (slug, old))
            continue
        h = h.replace(old, new)
        open(p, 'w', encoding='utf-8').write(h)
        touched[slug] = touched.get(slug, 0) + 1

    for slug, extras in SIDEBAR_EXTRA.items():
        p = path(slug)
        h = open(p, encoding='utf-8').read()
        m = re.search(r'(<h2 class="widget-title">Serviços</h2> <ul>)(.*?)(</ul>)', h, re.S)
        block = m.group(2)
        add = ''.join('<li><a href="../%s/" title="%s">%s</a></li>' % (s, lb, lb)
                      for s, lb in extras if '../%s/' % s not in block)
        if add:
            h = h[:m.start(2)] + block + add + h[m.end(2):]
            open(p, 'w', encoding='utf-8').write(h)
            touched[slug] = touched.get(slug, 0) + 1

    for slug, n in sorted(touched.items()):
        print('atualizada servico/%s/ (%d alteracoes)' % (slug, n))


if __name__ == '__main__':
    main()
