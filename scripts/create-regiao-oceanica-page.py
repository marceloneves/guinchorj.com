#!/usr/bin/env python3
"""Cria página hub reboque-regiao-oceanica e atualiza configs/cards/rodapé."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
TEMPLATE = ROOT / "servico/reboque-baixada-fluminense/index.html"
TARGET_DIR = ROOT / "servico/reboque-regiao-oceanica"
TARGET = TARGET_DIR / "index.html"
REGIONAL_FILE = SCRIPTS / "regional-services.json"
REGIONS_FILE = SCRIPTS / "service-regions.json"

NEW_SLUG = "reboque-regiao-oceanica"
REMOVE_FROM_FOOTER = [
    "reboque-em-niteroi",
    "reboque-sao-goncalo",
    "reboque-itaborai",
    "reboque-em-marica",
    "reboque-em-mage",
    "reboque-em-guapimirim",
    "reboque-em-rio-bonito",
    "reboque-em-silva-jardim",
]

CITY_LINKS = [
    ("reboque-em-niteroi", "Reboque em Niterói 24 horas"),
    ("reboque-sao-goncalo", "Reboque em São Gonçalo 24 horas"),
    ("reboque-itaborai", "Reboque em Itaboraí"),
    ("reboque-em-marica", "Reboque em Maricá"),
    ("reboque-em-mage", "Reboque em Magé"),
    ("reboque-em-guapimirim", "Reboque em Guapimirim"),
    ("reboque-em-rio-bonito", "Reboque em Rio Bonito"),
    ("reboque-em-silva-jardim", "Reboque em Silva Jardim"),
]

CITY_LIST_HTML = "\n".join(
    f'<li><a href="../{slug}/" title="{title}">{title}</a></li>'
    for slug, title in CITY_LINKS
)

WRITTEN_CONTENT = f"""
<h2 style="text-align:center">Precisa de Reboque na Região Oceânica?</h2>
<p style="text-align: center;">
<i class="fa fa-phone" aria-hidden="true"></i>
<a href="tel:21959543043" title="Telefone" style="display: inline-block;" rel="nofollow">(21) 95954-3043</a>
| <i class="fa fa-whatsapp" aria-hidden="true"></i>
<a href="https://api.whatsapp.com/send?phone=5521959543043&amp;text=Ol%C3%A1,%20estou%20entrando%20em%20contato%20pelo%20site" title="Whatsapp" rel="nofollow external noopener" target="_blank" style="display: inline-block;">(21) 95954-3043</a>
</p>
<p>Seu veículo parou na <strong>Ponte Rio-Niterói</strong>, na <strong>BR-101</strong>, na <strong>RJ-106</strong> ou em algum município da <strong>Região Oceânica</strong>? A <strong>Guincho RJ</strong> oferece atendimento de <strong>reboque na Região Oceânica</strong> com remoção segura, agilidade e orientação clara em vias litorâneas, avenidas urbanas e acessos à Baía de Guanabara.</p>
<p>A Região Oceânica reúne cidades do leste fluminense, litoral oceânico, áreas residenciais, centros comerciais, trechos de restinga, rodovias de ligação e acessos entre Niterói, São Gonçalo e o litoral. Por isso, uma pane em locais como <strong>Niterói</strong>, <strong>São Gonçalo</strong>, <strong>Maricá</strong>, <strong>Itaboraí</strong> ou <strong>Magé</strong> exige planejamento, equipamento adequado e conhecimento da região.</p>
<p>A <strong>Guincho RJ atua desde 1995</strong> com guincho, reboque e assistência veicular no Rio de Janeiro e região. Na Região Oceânica, o atendimento contempla carros de passeio, motos, SUVs, utilitários, picapes, vans e remoções programadas para oficinas, concessionárias, residências, empresas ou outros destinos indicados pelo cliente.</p>
<h2>1. Atendimento de reboque em toda a Região Oceânica</h2>
<p>O serviço de <strong>reboque na Região Oceânica</strong> é indicado para veículos que não podem continuar circulando com segurança por pane mecânica, pane elétrica, bateria descarregada, superaquecimento, pneu furado, falta de combustível, colisão, veículo travado ou necessidade de transporte programado.</p>
<p>O atendimento pode acontecer na BR-101, em avenidas principais, ruas urbanas, condomínios, garagens, estacionamentos, trechos litorâneos e pontos de referência dos principais municípios. A remoção considera distância, tipo de veículo, local da ocorrência, destino e condições de acesso.</p>
<h2>2. Cidades atendidas na Região Oceânica</h2>
<p>Organizamos a cobertura da Região Oceânica por município. Confira as páginas específicas de cada cidade:</p>
<ul>
{CITY_LIST_HTML}
</ul>
<h2>3. Situações mais comuns de atendimento</h2>
<p>O reboque na Região Oceânica pode ser acionado em panes na BR-101, falhas em avenidas movimentadas, superaquecimento no trânsito intenso, pneus furados, colisões leves, veículos que não pegam após parada em comércio ou remoções programadas para oficina ou pátio.</p>
<h2>4. Como solicitar reboque na Região Oceânica</h2>
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
        ("reboque-baixada-fluminense", NEW_SLUG),
        (
            "Reboque na Baixada Fluminense 24h | Chegamos em 15 min",
            "Reboque na Região Oceânica 24h | Chegamos em 15 min",
        ),
        ("Reboque na Baixada Fluminense", "Reboque na Região Oceânica"),
        ("reboque na Baixada Fluminense", "reboque na Região Oceânica"),
        ("Baixada Fluminense", "Região Oceânica"),
        (
            "Rodovia Dutra (BR-116) ou em algum município da Região Oceânica",
            "Ponte Rio-Niterói, BR-101 ou em algum município da Região Oceânica",
        ),
        ("Rodovia Dutra (BR-116)", "Ponte Rio-Niterói e BR-101"),
        ("Via Light, BR-493", "RJ-106 e BR-101"),
        ("Grande Rio", "leste fluminense"),
        ("urbanos e rodoviários", "litorâneos e urbanos"),
        ("empresas, centros comerciais", "centros comerciais e trechos litorâneos"),
        ("Nova Iguaçu", "Niterói"),
        ("Duque de Caxias", "São Gonçalo"),
        ("São João de Meriti", "Maricá"),
        ("Belford Roxo", "Itaboraí"),
        ("Nilópolis", "Magé"),
        ("na Dutra", "na BR-101"),
        ("município", "município"),
    ]
    for old, new in replacements:
        html = html.replace(old, new)

    schema_cleanup = [
        ("Rodovia Dutra (BR-116)", "Ponte Rio-Niterói e BR-101"),
        ("Via Light, BR-493 e principais avenidas da região", "RJ-106, BR-101 e principais avenidas da região"),
        (
            "Principais Vias: Rodovia Dutra (BR-116), Via Light e BR-493",
            "Principais Vias: BR-101, RJ-106 e Ponte Rio-Niterói",
        ),
        ("rodovias movimentadas como a BR-116", "rodovias movimentadas como a BR-101"),
    ]
    for old, new in schema_cleanup:
        html = html.replace(old, new)

    return html


def update_regional_services() -> None:
    slugs = json.loads(REGIONAL_FILE.read_text(encoding="utf-8"))
    slugs = [slug for slug in slugs if slug not in REMOVE_FROM_FOOTER]
    if NEW_SLUG not in slugs:
        try:
            idx = slugs.index("reboque-em-teresopolis")
            slugs.insert(idx, NEW_SLUG)
        except ValueError:
            slugs.append(NEW_SLUG)
    REGIONAL_FILE.write_text(json.dumps(slugs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_service_regions() -> None:
    regions = json.loads(REGIONS_FILE.read_text(encoding="utf-8"))
    regions["regiao-oceanica"] = [NEW_SLUG, *REMOVE_FROM_FOOTER]
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
