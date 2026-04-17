from __future__ import annotations

from datetime import date

import pandas as pd
import streamlit as st

FILTER_STATE_KEYS = {
    "date_range": "flt_date_range",
    "status": "flt_status",
    "priority": "flt_priority",
    "category": "flt_category",
    "phase": "flt_phase",
    "assignee": "flt_assignee",
    "sla": "flt_sla",
    "risk": "flt_risk",
    "severity": "flt_severity",
    "client": "flt_client",
}


def _reset_version() -> int:
    return int(st.session_state.get("_flt_reset_version", 0))


def _key(name: str) -> str:
    return f"{FILTER_STATE_KEYS[name]}_{_reset_version()}"


class FilterState:
    def __init__(
        self,
        date_range: tuple[date, date] | None,
        status: list[str],
        priority: list[str],
        category: list[str],
        phase: list[str],
        assignee: list[str],
        sla: list[str],
        risk: list[str],
        severity: list[str],
        client: list[str],
    ) -> None:
        self.date_range = date_range
        self.status = status
        self.priority = priority
        self.category = category
        self.phase = phase
        self.assignee = assignee
        self.sla = sla
        self.risk = risk
        self.severity = severity
        self.client = client


def _options(df: pd.DataFrame, col: str) -> list[str]:
    if col not in df.columns:
        return []
    return sorted(df[col].dropna().astype(str).unique().tolist())


def _safe_multiselect(label: str, options: list[str], key: str) -> list[str]:
    if not options:
        st.sidebar.write(f"{label}: sem opções disponíveis no recorte atual.")
        return []
    return st.sidebar.multiselect(
        label,
        options,
        default=[],
        placeholder="Selecione",
        key=key,
    )


def render_global_filters(df: pd.DataFrame) -> FilterState:
    st.sidebar.markdown("### Filtros Globais")
    date_range: tuple[date, date] | None = None
    date_col = ""
    for candidate in ["first_response_time", "created_at", "updated_at"]:
        if candidate in df.columns and df[candidate].notna().any():
            date_col = candidate
            break
    if date_col:
        min_dt = df[date_col].min().date()
        max_dt = df[date_col].max().date()
        picked = st.sidebar.date_input(
            "Período",
            value=(min_dt, max_dt),
            min_value=min_dt,
            max_value=max_dt,
            key=_key("date_range"),
        )
        if isinstance(picked, tuple) and len(picked) == 2:
            date_range = picked

    status = _safe_multiselect("Status", _options(df, "ticket_status"), _key("status"))
    priority = _safe_multiselect("Prioridade", _options(df, "ticket_priority"), _key("priority"))
    category = _safe_multiselect(
        "Categoria",
        sorted(set(_options(df, "categoria_operacional") + _options(df, "category"))),
        _key("category"),
    )
    phase = _safe_multiselect("Fase", _options(df, "current_phase"), _key("phase"))
    assignee = _safe_multiselect("Responsável", _options(df, "assignee"), _key("assignee"))
    sla = _safe_multiselect(
        "SLA",
        sorted(set(_options(df, "status_sla") + _options(df, "sla_status"))),
        _key("sla"),
    )
    risk = _safe_multiselect(
        "Risco",
        sorted(set(_options(df, "risco_atraso") + _options(df, "risk_level"))),
        _key("risk"),
    )
    severity = _safe_multiselect("Severidade", _options(df, "severidade"), _key("severity"))

    client_opt: list[str] = []
    if "customer_email" in df.columns:
        client_opt.extend(_options(df, "customer_email"))
    if "customer_name" in df.columns:
        client_opt.extend(_options(df, "customer_name"))
    client = _safe_multiselect("Cliente", sorted(set(client_opt)), _key("client"))

    return FilterState(date_range, status, priority, category, phase, assignee, sla, risk, severity, client)


def clear_global_filters() -> None:
    st.session_state["_flt_reset_version"] = _reset_version() + 1
    prefixes = list(FILTER_STATE_KEYS.values())
    for state_key in list(st.session_state.keys()):
        if any(state_key == prefix or state_key.startswith(f"{prefix}_") for prefix in prefixes):
            del st.session_state[state_key]


def apply_global_filters(df: pd.DataFrame, state: FilterState) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if state.date_range:
        start, end = state.date_range
        for candidate in ["first_response_time", "created_at", "updated_at"]:
            if candidate in out.columns:
                out = out[out[candidate].dt.date.between(start, end)]
                break
    if state.status and "ticket_status" in out.columns:
        out = out[out["ticket_status"].astype(str).isin(state.status)]
    if state.priority and "ticket_priority" in out.columns:
        out = out[out["ticket_priority"].astype(str).isin(state.priority)]
    if state.category and "categoria_operacional" in out.columns:
        out = out[out["categoria_operacional"].astype(str).isin(state.category)]
    elif state.category and "category" in out.columns:
        out = out[out["category"].astype(str).isin(state.category)]
    if state.phase and "current_phase" in out.columns:
        out = out[out["current_phase"].astype(str).isin(state.phase)]
    if state.assignee and "assignee" in out.columns:
        out = out[out["assignee"].astype(str).isin(state.assignee)]
    if state.sla and "status_sla" in out.columns:
        out = out[out["status_sla"].astype(str).isin(state.sla)]
    elif state.sla and "sla_status" in out.columns:
        out = out[out["sla_status"].astype(str).isin(state.sla)]
    if state.risk and "risco_atraso" in out.columns:
        out = out[out["risco_atraso"].astype(str).isin(state.risk)]
    elif state.risk and "risk_level" in out.columns:
        out = out[out["risk_level"].astype(str).isin(state.risk)]
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
