#!/usr/bin/env python3
"""Cria página hub reboque-litoral-lagos e atualiza configs/cards/rodapé."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
TEMPLATE = ROOT / "servico/reboque-regiao-serrana/index.html"
TARGET_DIR = ROOT / "servico/reboque-litoral-lagos"
TARGET = TARGET_DIR / "index.html"
REGIONAL_FILE = SCRIPTS / "regional-services.json"
REGIONS_FILE = SCRIPTS / "service-regions.json"

NEW_SLUG = "reboque-litoral-lagos"
REMOVE_FROM_FOOTER = [
    "reboque-em-araruama",
    "reboque-em-cabo-frio",
    "reboque-em-arraial-do-cabo",
    "reboque-em-armacao-dos-buzios",
    "reboque-em-saquarema",
    "reboque-em-sao-pedro-da-aldeia",
    "reboque-em-iguaba-grande",
]

CITY_LINKS = [
    ("reboque-em-cabo-frio", "Reboque em Cabo Frio"),
    ("reboque-em-araruama", "Reboque em Araruama"),
    ("reboque-em-saquarema", "Reboque em Saquarema"),
    ("reboque-em-armacao-dos-buzios", "Reboque em Armação dos Búzios"),
    ("reboque-em-arraial-do-cabo", "Reboque em Arraial do Cabo"),
    ("reboque-em-sao-pedro-da-aldeia", "Reboque em São Pedro da Aldeia"),
    ("reboque-em-iguaba-grande", "Reboque em Iguaba Grande"),
]

CITY_LIST_HTML = "\n".join(
    f'<li><a href="../{slug}/" title="{title}">{title}</a></li>'
    for slug, title in CITY_LINKS
)

WRITTEN_CONTENT = f"""
<h2 style="text-align:center">Precisa de Reboque no Litoral Lagos?</h2>
<p style="text-align: center;">
<i class="fa fa-phone" aria-hidden="true"></i>
<a href="tel:21959543043" title="Telefone" style="display: inline-block;" rel="nofollow">(21) 95954-3043</a>
| <i class="fa fa-whatsapp" aria-hidden="true"></i>
<a href="https://api.whatsapp.com/send?phone=5521959543043&amp;text=Ol%C3%A1,%20estou%20entrando%20em%20contato%20pelo%20site" title="Whatsapp" rel="nofollow external noopener" target="_blank" style="display: inline-block;">(21) 95954-3043</a>
</p>
<p>Seu veículo parou na <strong>BR-101</strong>, na <strong>RJ-106</strong>, na <strong>RJ-124</strong> ou em algum município do <strong>Litoral Lagos</strong>? A <strong>Guincho RJ</strong> oferece atendimento de <strong>reboque no Litoral Lagos</strong> com remoção segura, agilidade e orientação clara em trechos litorâneos, avenidas urbanas e acessos à Região dos Lagos.</p>
<p>O Litoral Lagos reúne cidades turísticas, praias, condomínios, marinas, centros comerciais, rodovias de ligação e alta circulação sazonal. Por isso, uma pane em locais como <strong>Cabo Frio</strong>, <strong>Araruama</strong>, <strong>Búzios</strong>, <strong>Arraial do Cabo</strong> ou <strong>Saquarema</strong> exige planejamento, equipamento adequado e conhecimento da região.</p>
<p>A <strong>Guincho RJ atua desde 1995</strong> com guincho, reboque e assistência veicular no Rio de Janeiro e região. No Litoral Lagos, o atendimento contempla carros de passeio, motos, SUVs, utilitários, picapes, vans e remoções programadas para oficinas, concessionárias, residências, hotéis ou outros destinos indicados pelo cliente.</p>
<h2>1. Atendimento de reboque em todo o Litoral Lagos</h2>
<p>O serviço de <strong>reboque no Litoral Lagos</strong> é indicado para veículos que não podem continuar circulando com segurança por pane mecânica, pane elétrica, bateria descarregada, superaquecimento, pneu furado, falta de combustível, colisão, veículo travado ou necessidade de transporte programado.</p>
<p>O atendimento pode acontecer na BR-101, em avenidas principais, ruas urbanas, condomínios, garagens, estacionamentos, trechos litorâneos e pontos de referência dos principais municípios. A remoção considera distância, tipo de veículo, local da ocorrência, destino e condições de acesso.</p>
<h2>2. Cidades atendidas no Litoral Lagos</h2>
<p>Organizamos a cobertura do Litoral Lagos por município. Confira as páginas específicas de cada cidade:</p>
<ul>
{CITY_LIST_HTML}
</ul>
<h2>3. Situações mais comuns de atendimento</h2>
<p>O reboque no Litoral Lagos pode ser acionado em panes na BR-101, falhas em avenidas movimentadas, superaquecimento no trânsito de temporada, pneus furados, colisões leves, veículos que não pegam após parada em hotel ou remoções programadas para oficina ou pátio.</p>
<h2>4. Como solicitar reboque no Litoral Lagos</h2>
<p>Entre em contato pelo telefone ou WhatsApp <strong>(21) 95954-3043</strong>. Informe localização exata, município, ponto de referência, destino do veículo e condição do carro para agilizar o atendimento.</p>
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

    replacements = [
        ("reboque-regiao-serrana", NEW_SLUG),
        (
            "Reboque na Região Serrana 24h | Chegamos em 15 min",
            "Reboque no Litoral Lagos 24h | Chegamos em 15 min",
        ),
        ("Reboque na Região Serrana", "Reboque no Litoral Lagos"),
        ("reboque na Região Serrana", "reboque no Litoral Lagos"),
        ("Região Serrana", "Litoral Lagos"),
        ("BR-040, RJ-130 ou em algum município do Litoral Lagos", "BR-101, RJ-106 ou em algum município do Litoral Lagos"),
        ("BR-040 e RJ-130", "BR-101 e RJ-106"),
        ("RJ-116 e BR-040", "RJ-124 e BR-101"),
        ("serra fluminense", "litoral norte fluminense"),
        ("de serra e urbanos", "litorâneos e urbanos"),
        ("centros comerciais e trechos de serra", "centros comerciais e trechos litorâneos"),
        ("Serra dos Órgãos", "Região dos Lagos"),
        ("Petrópolis", "Cabo Frio"),
        ("Teresópolis", "Araruama"),
        ("Nova Friburgo", "Búzios"),
        ("Itatiaia", "Arraial do Cabo"),
        ("Itaipava", "Saquarema"),
        ("na BR-040", "na BR-101"),
        ("trechos de serra", "trechos litorâneos"),
        ("subidas", "avenidas movimentadas"),
    ]
    for old, new in replacements:
        html = html.replace(old, new)

    schema_cleanup = [
        ("BR-040 e RJ-130", "BR-101 e RJ-106"),
        ("RJ-116, BR-040 e principais avenidas da região", "RJ-124, BR-101 e principais avenidas da região"),
        (
            "Principais Vias: BR-040, RJ-130 e RJ-116",
            "Principais Vias: BR-101, RJ-106 e RJ-124",
        ),
        ("rodovias sinuosas como a BR-040", "rodovias movimentadas como a BR-101"),
    ]
    for old, new in schema_cleanup:
        html = html.replace(old, new)

    return html


def update_regional_services() -> None:
    slugs = json.loads(REGIONAL_FILE.read_text(encoding="utf-8"))
    slugs = [slug for slug in slugs if slug not in REMOVE_FROM_FOOTER]
    if NEW_SLUG not in slugs:
        try:
            idx = slugs.index("reboque-em-grumari")
            slugs.insert(idx, NEW_SLUG)
        except ValueError:
            slugs.append(NEW_SLUG)
    REGIONAL_FILE.write_text(json.dumps(slugs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_service_regions() -> None:
    regions = json.loads(REGIONS_FILE.read_text(encoding="utf-8"))
    regions["litoral-lagos"] = [NEW_SLUG, *REMOVE_FROM_FOOTER]
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
