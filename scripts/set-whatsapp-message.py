#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reescreve o texto pre-preenchido dos links de WhatsApp para identificar a
origem (site guinchorj.com) e a pagina de onde o clique veio.

Antes:  Preciso de guincho em Valença. Pode me ajudar?
Depois: Olá! Vim pelo site guinchorj.com e preciso de guincho em Valença.
        Pode me ajudar?
"""
import glob
import os
import re
from urllib.parse import quote, unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = ('node_modules/', 'wp-content/', '.vercel/')

RE_LINK = re.compile(r'(api\.whatsapp\.com/send\?phone=\d+&amp;text=)([^"]+)')
PREFIXO = 'Olá! Vim pelo site guinchorj.com'
RE_SAUDACAO = re.compile(r'^(Olá|Ola|Oi)[,!]?\s+', re.I)


def caminho_publico(rel):
    """servico/reboque-em-valenca/index.html -> /servico/reboque-em-valenca/"""
    rel = rel.replace(os.sep, '/')
    if rel == 'index.html':
        return '/'
    if rel.endswith('/index.html'):
        return '/' + rel[:-len('index.html')]
    return '/' + rel


def novo_texto(antigo, pagina):
    """Prefixa o pedido com a origem, preservando o texto original do link."""
    if antigo.startswith(PREFIXO):
        return None  # ja identificado
    pedido = RE_SAUDACAO.sub('', antigo).strip()
    if not pedido.lower().startswith('preciso'):
        return None
    pedido = pedido[0].lower() + pedido[1:]
    if not pedido.endswith(('?', '.', '!')):
        pedido += '. Pode me ajudar?'
    return '%s e %s' % (PREFIXO, pedido)


def main():
    arquivos = [p for p in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)
                if not any(s in p.replace(os.sep, '/') for s in SKIP)]
    alterados = trocas = 0
    nao_reconhecidos = set()
    for p in sorted(arquivos):
        rel = os.path.relpath(p, ROOT)
        pagina = caminho_publico(rel)
        h = open(p, encoding='utf-8').read()
        n = [0]

        def sub(m):
            antigo = unquote(m.group(2))
            novo = novo_texto(antigo, pagina)
            if novo is None:
                nao_reconhecidos.add(antigo)
                return m.group(0)
            n[0] += 1
            return m.group(1) + quote(novo, safe='')

        novo_html = RE_LINK.sub(sub, h)
        if n[0]:
            open(p, 'w', encoding='utf-8').write(novo_html)
            alterados += 1
            trocas += n[0]
    print('%d arquivos, %d links de WhatsApp atualizados' % (alterados, trocas))
    for t in sorted(nao_reconhecidos):
        print('  nao reconhecido (mantido): %r' % t)


if __name__ == '__main__':
    main()
