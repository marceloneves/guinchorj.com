#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera as paginas municipais do silo Sul Fluminense.

Clona o chrome (head, menu, rodape) da pagina de Volta Redonda e substitui
head/JSON-LD/breadcrumb/artigo pelo conteudo de scripts/sul_fluminense_content.py.
Tambem atualiza o sitemap de servicos e o interlinking do hub e das paginas irmas.
"""
import importlib.util
import json
import os
import re
import sys
from datetime import datetime
from urllib.parse import quote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, 'servico', 'reboque-em-volta-redonda', 'index.html')
SITEMAP = os.path.join(ROOT, 'servico-sitemap.xml')
HUB = os.path.join(ROOT, 'servico', 'reboque-sul-fluminense', 'index.html')

BASE_CITY = 'Volta Redonda'
BASE_SLUG = 'reboque-em-volta-redonda'
BASE_TITLE = 'Reboque em Volta Redonda 24h | Guincho na Cidade do Aço'
SITE = 'https://guinchorj.com'

spec = importlib.util.spec_from_file_location(
    'sf_content', os.path.join(ROOT, 'scripts', 'sul_fluminense_content.py'))
content = importlib.util.module_from_spec(spec)
spec.loader.exec_module(content)


def wa(city):
    return 'Preciso%20de%20guincho%20em%20' + quote(city, safe='') + '.%20Pode%20me%20ajudar%3F'


def render_items(kind, items):
    lis = ''.join('<li><p>%s</p></li>' % it for it in items)
    if kind == 'ol':
        return '<ol start="1">%s</ol>' % lis
    return '<ul>%s</ul>' % lis


def render_article(c):
    city = c['city']
    watext = wa(city)
    sidebar = ''.join(
        '<li><a href="../%s/" title="%s">%s</a></li>' % (slug, label, label)
        for slug, label in c['sidebar'])

    body = ''.join(c['lead'])
    body += '<section class="atendimento-local"><h2>%s</h2>%s</section>' % (
        c['local']['h2'], ''.join(c['local']['p']))
    for s in c['sections']:
        body += '<h2>%s</h2><p>%s</p>%s' % (s['h2'], s['p'], render_items(s['type'], s['items']))
        if s.get('after'):
            body += s['after']
    body += '<h2>8. Perguntas Frequentes (FAQ)</h2>'
    for q, a in c['faq_visible']:
        body += '<p><b>%s</b></p><p>%s</p>' % (q, a)

    return (
        '<section class="services-details-area ptb-100">'
        '<h2 class="skip-link">Reboque em {city}</h2>'
        '<div class="container"> <div class="row"> <div class="col-lg-4 col-md-12">'
        '<aside aria-label="Serviços relacionados">'
        '<nav class="widget-area" id="secondary"> <section class="widget widget_categories">'
        '<h2 class="widget-title">Serviços</h2> <ul>{sidebar}</ul> </section>'
        '<section class="widget widget_hours"> <h3 class="widget-title">Solicite um orçamento</h3> <ul>'
        '<li> Telefone <span><a href="tel:+5521959543043" title="Telefone" rel="nofollow">(21) 95954-3043</a></span> </li>'
        '<li> Whatsapp <span><a href="https://api.whatsapp.com/send?phone=5521959543043&amp;text={watext}"'
        ' title="Whatsapp" target="_blank" rel="noopener nofollow">(21) 95954-3043</a></span> </li>'
        '<li> E-mail <span><a title="E-mail" rel="nofollow" style="text-transform:lowercase;"'
        ' href="mailto:contato@guinchorj.com">contato@guinchorj.com</a></span> </li>'
        '</ul> </section> </nav></aside></div>'
        '<article class="col-lg-8 col-md-12 order-first order-md-1">'
        '<h2 class="skip-link">Reboque em {city}</h2>'
        '<div class="services-details-desc"> <figure class="image" style="display:flex;align-items:center;justify-content:center;">'
        '<img width="670" height="441" src="../../wp-content/uploads/2025/08/guinchorj-rio-de-janeiro-670x441.webp"'
        ' class="img-responsive wp-post-image" alt="Reboque em {city}" title="Reboque em {city}"'
        ' loading="eager" decoding="async" style="max-width:100%;height:auto;border-radius:10px"></figure>'
        ' <div class="writen_content"> <p class="lead" style="text-align:center">Precisa de Reboque em {city}?</p>'
        '<p style="text-align: center;"> <i class="fa fa-phone" aria-hidden="true"></i>'
        ' <a href="tel:+5521959543043" title="Telefone" style="display: inline-block;" rel="nofollow">(21) 95954-3043</a> | '
        '<i class="fa fa-whatsapp" aria-hidden="true"></i>'
        ' <a href="https://api.whatsapp.com/send?phone=5521959543043&amp;text={watext}" title="Whatsapp"'
        ' rel="nofollow external noopener" target="_blank" style="display: inline-block;">(21) 95954-3043</a>'
        ' Atendimento 24 horas em toda a região do Médio Paraíba.</p> <div class="contact-form"> </div>'
        '<div class="markdown" dir="ltr">{body}</div> </div> </div> </article> </div> </div> </section>'
    ).format(city=city, sidebar=sidebar, watext=watext, body=body)


def build_jsonld(base_graph, c):
    url = '%s/servico/%s/' % (SITE, c['slug'])
    graph = json.loads(json.dumps(base_graph))
    for node in graph['@graph']:
        if node.get('@type') == 'Service':
            node['@id'] = url + '#service'
            node['name'] = 'Reboque em %s' % c['city']
            node['description'] = c['desc']
            node['url'] = url
            node['areaServed'] = c['area']
            node['mainEntityOfPage'] = {'@id': url + '#webpage'}
            faq = node['subjectOf']
            faq['@id'] = url + '#faq'
            faq['mainEntity'] = [
                {'@type': 'Question', 'name': q,
                 'acceptedAnswer': {'@type': 'Answer', 'text': a}}
                for q, a in c['faq_schema']]
        elif node.get('@type') == 'WebPage':
            node['name'] = 'Reboque em %s' % c['city']
            node['url'] = url
            node['description'] = c['desc']
            node['@id'] = url + '#webpage'
            node['mainEntity'] = {'@id': url + '#service'}
            crumbs = node['breadcrumb']['itemListElement']
            crumbs[-1]['name'] = c['city']
            crumbs[-1].pop('item', None)
    return json.dumps(graph, ensure_ascii=False)


def main():
    base = open(BASE, encoding='utf-8').read()
    base_jsonld = json.loads(
        re.search(r'<script type="application/ld\+json">(.*?)</script>', base, re.S).group(1))
    base_desc = re.search(r'<meta name="description" content="([^"]*)"', base).group(1)
    base_article = base[base.find('<section class="services-details-area'):
                        base.find('<section class="solution-area')]
    now = datetime.now().astimezone()
    stamp = now.strftime('%Y-%m-%dT%H:%M:%S%z')
    stamp = stamp[:-2] + ':' + stamp[-2:]

    created = []
    for c in content.CITIES:
        h = base
        # placeholders: o artigo e o JSON-LD sao inseridos DEPOIS das substituicoes
        # globais, para nao reescrever mencoes legitimas a Volta Redonda no texto.
        h = h.replace(re.search(r'<script type="application/ld\+json">.*?</script>', h, re.S).group(0),
                      '@@JSONLD@@')
        h = h.replace(base_article, '@@ARTICLE@@')
        h = h.replace('<title>%s</title>' % BASE_TITLE, '<title>%s</title>' % c['title'])
        h = h.replace(base_desc, c['desc'])
        h = h.replace(BASE_TITLE, c['title'])
        h = h.replace('servico/%s/' % BASE_SLUG, 'servico/%s/' % c['slug'])
        h = re.sub(r'(<meta property="og:updated_time" content=")[^"]*(")',
                   r'\g<1>%s\g<2>' % stamp, h)
        h = h.replace(quote(BASE_CITY, safe=''), quote(c['city'], safe=''))
        h = h.replace(BASE_CITY, c['city'])

        residuo = [t for t in (BASE_CITY, 'Cidade do Aço', 'servico/%s/' % BASE_SLUG,
                               quote(BASE_CITY, safe='')) if t in h]
        if residuo:
            sys.exit('ERRO: sobrou referencia a %s em %s' % (residuo, c['slug']))

        h = h.replace('@@JSONLD@@',
                      '<script type="application/ld+json">%s</script>' % build_jsonld(base_jsonld, c))
        h = h.replace('@@ARTICLE@@', render_article(c))

        outdir = os.path.join(ROOT, 'servico', c['slug'])
        os.makedirs(outdir, exist_ok=True)
        with open(os.path.join(outdir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(h)
        created.append(c['slug'])
        print('criada servico/%s/index.html (%d KB)' % (c['slug'], len(h.encode()) // 1024))

    update_sitemap(created, stamp)
    update_hub(created)
    print('OK: %d paginas' % len(created))


def update_sitemap(slugs, stamp):
    xml = open(SITEMAP, encoding='utf-8').read()
    utc = datetime.now().strftime('%Y-%m-%dT%H:%M:%S+00:00')
    block = ''
    for slug in slugs:
        loc = '%s/servico/%s/' % (SITE, slug)
        if loc in xml:
            continue
        block += '\t<url>\n\t\t<loc>%s</loc>\n\t\t<lastmod>%s</lastmod>\n\t</url>\n' % (loc, utc)
    if block:
        xml = xml.replace('</urlset>', block + '</urlset>')
        open(SITEMAP, 'w', encoding='utf-8').write(xml)
        print('sitemap: +%d URLs' % len(slugs))


def update_hub(slugs):
    """Adiciona as novas cidades a lista '3. Cidades atendidas' e ao sidebar do hub."""
    html = open(HUB, encoding='utf-8').read()
    extras = [
        ('reboque-em-barra-mansa', 'Reboque em Barra Mansa', 'a segunda maior cidade da região, na Dutra e na BR-393'),
        ('reboque-em-barra-do-pirai', 'Reboque em Barra do Piraí', 'entroncamento do Vale do Café, na BR-393'),
        ('reboque-em-pirai', 'Reboque em Piraí', 'a descida da Serra das Araras, na Via Dutra'),
        ('reboque-em-pinheiral', 'Reboque em Pinheiral', 'trecho urbano da Via Dutra entre Volta Redonda e Piraí'),
        ('reboque-em-porto-real', 'Reboque em Porto Real', 'o polo automotivo do Médio Paraíba'),
        ('reboque-em-quatis', 'Reboque em Quatis', 'sede e os distritos de Falcão e Ribeirão de São Joaquim'),
        ('reboque-em-rio-claro-rj', 'Reboque em Rio Claro', 'a serra da RJ-155 rumo a Angra dos Reis'),
        ('reboque-em-rio-das-flores', 'Reboque em Rio das Flores', 'estradas rurais do Vale do Café'),
        ('reboque-em-valenca', 'Reboque em Valença', 'Conservatória e os seis distritos do município'),
    ]
    marker = '<a href="../reboque-em-penedo/" title="Reboque em Penedo">Reboque em Penedo</a> — a Colônia Finlandesa, distrito de Itatiaia.</li>'
    add = ''.join(
        '<li><a href="../%s/" title="%s">%s</a> — %s.</li>' % (slug, label, label, desc)
        for slug, label, desc in extras if '../%s/' % slug not in html)
    if add and marker in html:
        html = html.replace(marker, marker + add)
        open(HUB, 'w', encoding='utf-8').write(html)
        print('hub: +%d links de cidade' % len(extras))


if __name__ == '__main__':
    main()
