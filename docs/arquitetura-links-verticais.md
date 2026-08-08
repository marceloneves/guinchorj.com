# Arquitetura de links verticais — guinchorj.com

Especificação operacional dos links verticais da hierarquia bairro → zona → cidade → home.

A interligação lateral entre bairros de uma mesma zona **já existe e não é tocada aqui**.

---

## Levantamento no repositório (antes da especificação)

- **33 links contextuais com âncora exata "reboque no Rio de Janeiro" apontam hoje para a home** (`../../`), espalhados por 43 páginas. O recurso escasso da regra 2 já está gasto — e gasto no alvo errado.
- O sidebar dos bairros **já tem** o link vertical para a zona como primeiro item. O corpo também linka a zona contextualmente ("Zona Sul"). Vertical bairro→zona: já existe.
- Breadcrumb atual é `Home > Serviços > Bairro`. Faltam cidade e zona. E tem bug: os três itens carregam `aria-current="page"`.
- Profundidade já está ok — a home linka as 4 zonas direto nos cards, então bairro fica a 2 cliques.

**Mapeamento real** (`scripts/service-regions.json`):

| Zona/região | Páginas |
|---|---:|
| zona-norte | 83 |
| zona-oeste | 34 |
| zona-sul | 30 |
| centro | 5 |
| **subtotal capital** | **152** |
| baixada-fluminense | 14 |
| regiao-oceanica | 9 |
| litoral-lagos | 8 |
| regiao-serrana | 6 |
| costa-verde | 5 |
| **subtotal fora da capital** | **42** |

### Observações sobre as regras recebidas

- A **regra 6 não existe** na lista enviada (pula de 5 para 7).
- A **regra 5 está truncada** ("e de la a página da cidade"). Interpretada como: bairro precisa de contextual para cima até a zona *e* até a cidade.

---

## 1. Hierarquia com links verticais

```
HOME (entidade "Guincho RJ")
 │  ↓ 1 contextual, âncora exata                         [existe]
 │  ↓ 1 navegacional, rodapé "Reboque na capital" (320)  [existe]
 │  ↓ 4 navegacionais, cards de zona                     [existe]
 │
 └─ /reboque-rio-de-janeiro/   ......................... CIDADE
     │  ↑ contextual p/ home: NÃO — evita reciprocidade (regra 7)
     │  ↓ 4 contextuais p/ zonas                         [existe]
     │  ↓ 1 contextual p/ /regioes/                      [existe]
     │
     ├─ ZONAS DA CAPITAL — 4 páginas
     │   │  ↑ 1 contextual p/ cidade                     [FALTA]
     │   │  ↑ 1 navegacional sidebar p/ cidade           [FALTA]
     │   │  ↓ N contextuais p/ bairros                   [existe]
     │   │
     │   └─ BAIRROS — 152 páginas
     │       ↑ contextual p/ zona                        [existe]
     │       ↑ contextual p/ cidade                      [FALTA — hoje vai p/ home]
     │       ↑ navegacional sidebar p/ zona              [existe]
     │       ↔ laterais entre irmãos       ............. NÃO TOCAR
     │
     └─ /regioes/   ................................... ESTADO
         │  ↑ 1 contextual p/ cidade                     [FALTA]
         │  ↓ 7 navegacionais p/ regiões externas        [existe]
         │
         └─ REGIÕES FORA DA CAPITAL — 42 páginas
             ↑ contextual p/ /regioes/                   [FALTA]
             ↑ NÃO linkar para a cidade
```

O ponto crítico do desenho: **regiões fora da capital não sobem para `/reboque-rio-de-janeiro/`**. Duque de Caxias não é Rio de Janeiro. Misturar isso polui o sinal geográfico da página da cidade.

---

## 2. Tabela de links verticais

