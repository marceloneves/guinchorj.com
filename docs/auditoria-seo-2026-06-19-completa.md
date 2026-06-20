# 🔍 SEO Audit — guinchorj.com

**Guincho/Reboque RJ · local service (SAB) · ~360 páginas · 19/06/2026**

Auditoria via `/seo audit` (orquestração multi-agente: technical, content, schema, sitemap, performance, visual, geo, local, sxo). Findings consolidados com verificação direta no site live.

## SEO Health Score: **77 / 100** 🟢 Bom

| Categoria | Peso | Score |
|---|---|---|
| Technical | 22% | 85 |
| Content / E-E-A-T | 23% | 62 |
| On-Page | 20% | 75 |
| Schema | 10% | 88 |
| Performance | 10% | 80 |
| AI Search (GEO) | 10% | 85 |
| Images | 5% | 70 |

**Verificado no live (deploy OK):** openingHours `Mo-Su 24h`, asset URLs limpas (0 `﹖`), home 556KB→325KB, sameAs (Instagram + Google), redirects 301 (guadalupe/queimados), ícones FontAwesome renderizam, menu mobile abre, HSTS ativo, robots abre p/ todos + sitemap declarado, **llms.txt presente e estruturado**.

---

## 🔴 Critical

Nenhum bloqueio de indexação.

- Menu mobile e ícones FontAwesome = **OK**, confirmados no live (o "menu não abre" reportado foi falso-positivo de actionability do Playwright `.click()`; teste DOM mostra `#mobile-nav` none→block, `is-open:true`, jQuery ok, 0 erros).

## 🟠 High

### 1. Conteúdo fino/duplicado em 200+ páginas de bairro (`servico/`)
Maior risco SEO. Quality gate: 200+ location pages = zona de HARD STOP. Páginas near-idênticas (template + troca de bairro) arriscam thin content / index bloat / canibalização.
- **1º princípio:** Google premia conteúdo único por intenção local; texto repetido dilui.
- **Fix:** garantir 60%+ único por página (referências locais reais — vias, pontos de referência, tempo de chegada, casos), ou consolidar bairros de baixa busca em hubs.
- **Como saber que falhou:** GSC "Descoberta — não indexada" subindo nessas URLs.

### 2. Banner herói da home praticamente vazio (2.8KB) → renderiza caixa cinza
`Imagem-Banner-scaled.webp` carrega 200 mas tem só 2830 bytes p/ 2560×600 (imagem quase em branco).
- **Fix:** imagem real de marca (guincho / skyline RJ), otimizada WebP. Afeta 1ª impressão / CTR / confiança.

### 3. Logo mobile tap-target 58×17px (regressão da redução `-50%`)
- **Fix:** altura / área de toque ≥48×48px no mobile (envolver com padding, não só `max-width:58px`).

### 4. Telefone truncado em servico mobile
`(21) 95954-` cortado mid-string — `overflow:hidden` / `max-width` sem wrap. Perde contato no mobile em todas as páginas de serviço.

## 🟡 Medium

### 5. Headers de segurança ausentes
Só HSTS presente. Faltam `X-Content-Type-Options: nosniff`, `X-Frame-Options`, CSP. Adicionar em `vercel.json`.

### 6. Floats WhatsApp/telefone sobrepõem CTA "Solicite um Orçamento" no mobile
Sobreposição ~20-25% da área de toque do botão primário. Reposicionar.

### 7. Tap-targets pequenos
Nav / breadcrumb / sidebar links <48px de altura → avisos Mobile Usability no GSC.

### 8. LCP 3.3s
Webfonts de ícone no caminho crítico + CSS inline ainda ~270KB/página. Considerar `preload` do woff2 (FA/boxicons); avaliar trim adicional de CSS. (CLS 0 e TBT 0 já ótimos.)

### 9. E-E-A-T raso
Adicionar autor / responsável técnico, reforçar Quem Somos, provas (anos de operação, frota, depoimentos).

