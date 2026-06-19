# Auditoria SEO — guinchorj.com

**Data:** 19/06/2026
**Escopo:** 319 páginas de conteúdo (HTML estático exportado do WordPress / Rank Math)
**Tipo de negócio:** Serviço local (guincho/reboque 24h) — Service-Area Business, Rio de Janeiro e Região Metropolitana, desde 1995
**Método:** Análise dos arquivos-fonte locais (não crawl ao vivo). Core Web Vitals de campo não foram medidos (requer dados ao vivo do CrUX/PageSpeed).

---

## SEO Health Score: **84 / 100** (B+)

| Categoria | Peso | Nota | Observação |
|-----------|------|------|------------|
| SEO Técnico | 22% | 88 | Canônicas 100%, sem noindex, títulos únicos. 1 título duplicado. |
| Qualidade de Conteúdo | 23% | 82 | Conteúdo genuinamente único (~69%), bom E-E-A-T. Faltam provas sociais. |
| On-Page | 20% | 88 | Títulos/descrições/H1 sólidos. 1 par canibalizando. |
| Schema / Dados estruturados | 10% | 72 | Grafo completo, mas 3 defeitos sistêmicos (ver abaixo). |
| Performance (CWV) | 10% | 78* | WebP + lazy load. HTML pesado e 1 PNG de 505 KB. *não medido em campo |
| Prontidão para IA (GEO) | 10% | 88 | llms.txt, robots liberado, FAQPage, entidade forte. |
| Imagens | 5% | 80 | Maioria WebP. 1 PNG grande; alt text a revisar. |

---

## Veredito principal: a estratégia de 204 páginas é DEFENSÁVEL

O maior risco aparente do site — **204 páginas de serviço por bairro/região** (`/servico/<bairro>/`) — está **muito acima do hard-stop de 50+ páginas de localização** da maioria das diretrizes anti-doorway. Porém, a análise de duplicação mostra que **não são páginas-porta (doorway pages)**:

- **~1.250–1.360 palavras** por página (bem acima do limite de conteúdo raso).
- Após normalizar o nome do bairro, duas páginas compartilham apenas **~31% de similaridade de caracteres / 16% de sobreposição de frases** → **≈69% de conteúdo único**, acima do gate de 60%.
- Títulos: **203/204 únicos**. Descrições: **203/204 únicas**, 0 ausentes. 1 H1 por página.

**Conclusão:** manter a estratégia. O conteúdo é diferenciado o suficiente para se sustentar. O foco deve ser corrigir os defeitos sistêmicos abaixo (que se multiplicam por 200+ páginas), não podar páginas.

---

## 🔴 Crítico / Alto — corrigir primeiro

### 1. `openingHours` exclui domingo (contradiz o "24 horas")
**205 páginas** declaram no schema:
```
"openingHours":"Mo-Fr 00:00-24:00, Sa 00:00-24:00"
```
Isso é **segunda a sábado** — o **domingo está de fora**, contradizendo a promessa de marketing "guincho 24 horas". Para um serviço 24/7, o Google pode exibir o negócio como fechado aos domingos.
**Correção:** trocar por `"openingHours":"Mo-Su 00:00-24:00"` em todas as 205 ocorrências.
**Como saber se falhou:** Rich Results Test mostrando horário de funcionamento; verificar que domingo aparece como aberto.

### 2. Páginas duplicadas de Guadalupe (canibalização)
Dois diretórios para o mesmo bairro, com **título idêntico** (`Reboque em Guadalupe no RJ 24h`):
- `servico/reboque-guadalupe/`
- `servico/reboque-guadalupe-rj/`

**Correção:** escolher a URL canônica (preferir o padrão dominante `-rj`), aplicar **301** da outra para ela, remover a perdedora do sitemap e atualizar links internos. Esse é o único título duplicado de 204.

### 3. Schema sem provas sociais — `aggregateRating` ausente em 100% das páginas
**0 páginas** têm `aggregateRating`/`Review`. Estrelas no SERP elevam muito o CTR em buscas locais.
**Correção:** se houver avaliações reais (Google Business Profile), adicionar `aggregateRating` (com `ratingValue` e `reviewCount` reais) ao schema `LocalBusiness`/`Service`. **Nunca inventar avaliações** — usar apenas dados verificáveis.
**Como saber se falhou:** estrelas não aparecem no Rich Results Test ou são rejeitadas por falta de reviews on-page correspondentes.

---

## 🟡 Médio

### 4. `Service.image` usa URL relativa no JSON-LD (212 páginas)
```
"image":"../../wp-content/uploads/2025/10/Guincho_1-670x441.webp"
```
O Schema.org exige **URLs absolutas**. 0 imagens de schema de serviço usam `https://`. O Google pode não resolver caminhos relativos em JSON-LD (a correção recente reparou os caminhos quebrados, mas os deixou relativos).
**Correção:** prefixar com `https://guinchorj.com/` em todas as 212 ocorrências.

