#!/usr/bin/env python3
"""Cria página hub reboque-costa-verde e atualiza configs/cards/rodapé."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
TEMPLATE = ROOT / "servico/reboque-em-angra-dos-reis/index.html"
TARGET_DIR = ROOT / "servico/reboque-costa-verde"
TARGET = TARGET_DIR / "index.html"
REGIONAL_FILE = SCRIPTS / "regional-services.json"
REGIONS_FILE = SCRIPTS / "service-regions.json"

NEW_SLUG = "reboque-costa-verde"
REMOVE_FROM_FOOTER = [
    "reboque-em-angra-dos-reis",
    "reboque-em-paraty",
    "reboque-em-mangaratiba",
    "reboque-em-itaguai",
]

CITY_LINKS = [
    ("reboque-em-angra-dos-reis", "Reboque em Angra dos Reis", "Reboque em Angra dos Reis"),
    ("reboque-em-paraty", "Reboque em Paraty", "Reboque em Paraty"),
    ("reboque-em-mangaratiba", "Reboque em Mangaratiba", "Reboque em Mangaratiba"),
    ("reboque-em-itaguai", "Reboque em Itaguaí", "Reboque em Itaguaí"),
]

WRITTEN_CONTENT = """
<h2 style="text-align:center">Precisa de Reboque na Costa Verde?</h2>
<p style="text-align: center;">
<i class="fa fa-phone" aria-hidden="true"></i>
<a href="tel:21959543043" title="Telefone" style="display: inline-block;" rel="nofollow">(21) 95954-3043</a>
| <i class="fa fa-whatsapp" aria-hidden="true"></i>
<a href="https://api.whatsapp.com/send?phone=5521959543043&amp;text=Ol%C3%A1,%20estou%20entrando%20em%20contato%20pelo%20site" title="Whatsapp" rel="nofollow external noopener" target="_blank" style="display: inline-block;">(21) 95954-3043</a>
</p>
<p>Seu veículo parou na <strong>BR-101 (Rio-Santos)</strong>, no trecho da <strong>Costa Verde</strong> ou em cidades como <strong>Angra dos Reis</strong>, <strong>Paraty</strong>, <strong>Mangaratiba</strong> e <strong>Itaguaí</strong>? A <strong>Guincho RJ</strong> oferece atendimento de <strong>reboque na Costa Verde</strong> com remoção segura, agilidade e orientação clara em trechos litorâneos, serras de acesso e vias de ligação com o Grande Rio.</p>
<p>A Costa Verde é uma das regiões mais importantes do litoral fluminense. Reúne cidades turísticas, portos, marinas, condomínios, hotéis, trechos de mata atlântica, curvas da Rio-Santos, túneis, pontes e acessos para o sul do estado. Por isso, uma pane em locais como o centro de Angra, o histórico de Paraty, Mangaratiba ou Itaguaí exige planejamento, equipamento adequado e conhecimento da região.</p>
<p>A <strong>Guincho RJ atua desde 1995</strong> com guincho, reboque e assistência veicular no Rio de Janeiro e região. Na Costa Verde, o atendimento contempla carros de passeio, motos, SUVs, utilitários, picapes, vans e remoções programadas para oficinas, concessionárias, residências, hotéis, marinas ou outros destinos indicados pelo cliente.</p>
<h2>1. Atendimento de reboque em toda a Costa Verde</h2>
<p>O serviço de <strong>reboque na Costa Verde</strong> é indicado para veículos que não podem continuar circulando com segurança por pane mecânica, pane elétrica, bateria descarregada, superaquecimento, pneu furado, falta de combustível, colisão, veículo travado ou necessidade de transporte programado.</p>
<p>O atendimento pode acontecer na Rio-Santos, em ruas urbanas, condomínios, garagens, estacionamentos, áreas portuárias, trechos de serra e pontos de referência das principais cidades da região. A remoção considera distância, tipo de veículo, local da ocorrência, destino e condições de acesso.</p>
<h2>2. Cidades atendidas na Costa Verde</h2>
<p>Organizamos a cobertura da Costa Verde por município. Confira as páginas específicas de cada cidade:</p>
<ul>
<li><a href="../reboque-em-angra-dos-reis/" title="Reboque em Angra dos Reis">Reboque em Angra dos Reis</a></li>
<li><a href="../reboque-em-paraty/" title="Reboque em Paraty">Reboque em Paraty</a></li>
<li><a href="../reboque-em-mangaratiba/" title="Reboque em Mangaratiba">Reboque em Mangaratiba</a></li>
<li><a href="../reboque-em-itaguai/" title="Reboque em Itaguaí">Reboque em Itaguaí</a></li>
</ul>
<h2>3. Situações mais comuns de atendimento</h2>
<p>O reboque na Costa Verde pode ser acionado em panes na Rio-Santos, falhas em trechos de serra, superaquecimento em viagens longas, pneus furados em vias sem acostamento, colisões leves, veículos que não pegam após parada em hotel ou marina e remoções programadas para oficina ou pátio.</p>
<h2>4. Como solicitar reboque na Costa Verde</h2>
<p>Entre em contato pelo telefone ou WhatsApp <strong>(21) 95954-3043</strong>. Informe localização exata, cidade, ponto de referência, destino do veículo e condição do carro para agilizar o atendimento.</p>
""".strip()


def build_page_html() -> str:
    html = TEMPLATE.read_text(encoding="utf-8")

    html = re.sub(
        r"<div class=\"writen_content\">.*?(?=</div>\s*</div>\s*</div>\s*</div>\s*</section>)",
        f'<div class="writen_content"> {WRITTEN_CONTENT} ',
        html,
        count=1,
        flags=re.DOTALL,
    )

    targeted = [
        (
            "<title>Reboque em Angra dos Reis 24h | Chegamos em 15 min</title>",
            "<title>Reboque na Costa Verde 24h | Chegamos em 15 min</title>",
        ),
        (
            'property="og:title" content="Reboque em Angra dos Reis 24h | Chegamos em 15 min"',
            'property="og:title" content="Reboque na Costa Verde 24h | Chegamos em 15 min"',
        ),
        (
            "<h1>Reboque em Angra dos Reis</h1>",
            "<h1>Reboque na Costa Verde</h1>",
        ),
        (
            '<a title="Reboque em Angra dos Reis" href="./"><span>Reboque em Angra dos Reis</span></a>',
            '<a title="Reboque na Costa Verde" href="./"><span>Reboque na Costa Verde</span></a>',
        ),
        (
            'content="Seu veículo parou na Rio-Santos ou nas proximidades do Porto?',
            'content="Seu veículo parou na BR-101 (Rio-Santos) ou em alguma cidade da Costa Verde?',
        ),
        (
            "Reboque em Angra dos Reis com atendimento rápido, seguro e eficiente",
            "Reboque na Costa Verde com atendimento rápido, seguro e eficiente",
        ),
        (
            'alt="Reboque em Angra dos Reis 24 horas"',
            'alt="Reboque na Costa Verde 24 horas"',
        ),
        (
            'title="Reboque em Angra dos Reis 24 horas"',
            'title="Reboque na Costa Verde 24 horas"',
        ),
    ]
    for old, new in targeted:
        html = html.replace(old, new)

    html = html.replace(
        'title="Reboque na Costa Verde">Reboque na Costa Verde</a></li>\n<li><a href="../reboque-em-paraty/"',
        'title="Reboque em Angra dos Reis">Reboque em Angra dos Reis</a></li>\n<li><a href="../reboque-em-paraty/"',
    )

    schema_cleanup = [
        ("Reboque em Angra dos Reis 24h | Chegamos em 15 min", "Reboque na Costa Verde 24h | Chegamos em 15 min"),
        ("Reboque em Angra dos Reis", "Reboque na Costa Verde"),
        ("reboque em Angra dos Reis", "reboque na Costa Verde"),
        ("nas proximidades do Porto?", "na BR-101 (Rio-Santos) ou em alguma cidade da Costa Verde?"),
        ("Seu veículo parou na Rio-Santos ou nas proximidades do Porto?", "Seu veículo parou na BR-101 (Rio-Santos) ou em alguma cidade da Costa Verde?"),
    ]
    for old, new in schema_cleanup:
        html = html.replace(old, new)

    html = html.replace(
        'href="../reboque-em-angra-dos-reis/" title="Reboque na Costa Verde">Reboque na Costa Verde</a>',
        'href="../reboque-em-angra-dos-reis/" title="Reboque em Angra dos Reis">Reboque em Angra dos Reis</a>',
    )

    return html


def update_regional_services() -> None:
    slugs = json.loads(REGIONAL_FILE.read_text(encoding="utf-8"))
    slugs = [slug for slug in slugs if slug not in REMOVE_FROM_FOOTER]
    if NEW_SLUG not in slugs:
        try:
            idx = slugs.index("reboque-em-itatiaia")
            slugs.insert(idx + 1, NEW_SLUG)
        except ValueError:
            slugs.append(NEW_SLUG)
    REGIONAL_FILE.write_text(json.dumps(slugs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_service_regions() -> None:
    regions = json.loads(REGIONS_FILE.read_text(encoding="utf-8"))
    regions["costa-verde"] = [NEW_SLUG, *REMOVE_FROM_FOOTER]
    REGIONS_FILE.write_text(json.dumps(regions, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run_script(name: str) -> None:
    subprocess.run([sys.executable, str(SCRIPTS / name)], check=True)


def main() -> None:
    if not TEMPLATE.exists():
        raise SystemExit("Template não encontrado.")

    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    TARGET.write_text(build_page_html(), encoding="utf-8")

    update_regional_services()
    update_service_regions()

    run_script("update-service-footer-silos.py")
    run_script("update-home-service-cards.py")
    run_script("update-service-sidebar-silos.py")

    print(f"Página criada: servico/{NEW_SLUG}/")
    print(f"Rodapé/cards: removidos {len(REMOVE_FROM_FOOTER)} links, adicionado {NEW_SLUG}")


if __name__ == "__main__":
    main()