## 🟢 Low

10. Recomprimir imagens de card restantes (~18KB, Lighthouse).
11. FAQPage — manter para citação LLM (rich result FAQ aposentado mai/2026), não expandir para SERP.

---

## Plano priorizado (sequência por dependência)

1. **#1 conteúdo bairros** (semana 1-2) — destrava qualidade de todo o silo.
2. **#2 herói + #3 logo + #4 telefone** (mesmo deploy — UX/conversão mobile, rápido).
3. **#5 headers** (1 bloco em vercel.json) + **#6 floats**.
4. **#8 LCP** após medir novo Lighthouse pós-purge.
5. **#9 E-E-A-T** contínuo.

---

## Contexto: correções já aplicadas nesta sessão (19/06/2026)

- Excluídas páginas duplicadas/erradas (`reboque-guadalupe`, `regioes-atendidas/queimados`) + 301 + sitemap + links repointados.
- Corrigido silo de `reboque-costa-barros` (Zona Oeste → Zona Norte).
- Schema: openingHours domingo 24h, Service.image absoluta (407 ocorrências), sameAs Google na home.
- Logo header reduzido 50% (317 páginas).
- PNG 493KB → WebP 47KB.
- PurgeCSS: CSS inline -43%/-57% por página, preservando @font-face.
- URLs de asset `﹖` (U+FE56) corrigidas → ícones FA + menu mobile voltaram a funcionar.

---

## SXO — Search Experience Optimization (Gap Score 61/100)

Persona primária: **motorista em pane** (mobile, estresse, intenção de emergência). Análise de SERP vs tipo de página entregue.

### CRITICAL SXO

**A. Hierarquia de CTA invertida (todas as páginas)** — hero usa "Solicite um Orçamento" (form) como ação primária. Intenção dominante do mercado = emergência → o telefone deveria dominar.
- **Fix:** hero com `Ligar agora — (21) 95954-3043` (botão grande, cor contrastante) > `WhatsApp` (pré-preenchido por bairro) > form rebaixado a terciário.
- Provavelmente a maior alavanca de conversão do site.

**B. Zero AggregateRating em 203 páginas** — nenhuma estrela no snippet do SERP. Concorrentes mostram "4.7 ★ (214)". Custa CTR em toda query.
- **Fix:** adicionar `AggregateRating` ao bloco LocalBusiness com dados REAIS do Google Business Profile (rating + reviewCount). **Requer número real** — não inventar.

### HIGH SXO
- **"Chegamos em 15 min"** está no title mas não no hero → trazer como badge sob o H1.
- **"Desde 1995"** (31 anos — maior diferencial do mercado) está enterrado → mover pro hero.
- **Sem prova social on-page** — adicionar 3-5 depoimentos por bairro acima do FAQ.
- **Funil blog→conversão quebrado** — adicionar barra CTA sticky nos artigos.

### MEDIUM SXO
- Páginas de bairro longas demais p/ query de emergência — reestruturar above-fold (H1 + badges + 2 botões antes do scroll).
- WhatsApp pré-preenchido genérico ("Olá, estou entrando em contato") → contextual por bairro.
- Tabela de preço simples (compacto/SUV/utilitário) por zona em cada página.
- Profundidade de URL vs concorrente (`/servico/reboque-em-copacabana/` vs `/copacabana/`) — avaliar flatten com 301.

### Schema faltando (SXO + Schema)
`AggregateRating`, `Review`, `ServiceArea` ausentes. AggregateRating é o de maior impacto (estrelas no SERP).

---

## Notas de método

- Score 77/100 reflete base sólida (técnico/schema/GEO fortes) puxada para baixo pelo risco de conteúdo fino no silo programático de bairros.
- Agents seo `technical/content/schema/sitemap/geo/local/sxo` executaram exploração mas não emitiram síntese final; findings consolidados a partir do agent visual (relatório completo) + verificação direta no live + conhecimento da sessão.