### 5. Performance — HTML pesado e 1 PNG grande
- **HTML da home: 556 KB** — o CSS é inlined e repetido em cada página (bom para render-blocking, ruim para peso/transferência).
- Maior asset do site: **`reboque-rj-670x441.png` (505 KB)** em PNG — deveria ser WebP (o resto do site já é WebP: 1305 WebP vs 59 JPG vs 1 PNG).
**Correção:** converter o PNG para WebP; avaliar extrair o CSS crítico para um arquivo cacheável compartilhado em vez de inline por página.
**Nota:** CWV de campo (LCP/INP/CLS) não foram medidos — rodar PageSpeed Insights / CrUX nas páginas-pilar para confirmar.

### 6. `sameAs` fraco para a entidade
Home tem apenas `sameAs: [instagram.com/guinchorj]`. Entidade mais forte (melhor para IA e Knowledge Graph) com mais perfis verificáveis.
**Correção:** adicionar Google Business Profile, Facebook e demais perfis reais ao array `sameAs` do `Organization`/`LocalBusiness`.

---

## 🟢 Pontos fortes (manter)

- **Indexabilidade impecável:** 319/319 páginas com `canonical` self-referente; **zero** vazamentos de `noindex`.
- **On-page consistente:** títulos e descrições únicos e presentes; 1 H1 por página.
- **Conteúdo defensável:** ~69% único e 1.250+ palavras nas páginas de bairro.
- **NAP consistente:** telefone `(21) 95954-3043` idêntico em todas as páginas (2.654 ocorrências).
- **Conversão local forte:** link `tel:` **e** WhatsApp em **todas as 319 páginas** — ideal para intenção de urgência.
- **Grafo de schema rico:** Service (596), Offer (596), BreadcrumbList (319), FAQPage (148), BlogPosting (203), PostalAddress/GeoCoordinates/ContactPoint, Organization, WebSite. **Sem HowTo** (corretamente — deprecado).
- **Sitemaps limpos:** 204 URLs de serviço = 204 arquivos em disco. **Zero 404s, zero órfãos.**
- **Imagens:** maioria WebP, `loading="lazy"` aplicado (15/18 na home).
- **GEO/IA:** `llms.txt` presente, completo e fiel às URLs; `robots.txt` libera todos os crawlers (incl. GPTBot/ClaudeBot/PerplexityBot); conteúdo citável.

### Nota sobre FAQPage (148 páginas) — informativo, **não** remover
O Google aposentou os rich results de FAQ para todos os sites em **7/maio/2026**. O FAQPage **não gera mais destaque no SERP**, mas **mantém valor para citação por IA** (AI Overviews, ChatGPT, Perplexity). **Recomendação: manter.** Não criar novos FAQPage visando SERP do Google; para Q&A genuíno de usuário, preferir `QAPage`.

---

## Plano de ação priorizado (com sequência de dependências)

| # | Ação | Severidade | Esforço | Páginas |
|---|------|-----------|---------|---------|
| 1 | `openingHours` → `Mo-Su 00:00-24:00` | Alto | Baixo (find/replace) | 205 |
| 2 | 301 de uma das páginas Guadalupe + remover do sitemap | Alto | Baixo | 2 |
| 3 | `Service.image` → URL absoluta `https://` | Médio | Baixo (find/replace) | 212 |
| 4 | Adicionar `aggregateRating` real (depende de ter reviews do GBP) | Alto | Médio | todas |
| 5 | Converter `reboque-rj-*.png` → WebP | Médio | Baixo | 1 asset |
| 6 | Enriquecer `sameAs` (GBP, Facebook…) | Médio | Baixo | home/template |
| 7 | Medir CWV de campo (PageSpeed/CrUX) nas páginas-pilar | Médio | Baixo | amostra |

**Sequência:** 1, 2, 3, 5, 6 são correções mecânicas independentes — podem ir juntas em um único commit/deploy. 4 depende de existir base de avaliações verificáveis. 7 é diagnóstico e desbloqueia decisões de performance.

**Indicadores para monitorar (sem re-auditar):**
- GSC → cobertura: confirmar que a página Guadalupe redirecionada sai do índice e a canônica permanece.
- GSC → aprimoramentos / Resultados avançados: horário de funcionamento e (se aplicável) avaliações sem erros.
- GBP Insights → ligações e cliques no WhatsApp (proxy de conversão local).

---

*Auditoria gerada via `/seo audit` (orquestração multi-agente claude-seo) + verificação direta dos arquivos-fonte.*
