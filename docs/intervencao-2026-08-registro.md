# Registro da intervenção — agosto de 2026

Data: 2026-08-08
Commits: `28e1e19..cfa1f5d` (22 commits, todos publicados)
Estado final: working tree limpo, CI verde, 320 páginas com 0 erros e 0 avisos

Documento de referência. A lista é longa e daqui a alguns meses o contexto se perde.

---

## Problema de origem

A home estava otimizada para "reboque no Rio de Janeiro" e perdia a primeira página para `reboque.rio.br`. Decisão tomada: criar página dedicada em `/reboque-rio-de-janeiro/` para assumir o termo e reposicionar a home como página institucional da entidade "Guincho RJ".

---

## O que foi feito

### Reposicionamento

- Home desotimizada: title, meta, og/twitter, H1 e todos os H2/H3 sem o termo
- `/reboque-rio-de-janeiro/` criada como alvo, sem `LocalBusiness` (a entidade permanece na home)
- 18 pontos de apoio operacional fora da capital migrados da home para `/regioes/`, na íntegra
- Cards da home reorganizados: 4 zonas da capital com imagem, 7 regiões externas como cards menores subordinados
- `LocalBusiness`: `name` passa a "Guincho RJ", `areaServed` tipado como `City`

### Arquitetura de links verticais

| Origem | Destino | Quantidade |
|---|---|---:|
| Home | cidade | 1 contextual (âncora exata) + rodapé |
| 4 zonas | cidade | 4 contextuais + 4 sidebar |
| 148 bairros | cidade | 148 contextuais + 148 sidebar |
| 42 localidades externas | `/regioes/` | 42 contextuais |
| 29 posts de blog | cidade | 29 contextuais |
| 320 páginas | cidade | rodapé sitewide |

A página da cidade saiu de **0 para 321 links internos**.

Distribuição de âncoras nos 148 bairros, para não gerar padrão de âncora exata:

```
 22  reboque no Rio de Janeiro    (curada por volume de busca)
 30  reboque no Rio
 30  guincho no Rio de Janeiro
 33  atendimento na capital
 33  reboque na cidade do Rio
```

### Breadcrumb

Reescrito em 319 páginas. Corrigiu três defeitos que existiam em toda a base:

- `aria-current="page"` duplicado em 246 páginas
- self-link `href="./"` no último item em 319 páginas
- nível `/servicos/` que não correspondia à hierarquia real
- `BreadcrumbList` com `item` em caminho relativo (inválido) → URL absoluta

Trilhas:

```
capital   Guincho RJ › Reboque no Rio de Janeiro › [Zona] › [Bairro]
fora      Guincho RJ › Regiões atendidas › [Região] › [Localidade]
blog      Guincho RJ › Blog › [Título]
```

### Redirects

35 redirects 301 cobrindo os 404 do Search Console (legado WordPress: `/author/*`, `/feed/`, paginação morta) e destinos renomeados.

**Bug encontrado só testando em produção:** o wildcard `:path*` da Vercel não casa com URL terminada em barra, e todas as URLs do relatório do Search Console terminam em barra. As 3 regras com wildcard retornavam 404 justamente nos casos reais. Corrigido com variantes de barra final.

Resultado: 16 dos 21 404 do relatório resolvem em 301 → 200, um salto só. Os 5 restantes são 404 por decisão (4 de `node_modules` vazado em deploy antigo e um `/*` fantasma).

### Correções de qualidade

- `hasOfferCatalog` restaurado de 7 para 192 ofertas, com `name` recebendo o serviço real e `url`/`image` absolutas
- 74 afirmações estatísticas sem fonte removidas de 28 páginas (percentuais inventados entre 69% e 88%, com verbo variado)
- `aggregateRating` falso removido de **208 páginas** no total: home, `/quem-somos/`, `/servicos/` e 205 páginas de serviço. Todas declaravam 4.9 com reviewCount 3 e nenhum objeto `Review`
- 7 hubs de região com `<div class="container">` sem fechar
- `reboque-caju-rj` e `reboque-costa-barros`, os dois únicos bairros sem link contextual para a própria zona
- 2 âncoras de bairro que apontavam para a home

### CI

Estava vermelho desde antes desta intervenção — em `28e1e19` já falhava com 30 erros. Como a Vercel publica independente do Actions, ninguém era bloqueado.

