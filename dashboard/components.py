from __future__ import annotations

from collections.abc import Iterable

import streamlit as st


def _html_escape(value: object) -> str:
    text = "" if value is None else str(value)
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def render_product_header(title: str, subtitle: str, show_intro: bool = True) -> None:
    st.markdown(
        (
            "<div class='product-header'>"
            f"<h1 class='main-title'>{_html_escape(title)}</h1>"
            f"<p class='sub-title'>{_html_escape(subtitle)}</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    if show_intro:
        st.markdown(
            "<p class='hero-copy'>"
            "Esta central transforma dados operacionais e workflows do Pipefy em uma camada de inteligência "
            "para acompanhar riscos, priorizar demandas e apoiar decisões de melhoria de processos."
            "</p>",
            unsafe_allow_html=True,
        )
        render_badge_row(
            [
                "SLA Monitoring",
                "Pipefy Integration",
                "Workflow Intelligence",
                "Automated Alerts",
                "Backlog Analytics",
            ]
        )


def render_section_header(title: str, caption: str | None = None) -> None:
    st.markdown(f"<div class='section-title'>{_html_escape(title)}</div>", unsafe_allow_html=True)
    if caption:
        st.markdown(f"<div class='section-caption'>{_html_escape(caption)}</div>", unsafe_allow_html=True)


def render_kpi_card(
    title: str,
    value: str,
    description: str,
    status: str | None = None,
    delta: str | None = None,
    icon: str | None = None,
) -> None:
    class_map = {
        "saudavel": "kpi-saude",
        "atencao": "kpi-atencao",
        "critico": "kpi-critico",
        "neutro": "kpi-neutro",
        None: "kpi-neutro",
    }
    css_class = class_map.get((status or "neutro").lower(), "kpi-neutro")
    icon_html = f"{_html_escape(icon)} " if icon else ""
    delta_html = f"<div class='kpi-delta'>{_html_escape(delta)}</div>" if delta else ""
    st.markdown(
        (
            f"<div class='kpi-card {css_class}'>"
            f"<div class='kpi-title'>{icon_html}{_html_escape(title)}</div>"
            f"<div class='kpi-value'>{_html_escape(value)}</div>"
            f"<div class='kpi-desc'>{_html_escape(description)}</div>"
            f"{delta_html}"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_kpi_cards(cards: list[dict[str, str | None]], cols: int = 4) -> None:
    rows = [cards[idx : idx + cols] for idx in range(0, len(cards), cols)]
    for row in rows:
        columns = st.columns(len(row))
        for col, card in zip(columns, row, strict=False):
            with col:
                render_kpi_card(
                    title=str(card.get("title", "-")),
                    value=str(card.get("value", "-")),
                    description=str(card.get("description", "")),
                    status=card.get("status"),
                    delta=card.get("delta"),
                    icon=card.get("icon"),
                )


def render_metric_cards(metrics: list[tuple[str, str]], cols: int = 4) -> None:
    cards = [{"title": label, "value": value, "description": ""} for label, value in metrics]
    render_kpi_cards(cards, cols=cols)


def render_badge(text: str, level: str) -> None:
    map_cls = {
        "saudavel": "badge-ok",
        "atencao": "badge-warn",
        "critico": "badge-bad",
        "neutro": "badge-neutral",
    }
    badge_class = map_cls.get(level.lower(), "badge-neutral")
    st.markdown(f"<span class='badge {badge_class}'>{_html_escape(text)}</span>", unsafe_allow_html=True)


def render_badge_row(labels: list[str]) -> None:
    chips = "".join([f"<span class='chip'>{_html_escape(item)}</span>" for item in labels])
    st.markdown(chips, unsafe_allow_html=True)


def render_bullet_summary(lines: Iterable[str]) -> None:
    for line in lines:
        st.markdown(
            (
                "<div class='insight-card'>"
                "<h4 class='insight-title'>Insight</h4>"
                f"<p class='insight-text'>{_html_escape(line)}</p>"
                "</div>"
            ),
            unsafe_allow_html=True,
        )


def render_story_section(title: str, lines: Iterable[str]) -> None:
    render_section_header(title)
    render_bullet_summary(lines)


def render_capabilities(capabilities: list[str]) -> None:
    st.markdown("#### Capacidades do Produto")
    joined = "".join([f"<span class='chip'>{_html_escape(item)}</span>" for item in capabilities])
    st.markdown(joined, unsafe_allow_html=True)


def render_health_score(score: float, classification: str, factors: list[str], recommendation: str) -> None:
    clipped = max(0.0, min(100.0, float(score)))
    st.markdown("<div class='health-card'>", unsafe_allow_html=True)
    st.markdown(f"<p class='health-score'>{clipped:.1f}</p>", unsafe_allow_html=True)
    st.markdown(
        f"<p class='health-label'>Índice de Saúde Operacional: {_html_escape(classification)}</p>",
        unsafe_allow_html=True,
    )
    st.progress(clipped / 100.0)
    if factors:
        st.caption("Fatores de impacto")
        for factor in factors:
            st.write(f"- {factor}")
    st.caption(f"Recomendação principal: {recommendation}")
    st.markdown("</div>", unsafe_allow_html=True)


def render_data_source_status(source: str, status: str, details: list[str] | None = None) -> None:
    st.markdown(
        (
            "<div class='data-source'>"
            "<div class='data-source-title'>Fonte de dados</div>"
            f"<p class='data-source-line'>Fonte: {_html_escape(source)}</p>"
            f"<p class='data-source-line'>Status: {_html_escape(status)}</p>"
            "</div>"
        ),
        unsafe_allow_html=True,
    )
    if details:
        for line in details:
            st.caption(line)


def render_footer() -> None:
    st.markdown(
        (
            "<div class='footer-block'>"
            "Central de Automação e Operações<br/>"
            "Python • SQL • Streamlit • Pipefy • Automação • Analytics"
            "</div>"
        ),
        unsafe_allow_html=True,
    )


def render_no_data(message: str) -> None:
    st.info(message)
