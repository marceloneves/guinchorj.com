#!/usr/bin/env python3
"""Cria página hub reboque-regiao-serrana e atualiza configs/cards/rodapé."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
TEMPLATE = ROOT / "servico/reboque-regiao-oceanica/index.html"
TARGET_DIR = ROOT / "servico/reboque-regiao-serrana"
TARGET = TARGET_DIR / "index.html"
REGIONAL_FILE = SCRIPTS / "regional-services.json"
REGIONS_FILE = SCRIPTS / "service-regions.json"

NEW_SLUG = "reboque-regiao-serrana"
REMOVE_FROM_FOOTER = [
    "reboque-em-teresopolis",
    "reboque-em-petropolis",
    "reboque-em-nova-friburgo",
    "reboque-em-itatiaia",
    "reboque-em-itaipava",
]

CITY_LINKS = [
    ("reboque-em-teresopolis", "Reboque em Teresópolis"),
    ("reboque-em-petropolis", "Reboque em Petrópolis"),
    ("reboque-em-nova-friburgo", "Reboque em Nova Friburgo"),
    ("reboque-em-itatiaia", "Reboque em Itatiaia"),
    ("reboque-em-itaipava", "Reboque em Itaipava"),
]

CITY_LIST_HTML = "\n".join(
    f'<li><a href="../{slug}/" title="{title}">{title}</a></li>'
    for slug, title in CITY_LINKS
)

WRITTEN_CONTENT = f"""
<h2 style="text-align:center">Precisa de Reboque na Região Serrana?</h2>
<p style="text-align: center;">
<i class="fa fa-phone" aria-hidden="true"></i>
<a href="tel:21959543043" title="Telefone" style="display: inline-block;" rel="nofollow">(21) 95954-3043</a>
| <i class="fa fa-whatsapp" aria-hidden="true"></i>
<a href="https://api.whatsapp.com/send?phone=5521959543043&amp;text=Ol%C3%A1,%20estou%20entrando%20em%20contato%20pelo%20site" title="Whatsapp" rel="nofollow external noopener" target="_blank" style="display: inline-block;">(21) 95954-3043</a>
</p>
<p>Seu veículo parou na <strong>BR-040</strong>, na <strong>RJ-130</strong>, na <strong>RJ-116</strong> ou em algum município da <strong>Região Serrana</strong>? A <strong>Guincho RJ</strong> oferece atendimento de <strong>reboque na Região Serrana</strong> com remoção segura, agilidade e orientação clara em trechos de serra, rodovias sinuosas e centros urbanos da região.</p>
<p>A Região Serrana reúne cidades de clima ameno, turismo, comércio, acessos montanhosos, curvas, túneis e ligação com o Rio de Janeiro e o interior. Por isso, uma pane em locais como <strong>Petrópolis</strong>, <strong>Teresópolis</strong>, <strong>Nova Friburgo</strong>, <strong>Itatiaia</strong> ou <strong>Itaipava</strong> exige planejamento, equipamento adequado e conhecimento da região.</p>
<p>A <strong>Guincho RJ atua desde 1995</strong> com guincho, reboque e assistência veicular no Rio de Janeiro e região. Na Região Serrana, o atendimento contempla carros de passeio, motos, SUVs, utilitários, picapes, vans e remoções programadas para oficinas, concessionárias, residências, hotéis ou outros destinos indicados pelo cliente.</p>
<h2>1. Atendimento de reboque em toda a Região Serrana</h2>
<p>O serviço de <strong>reboque na Região Serrana</strong> é indicado para veículos que não podem continuar circulando com segurança por pane mecânica, pane elétrica, bateria descarregada, superaquecimento, pneu furado, falta de combustível, colisão, veículo travado ou necessidade de transporte programado.</p>
<p>O atendimento pode acontecer na BR-040, em ruas urbanas, condomínios, garagens, estacionamentos, trechos de serra e pontos de referência dos principais municípios. A remoção considera distância, tipo de veículo, local da ocorrência, destino e condições de acesso.</p>
<h2>2. Cidades atendidas na Região Serrana</h2>
<p>Organizamos a cobertura da Região Serrana por município. Confira as páginas específicas de cada cidade:</p>
<ul>
{CITY_LIST_HTML}
</ul>
<h2>3. Situações mais comuns de atendimento</h2>
<p>O reboque na Região Serrana pode ser acionado em panes em subidas, falhas em trechos de serra, superaquecimento em viagens longas, pneus furados, colisões leves, veículos que não pegam após parada em hotel ou remoções programadas para oficina ou pátio.</p>
<h2>4. Como solicitar reboque na Região Serrana</h2>
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
        ("reboque-regiao-oceanica", NEW_SLUG),
        (
            "Reboque na Região Oceânica 24h | Chegamos em 15 min",
            "Reboque na Região Serrana 24h | Chegamos em 15 min",
        ),
        ("Reboque na Região Oceânica", "Reboque na Região Serrana"),
        ("reboque na Região Oceânica", "reboque na Região Serrana"),
        ("Região Oceânica", "Região Serrana"),
        ("Ponte Rio-Niterói, BR-101 ou em algum município da Região Serrana", "BR-040, RJ-130 ou em algum município da Região Serrana"),
        ("Ponte Rio-Niterói e BR-101", "BR-040 e RJ-130"),
        ("RJ-106 e BR-101", "RJ-116 e BR-040"),
        ("leste fluminense", "serra fluminense"),
        ("litorâneos e urbanos", "de serra e urbanos"),
        ("centros comerciais e trechos litorâneos", "centros comerciais e trechos de serra"),
        ("Baía de Guanabara", "Serra dos Órgãos"),
        ("Niterói", "Petrópolis"),
        ("São Gonçalo", "Teresópolis"),
        ("Maricá", "Nova Friburgo"),
        ("Itaboraí", "Itatiaia"),
        ("Magé", "Itaipava"),
        ("na BR-101", "na BR-040"),
    ]
    for old, new in replacements:
        html = html.replace(old, new)

    schema_cleanup = [
        ("Ponte Rio-Niterói e BR-101", "BR-040 e RJ-130"),
        ("RJ-106, BR-101 e principais avenidas da região", "RJ-116, BR-040 e principais avenidas da região"),
        (
            "Principais Vias: BR-101, RJ-106 e Ponte Rio-Niterói",
            "Principais Vias: BR-040, RJ-130 e RJ-116",
        ),
        ("rodovias movimentadas como a BR-101", "rodovias sinuosas como a BR-040"),
    ]
    for old, new in schema_cleanup:
        html = html.replace(old, new)

    return html


def update_regional_services() -> None:
    slugs = json.loads(REGIONAL_FILE.read_text(encoding="utf-8"))
    slugs = [slug for slug in slugs if slug not in REMOVE_FROM_FOOTER]
    if NEW_SLUG not in slugs:
        try:
            idx = slugs.index("reboque-costa-verde")
            slugs.insert(idx, NEW_SLUG)
        except ValueError:
            slugs.append(NEW_SLUG)
    REGIONAL_FILE.write_text(json.dumps(slugs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def update_service_regions() -> None:
    regions = json.loads(REGIONS_FILE.read_text(encoding="utf-8"))
    regions["regiao-serrana"] = [NEW_SLUG, *REMOVE_FROM_FOOTER]
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
