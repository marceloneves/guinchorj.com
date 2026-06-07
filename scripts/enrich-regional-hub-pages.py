#!/usr/bin/env python3
"""Enriquece os 5 hubs regionais finos com conteúdo localizado e FAQ."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WRITTEN_PATTERN = re.compile(
    r'(<div class="writen_content">)(.*?)(</div>\s*</div>)(?=\s*(?:<nav|<aside|</article|$))',
    re.DOTALL,
)

PHONE_BLOCK = """
<p style="text-align: center;">
<i class="fa fa-phone" aria-hidden="true"></i>
<a href="tel:21959543043" title="Telefone" style="display: inline-block;" rel="nofollow">(21) 95954-3043</a>
| <i class="fa fa-whatsapp" aria-hidden="true"></i>
<a href="https://api.whatsapp.com/send?phone=5521959543043&amp;text=Ol%C3%A1,%20estou%20entrando%20em%20contato%20pelo%20site" title="Whatsapp" rel="nofollow external noopener" target="_blank" style="display: inline-block;">(21) 95954-3043</a>
</p>
""".strip()


def city_list(items: list[tuple[str, str]]) -> str:
    return "\n".join(
        f'<li><a href="../{slug}/" title="{title}">{title}</a></li>'
        for slug, title in items
    )


def faq_block(items: list[tuple[str, str]]) -> str:
    parts = []
    for q, a in items:
        parts.append(f"<h3>{q}</h3><p>{a}</p>")
    return "\n".join(parts)


def official_block(region_label: str) -> str:
    return f"""
