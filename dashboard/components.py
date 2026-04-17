from __future__ import annotations

from collections.abc import Iterable

import streamlit as st


def render_product_header(title: str, subtitle: str) -> None:
    st.markdown(f"<div class='main-title'>{title}</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='sub-title'>{subtitle}</div>", unsafe_allow_html=True)


def render_section_header(title: str, caption: str | None = None) -> None:
    st.markdown(f"<div class='section-title'>{title}</div>", unsafe_allow_html=True)
    if caption:
        st.markdown(f"<div class='section-caption'>{caption}</div>", unsafe_allow_html=True)


def render_metric_cards(metrics: list[tuple[str, str]], cols: int = 4) -> None:
    rows = [metrics[idx : idx + cols] for idx in range(0, len(metrics), cols)]
    for row in rows:
        columns = st.columns(len(row))
        for col, (label, value) in zip(columns, row, strict=False):
            col.markdown(
                (
                    "<div class='metric-card'>"
                    f"<div class='metric-label'>{label}</div>"
                    f"<div class='metric-value'>{value}</div>"
                    "</div>"
                ),
                unsafe_allow_html=True,
            )


def render_badge(text: str, level: str) -> None:
    map_cls = {"saudavel": "badge-ok", "atencao": "badge-warn", "critico": "badge-bad"}
    badge_class = map_cls.get(level.lower(), "badge-warn")
    st.markdown(f"<span class='badge {badge_class}'>{text}</span>", unsafe_allow_html=True)


def render_bullet_summary(lines: Iterable[str]) -> None:
    for line in lines:
        st.write(f"- {line}")


def render_capabilities(capabilities: list[str]) -> None:
    st.markdown("#### Capacidades do Produto")
    joined = "".join([f"<span class='chip'>{item}</span>" for item in capabilities])
    st.markdown(joined, unsafe_allow_html=True)


def render_no_data(message: str) -> None:
    st.info(message)
