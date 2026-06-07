#!/usr/bin/env python3
"""Audita se links regionais (rodapé, header, sidebar, conteúdo) respeitam os silos."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGIONS_FILE = ROOT / "scripts" / "service-regions.json"
REGIONAL_FILE = ROOT / "scripts" / "regional-services.json"

HREF_PATTERN = re.compile(r'href="([^"]+)"')
FOOTER_BLOCK = re.compile(
    r"<h3>Serviços</h3><ul class=\"quick-links\">(.*?)</ul>",
    re.DOTALL,
)
SIDEBAR_BLOCK = re.compile(
    r'<aside aria-label="Serviços relacionados">(.*?)</aside>',
    re.DOTALL,
)
HEADER_END = re.compile(r"<main\b")
FOOTER_START = re.compile(r"<footer\b")
ARTICLE_BLOCK = re.compile(
    r'<article class="col-lg-(?:8|12)[^"]*">(.*?)</article>',
    re.DOTALL,
)

REGION_LABELS = {
    "rio-geral": "Rio de Janeiro (geral)",
    "zona-sul": "Zona Sul",
    "zona-norte": "Zona Norte",
    "zona-oeste": "Zona Oeste",
    "centro": "Centro",
    "baixada-fluminense": "Baixada Fluminense",
    "regiao-oceanica": "Região Oceânica",
    "regiao-serrana": "Região Serrana",
    "costa-verde": "Costa Verde",
    "litoral-lagos": "Litoral Lagos",
    "tipos-veiculo": "Tipos de veículo",
}


def load_pillars(regions: dict[str, list[str]], regional_hubs: list[str]) -> dict[str, str]:
    hubs = set(regional_hubs)
    pillars: dict[str, str] = {}
    for region, slugs in regions.items():
        if region in {"rio-geral", "tipos-veiculo"}:
            continue
        pillar = next((slug for slug in slugs if slug in hubs), None)
        if pillar:
            pillars[region] = pillar
    return pillars


def count_pillar_links(content: str, pillar_slug: str) -> int:
    return len(re.findall(rf'href="\.\./{re.escape(pillar_slug)}/"', content))


@dataclass
class SectionReport:
    ok: bool = True
    found: set[str] = field(default_factory=set)
    unexpected: set[str] = field(default_factory=set)
    missing_expected: set[str] = field(default_factory=set)
    notes: list[str] = field(default_factory=list)


@dataclass
class PageReport:
    slug: str
    region: str
    footer: SectionReport = field(default_factory=SectionReport)
    header: SectionReport = field(default_factory=SectionReport)
    sidebar: SectionReport = field(default_factory=SectionReport)
    content: SectionReport = field(default_factory=SectionReport)


def load_data() -> tuple[dict[str, list[str]], list[str], dict[str, str], set[str]]:
    regions: dict[str, list[str]] = json.loads(REGIONS_FILE.read_text(encoding="utf-8"))
    regional_hubs: list[str] = json.loads(REGIONAL_FILE.read_text(encoding="utf-8"))
    page_to_region: dict[str, str] = {}
    for region, slugs in regions.items():
        for slug in slugs:
            page_to_region[slug] = region

    all_service_slugs = {
        path.parent.name for path in (ROOT / "servico").glob("*/index.html")
    }
    return regions, regional_hubs, page_to_region, all_service_slugs


def hrefs_from(html: str) -> list[str]:
    return HREF_PATTERN.findall(html)


def service_slugs_from_hrefs(hrefs: list[str], all_slugs: set[str]) -> set[str]:
    found: set[str] = set()
    for href in hrefs:
        href = href.split("#")[0].split("?")[0].strip()
        if not href or href.startswith(("tel:", "mailto:", "javascript:", "http://", "https://")):
            continue

        match = re.search(r"(?:^|/)servico/([^/]+)/?$", href)
        if match and match.group(1) in all_slugs:
            found.add(match.group(1))
            continue

        match = re.match(r"\.\./([^/]+)/?$", href)
        if match and match.group(1) in all_slugs:
            found.add(match.group(1))
            continue

        match = re.search(r"\.\./(?:\.\./)*servico/([^/]+)/?$", href)
        if match and match.group(1) in all_slugs:
            found.add(match.group(1))

    return found


def split_page(html: str) -> tuple[str, str, str]:
    main_match = HEADER_END.search(html)
    footer_match = FOOTER_START.search(html)
    if not main_match or not footer_match:
        return html, "", ""

    header = html[: main_match.start()]
    main = html[main_match.start() : footer_match.start()]
    footer = html[footer_match.start() :]
    return header, main, footer


def expected_sidebar_slugs(
    slug: str,
    region: str,
    regions: dict[str, list[str]],
    regional_hubs: list[str],
) -> set[str]:
    if region == "rio-geral":
        return set(regional_hubs) - {slug}
    return set(regions[region]) - {slug}


def expected_content_slugs(
    slug: str,
    region: str,
    regions: dict[str, list[str]],
) -> set[str] | None:
    """Conteúdo deve linkar apenas serviços da mesma região (exceto tipos-veiculo)."""
    if region == "tipos-veiculo":
        return set(regions[region]) - {slug}
    if region == "rio-geral":
        return None
    return set(regions[region]) - {slug}


def audit_section(
    html: str,
    allowed: set[str] | None,
    *,
    require_exact: set[str] | None = None,
    optional: bool = False,
) -> SectionReport:
    report = SectionReport()
    report.found = service_slugs_from_hrefs(hrefs_from(html), all_slugs_cache)

    if not html.strip():
        if optional:
            report.notes.append("seção ausente")
            return report
        report.ok = False
        report.notes.append("seção ausente")
        return report

    if require_exact is not None:
        report.missing_expected = require_exact - report.found
        report.unexpected = report.found - require_exact
        report.ok = not report.unexpected and not report.missing_expected
        return report

    if allowed is None:
        report.notes.append("sem restrição regional")
        return report

    report.unexpected = report.found - allowed
    report.ok = not report.unexpected
    return report


all_slugs_cache: set[str] = set()


def audit_service_page(
    path: Path,
    regions: dict[str, list[str]],
    regional_hubs: list[str],
    page_to_region: dict[str, str],
    region_pillars: dict[str, str],
) -> PageReport:
    slug = path.parent.name
    region = page_to_region[slug]
    html = path.read_text(encoding="utf-8")
    header, main, footer = split_page(html)

    report = PageReport(slug=slug, region=region)

    footer_match = FOOTER_BLOCK.search(footer)
    footer_html = footer_match.group(1) if footer_match else footer
    report.footer = audit_section(
        footer_html,
        allowed=set(regional_hubs),
        require_exact=set(regional_hubs),
    )

    report.header = audit_section(
        header,
        allowed=set(regional_hubs),
        optional=True,
    )
    if report.header.found - set(regional_hubs):
        report.header.unexpected = report.header.found - set(regional_hubs)
        report.header.ok = False

    sidebar_match = SIDEBAR_BLOCK.search(main)
    sidebar_html = sidebar_match.group(1) if sidebar_match else ""
    sidebar_allowed = expected_sidebar_slugs(slug, region, regions, regional_hubs)
    report.sidebar = audit_section(sidebar_html, allowed=sidebar_allowed, optional=not sidebar_html)

    article_match = ARTICLE_BLOCK.search(main)
    content_html = article_match.group(1) if article_match else main
    content_allowed = expected_content_slugs(slug, region, regions)
    report.content = audit_section(content_html, allowed=content_allowed, optional=True)
    if content_allowed is not None:
        in_region_count = len(report.content.found & content_allowed)
        if in_region_count < 2 and len(content_allowed) >= 2:
            report.content.ok = False
            report.content.notes.append(
                f"conteúdo com {in_region_count} link(s) do cluster (mínimo 2)"
            )

    pillar_slug = region_pillars.get(region)
    if pillar_slug and slug == pillar_slug:
        satellites = set(regions[region]) - {slug}
        satellite_links = report.content.found & satellites
        missing = satellites - satellite_links
        if missing:
            report.content.ok = False
            report.content.notes.append(
                f"pilar sem link a {len(missing)} satélite(s): "
                f"{', '.join(sorted(missing)[:5])}"
                + (f" … +{len(missing) - 5}" if len(missing) > 5 else "")
            )
        elif satellites:
            report.content.notes.append(
                f"pilar com link a todos os {len(satellites)} satélites do cluster"
            )
    elif pillar_slug and slug != pillar_slug:
        pillar_count = count_pillar_links(content_html, pillar_slug)
        if pillar_count < 2:
            report.content.ok = False
            report.content.notes.append(
                f"conteúdo com {pillar_count} link(s) ao pilar {pillar_slug} (mínimo 2)"
            )

    return report


GLOBAL_CONTENT_EXCEPTIONS = frozenset(
    {
        "servicos/index.html",
        "index.html",
    }
)


def audit_non_service_page(
    path: Path,
    regional_hubs: list[str],
) -> PageReport | None:
    html = path.read_text(encoding="utf-8")
    if "<h3>Serviços</h3><ul class=\"quick-links\">" not in html:
        return None

    rel = path.relative_to(ROOT).as_posix()
    header, main, footer = split_page(html)
    report = PageReport(slug=rel, region="(global)")

    footer_match = FOOTER_BLOCK.search(footer)
    footer_html = footer_match.group(1) if footer_match else footer
    report.footer = audit_section(
        footer_html,
        allowed=set(regional_hubs),
        require_exact=set(regional_hubs),
    )

    report.header = audit_section(header, allowed=set(regional_hubs), optional=True)
    if report.header.found - set(regional_hubs):
        report.header.unexpected = report.header.found - set(regional_hubs)
        report.header.ok = False

    if rel in GLOBAL_CONTENT_EXCEPTIONS:
        report.content = SectionReport(
            ok=True,
            notes=["página catálogo/home — conteúdo não restrito por silo"],
        )
    else:
        cards_allowed = set(regional_hubs)
        report.content = audit_section(main, allowed=cards_allowed, optional=True)
        if report.content.found - cards_allowed:
            report.content.unexpected = report.content.found - cards_allowed
            report.content.ok = False

    return report


def summarize_region(
    region: str,
    reports: list[PageReport],
) -> dict[str, object]:
    region_reports = [report for report in reports if report.region == region]
    summary: dict[str, object] = {
        "label": REGION_LABELS.get(region, region),
        "pages": len(region_reports),
        "footer_ok": sum(1 for r in region_reports if r.footer.ok),
        "header_ok": sum(1 for r in region_reports if r.header.ok),
        "sidebar_ok": sum(1 for r in region_reports if r.sidebar.ok),
        "content_ok": sum(1 for r in region_reports if r.content.ok),
        "issues": [],
    }

    for report in region_reports:
        for section_name, section in (
            ("rodapé", report.footer),
            ("header", report.header),
            ("sidebar", report.sidebar),
            ("conteúdo", report.content),
        ):
            if section.ok:
                continue
            detail = {
                "page": report.slug,
                "section": section_name,
                "unexpected": sorted(section.unexpected),
                "missing": sorted(section.missing_expected),
                "notes": section.notes,
            }
            summary["issues"].append(detail)

    return summary


def main() -> None:
    global all_slugs_cache
    regions, regional_hubs, page_to_region, all_slugs_cache = load_data()
    region_pillars = load_pillars(regions, regional_hubs)

    service_reports: list[PageReport] = []
    for path in sorted((ROOT / "servico").glob("*/index.html")):
        service_reports.append(
            audit_service_page(
                path,
                regions,
                regional_hubs,
                page_to_region,
                region_pillars,
            )
        )

    global_reports: list[PageReport] = []
    for path in sorted(ROOT.rglob("index.html")):
        if "wp-content" in path.parts:
            continue
        rel = path.relative_to(ROOT)
        if len(rel.parts) >= 2 and rel.parts[0] == "servico":
            continue
        result = audit_non_service_page(path, regional_hubs)
        if result:
            global_reports.append(result)

    audit_regions = [
        key for key in regions if key not in {"tipos-veiculo", "rio-geral"}
    ] + ["rio-geral", "tipos-veiculo"]

    print("=" * 72)
    print("AUDITORIA DE SILOS REGIONAIS — guinchorj.com")
    print("=" * 72)
    print()
    print("Regras esperadas:")
    print("  • Rodapé (todas as páginas): somente os 10 hubs regionais")
    print("  • Header: sem links para bairros/cidades (ideal: nenhum /servico/ ou só hubs)")
    print("  • Sidebar (páginas /servico/): somente serviços da mesma região")
    print("  • Conteúdo (satélites): mín. 2 links do cluster + 2 ao pilar regional")
    print("  • Conteúdo (pilares): 1 link no conteúdo para cada satélite do cluster")
    print()

    pillar_reports = [
        report
        for report in service_reports
        if report.slug in region_pillars.values()
    ]
    print("=" * 72)
    print("PILARES REGIONAIS — links a satélites no conteúdo")
    print("=" * 72)
    pillar_issues = 0
    for report in sorted(pillar_reports, key=lambda item: item.region):
        satellites_linked = [
            note
            for note in report.content.notes
            if note.startswith("pilar com ")
        ]
        detail = satellites_linked[0] if satellites_linked else "—"
        failed = any(note.startswith("pilar sem link") for note in report.content.notes)
        complete = any(
            note.startswith("pilar com link a todos")
            for note in report.content.notes
        )
        if failed:
            pillar_issues += 1
        status = "OK" if complete and not failed else "FALHA"
        label = REGION_LABELS.get(report.region, report.region)
        detail = next(
            (note for note in report.content.notes if note.startswith("pilar ")),
            "—",
        )
        print(f"  {status} {label} ({report.slug}) — {detail}")
        for note in report.content.notes:
            if note.startswith("pilar sem link"):
                print(f"         {note}")
    print(f"\nPilares auditados: {len(pillar_reports)} | Com problema: {pillar_issues}\n")

    total_issues = pillar_issues
    for region in audit_regions:
        summary = summarize_region(region, service_reports)
        pages = summary["pages"]
        if not pages:
            continue

        issues = summary["issues"]
        total_issues += len(issues)
        status = "OK" if not issues else f"{len(issues)} problema(s)"

        print(f"## {summary['label']} ({pages} páginas) — {status}")
        print(
            f"   Rodapé: {summary['footer_ok']}/{pages} | "
            f"Header: {summary['header_ok']}/{pages} | "
            f"Sidebar: {summary['sidebar_ok']}/{pages} | "
            f"Conteúdo: {summary['content_ok']}/{pages}"
        )

        if issues:
            for issue in issues[:8]:
                print(f"   - {issue['page']} [{issue['section']}]")
                if issue["unexpected"]:
                    print(f"     fora da região: {', '.join(issue['unexpected'][:6])}")
                    if len(issue["unexpected"]) > 6:
                        print(f"     … +{len(issue['unexpected']) - 6} slugs")
                if issue["missing"]:
                    print(f"     faltando: {', '.join(issue['missing'][:6])}")
                for note in issue["notes"]:
                    print(f"     nota: {note}")
            if len(issues) > 8:
                print(f"   … +{len(issues) - 8} problemas nesta região")
        print()

    global_issues = [
        report
        for report in global_reports
        if not (report.footer.ok and report.header.ok and report.content.ok)
    ]
    print(f"## Páginas globais (home, blog, etc.) — {len(global_reports)} com rodapé")
    bad_global = len(global_issues)
    print(f"   Com problemas: {bad_global}")
    for report in global_issues[:10]:
        rel = report.slug
        parts = []
        if not report.footer.ok:
            parts.append(
                f"rodapé (+{sorted(report.footer.unexpected)[:3]} "
                f"-{sorted(report.footer.missing_expected)[:3]})"
            )
        if not report.header.ok:
            parts.append(f"header (+{sorted(report.header.unexpected)[:3]})")
        if not report.content.ok:
            parts.append(f"conteúdo (+{sorted(report.content.unexpected)[:3]})")
        print(f"   - {rel}: {'; '.join(parts)}")
    print()

    print("=" * 72)
    print(f"Total de problemas em /servico/: {total_issues}")
    print(f"Total de problemas em páginas globais: {bad_global}")
    print("=" * 72)

    if total_issues or bad_global:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
