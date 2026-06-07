#!/usr/bin/env python3
"""Validação de HTML semântico, acessibilidade e JSON-LD do site."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_PREFIX = "https://guinchorj.com"

JSON_LD_PATTERN = re.compile(
    r'<script type="application/ld\+json">(.*?)</script>',
    re.DOTALL,
)
WEBPAGE_TYPES = frozenset(
    {
        "WebPage",
        "AboutPage",
        "ContactPage",
        "CollectionPage",
        "SearchResultsPage",
        "FAQPage",
    }
)
WRITEN_FIRST_H2 = re.compile(
    r'class="writen_content">\s*<h2(?![^>]*sr-only)[^>]*>(.*?)</h2>',
    re.DOTALL | re.IGNORECASE,
)
H1_PATTERN = re.compile(r"<h1[^>]*>(.*?)</h1>", re.DOTALL | re.IGNORECASE)
POST_DATES_PATTERN = re.compile(r'class="post-dates">.*?<time datetime=', re.DOTALL)


@dataclass
class PageReport:
    path: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def iter_html_files() -> list[Path]:
    files: list[Path] = []
    for path in sorted(ROOT.rglob("*.html")):
        if "wp-content" in path.parts:
            continue
        if path.name == "_downloads.html":
            continue
        files.append(path)
    return files


def is_service_page(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    return len(rel.parts) >= 2 and rel.parts[0] == "servico"


def is_blog_post(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if rel.parts[0] != "blog" or rel.name != "index.html":
        return False
    if len(rel.parts) <= 2:
        return False
    if "page" in rel.parts:
        return False
    if len(rel.parts) == 3 and rel.parts[1] == "reboque-e-guincho":
        return False
    return True


def is_blog_listing(path: Path) -> bool:
    rel = path.relative_to(ROOT).as_posix()
    if rel in {"blog/index.html", "blog/reboque-e-guincho/index.html"}:
        return True
    if re.fullmatch(r"blog/page/\d+/index\.html", rel):
        return True
    return bool(re.fullmatch(r"blog/reboque-e-guincho/page/\d+/index\.html", rel))


def normalize_heading(text: str) -> str:
    clean = re.sub(r"<[^>]+>", "", text)
    return re.sub(r"\s+", " ", clean.strip().lower())


def node_types(node: dict) -> set[str]:
    value = node.get("@type")
    if isinstance(value, list):
        return {str(item) for item in value}
    if value is None:
        return set()
    return {str(value)}


def site_path_from_file(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        rel = rel[: -len("index.html")]
    if not rel.endswith("/"):
        rel += "/"
    return "/" + rel


def validate_seo_urls(html: str, path: Path, report: PageReport) -> None:
    expected = SITE_PREFIX + site_path_from_file(path)

    canonical = re.search(r'rel="canonical"\s+href="([^"]+)"', html, re.IGNORECASE)
    if not canonical:
        report.errors.append("canonical ausente")
    elif not canonical.group(1).startswith("https://"):
        report.errors.append(f"canonical não é URL absoluta: {canonical.group(1)}")
    elif canonical.group(1) != expected:
        report.errors.append(f"canonical incorreto: {canonical.group(1)}")

    hreflang_links = re.findall(
        r'<link[^>]*\bhreflang="[^"]+"[^>]*\bhref="([^"]+)"'
        r'|<link[^>]*\bhref="([^"]+)"[^>]*\bhreflang="[^"]+"',
        html,
        re.IGNORECASE,
    )
    if not hreflang_links:
        report.warnings.append("hreflang ausente")
    else:
        for match in hreflang_links:
            href = match[0] or match[1]
            if not href.startswith("https://"):
                report.errors.append(f"hreflang não é URL absoluta: {href}")
            elif href != expected:
                report.errors.append(f"hreflang incorreto: {href}")

    og_url = re.search(r'property="og:url"\s+content="([^"]+)"', html, re.IGNORECASE)
    if og_url and not og_url.group(1).startswith("https://"):
        report.errors.append(f"og:url não é URL absoluta: {og_url.group(1)}")
    elif og_url and og_url.group(1) != expected:
        report.errors.append(f"og:url incorreto: {og_url.group(1)}")


def validate_json_ld(html: str, report: PageReport) -> None:
    blocks = JSON_LD_PATTERN.findall(html)
    if not blocks:
        report.errors.append("JSON-LD ausente")
        return

    for index, block in enumerate(blocks, start=1):
        if not block.strip():
            report.errors.append(f"JSON-LD #{index} vazio")
            continue
        try:
            data = json.loads(block)
        except json.JSONDecodeError as exc:
            report.errors.append(f"JSON-LD #{index} inválido: {exc.msg}")
            continue

        payload = json.dumps(data, ensure_ascii=False)
        if "@graph" in data:
            graph = data["@graph"]
            if not isinstance(graph, list) or not graph:
                report.errors.append("JSON-LD @graph vazio")
                continue
            has_entity = any(
                not types.intersection(WEBPAGE_TYPES) and types
                for node in graph
                for types in [node_types(node)]
            )
            has_webpage = any(
                types.intersection(WEBPAGE_TYPES)
                for node in graph
                for types in [node_types(node)]
            )
            if not has_entity and not has_webpage:
                report.warnings.append("JSON-LD @graph sem entidade principal")
            if "mainEntity" not in payload and "AboutPage" not in payload:
                if not any(
                    "CollectionPage" in node_types(node) for node in graph
                ):
                    report.warnings.append("JSON-LD sem mainEntity explícito")
            if "BreadcrumbList" not in payload and not any(
                "CollectionPage" in node_types(node) for node in graph
            ):
                report.warnings.append("JSON-LD sem BreadcrumbList")
        elif "mainEntityOfPage" not in payload and data.get("@type") not in (
            *WEBPAGE_TYPES,
        ):
            report.warnings.append("JSON-LD sem @graph/mainEntityOfPage")


def validate_page(path: Path) -> PageReport:
    html = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT).as_posix()
    report = PageReport(path=rel)

    if 'role="banner"' not in html:
        report.errors.append("header role=banner ausente")
    if 'id="conteudo"' not in html:
        report.errors.append("main#conteudo ausente")
    if 'role="contentinfo"' not in html:
        report.errors.append("footer role=contentinfo ausente")
    if 'class="skip-link"' not in html:
        report.errors.append("skip-link ausente")

    h1_count = len(re.findall(r"<h1\b", html, re.IGNORECASE))
    if h1_count != 1:
        report.errors.append(f"esperado 1 h1, encontrado {h1_count}")

    if '<div class="page-title-area' in html:
        report.errors.append("page-title-area ainda em div")

    if '<ul class="breadcrumb"' in html:
        report.errors.append("breadcrumb ainda usa ul")

    if 'aria-label="Menu principal"' not in html:
        report.errors.append("menu principal sem aria-label")

    if 'aria-label="Menu mobile"' not in html:
        report.warnings.append("menu mobile sem aria-label")

    if 'aria-controls="mobile-nav"' not in html or 'aria-expanded=' not in html:
        report.errors.append("botão do menu mobile sem aria-controls/aria-expanded")

    if 'aria-label="Institucional"><ul class="quick-links"' not in html:
        report.errors.append("rodapé sem nav Institucional")
    if 'aria-label="Serviços"><ul class="quick-links"' not in html:
        report.errors.append("rodapé sem nav Serviços")

    if '<section class="solution-area' in html and (
        'aria-label="Solicite um orçamento"' not in html
    ):
        report.errors.append("solution-area sem aria-label")

    if is_blog_post(path) and not POST_DATES_PATTERN.search(html):
        report.errors.append("post-dates sem elemento time")

    if is_service_page(path):
        if '<figure class="image"' not in html:
            report.errors.append("serviço sem figure.image no hero")

    if is_blog_listing(path):
        blocks = JSON_LD_PATTERN.findall(html)
        if blocks:
            data = json.loads(blocks[0])
            graph_types = [
                node.get("@type")
                for node in data.get("@graph", [])
                if isinstance(node, dict)
            ]
            if "CollectionPage" not in graph_types:
                report.errors.append("listagem de blog sem CollectionPage no JSON-LD")

    h1_match = H1_PATTERN.search(html)
    h2_match = WRITEN_FIRST_H2.search(html)
    if h1_match and h2_match:
        h1_norm = normalize_heading(h1_match.group(1))
        h2_norm = normalize_heading(h2_match.group(1))
        if h1_norm and h1_norm == h2_norm:
            report.errors.append("h1 e primeiro h2 duplicados no conteúdo")

    if rel == "index.html":
        if '<main id="conteudo" role="main"><h1 class="sr-only">' not in html:
            report.warnings.append("home sem h1 dentro do main")
        for landmark in ("about-titulo", "blog-titulo", "hero-titulo"):
            if landmark not in html:
                report.errors.append(f"home sem landmark {landmark}")
        if '<section class="main-banner-area' not in html:
            report.errors.append("home sem section.main-banner-area")

    if rel == "perguntas-frequentes-sobre-guincho-e-reboque-no-rj/index.html":
        if 'aria-labelledby="faq-titulo"' not in html:
            report.errors.append("FAQ sem aria-labelledby")
        if re.search(
            r'class="faq-guincho-rj"[^>]*>.*?<h2>',
            html,
            re.DOTALL,
        ):
            report.errors.append("FAQ com perguntas ainda em h2")

    if is_service_page(path):
        if '<header class="page-title-area' not in html:
            report.errors.append("serviço sem header.page-title-area")
        if 'aria-label="Trilha de navegação"' not in html:
            report.errors.append("serviço sem nav de breadcrumb")
        if '<article class="col-lg-8' not in html:
            report.errors.append("serviço sem article principal")
        if '<aside aria-label="Serviços relacionados">' not in html:
            report.errors.append("serviço sem aside de sidebar")

    if rel == "index.html":
        if '<main id="conteudo" role="main"><h1 class="sr-only">' not in html:
            report.warnings.append("home sem h1 dentro do main")

    if '<div class="blog-item">' in html:
        report.errors.append("blog-item ainda em div")

    if '<div class="pagination-area">' in html:
        report.errors.append("paginação ainda em div")

    logo_match = re.search(r'class="logo[^"]*"[^>]*alt="([^"]*)"', html)
    if logo_match and logo_match.group(1):
        report.warnings.append("logo com alt descritivo (esperado alt=\"\")")

    validate_seo_urls(html, path, report)
    validate_json_ld(html, report)
    return report


def main() -> None:
    reports = [validate_page(path) for path in iter_html_files()]
    errors = [report for report in reports if report.errors]
    warnings = [report for report in reports if report.warnings]

    print(f"Páginas analisadas: {len(reports)}")
    print(f"Com erro: {len(errors)}")
    print(f"Com aviso: {len(warnings)}")

    if errors:
        print("\nErros:")
        for report in errors[:30]:
            print(f"  {report.path}")
            for item in report.errors:
                print(f"    - {item}")
        if len(errors) > 30:
            print(f"  ... e mais {len(errors) - 30} páginas")

    if warnings and "--strict" not in sys.argv:
        print("\nAvisos (primeiras 10 páginas):")
        for report in warnings[:10]:
            print(f"  {report.path}")
            for item in report.warnings:
                print(f"    - {item}")

    if errors or ("--strict" in sys.argv and warnings):
        sys.exit(1)


if __name__ == "__main__":
    main()
