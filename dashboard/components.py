from __future__ import annotations

from collections.abc import Iterable

import streamlit as st


def render_product_header(title: str, subtitle: str) -> None:
    st.markdown(
        (
            "<div class='product-header'>"
            f"<div class='main-title'>{title}</div>"
            f"<div class='sub-title'>{subtitle}</div>"
            "<div class='intro-copy'>"
            "Esta central transforma dados operacionais e workflows do Pipefy em uma camada de inteligência para "
            "acompanhar riscos, priorizar demandas e apoiar decisões de melhoria de processos."
            "</div>"
            "<span class='chip'>SLA Monitoring</span>"
            "<span class='chip'>Pipefy Integration</span>"
            "<span class='chip'>Workflow Intelligence</span>"
            "<span class='chip'>Automated Alerts</span>"
            "<span class='chip'>Backlog Analytics</span>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_section_header(title: str, caption: str | None = None) -> None:
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    if caption:
        st.markdown(f"<div class='section-caption'>{caption}</div>", unsafe_allow_html=True)


def render_kpi_card(
    title: str,
    value: str,
    description: str,
    status: str = "neutro",
    delta: str | None = None,
    icon: str | None = None,
) -> str:
    _ = icon  # intentionally ignored for a cleaner executive visual
    delta_html = f"<span class='metric-delta'>{delta}</span>" if delta else ""
    return (
        f"<div class='metric-card status-{status}'>"
        "<div class='metric-top'>"
        f"<div class='metric-label'>{title}</div>"
        f"{delta_html}"
        "</div>"
        f"<div class='metric-value'>{value}</div>"
        f"<div class='metric-description'>{description}</div>"
        "</div>"
    )


def render_kpi_grid(cards: list[dict[str, str]], cols: int = 4) -> None:
    rows = [cards[idx : idx + cols] for idx in range(0, len(cards), cols)]
    for row in rows:
        row_cols = st.columns(len(row))
        for col, card in zip(row_cols, row, strict=False):
            col.markdown(
                render_kpi_card(
                    title=card.get("title", ""),
                    value=card.get("value", ""),
                    description=card.get("description", ""),
                    status=card.get("status", "neutro"),
                    delta=card.get("delta"),
                    icon=card.get("icon"),
                ),
                unsafe_allow_html=True,
            )


def render_metric_cards(metrics: list[tuple[str, str]], cols: int = 4) -> None:
    cards = [
        {
            "title": label,
            "value": value,
            "description": "Indicador operacional monitorado em tempo real.",
            "status": "neutro",
        }
        for label, value in metrics
    ]
    render_kpi_grid(cards, cols=cols)


def render_badge(text: str, level: str) -> None:
    map_cls = {"saudavel": "badge-ok", "atencao": "badge-warn", "critico": "badge-bad", "info": "badge-info"}
    badge_class = map_cls.get(level.lower(), "badge-warn")
    st.markdown(f"<span class='badge {badge_class}'>{text}</span>", unsafe_allow_html=True)


def render_bullet_summary(lines: Iterable[str]) -> None:
    for line in lines:
        st.markdown(f"<div class='insight-item'>• {line}</div>", unsafe_allow_html=True)


def render_story_block(title: str, lines: Iterable[str]) -> None:
    body = "".join([f"<div class='insight-item'>• {line}</div>" for line in lines])
    st.markdown(
        f"<div class='insight-card'><div class='insight-title'>{title}</div>{body}</div>",
        unsafe_allow_html=True,
    )


def render_capabilities(capabilities: list[str]) -> None:
    st.markdown("#### Capacidades do Produto")
    descriptions = {
        "Monitoramento de SLA": "Acompanha conformidade de prazo por demanda e por fase.",
        "Integração com Pipefy": "Conecta workflow operacional à camada analítica executiva.",
        "Detecção de gargalos": "Identifica concentração de volume e atraso em fases críticas.",
        "Priorização automática": "Classifica riscos para orientar fila e capacidade operacional.",
        "Alertas operacionais": "Dispara sinais de SLA, criticidade e ausência de responsável.",
        "Inteligência de backlog": "Mostra distribuição de backlog por prioridade e responsável.",
        "Recomendações executivas": "Gera direcionamentos orientados por dados.",
        "Exportação de alertas": "Permite baixar filas de ação em CSV para operação.",
    }
    cards = ""
    for item in capabilities:
        cards += (
            "<div class='cap-card'>"
            f"<div class='cap-title'>{item}</div>"
            f"<div class='cap-desc'>{descriptions.get(item, 'Capacidade analítica operacional.')}</div>"
            "</div>"
        )
    st.markdown(f"<div class='cap-grid'>{cards}</div>", unsafe_allow_html=True)


def render_no_data(message: str) -> None:
    st.info(message)


def render_health_score_card(
    score: int,
    classification: str,
    explanation: str,
    drivers: list[str],
    recommendation: str,
) -> None:
    fill = max(0, min(100, int(score)))
    drivers_html = "".join([f"<div class='insight-item'>• {driver}</div>" for driver in drivers])
    st.markdown(
        (
            "<div class='health-card'>"
            "<div class='section-title'>Índice de Saúde Operacional</div>"
            f"<div class='health-score'>{fill}</div>"
            f"<div class='health-label'>{classification} • {explanation}</div>"
            f"<div class='health-progress'><div class='health-fill' style='width:{fill}%;'></div></div>"
            f"{drivers_html}"
            f"<div class='insight-item'><strong>Recomendação principal:</strong> {recommendation}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_data_source_status(source: str, status: str, detail: str) -> None:
    st.markdown(
        (
            "<div class='status-panel'>"
            "<div class='status-title'>Fonte de dados</div>"
            f"<div class='status-value'>{source}</div>"
            f"<div class='metric-description'>Status: {status} • {detail}</div>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_product_footer() -> None:
    st.markdown(
        "<div class='product-footer'>Central de Automação e Operações<br>"
        "Python • SQL • Streamlit • Pipefy • Automação • Analytics</div>",
        unsafe_allow_html=True,
    )
