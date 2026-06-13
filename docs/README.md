# Documentação de clusters — GuinchoRJ

Esta pasta reúne a estratégia editorial e de linkagem interna dos clusters de conteúdo do site.

Cada cluster tem um arquivo próprio em `clusters/`, com artigo pilar, subclusters, slugs e regras de interlinking.

## Convenção de categorias no blog

Cada cluster editorial vira uma **categoria** no blog, com pasta e URL próprias (mesmo padrão de `reboque-e-guincho`):

| Elemento | Padrão |
|----------|--------|
| Slug da categoria | `{slug-do-cluster}` |
| Pasta no repositório | `blog/{slug-do-cluster}/` |
| Hub do cluster | `/blog/{slug-do-cluster}/` |
| Artigos satélite | `/blog/{slug-do-artigo}/` (categoria só no filtro, não na URL) |
| `articleSection` (schema) | Nome legível da categoria (ex.: `Manual do Motorista`) |

## Clusters documentados

| Cluster | Categoria | Arquivo | Status |
|---------|-----------|---------|--------|
| EEAT — Manual do Motorista | `manual-do-motorista` | [clusters/manual-do-motorista.md](clusters/manual-do-motorista.md) | Pilar publicado |

## Como usar

1. Novos clusters enviados no chat devem ser documentados em `docs/clusters/{slug-do-cluster}.md`.
2. Atualizar esta tabela ao adicionar um cluster.
3. A implementação técnica (HTML, sitemap, hub) segue a especificação de cada arquivo.
