# Cluster EEAT — Manual do Motorista

## Objetivo do cluster

Transformar o GuinchoRJ em uma autoridade em assistência veicular, fortalecendo indiretamente todas as páginas comerciais de **Reboque em + localidade** através da autoridade temática e da linkagem interna.

---

## Artigo pilar

| Título | Slug |
|--------|------|
| Manual do Motorista: Problemas Comuns no Carro e Como Resolver | `manual-do-motorista` |

Este será o **hub principal** do cluster.

**Status:** pilar publicado em `/blog/manual-do-motorista/` (07/06/2026).

---

## Categoria no blog

Todo o cluster fica na categoria **`manual-do-motorista`**.

| Elemento | Valor |
|----------|-------|
| Slug da categoria | `manual-do-motorista` |
| Pasta do pilar | `blog/manual-do-motorista/` |
| Hub (pilar) | `/blog/manual-do-motorista/` |
| Artigos satélite | `/blog/{slug-do-artigo}/` (sem categoria na URL) |
| Schema `articleSection` | `Manual do Motorista` |

**Exemplos de URL:**

- Pilar: `/blog/manual-do-motorista/`
- Satélite: `/blog/bateria-descarregada/`
- Satélite: `/blog/carro-nao-liga/`

**Breadcrumb:** Home → Blog → Manual do Motorista → {Título do artigo}

---

## Subcluster 1 — Problemas na partida

| Título | Slug |
|--------|------|
| Carro Não Liga: Principais Causas e O Que Fazer | `carro-nao-liga` |
| Bateria Descarregada: Como Resolver o Problema | `bateria-descarregada` |
| Alternador com Defeito: Principais Sintomas | `alternador-com-defeito` |
| Carro Não Reconhece a Chave: O Que Fazer | `carro-nao-reconhece-chave` |
| Carro Descarregado Depois de Ficar Parado | `carro-descarregado` |

---

## Subcluster 2 — Problemas no motor

| Título | Slug |
|--------|------|
| Motor Ferveu: O Que Fazer e O Que Não Fazer | `motor-ferveu` |
| Carro Falhando em Movimento: O Que Pode Ser | `carro-falhando` |
| Motor Fundido: Principais Sintomas e Causas | `motor-fundido` |
| Correia Dentada Rompeu: Quais São os Riscos? | `correia-dentada-rompida` |
| Fumaça Saindo do Motor: O Que Fazer | `fumaca-saindo-do-motor` |
| Água Entrou no Motor Após Alagamento: O Que Fazer | `agua-no-motor` |

---

## Subcluster 3 — Problemas elétricos

| Título | Slug |
|--------|------|
| Pane Elétrica no Carro: Principais Causas | `pane-eletrica-no-carro` |
| Luz da Injeção Acesa: O Que Significa? | `luz-da-injecao-acesa` |
| Luz do Óleo Acesa: Posso Continuar Dirigindo? | `luz-do-oleo-acesa` |
| Luz da Bateria Acesa no Painel: O Que Fazer | `luz-da-bateria-acesa` |
| EPC Aceso no Painel: O Que Significa | `luz-epc-acesa` |

---

## Subcluster 4 — Câmbio

| Título | Slug |
|--------|------|
| Câmbio Automático Travado: O Que Fazer | `cambio-automatico-travado` |
| Carro Automático Não Engata Marcha | `carro-automatico-nao-engata-marcha` |
| Posso Rebocar um Carro Automático? | `rebocar-carro-automatico` |

---

## Subcluster 5 — Pneus, freios e direção

| Título | Slug |
|--------|------|
| Pneu Furado: Como Resolver com Segurança | `pneu-furado` |
| Freio Duro: Principais Causas | `freio-duro` |
| Volante Pesado: O Que Pode Ser | `volante-pesado` |
| Carro Vibrando em Movimento: O Que Pode Ser | `carro-vibrando` |

---

## Subcluster 6 — Emergências