- 30 erros de hreflang em 10 posts "Pode…" que herdaram o `<link rel="alternate">` da casca de origem
- `graphify-out/` excluído do validador (artefato de build, gerava 11 erros fantasma)
- `Organization` de `/quem-somos/` sem `mainEntityOfPage`
- `actions/checkout` v4 → v5

Resultado: 320 páginas, 0 erros, 0 avisos, exit 0.

---

## O que a análise descartou

Duas hipóteses caras foram testadas e derrubadas:

**"142 páginas de bairro são template com variável trocada."** Falso. Jaccard mediano de 0,001 entre 4000 pares, nenhum par acima de 0,44, texto entre 664 e 3390 palavras. São páginas de conteúdo real e único. Não há reescrita de meses a fazer.

**"O concorrente ganha por arquitetura."** Falso. Ver `comparativo-estrutural-reboque-rio-br.md`. O guinchorj.com tem 321 URLs contra 129, 190 páginas de bairro contra 112, breadcrumb e `BreadcrumbList` que ele não tem, e tipagem `Service`/`LocalBusiness` onde ele usa `Article` com autor `Person`. Conteúdo empatado (869 contra 815 palavras).

Eliminadas arquitetura e conteúdo, **sobra autoridade externa** como explicação para a diferença de posição.

---

## O que acompanhar

Reprocessamento de 321 páginas leva semanas. Não esperar resultado imediato.

O sinal a observar no Search Console é a consulta **"reboque rio de janeiro"** na aba **Páginas**: o esperado é `/reboque-rio-de-janeiro/` substituir a home. Se em 8 a 10 semanas as duas ainda estiverem alternando, sobrou o termo em algum lugar da home.

Ações manuais recomendadas após o deploy:

- Enviar `/reboque-rio-de-janeiro/` para indexação
- Reenviar `sitemap_index.xml`

---

## Itens abertos

### 1. O gerador — prioridade

É a fonte, não o sintoma. Dez posts nasceram com hreflang da casca de origem e 83 nascem com `<div>` sem fechar. Enquanto ele não for corrigido, cada página nova nasce com os mesmos defeitos e o conserto é eterno.

Evidência de que é falha de processo e não descuido: a página `/reboque-rio-de-janeiro/` foi criada nesta intervenção a partir da casca de `/regioes/` e caiu exatamente na mesma armadilha do hreflang.

### 2. 95 páginas com HTML desbalanceado

83 do blog, 7 de `regioes-atendidas/`, 5 institucionais. Não é o mesmo defeito simples dos hubs: nas do blog há 4 divs abertos contra 3 fechados e três `</article>` para um `<article>` aberto. Exige parser HTML de verdade, não regex — corrigir 90 páginas com substituição cega quebra layout em escala.

Agora é seguro atacar: o CI está verde, então adicionar `html.parser` ao validador mostra exatamente quais quebram, num pipeline que voltou a significar alguma coisa.

### 3. `service-regions.json` mistura via e bairro

6 páginas de via estão classificadas como bairro: Linha Amarela, Linha Vermelha, Avenida Brasil, Aterro do Flamengo, Túnel Rebouças, Túnel Santa Bárbara. Não trava nada hoje, mas atrapalha quando for preciso tratar via diferente de bairro.

Também: `norte-fluminense` e `sul-fluminense` não constam no arquivo, embora existam no site; e `reboque-guadalupe` consta mas não existe em disco.

### 4. Backlinks — fora do repositório

O único dado que falta. Exige navegador e não se resolve no código.

- Ahrefs Backlink Checker com `reboque.rio.br` → número de domínios de referência
- Search Console → Links → Sites com mais links → perfil próprio

Se a diferença for grande, o próximo mês é link building, e o trabalho muda de natureza: parcerias com oficinas e seguradoras, diretórios do setor, Google Business Profile com avaliações reais, imprensa local. Nada disso é on-page.

---

## Documentos relacionados

```
docs/arquitetura-links-verticais.md              spec dos links verticais
docs/levantamento-qualidade-conteudo-bairros.md  duplicação e estatísticas inventadas
docs/comparativo-estrutural-reboque-rio-br.md    comparativo com o concorrente
```