<h2>Dados oficiais da Guincho RJ</h2>
<p><strong>Empresa:</strong> Guincho RJ</p>
<p><strong>Atuação:</strong> desde 1995</p>
<p><strong>Região:</strong> {region_label}</p>
<p><strong>Endereço:</strong> Avenida Presidente Vargas, 1120 — Centro, Rio de Janeiro – RJ, CEP 20071-002</p>
<p><strong>E-mail:</strong> <a href="mailto:contato@guinchorj.com">contato@guinchorj.com</a></p>
<p><strong>Telefone/WhatsApp:</strong> <a href="tel:+5521959543043">(21) 95954-3043</a></p>
""".strip()


HUBS: dict[str, str] = {}

# --- Baixada Fluminense ---
HUBS["reboque-baixada-fluminense"] = f"""
<p class="lead" style="text-align:center">Precisa de Reboque na Baixada Fluminense?</p>
{PHONE_BLOCK}
<p>Seu veículo parou na <strong>Rodovia Presidente Dutra (BR-116)</strong>, na <strong>Via Light</strong>, na <strong>BR-493 (Rio-Magé)</strong>, na <strong>BR-465 (Arco Metropolitano)</strong> ou em algum município da <strong>Baixada Fluminense</strong>? A <strong>Guincho RJ</strong> oferece <strong>reboque na Baixada Fluminense</strong> com remoção segura, orientação clara e atendimento conforme rota, distância e disponibilidade operacional.</p>
<p>A Baixada concentra um dos maiores fluxos rodoviários do estado: ligação com o Rio de Janeiro, polos industriais, terminais logísticos, shoppings, hospitais e bairros densamente populosos. Panes na <strong>Dutra</strong>, no entroncamento com a <strong>Linha Vermelha</strong>, em avenidas como a <strong>Ayrton Senna</strong> (Nova Iguaçu) ou na <strong>Washington Luiz</strong> (São João de Meriti) exigem guincho que conheça acessos, retornos e horários de pico.</p>
<p>A <strong>Guincho RJ atua desde 1995</strong> no Rio de Janeiro e Região Metropolitana. Na Baixada, atendemos carros, motos, SUVs, utilitários, picapes e vans — inclusive remoções programadas para oficinas, concessionárias, residências, empresas e pátios.</p>
<h2>1. Por que a Baixada Fluminense exige operação especializada?</h2>
<p>A região combina <strong>rodovias federais de alto fluxo</strong>, vias municipais estreitas, condomínios verticais, áreas industriais e trechos com obras ou interdições frequentes. Um reboque mal posicionado na Dutra ou na Via Light pode agravar congestionamento e aumentar risco para motoristas e equipe.</p>
<p>Por isso, antes da remoção, orientamos o cliente a informar município, km aproximado (se estiver em rodovia), faixa de rolamento, ponto de referência, se há acostamento seguro, se o veículo liga, se há rodas travadas e qual o destino — oficina, residência, pátio ou outra cidade.</p>
<h2>2. Principais vias e corredores atendidos</h2>
<p>O atendimento na Baixada Fluminense costuma ser acionado em:</p>
<ul>
<li><strong>BR-116 (Rodovia Presidente Dutra)</strong> — trechos entre Duque de Caxias, Nova Iguaçu, Seropédica e Japeri;</li>
<li><strong>Via Light</strong> — ligação rápida entre municípios da Baixada e Zona Norte do Rio;</li>
<li><strong>BR-493 (Rio-Magé)</strong> — acesso ao complexo industrial e ligação com Magé;</li>
<li><strong>BR-465 (Arco Metropolitano)</strong> — entroncamentos em Nova Iguaçu e região;</li>
<li><strong>Av. Ayrton Senna</strong>, <strong>Av. Governador Amaral Peixoto</strong>, <strong>Av. Brigadeiro Lima e Silva</strong> e demais corredores urbanos dos municípios atendidos.</li>
</ul>
<h2>3. Cidades atendidas na Baixada Fluminense</h2>
<p>Organizamos a cobertura por município. Acesse a página específica de cada cidade:</p>
<ul>
{city_list([
    ("reboque-em-nova-iguacu-no-rj", "Reboque em Nova Iguaçu 24 horas"),
    ("reboque-em-duque-de-caixas-no-rj", "Reboque em Duque de Caxias no RJ"),
    ("reboque-em-belfort-roxo-no-rj", "Reboque em Belford Roxo 24 horas"),
    ("reboque-em-sao-joao-de-meriti-no-rj", "Reboque em São João de Meriti no RJ"),
    ("reboque-nilopolis", "Reboque em Nilópolis"),
    ("reboque-mesquita", "Reboque em Mesquita"),
    ("reboque-em-queimados", "Reboque em Queimados 24 horas"),
    ("reboque-em-japeri", "Reboque em Japeri"),
    ("reboque-em-paracambi", "Reboque em Paracambi"),
    ("reboque-em-seropedica", "Reboque em Seropédica"),
    ("reboque-guadalupe-rj", "Reboque em Guadalupe no RJ"),
    ("reboque-guadalupe", "Reboque em Guadalupe"),
    ("reboque-dutra-rj", "Reboque na Dutra no RJ"),
])}
</ul>
<h2>4. Situações mais comuns na Baixada</h2>
<p>Entre as ocorrências mais frequentes estão superaquecimento na Dutra em horário de pico, pane seca em filas de pedágio, pneu furado em acostamento estreito, bateria descarregada após parada prolongada, colisão leve em cruzamentos movimentados, veículo que não pega após abastecimento e remoção programada de carros comprados em lojas ou leilões da região.</p>
<p>Em áreas industriais de Duque de Caxias e Seropédica, também atendemos utilitários e vans de serviço conforme avaliação de peso e equipamento necessário.</p>
<h2>5. Tipos de veículos e destinos</h2>
<p>Atendemos carros de passeio, motos, SUVs, picapes, vans e utilitários leves. O transporte pode ser para oficinas mecânicas, concessionárias, residências, empresas, shoppings (com autorização do estacionamento) ou outras regiões — incluindo Rio de Janeiro, Niterói e Zona Oeste — conforme rota combinada no atendimento.</p>
<h2>6. Como solicitar reboque na Baixada Fluminense</h2>
<p>Ligue ou envie WhatsApp para <strong>(21) 95954-3043</strong>. Informe município, endereço ou km da rodovia, marca/modelo do veículo, se está em local seguro, destino desejado e se há alguma restrição de acesso (portaria, garagem, rampa inclinada).</p>
<h2>7. Perguntas frequentes sobre reboque na Baixada Fluminense</h2>
{faq_block([
    ("O guincho atende na Rodovia Dutra 24 horas?", "Sim. A Guincho RJ oferece atendimento 24 horas na Baixada Fluminense, inclusive na Dutra, Via Light e principais avenidas, conforme disponibilidade operacional, localização exata, condições de segurança e tipo de ocorrência."),
    ("Quanto tempo demora o guincho na Baixada?", "O tempo depende do trânsito, horário, ponto exato (rodovia ou via urbana), distância até o veículo e disponibilidade da equipe mais próxima. Em horários de pico na Dutra ou Via Light, a previsão pode ser maior — por isso pedimos referência precisa e, se possível, km da rodovia."),
    ("Vocês removem veículo da Dutra para Nova Iguaçu ou Duque de Caxias?", "Sim. Realizamos remoções entre municípios da Baixada e para outras regiões do Grande Rio, conforme rota, distância, tipo de veículo e orçamento informado antes da confirmação."),
    ("Atendem pane na Via Light e no Arco Metropolitano?", "Sim, conforme avaliação. Informe se o veículo está em faixa de rolamento, acostamento ou área de emergência, e se há condições seguras para a aproximação do guincho."),
    ("Quais formas de pagamento são aceitas?", "As formas de pagamento são informadas no atendimento. Normalmente podem ser combinadas opções como Pix, cartão de débito, cartão de crédito, dinheiro ou outras disponíveis pelo canal oficial da Guincho RJ."),
])}
{official_block("Baixada Fluminense")}
<h2>8. Solicite reboque na Baixada Fluminense</h2>
<p>Se você precisa de <strong>guincho ou reboque na Baixada Fluminense</strong>, fale agora com a Guincho RJ pelo <a href="tel:+5521959543043">(21) 95954-3043</a>. Atendimento com orientação clara, cuidado no transporte e orçamento informado antes da confirmação do serviço.</p>
""".strip()

# --- Costa Verde ---
HUBS["reboque-costa-verde"] = f"""
<p class="lead" style="text-align:center">Precisa de Reboque na Costa Verde?</p>
{PHONE_BLOCK}
<p>Seu veículo parou na <strong>BR-101 (Rio-Santos)</strong>, no <strong>Contorno de Itaguaí</strong>, no acesso à <strong>Ilha Grande (Mangaratiba/Conceição de Jacareí)</strong> ou em cidades como <strong>Angra dos Reis</strong>, <strong>Paraty</strong>, <strong>Mangaratiba</strong> e <strong>Itaguaí</strong>? A <strong>Guincho RJ</strong> oferece <strong>reboque na Costa Verde</strong> com remoção segura em trechos litorâneos, serras de acesso e vias de ligação com o Grande Rio.</p>
<p>A Costa Verde mistura <strong>turismo, portos, marinas, condomínios, trechos de mata atlântica e curvas da Rio-Santos</strong>. Panes no Sistema Costa Verde (Angra), no centro histórico de Paraty, no Porto de Itaguaí ou em Mangaratiba — porta de embarque para a Ilha Grande — pedem guincho que considere acostamento, sinalização, declividade e distância até oficina ou pátio.</p>
<p>Desde <strong>1995</strong>, a Guincho RJ atua no Rio de Janeiro e região com carros, motos, SUVs, utilitários, picapes e vans. Na Costa Verde, também atendemos remoções programadas para hotéis, marinas, condomínios e transporte intermunicipal conforme rota e disponibilidade.</p>
<h2>1. Desafios do reboque na Costa Verde</h2>
<p>A Rio-Santos tem trechos sinuosos, túneis, pontes e áreas com acostamento limitado. Em Paraty, ruas estreitas do centro histórico exigem avaliação de manobra; em Angra, o relevo entre praia e serra pode complicar acesso de plataforma. No Porto de Itaguaí e em Mangaratiba, o fluxo de caminhões e ônibus de turismo aumenta a necessidade de remoção rápida e bem sinalizada.</p>
<p>Antes do deslocamento, pedimos cidade, ponto de referência (hotel, marina, posto, km da BR-101), tipo de veículo, se há chave disponível, se o carro liga e destino — oficina local, Rio de Janeiro ou outro município.</p>
<h2>2. Vias e pontos críticos de atendimento</h2>
<ul>
<li><strong>BR-101 (Rio-Santos)</strong> — trecho Costa Verde entre Itaguaí, Mangaratiba, Angra dos Reis e Paraty;</li>
<li><strong>RJ-149</strong> e acessos ao <strong>Sistema Costa Verde</strong> (Angra dos Reis);</li>
<li><strong>Centro histórico de Paraty</strong> — ruas de paralelepípedo e restrições de circulação;</li>
<li><strong>Porto de Itaguaí</strong> e <strong>Contorno de Itaguaí</strong> — área portuária e industrial;</li>
<li><strong>Conceição de Jacareí / Mangaratiba</strong> — embarque para Ilha Grande e condomínios litorâneos;</li>
<li><strong>BR-493</strong> — ligação Itaguaí com Baixada e Rio de Janeiro.</li>
</ul>
<h2>3. Cidades atendidas na Costa Verde</h2>
<p>Confira as páginas específicas de cada município:</p>
<ul>
{city_list([
    ("reboque-em-angra-dos-reis", "Reboque em Angra dos Reis"),
    ("reboque-em-paraty", "Reboque em Paraty"),
    ("reboque-em-mangaratiba", "Reboque em Mangaratiba"),
    ("reboque-em-itaguai", "Reboque em Itaguaí"),
])}
</ul>
<h2>4. Ocorrências frequentes na região</h2>
<p>Superaquecimento em subidas para Angra, pneu furado em trecho sem acostamento na Rio-Santos, pane seca após fila no ferry ou porto, bateria descarregada em estacionamento de hotel, veículo de turista parado em Paraty no fim de semana e remoção programada de lanchas/jet skis com carreta (conforme avaliação) estão entre os chamados mais comuns.</p>
<h2>5. Transporte intermunicipal e destinos</h2>
<p>Além de oficinas locais, podemos transportar o veículo para o Rio de Janeiro, Baixada Fluminense ou outras regiões conforme distância, tipo de carro e orçamento. Informe sempre o destino final para calcular rota e equipamento adequado.</p>
<h2>6. Como acionar o guincho na Costa Verde</h2>
<p>WhatsApp ou telefone <strong>(21) 95954-3043</strong>. Envie localização, cidade, referência, condição do veículo e se está em rodovia (informe km sentido Angra ou Rio, se souber).</p>
<h2>7. Perguntas frequentes sobre reboque na Costa Verde</h2>
{faq_block([
    ("Vocês atendem pane na BR-101 Rio-Santos?", "Sim. Atendemos ocorrências na BR-101 na Costa Verde, conforme localização, acostamento disponível, condições de segurança e disponibilidade operacional. Informe km aproximado e sentido da via quando possível."),
    ("É possível rebocar carro do centro histórico de Paraty?", "Sim, conforme avaliação de acesso, largura da via, restrições locais e equipamento necessário. Descreva a rua exata e se há moradores ou comércio bloqueando manobra."),
    ("O reboque leva veículo de Angra para o Rio de Janeiro?", "Sim. Fazemos transporte intermunicipal conforme rota, distância, tipo de veículo e orçamento combinado no atendimento."),
    ("Atendem perto do Porto de Itaguaí e da CSN?", "Sim. Atendemos Itaguaí, área portuária e vias de acesso, incluindo Contorno de Itaguaí e BR-493, conforme condições do local e autorização para entrada em áreas restritas quando aplicável."),
    ("Quanto custa o reboque na Costa Verde?", "O valor depende da distância percorrida pelo guincho, tipo de veículo, horário, complexidade do acesso (serra, centro histórico, rodovia) e destino. O orçamento é informado antes da confirmação do serviço."),
])}
{official_block("Costa Verde")}
<h2>8. Solicite reboque na Costa Verde</h2>
<p>Precisa de <strong>guincho ou reboque na Costa Verde</strong>? Fale com a Guincho RJ: <a href="tel:+5521959543043">(21) 95954-3043</a>. Atendimento 24 horas conforme disponibilidade operacional.</p>
""".strip()

# --- Litoral Lagos ---
HUBS["reboque-litoral-lagos"] = f"""
<p class="lead" style="text-align:center">Precisa de Reboque no Litoral Lagos?</p>
{PHONE_BLOCK}
<p>Seu veículo parou na <strong>BR-101</strong>, na <strong>RJ-106 (Região dos Lagos)</strong>, na <strong>RJ-124</strong>, na <strong>RJ-140</strong> ou em municípios como <strong>Cabo Frio</strong>, <strong>Araruama</strong>, <strong>Búzios</strong>, <strong>Arraial do Cabo</strong> e <strong>Saquarema</strong>? A <strong>Guincho RJ</strong> oferece <strong>reboque no Litoral Lagos</strong> com orientação clara em trechos litorâneos, alta temporada e acessos à Região dos Lagos.</p>
<p>O Litoral Lagos combina <strong>turismo de praia, condomínios, marinas, rodovias estaduais e circulação sazonal intensa</strong> — especialmente em feriados e verão. Panes na entrada de Cabo Frio, no acesso a Búzios, em Saquarema na RJ-106 ou em Araruama exigem guincho que conheça desvios, retornos e pontos seguros para carga do veículo.</p>
<p>A Guincho RJ, <strong>desde 1995</strong>, atende carros, motos, SUVs, utilitários e vans no Rio e região. No Litoral Lagos, também fazemos remoções para oficinas, hotéis, pousadas e transporte de retorno ao Rio de Janeiro conforme rota acordada.</p>
<h2>1. Por que o Litoral Lagos precisa de reboque preparado?</h2>
<p>Na alta temporada, vias como a RJ-106 e trechos da BR-101 próximos a Cabo Frio e Búzios ficam congestionadas — aumentando pane por superaquecimento e colisões leves. Em Arraial do Cabo e região dos lagos, vento, maresia e estradas litorâneas exigem cuidado extra na fixação do veículo na plataforma.</p>
<p>Informe se o carro está em condomínio fechado, estacionamento de praia, posto ou acostamento, e se há restrição de horário para entrada de guincho em resorts ou loteamentos.</p>
<h2>2. Principais vias e acessos atendidos</h2>
<ul>
<li><strong>BR-101</strong> — ligação Rio–Região dos Lagos e Norte Fluminense;</li>
<li><strong>RJ-106</strong> — corredor Saquarema, Araruama, Cabo Frio e entroncamentos regionais;</li>
<li><strong>RJ-124</strong> — acesso a Iguaba Grande e municípios do entorno;</li>
<li><strong>RJ-140 / RJ-114</strong> — rotas para Búzios e região da Península;</li>
<li><strong>Av. do Contorno, Av. Assunção</strong> (Cabo Frio) e vias turísticas de alta fluxo sazonal.</li>
</ul>
<h2>3. Cidades atendidas no Litoral Lagos</h2>
<p>Acesse a página de reboque de cada município:</p>
<ul>
{city_list([
    ("reboque-em-cabo-frio", "Reboque em Cabo Frio"),
    ("reboque-em-araruama", "Reboque em Araruama"),
    ("reboque-em-arraial-do-cabo", "Reboque em Arraial do Cabo"),
    ("reboque-em-armacao-dos-buzios", "Reboque em Armação dos Búzios"),
    ("reboque-em-saquarema", "Reboque em Saquarema"),
    ("reboque-em-sao-pedro-da-aldeia", "Reboque em São Pedro da Aldeia"),
    ("reboque-em-iguaba-grande", "Reboque em Iguaba Grande"),
])}
</ul>
<h2>4. Situações comuns no Litoral Lagos</h2>
<p>Pneu furado em estrada para praia, bateria descarregada após estacionamento prolongado em feriado, superaquecimento em fila de entrada de cidade, pane seca longe de posto, veículo de locadora parado em Búzios e remoção programada de carros de veranistas de retorno ao Rio.</p>
<h2>5. Atendimento em alta temporada</h2>
<p>Em janeiro, julho e feriados prolongados, a demanda na Região dos Lagos cresce. Antecipe informações (localização compartilhada, referência visível, destino) para agilizar o despacho. O tempo de chegada varia conforme trânsito e distância da equipe disponível.</p>
<h2>6. Como solicitar reboque no Litoral Lagos</h2>
<p>Contato: <strong>(21) 95954-3043</strong> (telefone e WhatsApp). Informe município, bairro, ponto de referência, tipo de veículo e destino desejado.</p>
<h2>7. Perguntas frequentes sobre reboque no Litoral Lagos</h2>
{faq_block([
    ("O guincho atende Cabo Frio e Búzios no verão?", "Sim. Atendemos a Região dos Lagos o ano todo, inclusive em alta temporada. O prazo de chegada pode variar conforme trânsito, localização e disponibilidade operacional no momento do chamado."),
    ("Vocês levam o carro de Arraial do Cabo para o Rio de Janeiro?", "Sim. Realizamos transporte intermunicipal conforme rota, distância, tipo de veículo e orçamento informado antes da confirmação."),
    ("Atendem pane na RJ-106 e na BR-101?", "Sim, conforme avaliação de segurança no local. Informe km aproximado, sentido da via e se o veículo está em acostamento ou faixa de rolamento."),
    ("Reboque funciona em condomínio ou resort fechado?", "Sim, conforme autorização da portaria e condições de acesso. Avise se há restrição de horário ou limitação de altura/largura na entrada."),
    ("Quais formas de pagamento aceitas?", "Pix, cartão e outras opções são informadas no atendimento, conforme disponibilidade no canal oficial da Guincho RJ."),
])}
{official_block("Litoral Lagos")}
<h2>8. Solicite reboque no Litoral Lagos</h2>
<p>Para <strong>guincho ou reboque no Litoral Lagos</strong>, ligue <a href="tel:+5521959543043">(21) 95954-3043</a>. Atendimento 24 horas conforme disponibilidade operacional na região.</p>
""".strip()

# --- Região Oceânica ---
HUBS["reboque-regiao-oceanica"] = f"""
<p class="lead" style="text-align:center">Precisa de Reboque na Região Oceânica?</p>
{PHONE_BLOCK}
<p>Seu veículo parou na <strong>Ponte Rio-Niterói</strong>, na <strong>BR-101</strong>, na <strong>RJ-106</strong>, na <strong>RJ-104 (Rod. Niterói-Manilha)</strong> ou em municípios como <strong>Niterói</strong>, <strong>São Gonçalo</strong>, <strong>Maricá</strong>, <strong>Itaboraí</strong> e <strong>Magé</strong>? A <strong>Guincho RJ</strong> oferece <strong>reboque na Região Oceânica</strong> com remoção segura em vias litorâneas, avenidas urbanas e acessos à Baía de Guanabara.</p>
<p>A Região Oceânica liga o Rio de Janeiro ao leste fluminense por pontes, rodovias e corredores de alta demanda. Panes no <strong>Centro de Niterói</strong>, no <strong>Alcântara (São Gonçalo)</strong>, em <strong>Maricá (Barra de Maricá)</strong>, no trecho <strong>Manilha–Itaboraí</strong> ou em Magé exigem guincho familiarizado com retornos, obras e fluxo intenso de caminhões e ônibus.</p>
<p>Desde <strong>1995</strong>, a Guincho RJ atende carros, motos, SUVs, utilitários, picapes e vans. Na Região Oceânica, também removemos veículos para oficinas, concessionárias, residências e transporte cruzado com Rio de Janeiro e Baixada conforme rota.</p>
<h2>1. Particularidades do reboque na Região Oceânica</h2>
<p>A proximidade com a <strong>Ponte Rio-Niterói</strong> e a <strong>BR-101</strong> faz com que muitas panes ocorram em vias rápidas com pouco espaço para parada. Em São Gonçalo e Niterói, ruas com comércio intenso e obras de infraestrutura complicam manobra de plataforma. Em Maricá e região das lagunas, vento e areia podem afetar veículos estacionados próximos à orla.</p>
<p>Peça atendimento informando município, bairro, se está em ponte/viaduto (nunca permaneça no carro em local de risco), ponto de referência e destino — Centro do Rio, Baixada, Zona Norte ou oficina local.</p>
<h2>2. Vias e corredores prioritários</h2>
<ul>
<li><strong>Ponte Rio-Niterói</strong> e acessos — ligação Rio–Niterói (atenção às normas de parada e sinalização);</li>
<li><strong>BR-101</strong> — trechos em Niterói, São Gonçalo, Itaboraí e Maricá;</li>
<li><strong>RJ-104 (Niterói–Manilha)</strong> — ligação litorânea e industrial;</li>
<li><strong>Av. Ernani do Amaral Peixoto, Av. Jornalista Rogério Coelho Neto</strong> (Niterói);</li>
<li><strong>Av. Presidente Juscelino, Av. Presidente Kennedy</strong> (São Gonçalo);</li>
<li><strong>RJ-106</strong> — ligação com Região dos Lagos e interior.</li>
</ul>
<h2>3. Cidades atendidas na Região Oceânica</h2>
<p>Confira as páginas por município:</p>
<ul>
{city_list([
    ("reboque-em-niteroi", "Reboque em Niterói"),
    ("reboque-sao-goncalo", "Reboque em São Gonçalo"),
    ("reboque-itaborai", "Reboque em Itaboraí"),
    ("reboque-em-marica", "Reboque em Maricá"),
    ("reboque-em-mage", "Reboque em Magé"),
    ("reboque-em-guapimirim", "Reboque em Guapimirim"),
    ("reboque-em-rio-bonito", "Reboque em Rio Bonito"),
    ("reboque-em-silva-jardim", "Reboque em Silva Jardim"),
])}
</ul>
<h2>4. Ocorrências frequentes</h2>
<p>Pane na fila da ponte, superaquecimento no trânsito de São Gonçalo, pneu furado na BR-101, bateria descarregada em estacionamento de shopping (Plaza, São Gonçalo Shopping), colisão leve em cruzamento de Niterói e remoção programada de veículos de frotas industriais em Itaboraí (Complexo Petroquímico — conforme regras de acesso).</p>
<h2>5. Pontos de apoio operacional</h2>
<p>A Guincho RJ utiliza pontos de apoio estratégicos na região metropolitana — incluindo apoio em <strong>Niterói (Trevo da Alameda São Boaventura / Contorno)</strong> para motos e atendimentos entre Niterói, Centro, Fonseca, Icaraí e Região Oceânica — conforme localização da ocorrência e disponibilidade no momento do chamado.</p>
<h2>6. Como solicitar reboque na Região Oceânica</h2>
<p>Ligue ou WhatsApp <strong>(21) 95954-3043</strong>. Informe município, endereço ou rodovia, referência, condição do veículo e destino final.</p>
<h2>7. Perguntas frequentes sobre reboque na Região Oceânica</h2>
{faq_block([
    ("Vocês atendem pane na Ponte Rio-Niterói?", "Em caso de pane em ponte ou viaduto, priorize segurança e sinalização. Acione a Guincho RJ informando local exato e condição do veículo. O atendimento depende das normas de trânsito, condições de parada e autorização dos órgãos competentes quando necessário."),
    ("Quanto tempo demora o guincho em Niterói ou São Gonçalo?", "Varia conforme trânsito, horário, bairro e distância da equipe disponível. Regiões como Icaraí, Centro de Niterói, Alcântara e Neves têm dinâmicas diferentes — referência precisa acelera o despacho."),
    ("É possível levar o carro de Maricá para o Rio de Janeiro?", "Sim. Transporte intermunicipal conforme rota, distância, tipo de veículo e orçamento combinado no atendimento."),
    ("Atendem Itaboraí e a região da RJ-104?", "Sim. Atendemos Itaboraí, Manilha, Porto do Caçu e vias de ligação, conforme acesso e condições de segurança no local."),
    ("Quais formas de pagamento são aceitas?", "Informadas no atendimento — normalmente Pix, cartão de débito/crédito e outras opções disponíveis oficialmente."),
])}
{official_block("Região Oceânica")}
<h2>8. Solicite reboque na Região Oceânica</h2>
<p>Precisa de <strong>guincho ou reboque na Região Oceânica</strong>? <a href="tel:+5521959543043">(21) 95954-3043</a> — Guincho RJ, atendimento 24 horas conforme disponibilidade operacional.</p>
""".strip()

# --- Região Serrana ---
HUBS["reboque-regiao-serrana"] = f"""
<p class="lead" style="text-align:center">Precisa de Reboque na Região Serrana?</p>
{PHONE_BLOCK}
<p>Seu veículo parou na <strong>BR-040 (Rio–Teresópolis)</strong>, na <strong>BR-495 (Rio–Petrópolis)</strong>, na <strong>RJ-130</strong>, na <strong>RJ-116</strong> ou em cidades como <strong>Petrópolis</strong>, <strong>Teresópolis</strong>, <strong>Nova Friburgo</strong> e <strong>Itatiaia</strong>? A <strong>Guincho RJ</strong> oferece <strong>reboque na Região Serrana</strong> com remoção segura em trechos de serra, curvas, túneis e centros urbanos montanhosos.</p>
<p>A Região Serrana combina <strong>turismo, clima úmido, declives acentuados, neblina e rodovias sinuosas</strong>. Panes na Serra dos Órgãos, na subida para Teresópolis, no Centro Histórico de Petrópolis, em Itaipava ou em Nova Friburgo exigem guincho com experiência em carga em rampa, freio de estacionamento falho e fixação reforçada.</p>
<p>Desde <strong>1995</strong>, a Guincho RJ atende carros, motos, SUVs, utilitários e vans. Na serra, avaliamos peso, tração, estado dos freios e necessidade de patins ou cabo auxiliar conforme a ocorrência.</p>
<h2>1. Desafios do reboque na serra fluminense</h2>
<p>Subidas longas na BR-040 e BR-495 provocam superaquecimento; descidas podem causar fading de freios. Curvas fechadas, túneis e chuva reduzem visibilidade — exigindo sinalização adequada antes da chegada do guincho. Em Petrópolis e Teresópolis, ruas íngremes e garagens com rampa estreita pedem informação prévia sobre altura, largura e se as rodas estão travadas.</p>
<p>Nunca tente descer ou subir serra com veículo em pane mecânica grave ou freios comprometidos. Acione o reboque e informe km da rodovia, sentido e condição do carro.</p>
<h2>2. Rodovias e trechos atendidos</h2>
<ul>
<li><strong>BR-040</strong> — Rio de Janeiro a Teresópolis (Serra dos Órgãos);</li>
<li><strong>BR-495 / BR-040</strong> — acesso Petrópolis, Itaipava e região imperial;</li>
<li><strong>RJ-130</strong> — ligação Teresópolis, Nova Friburgo e cidades do médio paraíba;</li>
<li><strong>RJ-116</strong> — trechos serranos e ligação com interior;</li>
<li><strong>RJ-169</strong> — acesso Itatiaia e região de parque;</li>
<li><strong>Centros de Petrópolis, Teresópolis e Nova Friburgo</strong> — ruas urbanas e áreas turísticas.</li>
</ul>
<h2>3. Cidades atendidas na Região Serrana</h2>
<p>Páginas específicas por município:</p>
<ul>
{city_list([
    ("reboque-em-petropolis", "Reboque em Petrópolis"),
    ("reboque-em-teresopolis", "Reboque em Teresópolis"),
    ("reboque-em-nova-friburgo", "Reboque em Nova Friburgo"),
    ("reboque-em-itatiaia", "Reboque em Itatiaia"),
    ("reboque-em-itaipava", "Reboque em Itaipava"),
])}
</ul>
<h2>4. Situações comuns na Região Serrana</h2>
<p>Superaquecimento na subida da BR-040, pane elétrica em neblina, pneu furado sem acostamento seguro, veículo que escorregou em rampa com freio de mão fraco, bateria descarregada em pousada ou hotel, turista parado em Itaipava no fim de semana e remoção programada de carros antigos em eventos automotivos de Petrópolis.</p>
<h2>5. Segurança em serra e mau tempo</h2>
<p>Com chuva forte, deslizamentos ou interdições, confirme se a via está liberada antes do deslocamento do guincho. Em caso de risco de enchente ou queda de barreira, acione também Defesa Civil e PRF/DETRAN quando aplicável. A Guincho RJ presta reboque, mas não substitui serviços de emergência pública.</p>
<h2>6. Como solicitar reboque na Região Serrana</h2>
<p><strong>(21) 95954-3043</strong> — telefone ou WhatsApp. Informe cidade, rodovia (e km se souber), se o veículo está em declive, se liga/neutraliza e destino (oficina local ou Rio de Janeiro).</p>
<h2>7. Perguntas frequentes sobre reboque na Região Serrana</h2>
{faq_block([
    ("Vocês atendem pane na BR-040 e na serra de Teresópolis?", "Sim, conforme condições de segurança, clima e localização. Informe km, sentido (Rio ou Teresópolis) e se há acostamento seguro para carga do veículo."),
    ("É possível rebocar carro com freio de mão travado em rua íngreme em Petrópolis?", "Sim, conforme avaliação. Informe inclinação da rua, se o veículo está em neutro, se há chave e se a rua permite manobra de plataforma ou patins."),
    ("O guincho leva veículo de Nova Friburgo para o Rio de Janeiro?", "Sim. Transporte intermunicipal conforme rota, distância, tipo de veículo e orçamento informado antes da confirmação."),
    ("Atendem Itaipava e região gastronômica nos finais de semana?", "Sim, conforme disponibilidade operacional. Em datas de pico, antecipe localização e referência para agilizar o atendimento."),
    ("Quanto custa reboque na serra?", "Depende da distância, declividade/acesso, tipo de veículo, horário e destino. Orçamento informado antes da confirmação do serviço."),
])}
{official_block("Região Serrana")}
<h2>8. Solicite reboque na Região Serrana</h2>
<p>Para <strong>guincho ou reboque na Região Serrana</strong>, contate a Guincho RJ: <a href="tel:+5521959543043">(21) 95954-3043</a>. Atendimento 24 horas conforme disponibilidade e condições de via.</p>
""".strip()


def update_hub(slug: str, content: str) -> int:
    path = ROOT / "servico" / slug / "index.html"
    if not path.exists():
        print(f"  SKIP (não encontrado): {slug}")
        return 0
    html = path.read_text(encoding="utf-8")
    match = WRITTEN_PATTERN.search(html)
    if not match:
        print(f"  ERRO: writen_content não encontrado em {slug}")
        return 0
    new_html = WRITTEN_PATTERN.sub(
        rf"\1 {content} \3",
        html,
        count=1,
    )
    if new_html == html:
        print(f"  ERRO: substituição falhou em {slug}")
        return 0
    path.write_text(new_html, encoding="utf-8")
    words = len(re.sub(r"<[^>]+>", " ", content).split())
    print(f"  OK {slug}: ~{words} palavras")
    return words


def main() -> None:
    total = 0
    for slug, content in HUBS.items():
        total += update_hub(slug, content)
    print(f"\n{len(HUBS)} hubs atualizados.")


if __name__ == "__main__":
    main()
