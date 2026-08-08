# Levantamento de qualidade de conteúdo — páginas de bairro

Data: 2026-08-08
Escopo: 148 páginas de bairro da capital + 42 localidades fora da capital
Método: read-only, sem alteração de arquivos

Motivação: durante o lote D, apareceu numa página de bairro a frase *"Dados indicam que 87% dos motoristas da zona norte já enfrentaram problemas veiculares."* A hipótese era que esse padrão estivesse replicado em ~142 páginas com o nome da zona trocado — o que significaria estatística inventada em escala, e páginas quase duplicadas.

**As duas hipóteses foram derrubadas.**

---

## 1. Estatísticas sem fonte: 28 ocorrências, não 142

```
28 afirmações estatísticas sem fonte
27 em páginas de bairro   (de 148 → 18%)
 1 fora da capital        (de 42)
16 valores percentuais distintos, de 69% a 88%
```

Não existe "87% replicado". Existe **texto spinado**: a mesma alegação com número, verbo e sujeito variados a cada página, aparentemente para não parecer template.

### Verbos de autoridade usados

| Ocorrências | Construção |
|---:|---|
| 3 | pesquisa indica |
| 3 | levantamento mostra |
| 3 | dados revelam |
| 3 | estatística revela |
| 2 | levantamento revela |
| 2 | dados mostram |
| 2 | pesquisa aponta |
| 2 | pesquisa revela |
| 2 | levantamento aponta |
| 1 | estatística aponta |
| 1 | levantamento indica |
| 1 | estatística indica |
| 1 | dados apontam |
| 1 | estudo aponta |
| 1 | dados indicam |

### Sujeito da alegação

| Ocorrências | Sujeito |
|---:|---|
| 13 | motoristas |
| 12 | condutores |
| 2 | proprietários |
| 1 | residentes |

### Exemplos reais

```
"Levantamento revela que NN% dos motoristas da zona norte já enfrentaram…"
"Dados mostram que NN% dos proprietários de veículos da zona norte já…"
"Pesquisa aponta que NN% dos motoristas da zona oeste já necessitaram…"
"Pesquisa indica que NN% dos motoristas da zona norte já necessitaram…"
"Pesquisa revela que NN% dos condutores da zona oeste já necessitaram…"
"Levantamento mostra que NN% dos motoristas da zona norte já necessitaram…"
```

### Páginas afetadas (28)

```
reboque-cachambi-rj                 reboque-em-andarai-no-rj
reboque-em-bangu-no-rj              reboque-em-bonsucesso-no-rj
reboque-em-guaratiba-no-rj          reboque-em-inhauma-no-rj
reboque-em-iraja-no-rj              reboque-em-laranjeiras-no-rj
reboque-em-madureira-no-rj          reboque-em-olaria-no-rj
reboque-em-paciencia-no-rj          reboque-em-realengo-no-rj
reboque-em-santa-cruz-no-rj         reboque-em-santa-teresa-no-rj
(+ 14 restantes)
```

### Avaliação

O volume é baixo — 18% das páginas de bairro, uma frase cada. É conserto de algumas horas, não de meses.

A natureza, porém, é pior do que descuido: a variação deliberada de número e verbo indica geração automatizada com spinning. Cada número é inventado; não há fonte para nenhum. Isso é passivo de E-E-A-T e de política de conteúdo, independente do volume.

**Recomendação:** remover as 28 frases, ou substituir por afirmação verificável sem número (ex.: "panes elétricas e mecânicas estão entre as ocorrências mais frequentes na região"). Não tentar "consertar" o número — não existe fonte para citar.

---

## 2. As páginas NÃO são quase-duplicadas

Esta era a pergunta de fundo: se duas páginas de bairro diferissem só pelo nome, o problema não seria a estatística, seria o conteúdo inteiro.

### Volume de texto

```
palavras por página (corpo, sem nav/aside/rodapé)
  mínimo    664
  mediana   869
  máximo   3390
```

Nenhuma página fina.

### Similaridade entre páginas

Jaccard sobre shingles de 8 palavras, 4000 pares aleatórios entre as 148:

```
mediana  0,001
média    0,011
p90      0,010
máximo   0,443
```

| Faixa | Pares | % |
|---|---:|---:|
| < 0,1 | 3838 | 95% |
| 0,1 – 0,3 | 155 | 3% |
| 0,3 – 0,5 | 7 | 0% |
| > 0,5 | 0 | 0% |

**Nenhum par passa de 0,44.** Se fossem template com variável trocada, a mediana estaria acima de 0,8. Está em 0,001.

### Os 7 pares acima de 0,3

```
0,443  reboque-anchieta-rj             <-> reboque-ricardo-de-albuquerque-rj
0,360  reboque-em-sao-cristovao-no-rj  <-> reboque-no-maracana-no-rj
0,336  reboque-em-bonsucesso-no-rj     <-> reboque-saude-rj
0,311  reboque-na-ilha-do-governador   <-> reboque-na-taquara-no-rj
0,310  reboque-em-vargem-pequena-no-rj <-> reboque-no-maracana-no-rj
0,305  reboque-no-arpoador-no-rj       <-> reboque-no-flamengo-no-rj
```

São bairros vizinhos com texto parcialmente convergente. 7 pares em 4000 não é problema estrutural — vale uma olhada, não uma reescrita.

---

## Consequência para a fila de trabalho

A hipótese de "142 páginas para reescrever" está descartada. O que sobra é:

1. **Remover as 28 frases estatísticas** — algumas horas
2. Os 7 pares com convergência parcial — opcional

Com o conteúdo fora do caminho crítico e a arquitetura de links interna já resolvida e publicada, a prioridade passa a ser **comparar o perfil de backlinks com `reboque.rio.br`**. Se o conteúdo não é o gargalo e a arquitetura acabou de ser corrigida, a diferença de autoridade é a explicação mais provável para a derrota na primeira página.

---

## Pendência relacionada: hasOfferCatalog

Durante a desotimização da home, o `hasOfferCatalog` do `LocalBusiness` caiu de **193 ofertas para 7**.

A remoção foi intencional: as 193 entradas antigas tinham todas `name: "Guincho e Reboque Rio de Janeiro"` — o termo desotimizado repetido 193 vezes — com o serviço real escondido no campo `description`, que é o campo errado para isso.

O efeito colateral não dimensionado: junto saíram as **193 `url`** apontando para as páginas de serviço, ou seja, a declaração estruturada do catálogo inteiro, no mesmo momento em que o Google reprocessa o site.

**Correção proposta:** reconstruir as 193 entradas com `name` recebendo o serviço real (hoje em `description`), preservando `url` e `image`. Some o termo repetido, voltam as 193 URLs.
