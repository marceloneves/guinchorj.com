#!/usr/bin/env python3
"""Cria página hub reboque-baixada-fluminense e atualiza configs/cards/rodapé."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
TEMPLATE = ROOT / "servico/reboque-costa-verde/index.html"
TARGET_DIR = ROOT / "servico/reboque-baixada-fluminense"
TARGET = TARGET_DIR / "index.html"
REGIONAL_FILE = SCRIPTS / "regional-services.json"
REGIONS_FILE = SCRIPTS / "service-regions.json"

NEW_SLUG = "reboque-baixada-fluminense"
REMOVE_FROM_FOOTER = [
    "reboque-em-nova-iguacu-no-rj",
    "reboque-em-duque-de-caixas-no-rj",
    "reboque-em-belfort-roxo-no-rj",
    "reboque-em-sao-joao-de-meriti-no-rj",
    "reboque-nilopolis",
    "reboque-mesquita",
    "reboque-em-queimados",
    "reboque-em-japeri",
    "reboque-em-paracambi",
    "reboque-em-seropedica",
    "reboque-dutra-rj",
]

CITY_LINKS = [
    ("reboque-em-nova-iguacu-no-rj", "Reboque em Nova Iguaçu 24 horas"),
    ("reboque-em-duque-de-caixas-no-rj", "Reboque em Duque de Caixas no RJ"),
    ("reboque-em-belfort-roxo-no-rj", "Reboque em Belford Roxo 24 horas"),
    ("reboque-em-sao-joao-de-meriti-no-rj", "Reboque em São João de Meriti no RJ"),
    ("reboque-nilopolis", "Reboque em Nilópolis"),
    ("reboque-mesquita", "Reboque em Mesquita"),
    ("reboque-em-queimados", "Reboque em Queimados 24 horas"),
    ("reboque-em-japeri", "Reboque em Japeri"),
    ("reboque-em-paracambi", "Reboque em Paracambi"),
    ("reboque-em-seropedica", "Reboque em Seropédica"),
    ("reboque-guadalupe-rj", "Reboque em Guadalupe no RJ"),
    ("reboque-dutra-rj", "Reboque na Dutra no RJ"),
]

CITY_LIST_HTML = "\n".join(
    f'<li><a href="../{slug}/" title="{title}">{title}</a></li>'
    for slug, title in CITY_LINKS
)

WRITTEN_CONTENT = f"""
<h2 style="text-align:center">Precisa de Reboque na Baixada Fluminense?</h2>
<p style="text-align: center;">
<i class="fa fa-phone" aria-hidden="true"></i>
<a href="tel:21959543043" title="Telefone" style="display: inline-block;" rel="nofollow">(21) 95954-3043</a>
| <i class="fa fa-whatsapp" aria-hidden="true"></i>
<a href="https://api.whatsapp.com/send?phone=5521959543043&amp;text=Ol%C3%A1,%20estou%20entrando%20em%20contato%20pelo%20site" title="Whatsapp" rel="nofollow external noopener" target="_blank" style="display: inline-block;">(21) 95954-3043</a>
</p>
<p>Seu veículo parou na <strong>Rodovia Presidente Dutra (BR-116)</strong>, na <strong>Via Light</strong>, na <strong>BR-493</strong> ou em algum município da <strong>Baixada Fluminense</strong>? A <strong>Guincho RJ</strong> oferece atendimento de <strong>reboque na Baixada Fluminense</strong> com remoção segura, agilidade e orientação clara em vias expressas, avenidas urbanas e acessos ao Grande Rio.</p>
<p>A Baixada Fluminense reúne cidades densamente populosas, corredores rodoviários, áreas industriais, centros comerciais, bairros residenciais e vias de ligação com o Rio de Janeiro. Por isso, uma pane em locais como <strong>Nova Iguaçu</strong>, <strong>Duque de Caxias</strong>, <strong>São João de Meriti</strong>, <strong>Belford Roxo</strong> ou <strong>Nilópolis</strong> exige planejamento, equipamento adequado e conhecimento da região.</p>
<p>A <strong>Guincho RJ atua desde 1995</strong> com guincho, reboque e assistência veicular no Rio de Janeiro e região. Na Baixada Fluminense, o atendimento contempla carros de passeio, motos, SUVs, utilitários, picapes, vans e remoções programadas para oficinas, concessionárias, residências, empresas ou outros destinos indicados pelo cliente.</p>
<h2>1. Atendimento de reboque em toda a Baixada Fluminense</h2>
<p>O serviço de <strong>reboque na Baixada Fluminense</strong> é indicado para veículos que não podem continuar circulando com segurança por pane mecânica, pane elétrica, bateria descarregada, superaquecimento, pneu furado, falta de combustível, colisão, veículo travado ou necessidade de transporte programado.</p>
<p>O atendimento pode acontecer na Dutra, em avenidas principais, ruas urbanas, condomínios, garagens, estacionamentos, áreas industriais e pontos de referência dos principais municípios. A remoção considera distância, tipo de veículo, local da ocorrência, destino e condições de acesso.</p>
<h2>2. Cidades atendidas na Baixada Fluminense</h2>
<p>Organizamos a cobertura da Baixada Fluminense por município. Confira as páginas específicas de cada cidade:</p>
<ul>
{CITY_LIST_HTML}
</ul>
<h2>3. Situações mais comuns de atendimento</h2>
<p>O reboque na Baixada Fluminense pode ser acionado em panes na Dutra, falhas em avenidas movimentadas, superaquecimento no trânsito intenso, pneus furados, colisões leves, veículos que não pegam após parada em comércio ou remoções programadas para oficina ou pátio.</p>
<h2>4. Como solicitar reboque na Baixada Fluminense</h2>
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
        ("reboque-costa-verde", NEW_SLUG),
        ("Reboque na Costa Verde 24h | Chegamos em 15 min", "Reboque na Baixada Fluminense 24h | Chegamos em 15 min"),
        ("Reboque na Costa Verde", "Reboque na Baixada Fluminense"),
        ("reboque na Costa Verde", "reboque na Baixada Fluminense"),
        ("Costa Verde", "Baixada Fluminense"),
        ("BR-101 (Rio-Santos) ou em alguma cidade da Baixada Fluminense", "Rodovia Dutra (BR-116) ou em algum município da Baixada Fluminense"),
        ("BR-101 (Rio-Santos)", "Rodovia Dutra (BR-116)"),
        ("Rio-Santos", "Dutra"),
        ("litoral fluminense", "Grande Rio"),
        ("litorâneos", "urbanos e rodoviários"),
        ("hotéis, marinas", "empresas, centros comerciais"),
    ]
    for old, new in replacements:
        html = html.replace(old, new)

    schema_cleanup = [
        ("Rodovia Dutra (BR-101)", "Rodovia Dutra (BR-116)"),
        ("rodovias sinuosas como a BR-101", "rodovias movimentadas como a BR-116"),
        ("Estrada do Contorno e acesso ao Colégio Naval", "Via Light, BR-493 e principais avenidas da região"),
        ("Principais Vias: Rodovia Dutra (BR-101)", "Principais Vias: Rodovia Dutra (BR-116), Via Light e BR-493"),
    ]
    for old, new in schema_cleanup:
        html = html.replace(old, new)

    return html


def update_regional_services() -> None:
    slugs = json.loads(REGIONAL_FILE.read_text(encoding="utf-8"))
    slugs = [slug for slug in slugs if slug not in REMOVE_FROM_FOOTER]
    if NEW_SLUG not in slugs:
        try:
            idx = slugs.index("reboque-em-niteroi")
            slugs.insert(idx, NEW_SLUG)
        except ValueError:
            slugs.append(NEW_SLUG)
    REGIONAL_FILE.write_text(json.dumps(slugs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_service_regions() -> None:
    regions = json.loads(REGIONS_FILE.read_text(encoding="utf-8"))
    regions["baixada-fluminense"] = [
        NEW_SLUG,
        "reboque-em-nova-iguacu-no-rj",
        "reboque-em-duque-de-caixas-no-rj",
        "reboque-em-belfort-roxo-no-rj",
        "reboque-em-sao-joao-de-meriti-no-rj",
        "reboque-nilopolis",
        "reboque-mesquita",
        "reboque-em-queimados",
        "reboque-em-japeri",
        "reboque-em-paracambi",
        "reboque-em-seropedica",
        "reboque-guadalupe",
        "reboque-guadalupe-rj",
        "reboque-dutra-rj",
    ]
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
