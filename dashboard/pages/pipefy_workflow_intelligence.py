from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PAGES_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PAGES_ROOT) not in sys.path:
    sys.path.insert(0, str(PAGES_ROOT))
try:
    from dashboard.charts import (
        pipefy_cards_by_phase,
        pipefy_cards_by_priority,
        pipefy_phase_priority_heatmap,
        pipefy_sla_by_phase,
    )
    from dashboard.components import (
        render_data_source_status,
        render_kpi_cards,
        render_no_data,
        render_section_header,
        render_story_section,
    )
    try:
        from dashboard.components import render_executive_mermaid
    except ImportError:
        def render_executive_mermaid(title: str, definition: str, height: int = 260) -> None:
            st.markdown(f"#### {title}")
            st.code(definition, language="mermaid")

    from dashboard.insights import executive_story_lines
    from integrations.pipefy.pipefy_pipeline import run_pipefy_pipeline
except Exception:
    from charts import (
        pipefy_cards_by_phase,
        pipefy_cards_by_priority,
        pipefy_phase_priority_heatmap,
        pipefy_sla_by_phase,
    )
    from components import (
        render_data_source_status,
        render_kpi_cards,
        render_no_data,
        render_section_header,
        render_story_section,
    )
    try:
        from components import render_executive_mermaid
    except ImportError:
        def render_executive_mermaid(title: str, definition: str, height: int = 260) -> None:
            st.markdown(f"#### {title}")
            st.code(definition, language="mermaid")

    from insights import executive_story_lines

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

EXECUTIVE_PIPEFY_FLOW = """
flowchart LR
    A[Pipefy API] --> B[Normalizacao de Dados]
    B --> C[Calculo de SLA e Risco]
    C --> D[Alertas Priorizados]
    D --> E[Backlog Executivo]
    E --> F[Acao Operacional]
    F --> G[Indicadores de Performance]
"""


