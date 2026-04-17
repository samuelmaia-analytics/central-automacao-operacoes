from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd
import streamlit as st

FILTER_STATE_KEYS = {
    "date_range": "flt_date_range",
    "status": "flt_status",
    "priority": "flt_priority",
    "category": "flt_category",
    "sla": "flt_sla",
    "severity": "flt_severity",
    "client": "flt_client",
}


@dataclass(frozen=True)
class FilterState:
    date_range: tuple[date, date] | None
    status: list[str]
    priority: list[str]
    category: list[str]
    sla: list[str]
    severity: list[str]
    client: list[str]


def _options(df: pd.DataFrame, col: str) -> list[str]:
    if col not in df.columns:
        return []
    return sorted(df[col].dropna().astype(str).unique().tolist())


def render_global_filters(df: pd.DataFrame) -> FilterState:
    st.sidebar.markdown("### Filtros Globais")
    date_range: tuple[date, date] | None = None
    if "first_response_time" in df.columns and df["first_response_time"].notna().any():
        min_dt = df["first_response_time"].min().date()
        max_dt = df["first_response_time"].max().date()
        picked = st.sidebar.date_input(
            "Período",
            value=(min_dt, max_dt),
            min_value=min_dt,
            max_value=max_dt,
            key=FILTER_STATE_KEYS["date_range"],
        )
        if isinstance(picked, tuple) and len(picked) == 2:
            date_range = picked

    status = st.sidebar.multiselect(
        "Status",
        _options(df, "ticket_status"),
        key=FILTER_STATE_KEYS["status"],
    )
    priority = st.sidebar.multiselect(
        "Prioridade",
        _options(df, "ticket_priority"),
        key=FILTER_STATE_KEYS["priority"],
    )
    category = st.sidebar.multiselect(
        "Categoria",
        _options(df, "categoria_operacional"),
        key=FILTER_STATE_KEYS["category"],
    )
    sla = st.sidebar.multiselect("SLA", _options(df, "status_sla"), key=FILTER_STATE_KEYS["sla"])
    severity = st.sidebar.multiselect(
        "Severidade",
        _options(df, "severidade"),
        key=FILTER_STATE_KEYS["severity"],
    )

    client_opt: list[str] = []
    if "customer_email" in df.columns:
        client_opt.extend(_options(df, "customer_email"))
    if "customer_name" in df.columns:
        client_opt.extend(_options(df, "customer_name"))
    client = st.sidebar.multiselect("Cliente", sorted(set(client_opt)), key=FILTER_STATE_KEYS["client"])

    return FilterState(date_range, status, priority, category, sla, severity, client)


def clear_global_filters() -> None:
    for key in FILTER_STATE_KEYS.values():
        if key in st.session_state:
            del st.session_state[key]


def apply_global_filters(df: pd.DataFrame, state: FilterState) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if state.date_range and "first_response_time" in out.columns:
        start, end = state.date_range
        out = out[out["first_response_time"].dt.date.between(start, end)]
    if state.status and "ticket_status" in out.columns:
        out = out[out["ticket_status"].astype(str).isin(state.status)]
    if state.priority and "ticket_priority" in out.columns:
        out = out[out["ticket_priority"].astype(str).isin(state.priority)]
    if state.category and "categoria_operacional" in out.columns:
        out = out[out["categoria_operacional"].astype(str).isin(state.category)]
    if state.sla and "status_sla" in out.columns:
        out = out[out["status_sla"].astype(str).isin(state.sla)]
    if state.severity and "severidade" in out.columns:
        out = out[out["severidade"].astype(str).isin(state.severity)]
    if state.client:
        m = pd.Series(False, index=out.index)
        if "customer_email" in out.columns:
            m = m | out["customer_email"].astype(str).isin(state.client)
        if "customer_name" in out.columns:
            m = m | out["customer_name"].astype(str).isin(state.client)
        out = out[m]
    return out
