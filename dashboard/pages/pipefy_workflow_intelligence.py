from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Ensure project root is importable when this page is executed directly by Streamlit.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from integrations.pipefy.pipefy_pipeline import run_pipefy_pipeline

REQUIRED_ALERT_COLUMNS = [
    "ticket_id",
    "title",
    "current_phase",
    "priority",
    "assignee",
    "sla_status",
    "risk_level",
    "automation_alert",
    "recommended_action",
    "card_url",
]


def _is_true(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


@st.cache_data(show_spinner=False)
def _load_pipefy_data(force_mock: bool) -> pd.DataFrame:
    return run_pipefy_pipeline(use_mock=force_mock)


def _safe_pct(numerator: int, denominator: int) -> float:
    return (numerator / denominator * 100) if denominator else 0.0


def render_pipefy_workflow_intelligence() -> None:
    st.markdown("## Central de Automação e Operações")
    st.caption(
        "Monitoramento operacional integrado ao Pipefy para acompanhar cards, fases, SLA, backlog, riscos e alertas automatizados."
    )
    st.markdown("### Inteligência Operacional com Pipefy")

    default_mock = _is_true(os.getenv("USE_PIPEFY_MOCK", "true")) or not os.getenv("PIPEFY_TOKEN")
    force_mock = st.sidebar.toggle("Pipefy em modo mock", value=default_mock, key="pipefy_force_mock")
    if st.sidebar.button("Atualizar dados Pipefy", key="refresh_pipefy"):
        _load_pipefy_data.clear()
    df = _load_pipefy_data(force_mock=force_mock)

    if df.empty:
        st.info("Sem dados Pipefy disponíveis.")
        return

    for col in ["created_at", "updated_at", "due_date", "closed_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    phase_filter = st.multiselect("Fase", sorted(df["current_phase"].dropna().astype(str).unique()))
    priority_filter = st.multiselect("Prioridade", sorted(df["priority"].dropna().astype(str).unique()))
    category_filter = st.multiselect("Categoria", sorted(df["category"].dropna().astype(str).unique()))
    assignee_filter = st.multiselect("Responsável", sorted(df["assignee"].dropna().astype(str).unique()))
    sla_filter = st.multiselect("SLA", sorted(df["sla_status"].dropna().astype(str).unique()))
    risk_filter = st.multiselect("Risco", sorted(df["risk_level"].dropna().astype(str).unique()))

    filtered = df.copy()
    if phase_filter:
        filtered = filtered[filtered["current_phase"].isin(phase_filter)]
    if priority_filter:
        filtered = filtered[filtered["priority"].isin(priority_filter)]
    if category_filter:
        filtered = filtered[filtered["category"].isin(category_filter)]
    if assignee_filter:
        filtered = filtered[filtered["assignee"].isin(assignee_filter)]
    if sla_filter:
        filtered = filtered[filtered["sla_status"].isin(sla_filter)]
    if risk_filter:
        filtered = filtered[filtered["risk_level"].isin(risk_filter)]

    if filtered.empty:
        st.warning("Os filtros retornaram zero cards.")
        return

    open_mask = filtered["status"].eq("open")
    overdue_mask = filtered["sla_status"].eq("SLA vencido")
    risk_mask = filtered["sla_status"].eq("SLA em risco")
    unassigned_mask = filtered["assignee"].eq("Unassigned")
    critical_mask = filtered["priority"].isin(["Crítica", "Critica"])
    avg_days = float(filtered["days_open"].mean()) if filtered["days_open"].notna().any() else 0.0
    in_sla = int(filtered["sla_status"].eq("Dentro do SLA").sum())
    sla_pct = _safe_pct(in_sla, len(filtered))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de cards", f"{len(filtered)}")
    c2.metric("Cards abertos", f"{int(open_mask.sum())}")
    c3.metric("Cards vencidos", f"{int(overdue_mask.sum())}")
    c4.metric("Cards em risco de SLA", f"{int(risk_mask.sum())}")

    c5, c6, c7, c8 = st.columns(4)
    c5.metric("Cards sem responsável", f"{int(unassigned_mask.sum())}")
    c6.metric("Cards críticos", f"{int(critical_mask.sum())}")
    c7.metric("Tempo médio em aberto", f"{avg_days:.1f} dias")
    c8.metric("% dentro do SLA", f"{sla_pct:.1f}%")

    g1, g2 = st.columns(2)
    g1.plotly_chart(
        px.bar(
            filtered["current_phase"].value_counts().rename_axis("fase").reset_index(name="volume"),
            x="fase",
            y="volume",
            title="Cards por fase",
        ),
        width="stretch",
    )
    g2.plotly_chart(
        px.bar(
            filtered["priority"].value_counts().rename_axis("priority").reset_index(name="volume"),
            x="priority",
            y="volume",
            title="Cards por prioridade",
        ),
        width="stretch",
    )

    g3, g4 = st.columns(2)
    g3.plotly_chart(
        px.bar(
            filtered["category"].value_counts().rename_axis("category").reset_index(name="volume"),
            x="category",
            y="volume",
            title="Cards por categoria",
        ),
        width="stretch",
    )
    sla_by_phase = (
        filtered.groupby(["current_phase", "sla_status"], as_index=False)["ticket_id"]
        .count()
        .rename(columns={"ticket_id": "volume"})
    )
    g4.plotly_chart(
        px.bar(
            sla_by_phase,
            x="current_phase",
            y="volume",
            color="sla_status",
            barmode="group",
            title="SLA por fase",
        ),
        width="stretch",
    )

    g5, g6 = st.columns(2)
    g5.plotly_chart(
        px.bar(
            filtered["assignee"].value_counts().rename_axis("assignee").reset_index(name="volume"),
            x="assignee",
            y="volume",
            title="Backlog por responsável",
        ),
        width="stretch",
    )
    temporal = (
        filtered.dropna(subset=["created_at"])
        .assign(data=lambda d: d["created_at"].dt.date)
        .groupby("data", as_index=False)["ticket_id"]
        .count()
        .rename(columns={"ticket_id": "volume"})
    )
    g6.plotly_chart(
        px.line(temporal, x="data", y="volume", markers=True, title="Evolução temporal dos cards"),
        width="stretch",
    )

    heatmap_data = (
        filtered.groupby(["current_phase", "priority"], as_index=False)["ticket_id"]
        .count()
        .rename(columns={"ticket_id": "volume"})
    )
    st.plotly_chart(
        px.density_heatmap(
            heatmap_data,
            x="current_phase",
            y="priority",
            z="volume",
            histfunc="sum",
            title="Heatmap fase x prioridade",
        ),
        width="stretch",
    )

    st.markdown("### Alertas operacionais")
    present_cols = [col for col in REQUIRED_ALERT_COLUMNS if col in filtered.columns]
    alerts = filtered[present_cols].copy()
    st.dataframe(alerts, width="stretch")
    st.download_button(
        "Exportar alertas em CSV",
        data=alerts.to_csv(index=False).encode("utf-8"),
        file_name="pipefy_alerts.csv",
        mime="text/csv",
    )

    phase_peak = filtered["current_phase"].value_counts().idxmax()
    highest_risk = filtered["risk_level"].value_counts().idxmax()
    top_action = filtered["recommended_action"].value_counts().idxmax()
    st.markdown("### Insights executivos")
    st.write(f"- A fase com maior concentração de cards é **{phase_peak}**.")
    st.write(f"- O maior risco operacional atual está em **{highest_risk}**.")
    st.write(f"- Existem **{int(unassigned_mask.sum())}** cards sem responsável.")
    st.write(f"- Existem **{int(overdue_mask.sum())}** cards com SLA vencido.")
    st.write(f"- A principal recomendação é **{top_action}**.")


if __name__ == "__main__":
    st.set_page_config(page_title="Central de Automação e Operações", layout="wide")
    render_pipefy_workflow_intelligence()
