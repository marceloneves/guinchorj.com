#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remove o botao flutuante de telefone das paginas com o numero local (24),
deixando so o de WhatsApp, que desce para a posicao de baixo."""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SLUGS = [
    'reboque-sul-fluminense',
    'reboque-em-volta-redonda', 'reboque-em-barra-mansa', 'reboque-em-resende',
    'reboque-em-itatiaia', 'reboque-em-penedo', 'reboque-em-porto-real',
    'reboque-em-quatis', 'reboque-em-barra-do-pirai', 'reboque-em-pirai',
    'reboque-em-pinheiral', 'reboque-em-rio-claro-rj', 'reboque-em-valenca',
    'reboque-em-rio-das-flores', 'reboque-em-niteroi',
]

RE_BOTAO = re.compile(r'<div class="floating-button-phone">.*?</div>', re.S)
CSS_ANTIGA = '.floating-button-whatsapp { right: 20px !important; bottom: 100px !important; top: auto !important; }'
CSS_NOVA = '.floating-button-whatsapp { right: 20px !important; bottom: 20px !important; top: auto !important; }'


def main():
    for slug in SLUGS:
        p = os.path.join(ROOT, 'servico', slug, 'index.html')
        h = open(p, encoding='utf-8').read()
        h, n = RE_BOTAO.subn('', h)
        css = h.count(CSS_ANTIGA)
        h = h.replace(CSS_ANTIGA, CSS_NOVA)
        open(p, 'w', encoding='utf-8').write(h)
        print('%-28s botao removido: %d | css reposicionada: %d' % (slug, n, css))


if __name__ == '__main__':
    main()
