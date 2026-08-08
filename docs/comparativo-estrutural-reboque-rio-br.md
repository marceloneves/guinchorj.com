# Comparativo estrutural — guinchorj.com × reboque.rio.br

Data: 2026-08-08
Método: inspeção pública (robots.txt, sitemap, HTML de home e de uma página de bairro). Read-only, sem ferramenta paga e sem sessão autenticada.

Motivação: a home do guinchorj.com perdia a primeira página para `reboque.rio.br` no termo "reboque no Rio de Janeiro". A pergunta é se ele ganha por arquitetura — caso em que o trabalho recém-concluído fecha a diferença — ou por autoridade externa, caso em que o próximo trabalho é link building.

---

## Quadro comparativo

| | guinchorj.com | reboque.rio.br |
|---|---:|---:|
| URLs no sitemap | **321** | 129 |
| Páginas de bairro/localidade | **190** | 112 |
| Profundidade até uma página de bairro | 2 cliques | **1 clique** |
| Breadcrumb visual | **sim (319 páginas)** | não |
| `BreadcrumbList` no schema | **sim** | não |
| Palavras numa página de bairro | **869 (mediana de 148)** | 815 (Tijuca) |
| Similaridade entre páginas de bairro | **Jaccard 0,001** | não medido |
| Tipagem de schema da página de bairro | `Service` em `LocalBusiness` | `Article` com autor `Person` |
| `aggregateRating` sem objeto `Review` | **205 páginas** ⚠️ | não usa |
| Links internos numa página de bairro | ~150 | 118 |
| CMS | estático | WordPress |

---

## Detalhamento do concorrente

### Sitemap

```
wp-sitemap.xml (índice)
  wp-sitemap-posts-post-1.xml         14 URLs
  wp-sitemap-posts-page-1.xml        112 URLs   <- as páginas de bairro
  wp-sitemap-taxonomies-category-1.xml 2 URLs
  wp-sitemap-users-1.xml               1 URL
  ----
                                     129 total
```

`robots.txt` padrão de WordPress, sem bloqueios relevantes.

### Arquitetura de links

```
home  ->  111 dos 112 bairros, diretamente
```

Arquitetura **plana**: não há nível intermediário de zona ou região. A home linka quase todos os bairros, e uma página de bairro linka outras 117.

99% dos bairros dele estão a 1 clique da home. Todos os 148 bairros da capital no guinchorj.com estão a 2 cliques.

### Página de bairro (`/tijuca-rj/`)

```
HTML bruto            63.444 bytes
palavras visíveis        815
h1                     "Reboque Tijuca RJ 24h"
h2 / h3                  6 / 4
breadcrumb               não
BreadcrumbList           não
JSON-LD                  1 bloco
@type       Article, ImageObject, Organization, Person, WebPage
aggregateRating          não
links internos           118
```

### Home

```
HTML bruto            96.517 bytes
palavras visíveis      1.590
h1        "Serviço de Reboque e Guincho no Rio de Ja…"
@type      Article, ImageObject, Organization, Person,
           SearchAction, WebPage, WebSite
links internos           131
```

---

## Leitura

### Onde o guinchorj.com ganha

**Escala.** 190 páginas de bairro e localidade contra 112. São 78 localidades que o concorrente não cobre.

**Hierarquia declarada.** Ele não tem breadcrumb, nem visual nem estruturado. Não há nível de zona. O Google não recebe nenhum sinal de agrupamento regional vindo dele. Essa é exatamente a estrutura que os lotes A–H construíram no guinchorj.com.

**Tipagem semântica.** Ele marca página de bairro como `Article` com autor `Person` — trata serviço local como post de blog. O guinchorj.com marca `Service` dentro de `LocalBusiness`, com `areaServed` tipado como `City`. É a modelagem correta para o negócio.

**Conteúdo não duplicado.** Medido no guinchorj.com: Jaccard mediano de 0,001 entre 4000 pares de páginas de bairro. Não foi medido no concorrente — exigiria baixar as 112 páginas.

### Onde o concorrente ganha

**Profundidade: 1 clique contra 2.** A home dele distribui PageRank direto para 111 bairros.

Isso é escolha, não erro. Ele troca hierarquia por distribuição direta. O guinchorj.com fez a troca inversa: cascata cidade → zona → bairro, que só compensa se as páginas de zona tiverem força própria.

A vantagem dele é compensável — o rodapé sitewide do guinchorj.com já dá link de todas as páginas para a cidade e para as 4 zonas.

### Conteúdo

Empate. 869 contra 815 palavras na página de bairro. Não é nesse eixo que a disputa se decide.

---

## Conclusão

**A hipótese "ele ganha por arquitetura" não se sustenta.** O guinchorj.com está melhor em escala, hierarquia, breadcrumb, tipagem de schema e volume de páginas. A única vantagem estrutural do concorrente — profundidade de 1 clique — é compensada pelo rodapé sitewide.

Com conteúdo empatado e arquitetura favorável, **sobra autoridade externa como explicação**.

---

## Ressalvas de método

**Sitemap não é índice.** As 129 URLs dele e as 321 do guinchorj.com são o que cada site *declara*, não o que o Google indexou. Para a aproximação real, `site:reboque.rio.br` no Google.

**Nada disto mede backlinks.** Inspeção pública de HTML não revela perfil de links externos. Essa é a peça que falta e exige Ahrefs Backlink Checker ou equivalente — dois minutos, mas precisa de alguém com navegador.

---

## Achado colateral

Durante a comparação: **205 páginas de serviço do guinchorj.com declaram `aggregateRating` de 4.9 com reviewCount 3, valor idêntico em todas, e nenhuma delas traz um único objeto `Review`.**

```
205  servico/*      aggregateRating em nó Service
  1  servicos/
205x "4.9 / 3"      valor idêntico
  0  páginas com objetos Review
```

Declarar nota agregada sem as avaliações correspondentes viola a política de dados estruturados do Google. A replicação idêntica em 205 páginas é o padrão que dispara revisão manual.

O concorrente **não usa `aggregateRating` em nenhuma página** — não corre esse risco.

O mesmo bloco já foi removido da home e de `/quem-somos/`. Restam as 205.