| Origem | Destino | Tipo | Âncora | Posição | Status |
|---|---|---|---|---|---|
| Home | Cidade | contextual | `reboque no Rio de Janeiro` | fim da lista de serviços | existe |
| Home | Cidade | navegacional | `Reboque na capital` | rodapé, 1º da coluna Serviços | existe |
| Home | 4 zonas | navegacional | `Zona Oeste`, `Zona Norte`… | cards | existe |
| Cidade | 4 zonas | contextual | nome da zona | seção "Cobertura por região" | existe |
| Cidade | /regioes/ | contextual | `regiões atendidas` | fim da cobertura | existe |
| **Zona** | **Cidade** | contextual | variada (item 6) | 1º parágrafo do corpo | **FALTA** |
| **Zona** | **Cidade** | navegacional | `Reboque na capital` | topo do sidebar | **FALTA** |
| Zona | bairros | contextual | nome do bairro | corpo | existe |
| **Bairro** | **Cidade** | contextual | variada (item 6) | repointar os 33 que vão p/ home | **FALTA** |
| Bairro | Zona | contextual | nome da zona | corpo | existe |
| Bairro | Zona | navegacional | nome completo da zona | sidebar, 1º item | existe |
| **/regioes/** | **Cidade** | contextual | `atendimento na capital` | intro | **FALTA** |
| **Região externa** | **/regioes/** | contextual | `regiões atendidas` | corpo | **FALTA** |
| Todas (320) | Cidade | navegacional | `Reboque na capital` | rodapé | existe |

Trabalho real: 4 zonas + 152 bairros + `/regioes/` + 42 regiões externas.

---

## 3. Sidebar — só os elementos verticais

**Não tocar** no bloco de irmãos laterais. A inserção é acima dele.

### Bairro — primeiro item, antes do link da zona que já existe

```html
<div class="sidebar-hierarquia">
  <a href="../../reboque-rio-de-janeiro/" title="Reboque na capital">Reboque na capital</a>
</div>
<!-- abaixo, inalterado: link da zona + irmãos laterais -->
```

### Zona — mesma inserção, sem o link da zona (é a própria página)

```html
<div class="sidebar-hierarquia">
  <a href="../../reboque-rio-de-janeiro/" title="Reboque na capital">Reboque na capital</a>
</div>
```

Um link só por sidebar, âncora fixa. Sidebar é navegacional: não é lugar de variar âncora nem de gastar exata.

---

## 4. Rodapé sitewide — coluna Serviços

Já aplicado em 320 páginas. Ordem atual, que é a recomendada:

```
Serviços
  1. Reboque na capital     → /reboque-rio-de-janeiro/    ← cidade
  2. Zona Oeste
  3. Zona Norte
  4. Zona Sul
  5. Centro                                               ← 4 zonas da capital
  6. Baixada Fluminense
  7. Região Oceânica
  8. Região Serrana
  9. Costa Verde
 10. Litoral e Região dos Lagos
 11. Sul Fluminense
 12. Norte Fluminense                                     ← fora da capital
```

A ordem espelha a hierarquia: cidade → zonas → estado. Âncora fixa nas 320 páginas, nenhuma variação — variar âncora em link replicado é o que gera padrão detectável.

Não adicionar `/regioes/` aqui: os 7 destinos externos já estão listados individualmente, e o guarda-chuva seria redundante.

---

## 5. Breadcrumb

### Formato

Bairro da capital, 4 níveis:

```
Guincho RJ  ›  Reboque no Rio de Janeiro  ›  Zona Sul  ›  Copacabana
```

Região fora da capital — a cidade **não entra**:

```
Guincho RJ  ›  Regiões atendidas  ›  Baixada Fluminense  ›  Duque de Caxias
```

### Dois defeitos do breadcrumb atual a corrigir junto

1. É `Home > Serviços > Bairro` — o nível `/servicos/` não corresponde à hierarquia real e some no desenho novo.
2. Os três `<li>` têm `class="breadcrumb-item active" aria-current="page"`. Só o último pode ter. Hoje o HTML declara três páginas atuais simultâneas.

### Markup correto

```html
<nav aria-label="Trilha de navegação">
  <ol class="breadcrumb">
    <li class="breadcrumb-item"><a href="../../"><span>Guincho RJ</span></a></li>
    <li class="breadcrumb-item"><a href="../../reboque-rio-de-janeiro/"><span>Reboque no Rio de Janeiro</span></a></li>
    <li class="breadcrumb-item"><a href="../reboque-na-zona-sul-no-rj/"><span>Zona Sul</span></a></li>
    <li class="breadcrumb-item active" aria-current="page"><span>Copacabana</span></li>
  </ol>
</nav>
```

O último item sem `<a>` — é a página atual.

### Schema BreadcrumbList

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Guincho RJ",
      "item": "https://guinchorj.com/" },
    { "@type": "ListItem", "position": 2, "name": "Reboque no Rio de Janeiro",
      "item": "https://guinchorj.com/reboque-rio-de-janeiro/" },
    { "@type": "ListItem", "position": 3, "name": "Zona Sul",
      "item": "https://guinchorj.com/servico/reboque-na-zona-sul-no-rj/" },
    { "@type": "ListItem", "position": 4, "name": "Copacabana" }
  ]
}
```

O último `ListItem` sem `item` — é a própria página. E o `name` do breadcrumb é rótulo curto ("Copacabana"), não o H1 inteiro ("Reboque em Copacabana no RJ 24 horas").

Sobre a regra 8: o breadcrumb tem 4 níveis, mas isso é rótulo de hierarquia, não profundidade de clique. Como a home linka as 4 zonas direto nos cards, todo bairro fica a **2 cliques**.

---

## 6. Distribuição das âncoras

O denominador honesto é o total de links internos que a página da cidade recebe:

```
320  navegacionais  (rodapé, âncora fixa "Reboque na capital")
152  contextuais    (bairros da capital)
  4  contextuais    (zonas)
  1  contextual     (home)
  1  contextual     (/regioes/)
───
478  links internos totais
```

Distribuição dos **158 contextuais**:

| Âncora | Qtd | % dos contextuais | % dos 478 |
|---|---:|---:|---:|
| `reboque no Rio de Janeiro` (exata) | 24 | 15% | **5,0%** |
| `reboque no Rio` | 32 | 20% | 6,7% |
| `guincho no Rio de Janeiro` | 32 | 20% | 6,7% |
| `atendimento na capital` | 35 | 22% | 7,3% |
| `reboque na cidade do Rio` | 35 | 22% | 7,3% |

A exata em 5% do total é a faixa segura. Se ela fosse para os 152 bairros, seriam 32% — perfil de link building manipulado.

Duas regras de aplicação que importam mais que os números:

- **Não distribuir em bloco.** Se os 24 exatos caírem todos na Zona Sul e os 35 de "atendimento na capital" todos na Zona Norte, o padrão fica geográfico e óbvio. Distribuir por hash do slug, não por ordem alfabética nem por zona.
- **Reservar a exata para os bairros de maior volume.** Copacabana, Barra, Tijuca, Campo Grande, Centro. São as páginas com mais autoridade própria — o link exato delas vale mais que o de um bairro de cauda longa.

Os 4 links das zonas: uma variação diferente em cada, nenhuma exata. A exata da home já cobre o nível mais alto.

---

## 7. Erros a evitar

### Deixar os 33 links exatos apontando para a home

É o erro que já está em produção. A home foi desotimizada no HTML, mas 33 páginas de bairro continuam dizendo ao Google que a home é sobre reboque no Rio de Janeiro. Enquanto isso não for repointado, a desotimização está pela metade e as duas páginas competem pelo mesmo termo — com a home vencendo, porque tem mais links.

### Fazer bairro linkar direto para a cidade pulando a zona

Se o bairro só sobe para a cidade, a página de zona perde a função e vira nó de passagem sem sinal. O bairro precisa dos dois: zona (relevância temática próxima) e cidade (hierarquia).

### Reciprocidade total cidade ↔ bairro

Se `/reboque-rio-de-janeiro/` linkar de volta para os 152 bairros, ela dilui em 152 saídas o PageRank que recebe de 478 entradas. A cidade linka as 4 zonas; as zonas distribuem para os bairros. Fluxo em cascata, não em teia.

### Região fora da capital subindo para a cidade

Duque de Caxias linkar para `/reboque-rio-de-janeiro/` diz ao Google que Caxias é Rio — contradiz o `areaServed` do schema, que as trata como cidades distintas. Elas sobem para `/regioes/`.

### Variar âncora no rodapé

Link replicado em 320 páginas com âncora rotativa é o oposto de natural: navegação de verdade tem rótulo fixo. Variação é para contextual.

### Manter três `aria-current="page"` no breadcrumb

Além de quebrar acessibilidade — leitor de tela anuncia três páginas atuais —, sinaliza markup gerado sem revisão, e o breadcrumb é justamente o elemento que o Google usa para inferir hierarquia.

### Colocar o link vertical do sidebar dentro do bloco lateral

O bloco de irmãos tem 32 links; enfiar o link da cidade ali faz ele ser lido como mais um irmão, não como pai. Por isso a especificação do item 3 põe num container próprio, acima.

---

## Prioridade de execução

Nada disto foi aplicado — é especificação.

O item de maior urgência é o **repointamento dos 33 links exatos**, que é onde a arquitetura atual contradiz a desotimização já aplicada na home.
