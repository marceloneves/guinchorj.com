#!/usr/bin/env python3
"""Adiciona a seção "Base Legal e Fontes Oficiais" aos bodies do cluster
Direitos e Obrigações do Motorista, antes do encerramento. Idempotente.

Regras especiais:
- Artigos sobre transporte de crianças: + item CONTRAN.
- Artigos sobre animais/pets: + item Orientações de segurança da PRF.
- Artigos que mencionam o artigo 252 do CTB: parágrafo "Base legal" logo após
  a explicação do artigo (fim da primeira seção que o menciona).
"""

from __future__ import annotations

import re
from pathlib import Path

CONTENT_DIR = Path(__file__).resolve().parent / "content/manual-do-motorista"

# slug -> heading do encerramento (a nova seção é inserida imediatamente antes dele)
ARTICLES = {
    "posso-dirigir-descalco": "<h2>Dirigir Descalço é Permitido e Não Gera Multa</h2>",
    "pode-dirigir-de-chinelo": "<h2>Pode Dirigir de Chinelo?</h2>",
    "pode-dirigir-sem-camisa": "<h2>Dirigir Sem Camisa é Permitido no Brasil?</h2>",
    "pode-fumar-dirigindo": "<h2>Pode Fumar Dirigindo?</h2>",
    "pode-comer-dirigindo": "<h2>Pode Comer Dirigindo?</h2>",
    "pode-usar-fone-de-ouvido-dirigindo": "<h2>Pode Usar Fone de Ouvido Dirigindo?</h2>",
    "pode-usar-celular-no-semaforo": "<h2>Pode Usar Celular no Semáforo?</h2>",
    "pode-dormir-dentro-do-carro-na-rua": "<h2>Pode Dormir Dentro do Carro na Rua?</h2>",
    "pode-transportar-cachorro-solto-no-carro": "<h2>Pode Transportar Cachorro Solto no Carro?</h2>",
    "pode-transportar-crianca-no-banco-da-frente": "<h2>Pode Transportar Criança no Banco da Frente?</h2>",
}

CHILDREN = {"pode-transportar-crianca-no-banco-da-frente"}
ANIMALS = {"pode-transportar-cachorro-solto-no-carro"}

LI_CONTRAN = """<li>
<a href="https://www.gov.br/transportes/pt-br/assuntos/transito/conteudo-Senatran/resolucoes-contran"
target="_blank"
rel="nofollow noopener">
Resoluções do CONTRAN sobre transporte de crianças
</a>
</li>
"""

LI_PRF_ORIENTACOES = """<li>
<a href="https://www.gov.br/prf/pt-br"
target="_blank"
rel="nofollow noopener">
Orientações de segurança da Polícia Rodoviária Federal
</a>
</li>
"""

BASE_LEGAL_INLINE = (
    '<p><strong>Base legal:</strong> artigo correspondente do '
    '<a href="https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm" '
    'target="_blank" rel="nofollow noopener">'
    'Código de Trânsito Brasileiro (Lei nº 9.503/1997)</a>.</p>'
)


def fontes_section(slug: str) -> str:
    extra = ""
    if slug in CHILDREN:
        extra += "\n" + LI_CONTRAN
    if slug in ANIMALS:
        extra += "\n" + LI_PRF_ORIENTACOES
    return f"""<h2>Base Legal e Fontes Oficiais</h2>

<p>As informações apresentadas neste artigo foram elaboradas com base na legislação de trânsito brasileira e em orientações de órgãos oficiais responsáveis pela regulamentação e fiscalização do trânsito no país.</p>

<p>As regras podem sofrer alterações ao longo do tempo. Por esse motivo, recomenda-se consultar sempre as fontes oficiais para obter informações atualizadas.</p>

<ul>
<li>
<a href="https://www.planalto.gov.br/ccivil_03/leis/l9503compilado.htm"
target="_blank"
rel="nofollow noopener">
Código de Trânsito Brasileiro (Lei nº 9.503/1997) – Presidência da República
</a>
</li>

<li>
<a href="https://www.gov.br/transportes/pt-br/assuntos/transito"
target="_blank"
rel="nofollow noopener">
Secretaria Nacional de Trânsito (SENATRAN)
</a>
</li>

<li>
<a href="https://www.gov.br/prf/pt-br"
target="_blank"
rel="nofollow noopener">
Polícia Rodoviária Federal (PRF)
</a>
</li>
{extra}</ul>

"""


def insert_inline_base_legal(html: str) -> tuple[str, bool]:
    """Insere o parágrafo 'Base legal' ao fim da 1ª seção que menciona o art. 252."""
    if "Base legal:</strong>" in html:
        return html, False
    m = re.search(r"artigo 252|art\.?\s*252", html, flags=re.IGNORECASE)
    if not m:
        return html, False
    nxt = html.find("<h2", m.end())
    if nxt == -1:
        return html, False
    insertion = BASE_LEGAL_INLINE + "\n\n"
    return html[:nxt] + insertion + html[nxt:], True


def process(slug: str, anchor: str) -> str:
    path = CONTENT_DIR / f"{slug}-body.html"
    html = path.read_text(encoding="utf-8")
    actions = []

    # 1) parágrafo interno "Base legal" (apenas se menciona art. 252)
    html, did_inline = insert_inline_base_legal(html)
    if did_inline:
        actions.append("inline-252")

    # 2) seção "Base Legal e Fontes Oficiais" antes do encerramento
    if "<h2>Base Legal e Fontes Oficiais</h2>" not in html:
        if anchor not in html:
            raise SystemExit(f"[{slug}] âncora não encontrada: {anchor}")
        html = html.replace(anchor, fontes_section(slug) + anchor, 1)
        actions.append("fontes-section")
    else:
        actions.append("fontes-ja-existe")

    path.write_text(html, encoding="utf-8")
    return ", ".join(actions) if actions else "sem-mudanca"


def main() -> None:
    for slug, anchor in ARTICLES.items():
        result = process(slug, anchor)
        print(f"{slug:45s} -> {result}")


if __name__ == "__main__":
    main()
