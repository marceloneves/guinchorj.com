# guinchorj.com

Site estático (HTML) de guincho/reboque no Rio de Janeiro. SEO programático: páginas por bairro/cidade (`servico/`), hubs de região (`regioes-atendidas/`, `servico/reboque-*-fluminense`, zonas) e cluster editorial (`blog/`).

## Instruções de trabalho

- **Sempre use Graphify para compreender a estrutura do projeto.** Antes de mapear relações entre páginas, silos cidade↔região ou o cluster editorial, consulte o grafo: `graphify query "<pergunta>"` (o grafo vive em `graphify-out/graph.json`). Reconstrua com `/graphify .` quando o conteúdo mudar muito.
- **Trabalhe em modo Caveman para minimizar consumo de tokens.** Respostas terse, sem artigos/filler/pleasantries. Substância técnica intacta. Código, commits e avisos de segurança em texto normal.

## Servir local

Site estático, sem build. Servir com:

```
python3 -m http.server 8000
```

Abrir http://localhost:8000