def _is_true(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


@st.cache_data(show_spinner=False)
def _load_pipefy_data(force_mock: bool, pipe_id: str | None = None) -> pd.DataFrame:
    return run_pipefy_pipeline(pipe_id=pipe_id, use_mock=force_mock)


def _safe_pct(numerator: int, denominator: int) -> float:
    return (numerator / denominator * 100.0) if denominator else 0.0


def _render_pipefy_filters(df: pd.DataFrame) -> pd.DataFrame:
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        phase_filter = st.multiselect("Fase", sorted(df["current_phase"].dropna().astype(str).unique()))
    with f2:
        priority_filter = st.multiselect("Prioridade", sorted(df["priority"].dropna().astype(str).unique()))
    with f3:
        category_filter = st.multiselect("Categoria", sorted(df["category"].dropna().astype(str).unique()))
    with f4:
        assignee_filter = st.multiselect("Responsável", sorted(df["assignee"].dropna().astype(str).unique()))
    f5, f6, f7 = st.columns(3)
    with f5:
        sla_filter = st.multiselect("SLA", sorted(df["sla_status"].dropna().astype(str).unique()))
    with f6:
        risk_filter = st.multiselect("Risco", sorted(df["risk_level"].dropna().astype(str).unique()))
    with f7:
        status_filter = st.multiselect("Status", sorted(df["status"].dropna().astype(str).unique()))

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
    if status_filter:
        filtered = filtered[filtered["status"].isin(status_filter)]
    return filtered


def render_pipefy_workflow_intelligence(show_page_intro: bool = False) -> None:
    if show_page_intro:
        st.markdown("## Central de Automação e Operações")
        st.caption(
            "Monitoramento operacional integrado ao Pipefy para acompanhar cards, fases, "
            "SLA, backlog, riscos e alertas."
        )
    render_section_header("Inteligência Operacional com Pipefy")
    render_executive_mermaid(
        title="Fluxo Executivo de Monitoramento",
        definition=EXECUTIVE_PIPEFY_FLOW,
    )

    token_exists = bool(os.getenv("PIPEFY_TOKEN", "").strip())
    default_mock = _is_true(os.getenv("USE_PIPEFY_MOCK", "true")) or not token_exists
    force_mock = st.sidebar.toggle("Pipefy em modo demonstração", value=default_mock, key="pipefy_force_mock")
    pipe_id = os.getenv("PIPEFY_PIPE_ID", "").strip() or None
    if st.sidebar.button("Atualizar dados Pipefy", key="refresh_pipefy"):
        _load_pipefy_data.clear()
    df = _load_pipefy_data(force_mock=force_mock, pipe_id=pipe_id)

    source = "Modo demonstração" if force_mock else "Pipefy API"
    status = "Dados simulados para portfólio" if force_mock else "Conectado"
    render_data_source_status(
        source=source,
        status=status,
        details=[
            f"Última atualização: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Cards carregados: {len(df)}",
            f"Pipe analisado: {pipe_id or 'Não informado'}",
        ],
    )

    if df.empty:
        render_no_data(
            "Sem dados Pipefy disponíveis no momento. Ative modo demonstração ou valide PIPEFY_TOKEN/PIPEFY_PIPE_ID."
        )
        return

    for col in ["created_at", "updated_at", "due_date", "closed_at"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    filtered = _render_pipefy_filters(df)
    if filtered.empty:
        render_no_data("Nenhum card corresponde aos filtros selecionados.")
        return

    open_mask = filtered["status"].eq("open")
    overdue_mask = filtered["sla_status"].eq("SLA vencido")
    risk_mask = filtered["sla_status"].eq("SLA em risco")
    unassigned_mask = filtered["assignee"].eq("Unassigned")
    critical_mask = filtered["priority"].isin(["Crítica", "Critica"])
    avg_days = float(filtered["days_open"].mean()) if filtered["days_open"].notna().any() else 0.0
    in_sla = int(filtered["sla_status"].eq("Dentro do SLA").sum())
    sla_pct = _safe_pct(in_sla, len(filtered))

    cards = [
        {
            "title": "Total de cards",
            "value": f"{len(filtered)}",
            "description": "Volume monitorado no workflow Pipefy.",
            "status": "neutro",
            "icon": "📌",
        },
        {
            "title": "Cards abertos",
            "value": f"{int(open_mask.sum())}",
            "description": "Cards em progresso no fluxo.",
            "status": "atencao" if open_mask.sum() else "saudavel",
            "icon": "📂",
        },
        {
            "title": "Cards vencidos",
            "value": f"{int(overdue_mask.sum())}",
            "description": "Cards com SLA vencido.",
            "status": "critico" if overdue_mask.sum() else "saudavel",
            "icon": "⚠️",
        },
        {
            "title": "Cards em risco SLA",
            "value": f"{int(risk_mask.sum())}",
            "description": "Cards próximos do vencimento de prazo.",
            "status": "atencao" if risk_mask.sum() else "saudavel",
            "icon": "⏱️",
        },
        {
            "title": "Cards sem responsável",
            "value": f"{int(unassigned_mask.sum())}",
            "description": "Demandas sem owner definido.",
            "status": "atencao" if unassigned_mask.sum() else "saudavel",
            "icon": "👥",
        },
        {
            "title": "Cards críticos",
            "value": f"{int(critical_mask.sum())}",
            "description": "Demandas com prioridade crítica.",
            "status": "critico" if critical_mask.sum() else "neutro",
            "icon": "🚨",
        },
        {
            "title": "Tempo médio em aberto",
            "value": f"{avg_days:.1f} dias",
            "description": "Idade média das demandas ativas.",
            "status": "neutro",
            "icon": "🕒",
        },
        {
            "title": "Percentual dentro do SLA",
            "value": f"{sla_pct:.1f}%",
            "description": "Conformidade do fluxo com prazo operacional.",
            "status": "saudavel" if sla_pct >= 85 else "atencao",
            "icon": "✅",
        },
    ]
    render_kpi_cards(cards, cols=4)

    c1, c2 = st.columns(2)
    with c1:
        st.caption("Este gráfico mostra onde o backlog está mais concentrado no workflow.")
        st.plotly_chart(pipefy_cards_by_phase(filtered), width="stretch")
    with c2:
        st.caption("Este gráfico mostra a distribuição de prioridade para orientar triagem.")
        st.plotly_chart(pipefy_cards_by_priority(filtered), width="stretch")

    c3, c4 = st.columns(2)
    with c3:
        st.caption("Este gráfico mostra quais categorias concentram maior volume operacional.")
        category_chart = px.bar(
            filtered["category"].value_counts().rename_axis("categoria").reset_index(name="volume"),
            x="categoria",
            y="volume",
            title="Cards por categoria",
            color_discrete_sequence=["#6366f1"],
        )
        category_chart.update_layout(template="plotly_white", height=360, margin={"l": 16, "r": 10, "t": 54, "b": 16})
        st.plotly_chart(category_chart, width="stretch")
    with c4:
        st.caption("Este gráfico mostra o desempenho de SLA em cada fase do processo.")
        st.plotly_chart(pipefy_sla_by_phase(filtered), width="stretch")

    c5, c6 = st.columns(2)
    with c5:
        st.caption("Este gráfico mostra a concentração de backlog por responsável.")
        assignee_chart = px.bar(
            filtered["assignee"].value_counts().rename_axis("responsavel").reset_index(name="volume"),
            x="responsavel",
            y="volume",
            title="Backlog por responsável",
            color_discrete_sequence=["#0ea5e9"],
        )
        assignee_chart.update_layout(template="plotly_white", height=360, margin={"l": 16, "r": 10, "t": 54, "b": 16})
        st.plotly_chart(assignee_chart, width="stretch")
    with c6:
        st.caption("Este gráfico mostra a evolução temporal de cards criados.")
        temporal = (
            filtered.dropna(subset=["created_at"])
            .assign(data=lambda d: d["created_at"].dt.date)
            .groupby("data", as_index=False)["ticket_id"]
            .count()
            .rename(columns={"ticket_id": "volume"})
        )
        temporal_chart = px.line(
            temporal,
            x="data",
            y="volume",
            title="Evolução temporal dos cards",
            markers=True,
            color_discrete_sequence=["#0f766e"],
        )
        temporal_chart.update_layout(template="plotly_white", height=360, margin={"l": 16, "r": 10, "t": 54, "b": 16})
        st.plotly_chart(temporal_chart, width="stretch")

    st.caption("Este heatmap mostra a concentração de volume entre fase e prioridade.")
    st.plotly_chart(pipefy_phase_priority_heatmap(filtered), width="stretch")

    render_section_header("Alertas Automatizados", "Fila operacional de cards com risco e ação recomendada.")
    present_cols = [col for col in REQUIRED_ALERT_COLUMNS if col in filtered.columns]
    alerts = filtered[present_cols].copy()
    alert_summary_cols = st.columns(4)
    alert_summary_cols[0].metric("Total de alertas", len(alerts))
    alert_summary_cols[1].metric(
        "Alertas críticos",
        int(alerts["risk_level"].astype(str).str.contains("High|Crítico", case=False, na=False).sum()),
    )
    alert_summary_cols[2].metric(
        "Alertas SLA", int(alerts["sla_status"].astype(str).str.contains("SLA", case=False, na=False).sum())
    )
    alert_summary_cols[3].metric("Sem responsável", int(unassigned_mask.sum()))

    st.dataframe(alerts, width="stretch")
    st.download_button(
        "Exportar alertas CSV",
        data=alerts.to_csv(index=False).encode("utf-8"),
        file_name="pipefy_alerts.csv",
        mime="text/csv",
    )

    stories = executive_story_lines(filtered)
    render_story_section("Insights Executivos", stories["insights"])
    render_story_section("Ações Recomendadas", stories["acoes"])


if __name__ == "__main__":
    st.set_page_config(page_title="Central de Automação e Operações", layout="wide")
    render_pipefy_workflow_intelligence(show_page_intro=True)