| Título | Slug |
|--------|------|
| Pane Seca: O Que Fazer Quando Acaba o Combustível | `pane-seca` |
| Carro Morreu no Trânsito: Como Agir com Segurança | `carro-morreu-no-transito` |
| Vazamento de Óleo no Carro: É Perigoso? | `vazamento-de-oleo` |
| Vazamento no Radiador: Como Proceder | `vazamento-no-radiador` |
| Carro Fazendo Barulho Estranho: Quando se Preocupar | `carro-fazendo-barulho` |

---

## Subcluster 7 — Situações comuns no Rio de Janeiro

| Título | Slug |
|--------|------|
| O Que Fazer se o Carro Quebrar na Linha Vermelha | `carro-quebrou-linha-vermelha` |
| O Que Fazer se o Carro Quebrar na Linha Amarela | `carro-quebrou-linha-amarela` |
| O Que Fazer se o Carro Quebrar na Avenida Brasil | `carro-quebrou-avenida-brasil` |
| O Que Fazer se o Carro Quebrar na Ponte Rio-Niterói | `carro-quebrou-ponte-rio-niteroi` |
| O Que Fazer se o Carro Quebrar na Dutra no Rio de Janeiro | `carro-quebrou-dutra` |
| O Que Fazer se o Carro Quebrar na Transolímpica | `carro-quebrou-transolimpica` |

---

## Resumo quantitativo

| Item | Quantidade |
|------|------------|
| Artigo pilar | 1 |
| Subclusters | 7 |
| Artigos satélite | 30 |
| **Total de conteúdos** | **31** |

---

## Estratégia de linkagem interna

### 1. Todos os artigos apontam para o artigo pilar

```
Carro Não Liga        → Manual do Motorista
Motor Ferveu          → Manual do Motorista
Pane Elétrica         → Manual do Motorista
```

### 2. Artigos do mesmo subcluster se interligam

**Subcluster 1 — Partida**

```
Carro Não Liga ↔ Bateria Descarregada ↔ Alternador com Defeito ↔ Carro Descarregado
```

**Subcluster 2 — Motor**

```
Motor Ferveu ↔ Água Entrou no Motor ↔ Motor Fundido ↔ Fumaça Saindo do Motor
```

**Subcluster 3 — Elétricos**

```
Pane Elétrica ↔ Luz da Injeção Acesa ↔ Luz da Bateria Acesa ↔ EPC Aceso
```

### 3. Artigos relacionados de outros subclusters também se conectam

| Origem | Destino |
|--------|---------|
| Carro Não Liga | Pane Elétrica |
| Motor Ferveu | Vazamento no Radiador |
| Carro Vibrando | Freio Duro |
| Câmbio Automático Travado | Posso Rebocar um Carro Automático? |

### 4. Todo artigo deve apontar para páginas comerciais

| Artigo | Páginas comerciais sugeridas |
|--------|------------------------------|
| Carro Não Liga | Reboque em Copacabana, Botafogo, Barra da Tijuca, Jacarepaguá |
| Motor Ferveu | Reboque Zona Sul, Zona Oeste, Niterói |
| Carro Quebrou na Linha Vermelha | Reboque Linha Vermelha |
| Carro Quebrou na Linha Amarela | Reboque Linha Amarela |
| Carro Quebrou na Avenida Brasil | Reboque Avenida Brasil |
| Carro Quebrou na Dutra | Reboque Dutra |
| Carro Quebrou na Ponte Rio-Niterói | Reboque Niterói |

---

## Fluxo de autoridade

```
Manual do Motorista (pilar)
        ↑
Subclusters (30 artigos)
        ↑
Artigos individuais
        ↓
Páginas de serviço
        ↓
Reboque em bairros / cidades / regiões / rodovias
```

---

## Expansão futura

Após os 30 artigos satélite, o cluster pode crescer para mais de 100 conteúdos através de novos subclusters:

- Luzes do painel
- Problemas em carros automáticos
- Problemas em carros elétricos e híbridos
- Problemas após enchentes e alagamentos
- Acidentes e colisões
- Manutenção preventiva
- Cuidados antes de viajar
- Problemas em SUVs e caminhonetes
- Assistência 24 horas
- Seguro e guincho
