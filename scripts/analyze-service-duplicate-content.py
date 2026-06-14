#!/usr/bin/env python3
"""Avalia conteudo repetitivo entre as paginas de servico.
Extrai o texto do <article> principal (conteudo unico), normaliza removendo
o nome do bairro, e mede similaridade (Jaccard sobre shingles de 5 palavras).
NAO altera nenhum arquivo - so analisa e reporta.
"""
import os, re, glob, html, unicodedata
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = sorted(glob.glob(os.path.join(ROOT, "servico", "*", "index.html")))

def extract_article(content):
    # pega do primeiro <article ...> ate o </article> correspondente (simplificado)
    m = re.search(r'<article\b[^>]*>(.*?)</article>', content, re.S | re.I)
    return m.group(1) if m else ""

def strip_tags(s):
    s = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', ' ', s, flags=re.S | re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    return s

def slug_words(path):
    slug = os.path.basename(os.path.dirname(path))  # reboque-em-copacabana
    return set(re.split(r'[-]', slug))

def normalize(text, extra_stop):
    text = text.lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    words = re.findall(r'[a-z0-9]+', text)
    # remove palavras do slug/bairro pra nao mascarar duplicacao real
    words = [w for w in words if w not in extra_stop]
    return words

def shingles(words, k=5):
    return set(tuple(words[i:i+k]) for i in range(len(words) - k + 1)) if len(words) >= k else set(tuple(words))

def jaccard(a, b):
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)

# stopwords genericas + termos do dominio que aparecem em todas
COMMON = set("reboque guincho rj rio de janeiro em no na do da o a e para com 24 horas servico servicos".split())

docs = {}
for p in PAGES:
    raw = open(p, encoding='utf-8', errors='ignore').read()
    art = extract_article(raw)
    txt = strip_tags(art)
    stop = COMMON | slug_words(p)
    words = normalize(txt, stop)
    rel = os.path.relpath(p, ROOT)
    docs[rel] = {'words': words, 'nwords': len(words), 'sh': shingles(words)}

print(f"Paginas analisadas: {len(docs)}")
nw = sorted(d['nwords'] for d in docs.values())
print(f"Palavras unicas por pagina (conteudo do article): min={nw[0]} mediana={nw[len(nw)//2]} max={nw[-1]}")

# clusteriza por similaridade alta
names = list(docs)
THRESH = 0.80
parent = {n: n for n in names}
def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
def union(a, b):
    parent[find(a)] = find(b)

pairs_high = []
for i in range(len(names)):
    a = docs[names[i]]['sh']
    for j in range(i+1, len(names)):
        s = jaccard(a, docs[names[j]]['sh'])
        if s >= THRESH:
            union(names[i], names[j])
            pairs_high.append((s, names[i], names[j]))

clusters = defaultdict(list)
for n in names:
    clusters[find(n)].append(n)
dupe_clusters = {k: v for k, v in clusters.items() if len(v) > 1}

print(f"\n=== Grupos de paginas QUASE IDENTICAS (Jaccard >= {THRESH}) ===")
print(f"Grupos: {len(dupe_clusters)} | paginas envolvidas: {sum(len(v) for v in dupe_clusters.values())}")
for k, v in sorted(dupe_clusters.items(), key=lambda kv: -len(kv[1])):
    print(f"\n  [{len(v)} paginas no grupo]")
    for n in sorted(v):
        print(f"     {n}  ({docs[n]['nwords']} palavras)")

# tambem mostra distribuicao de "maior similaridade com qualquer outra"
print("\n=== Top 20 paginas mais 'genericas' (maior similaridade media com as demais) ===")
import statistics
avg = []
sample = names  # full
for n in names:
    sims = []
    for m in names:
        if m == n: continue
        sims.append(jaccard(docs[n]['sh'], docs[m]['sh']))
    avg.append((statistics.mean(sims) if sims else 0, n))
for a, n in sorted(avg, reverse=True)[:20]:
    print(f"   sim_media={a:.2f}  {n}")
