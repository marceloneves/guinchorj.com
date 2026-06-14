#!/usr/bin/env python3
"""Gera a página pilar do cluster Manual do Motorista."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "blog/reboque-e-guincho/o-que-e-reboque-e-como-funciona/index.html"
BODY = ROOT / "scripts/content/manual-do-motorista-pillar-body.html"
OUTPUT = ROOT / "blog/manual-do-motorista/index.html"

TITLE = "Manual do Motorista: Problemas Comuns no Carro e Como Resolver"
SHORT_TITLE = "Manual do Motorista"
SLUG = "manual-do-motorista"
CANONICAL = f"https://guinchorj.com/blog/{SLUG}/"
DESCRIPTION = (
    "Entenda quais são os principais problemas que podem deixar um veículo parado, "
    "saiba quando é seguro continuar dirigindo e descubra quando buscar ajuda especializada."
)
DATE = "2026-06-07"
DATETIME = "2026-06-07T10:00:00-03:00"
CATEGORY = "Manual do Motorista"
CLOSING_HEADING = "Por Que Conhecer Esses Problemas Importa"
INDEX_AFTER_MARKER = "<h2>Quais Problemas Mais Deixam um Carro Parado</h2>"

SATELLITE_LINKS: dict[str, str] = {
    "Carro Não Liga": "carro-nao-liga",
    "Bateria Descarregada": "bateria-descarregada",
    "Carro Não Pega no Frio": "carro-nao-pega-no-frio",
    "Alternador com Defeito": "alternador-com-defeito",
    "Carro Não Reconhece a Chave": "carro-nao-reconhece-chave",
    "Carro Descarregado Depois de Ficar Parado": "carro-descarregado",
    "Motor Fervendo": "motor-ferveu",
    "Carro Esquentando Muito": "carro-esquentando-muito",
    "Motor Batendo": "motor-batendo",
    "Carro Falhando em Movimento": "carro-falhando",
    "Carro Perdendo Potência": "carro-perdendo-potencia",
    "Carro Engasgando": "carro-engasgando",
    "Carro Falhando em Marcha Lenta": "carro-falhando-marcha-lenta",
    "Carro Morrendo Sozinho": "carro-morrendo-sozinho",
    "Carro Consumindo Muito Combustível": "carro-consumindo-muito-combustivel",
    "Carro com Cheiro de Gasolina": "carro-com-cheiro-de-gasolina",
    "Motor Fundido": "motor-fundido",
    "Correia Dentada Rompida": "correia-dentada-rompida",
    "Fumaça Saindo do Motor": "fumaca-saindo-do-motor",
    "Cheiro de Queimado no Motor": "cheiro-de-queimado-no-motor",
    "Água no Motor Após Alagamentos": "agua-no-motor",
    "Pane Elétrica": "pane-eletrica-no-carro",
    "Luz da Injeção Eletrônica Acesa": "luz-da-injecao-acesa",
    "Luz do Óleo Acesa": "luz-do-oleo-acesa",
    "Luz da Bateria Acesa": "luz-da-bateria-acesa",
    "EPC Aceso no Painel": "luz-epc-acesa",
    "Câmbio Automático Travado": "cambio-automatico-travado",
    "Carro Automático Não Engata Marcha": "carro-automatico-nao-engata-marcha",
    "Posso Rebocar um Carro Automático?": "rebocar-carro-automatico",
    "Pneu Furado": "pneu-furado",
    "Freio Duro": "freio-duro",
    "Volante Pesado": "volante-pesado",
    "Carro Vibrando em Movimento": "carro-vibrando",
    "Pane Seca": "pane-seca",
    "Carro Morreu no Trânsito": "carro-morreu-no-transito",
    "Vazamento de Óleo no Carro": "vazamento-de-oleo",
    "Vazamento no Radiador": "vazamento-no-radiador",
    "Carro Fazendo Barulho Estranho": "carro-fazendo-barulho",
}

SATELLITE_ALIASES: dict[str, str] = {
    "Motor superaquecido": "motor-ferveu",
    "Pane elétrica": "pane-eletrica-no-carro",
    "Pane elétrica grave": "pane-eletrica-no-carro",
    "Água no motor": "agua-no-motor",
    "Câmbio automático travado": "cambio-automatico-travado",
    "Problemas no câmbio": "cambio-automatico-travado",
    "Falha nos freios": "freio-duro",
    "Problemas nos freios": "freio-duro",
}

SUBCLUSTERS: list[tuple[str, list[tuple[str, str]]]] = [
    (
        "Problemas na partida",
        [
            ("Carro Não Liga", "carro-nao-liga"),
            ("Bateria Descarregada", "bateria-descarregada"),
            ("Carro Não Pega no Frio", "carro-nao-pega-no-frio"),
            ("Alternador com Defeito", "alternador-com-defeito"),
            ("Carro Não Reconhece a Chave", "carro-nao-reconhece-chave"),
            ("Carro Descarregado Depois de Ficar Parado", "carro-descarregado"),
        ],
    ),
    (
        "Problemas no motor",
        [
            ("Motor Fervendo", "motor-ferveu"),
            ("Carro Esquentando Muito", "carro-esquentando-muito"),
            ("Motor Batendo", "motor-batendo"),
            ("Carro Falhando em Movimento", "carro-falhando"),
            ("Carro Perdendo Potência", "carro-perdendo-potencia"),
            ("Carro Engasgando", "carro-engasgando"),
            ("Carro Falhando em Marcha Lenta", "carro-falhando-marcha-lenta"),
            ("Carro Morrendo Sozinho", "carro-morrendo-sozinho"),
            ("Carro Consumindo Muito Combustível", "carro-consumindo-muito-combustivel"),
            ("Carro com Cheiro de Gasolina", "carro-com-cheiro-de-gasolina"),
            ("Motor Fundido", "motor-fundido"),
            ("Correia Dentada Rompida", "correia-dentada-rompida"),
            ("Fumaça Saindo do Motor", "fumaca-saindo-do-motor"),
            ("Cheiro de Queimado no Motor", "cheiro-de-queimado-no-motor"),
            ("Água no Motor Após Alagamentos", "agua-no-motor"),
        ],
    ),
    (
        "Problemas elétricos",
        [
            ("Pane Elétrica", "pane-eletrica-no-carro"),
            ("Luz da Injeção Eletrônica Acesa", "luz-da-injecao-acesa"),
            ("Luz do Óleo Acesa", "luz-do-oleo-acesa"),
            ("Luz da Bateria Acesa", "luz-da-bateria-acesa"),
            ("EPC Aceso no Painel", "luz-epc-acesa"),
        ],
    ),
    (
        "Câmbio",
        [
            ("Câmbio Automático Travado", "cambio-automatico-travado"),
            ("Carro Automático Não Engata Marcha", "carro-automatico-nao-engata-marcha"),
            ("Posso Rebocar um Carro Automático?", "rebocar-carro-automatico"),
        ],
    ),
    (
        "Pneus, freios e direção",
        [
            ("Pneu Furado", "pneu-furado"),
            ("Freio Duro", "freio-duro"),
            ("Volante Pesado", "volante-pesado"),
            ("Carro Vibrando em Movimento", "carro-vibrando"),
        ],
    ),
    (
        "Emergências",
        [
            ("Pane Seca", "pane-seca"),
            ("Carro Morreu no Trânsito", "carro-morreu-no-transito"),
            ("Vazamento de Óleo no Carro", "vazamento-de-oleo"),
            ("Vazamento no Radiador", "vazamento-no-radiador"),
            ("Carro Fazendo Barulho Estranho", "carro-fazendo-barulho"),
        ],
    ),
]

SERVICE_CTA = """
<h2>Precisa de reboque ou guincho no Rio de Janeiro?</h2>
<p>A Guincho RJ atua 24 horas no Rio de Janeiro, Niterói e região metropolitana. Veja nossos principais serviços:</p>
<ul>
<li><a href="../../servico/reboque-na-zona-sul-no-rj/" title="Reboque Zona Sul">Reboque Zona Sul</a></li>
<li><a href="../../servico/reboque-zona-oeste/" title="Reboque Zona Oeste">Reboque Zona Oeste</a></li>
<li><a href="../../servico/reboque-zona-norte-rj/" title="Reboque Zona Norte">Reboque Zona Norte</a></li>
<li><a href="../../servico/reboque-em-niteroi/" title="Reboque Niterói">Reboque Niterói</a></li>
<li><a href="../../servico/reboque-linha-vermelha-rj/" title="Reboque Linha Vermelha">Reboque Linha Vermelha</a></li>
<li><a href="../../servico/reboque-linha-amarela-rj/" title="Reboque Linha Amarela">Reboque Linha Amarela</a></li>
<li><a href="../../servico/reboque-avenida-brasil-rj/" title="Reboque Avenida Brasil">Reboque Avenida Brasil</a></li>
<li><a href="../../servico/reboque-dutra-rj/" title="Reboque Dutra">Reboque Dutra</a></li>
</ul>
<p>Telefone/WhatsApp: <a href="tel:+5521959543043"><strong>(21) 95954-3043</strong></a></p>
"""

COMPANY_FOOTER = """
<h2>Dados oficiais da Guincho RJ</h2>
<p><strong>Empresa:</strong> Guincho RJ</p>
<p><strong>Atuação:</strong> desde 1995</p>
<p><strong>Endereço:</strong> Avenida Presidente Vargas, 1120 — Centro, Rio de Janeiro – RJ, CEP 20071-002</p>
<p><strong>E-mail:</strong> <a href="mailto:contato@guinchorj.com">contato@guinchorj.com</a></p>
<p><strong>Telefone/WhatsApp:</strong> <a href="tel:+5521959543043">(21) 95954-3043</a></p>
<p><strong>Site:</strong> <a href="../../">guinchorj.com</a></p>
"""


def format_tables(html: str) -> str:
    def wrap_table(match: re.Match[str]) -> str:
        table_html = match.group(0)
        table_html = table_html.replace(
            "<table>",
            '<table class="table table-bordered artigo-table">',
            1,
        )
        return f'<div class="table-responsive">{table_html}</div>'

    return re.sub(r"<table>.*?</table>", wrap_table, html, flags=re.DOTALL)


def inject_assets(html: str) -> str:
    assets = '<link rel="stylesheet" href="../article-tables.css">'
    if "article-tables.css" in html:
        return html
    return html.replace("</head>", assets + "</head>", 1)


def inject_satellite_links(html: str) -> str:
    links = {**SATELLITE_LINKS, **SATELLITE_ALIASES}
    for title in sorted(links, key=len, reverse=True):
        slug = links[title]
        href = f"../{slug}/"
        for tag in ("h2", "h3"):
            pattern = rf"<{tag}>{re.escape(title)}</{tag}>"
            replacement = (
                f'<{tag}><a href="{href}" title="{title}">{title}</a></{tag}>'
            )
            html = re.sub(pattern, replacement, html)
    return html


def build_satellite_index() -> str:
    parts = [
        "<h2>Artigos do Manual do Motorista</h2>",
        "<p>Explore os guias detalhados sobre cada problema abordado neste manual:</p>",
    ]
    for group, articles in SUBCLUSTERS:
        parts.append(f"<h3>{group}</h3>")
        parts.append("<ul>")
        for title, slug in articles:
            parts.append(
                f'<li><a href="../{slug}/" title="{title}">{title}</a></li>'
            )
        parts.append("</ul>")
    return "\n".join(parts) + "\n"


def build_body() -> str:
    raw = BODY.read_text(encoding="utf-8").strip()
    raw = format_tables(raw)
    raw = inject_satellite_links(raw)
    index = build_satellite_index()
    if INDEX_AFTER_MARKER not in raw:
        raise SystemExit(
            f"Marcador do índice não encontrado: {INDEX_AFTER_MARKER}\n"
            "Ajuste INDEX_AFTER_MARKER no script do pilar."
        )
    raw = raw.replace(INDEX_AFTER_MARKER, index + INDEX_AFTER_MARKER, 1)
    closing_marker = f"<h2>{CLOSING_HEADING}</h2>"
    if closing_marker not in raw:
        raise SystemExit(
            f"Seção final não encontrada: {closing_marker}\n"
            "Use um título específico, não Conclusão."
        )
    raw = raw.replace(closing_marker, SERVICE_CTA + closing_marker, 1)
    raw += COMPANY_FOOTER
    return (
        f'<p class="lead" style="text-align:center">{TITLE}</p>'
        f'<p class="post-dates">Publicado em: <time datetime="{DATE}">07/06/2026</time> '
        f"- Atualizado em: <time datetime=\"{DATE}\">07/06/2026</time></p>"
        f'<article class="artigo-manual-do-motorista">{raw}</article>'
    )


def build_section(body_html: str) -> str:
    return (
        f'<section class="services-details-area ptb-100">'
        f'<h2 class="skip-link">{TITLE}</h2>'
        f'<div class="container"> <div class="row"> '
        f'<article class="col-lg-12 col-md-12">'
        f'<h2 class="skip-link">{TITLE}</h2>'
        f'<div class="services-details-desc"> '
        f'<div class="image" style="display:flex;align-items:center;justify-content:center;"> </div> '
        f'<div class="writen_content"> {body_html} </article> </div> </article> </div> </div> </section>'
    )


def fix_paths(html: str) -> str:
    html = html.replace("../../../", "../../")
    return html


def fix_nav_blog_link(html: str) -> str:
    """Pilar em /blog/manual-do-motorista/ deve apontar o menu Blog para /blog/."""
    return html.replace(
        '<a href="../../" class="nav-link">Blog</a>',
        '<a href="../" class="nav-link">Blog</a>',
    )


def replace_head(html: str) -> str:
    html = re.sub(r"<title>[^<]+</title>", f"<title>{TITLE}</title>", html, count=1)
    html = re.sub(
        r'name="description" content="[^"]*"',
        f'name="description" content="{DESCRIPTION}"',
        html,
        count=1,
    )
    html = re.sub(
        r'<link rel="canonical" href="[^"]+"',
        f'<link rel="canonical" href="{CANONICAL}"',
        html,
        count=1,
    )
    html = re.sub(
        r'property="og:title" content="[^"]+"',
        f'property="og:title" content="{TITLE}"',
        html,
        count=1,
    )
    html = re.sub(
        r'property="og:description" content="[^"]+"',
        f'property="og:description" content="{DESCRIPTION}"',
        html,
        count=1,
    )
    html = re.sub(
        r'property="og:url" content="[^"]+"',
        f'property="og:url" content="{CANONICAL}"',
        html,
        count=1,
    )
    html = re.sub(
        r'name="twitter:title" content="[^"]+"',
        f'name="twitter:title" content="{TITLE}"',
        html,
        count=1,
    )
    html = re.sub(
        r'name="twitter:description" content="[^"]+"',
        f'name="twitter:description" content="{DESCRIPTION}"',
        html,
        count=1,
    )
    html = re.sub(
        r'property="og:updated_time" content="[^"]+"',
        f'property="og:updated_time" content="{DATETIME}"',
        html,
        count=1,
    )
    return html


def replace_page_title(main: str) -> str:
    breadcrumb = (
        '<ol class="breadcrumb" style="display:flex;align-items:center;justify-content:center;">'
        '<li class="breadcrumb-item"><a title="Guincho e Reboque Rio de Janeiro" href="../../">'
        "<span>Guincho e Reboque Rio de Janeiro</span></a></li>"
        '<li class="breadcrumb-item"><a title="Blog" href="../"><span>Blog</span></a></li>'
        f'<li class="breadcrumb-item active" aria-current="page">'
        f'<a title="{SHORT_TITLE}" href="./"><span>{SHORT_TITLE}</span></a></li>'
        "</ol>"
    )
    header = (
        f'<header class="page-title-area item-bg-1"><div class="d-table"><div class="d-table-cell">'
        f'<div class="container"><div class="page-title-content"><h1>{TITLE}</h1>'
        f'<nav aria-label="Trilha de navegação">{breadcrumb}</nav>'
        f"</div></div></div></div></header>"
    )
    return re.sub(
        r'<header class="page-title-area item-bg-1">.*?</header>',
        header,
        main,
        count=1,
        flags=re.DOTALL,
    )


def replace_section(main: str, section: str) -> str:
    return re.sub(
        r'<section class="services-details-area ptb-100">.*?</section>',
        section,
        main,
        count=1,
        flags=re.DOTALL,
    )


def replace_schema(html: str) -> str:
    def repl(match: re.Match[str]) -> str:
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            return match.group(0)

        graph = data.get("@graph", [data])
        for node in graph:
            if node.get("@type") == "BlogPosting":
                node["headline"] = TITLE
                node["description"] = DESCRIPTION
                node["datePublished"] = DATETIME
                node["dateModified"] = DATETIME
                node["url"] = CANONICAL
                node["articleSection"] = CATEGORY
            if node.get("@type") == "BreadcrumbList":
                node["itemListElement"] = [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Home",
                        "item": "https://guinchorj.com/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "Blog",
                        "item": "https://guinchorj.com/blog/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": SHORT_TITLE,
                        "item": CANONICAL,
                    },
                ]
        return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False, separators=(",", ":"))}</script>'

    return re.sub(
        r'<script type="application/ld\+json">(\{.*?\})</script>',
        repl,
        html,
        count=1,
        flags=re.DOTALL,
    )


def main() -> None:
    html = fix_nav_blog_link(fix_paths(TEMPLATE.read_text(encoding="utf-8")))
    html = replace_head(html)
    html = replace_schema(html)
    html = inject_assets(html)

    main_match = re.search(r"(<main[^>]*>)(.*?)(</main>)", html, re.DOTALL)
    if not main_match:
        raise SystemExit("main não encontrado no template")

    main_inner = replace_page_title(main_match.group(2))
    main_inner = replace_section(main_inner, build_section(build_body()))
    html = html[: main_match.start()] + main_match.group(1) + main_inner + main_match.group(3) + html[main_match.end() :]

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Gerado: {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
