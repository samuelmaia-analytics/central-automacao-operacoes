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

from dashboard.components import (
    render_data_source_status,
    render_kpi_grid,
    render_no_data,
    render_product_footer,
    render_product_header,
    render_section_header,
    render_story_block,
)
from dashboard.insights import build_storytelling_blocks
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


def _infer_status_class(value: int, warn: int, critical: int) -> str:
    if value >= critical:
        return "critico"
    if value >= warn:
        return "atencao"
    return "saudavel"


def render_pipefy_workflow_intelligence() -> None:
    render_product_header(
        "Central de Automação e Operações",
        "Monitoramento integrado ao Pipefy para acompanhar cards, fases, SLA, backlog, riscos e alertas automatizados.",
    )
    render_section_header(
        "Inteligência Operacional com Pipefy",
        "Painel executivo para acompanhar saúde do workflow e decisões de priorização.",
    )

    token_present = bool(os.getenv("PIPEFY_TOKEN", "").strip())
    default_mock = _is_true(os.getenv("USE_PIPEFY_MOCK", "true")) or not token_present
    force_mock = st.sidebar.toggle("Pipefy em modo mock", value=default_mock, key="pipefy_force_mock")
    if st.sidebar.button("Atualizar dados Pipefy", key="refresh_pipefy"):
        _load_pipefy_data.clear()
    try:
        df = _load_pipefy_data(force_mock=force_mock)
    except Exception:
        st.warning("Falha ao carregar dados da API Pipefy. Alternando automaticamente para modo demonstração.")
        try:
            df = run_pipefy_pipeline(use_mock=True)
            force_mock = True
        except Exception:
            render_no_data("Não foi possível carregar dados Pipefy neste momento.")
            return
    source = "Modo demonstração" if force_mock else "Pipefy API"
    status = "Dados simulados para portfólio" if force_mock else "Conectado"
    pipe_id = os.getenv("PIPEFY_PIPE_ID", "Não informado")
    updated = pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    render_data_source_status(source=source, status=status, detail=f"Pipe analisado: {pipe_id} • Última atualização: {updated}")

    if df.empty:
        render_no_data("Nenhum card encontrado para o pipe selecionado. Verifique conexão, pipe_id ou execute seed.")
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

    if filtered.empty:
        render_no_data("Os filtros selecionados não retornaram dados. Ajuste os filtros e tente novamente.")
        return

    open_mask = filtered["status"].eq("open")
    overdue_mask = filtered["sla_status"].eq("SLA vencido")
    risk_mask = filtered["sla_status"].eq("SLA em risco")
    unassigned_mask = filtered["assignee"].eq("Unassigned")
    critical_mask = filtered["priority"].isin(["Crítica", "Critica"])
    avg_days = float(filtered["days_open"].mean()) if filtered["days_open"].notna().any() else 0.0
    in_sla = int(filtered["sla_status"].eq("Dentro do SLA").sum())
    sla_pct = _safe_pct(in_sla, len(filtered))

    kpi_cards = [
        {
            "title": "Total de cards",
            "value": f"{len(filtered)}",
            "description": "Volume total de demandas operacionais monitoradas.",
            "status": "neutro",
            "icon": "📌",
        },
        {
            "title": "Cards abertos",
            "value": f"{int(open_mask.sum())}",
            "description": "Demandas ainda em fluxo operacional.",
            "status": "atencao",
            "icon": "📂",
        },
        {
            "title": "Cards vencidos",
            "value": f"{int(overdue_mask.sum())}",
            "description": "Itens fora do prazo de SLA.",
            "status": _infer_status_class(int(overdue_mask.sum()), warn=3, critical=8),
            "icon": "⏰",
        },
        {
            "title": "Cards em risco de SLA",
            "value": f"{int(risk_mask.sum())}",
            "description": "Demandas próximas do vencimento.",
            "status": _infer_status_class(int(risk_mask.sum()), warn=4, critical=9),
            "icon": "⚠️",
        },
        {
            "title": "Cards sem responsável",
            "value": f"{int(unassigned_mask.sum())}",
            "description": "Cards sem atribuição ativa.",
            "status": _infer_status_class(int(unassigned_mask.sum()), warn=2, critical=6),
            "icon": "👤",
        },
        {
            "title": "Cards críticos",
            "value": f"{int(critical_mask.sum())}",
            "description": "Demandas com prioridade crítica.",
            "status": _infer_status_class(int(critical_mask.sum()), warn=3, critical=7),
            "icon": "🚨",
        },
        {
            "title": "Tempo médio em aberto",
            "value": f"{avg_days:.1f} dias",
            "description": "Média de permanência dos cards no fluxo.",
            "status": "neutro",
            "icon": "⏳",
        },
        {
            "title": "% dentro do SLA",
            "value": f"{sla_pct:.1f}%",
            "description": "Conformidade de prazo no recorte atual.",
            "status": "saudavel" if sla_pct >= 85 else "atencao" if sla_pct >= 70 else "critico",
            "icon": "✅",
        },
    ]
    render_kpi_grid(kpi_cards, cols=4)

    g1, g2 = st.columns(2)
    g1.plotly_chart(
        px.bar(
            filtered["current_phase"].value_counts().rename_axis("fase").reset_index(name="volume"),
            x="fase",
            y="volume",
            title="Cards por fase",
            color_discrete_sequence=["#1d4ed8"],
        ),
        width="stretch",
    )
    g1.caption("Este gráfico mostra onde o backlog está mais concentrado no workflow.")
    g2.plotly_chart(
        px.bar(
            filtered["priority"].value_counts().rename_axis("priority").reset_index(name="volume"),
            x="priority",
            y="volume",
            title="Cards por prioridade",
            color_discrete_sequence=["#7c3aed"],
        ),
        width="stretch",
    )
    g2.caption("Este gráfico mostra a distribuição de urgência da fila atual.")

    g3, g4 = st.columns(2)
    g3.plotly_chart(
        px.bar(
            filtered["category"].value_counts().rename_axis("category").reset_index(name="volume"),
            x="category",
            y="volume",
            title="Cards por categoria",
            color_discrete_sequence=["#0ea5e9"],
        ),
        width="stretch",
    )
    g3.caption("Este gráfico indica quais áreas concentram maior carga operacional.")
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
            color_discrete_map={"Dentro do SLA": "#16a34a", "SLA em risco": "#f59e0b", "SLA vencido": "#dc2626"},
        ),
        width="stretch",
    )
    g4.caption("Este gráfico evidencia pontos de risco de SLA por etapa do fluxo.")

    g5, g6 = st.columns(2)
    g5.plotly_chart(
        px.bar(
            filtered["assignee"].value_counts().rename_axis("assignee").reset_index(name="volume"),
            x="assignee",
            y="volume",
            title="Backlog por responsável",
            color_discrete_sequence=["#334155"],
        ),
        width="stretch",
    )
    g5.caption("Este gráfico mostra a distribuição de capacidade por responsável.")
    temporal = (
        filtered.dropna(subset=["created_at"])
        .assign(data=lambda d: d["created_at"].dt.date)
        .groupby("data", as_index=False)["ticket_id"]
        .count()
        .rename(columns={"ticket_id": "volume"})
    )
    g6.plotly_chart(
        px.line(
            temporal,
            x="data",
            y="volume",
            markers=True,
            title="Evolução temporal dos cards",
            color_discrete_sequence=["#1d4ed8"],
        ),
        width="stretch",
    )
    g6.caption("Este gráfico mostra tendência de entrada de demandas ao longo do tempo.")

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
            color_continuous_scale="Blues",
        ),
        width="stretch",
    )
    st.caption("Este gráfico destaca onde urgência e fase se combinam para formar gargalos.")

    render_section_header("Alertas Automatizados", "Fila operacional para ação imediata.")
    present_cols = [col for col in REQUIRED_ALERT_COLUMNS if col in filtered.columns]
    alerts = filtered[present_cols].copy().sort_values(["risk_level", "sla_status"], ascending=[False, True])
    query = st.text_input("Buscar card por título, fase ou responsável", value="", key="pipefy_alert_search")
    if query:
        mask = pd.Series(False, index=alerts.index)
        for col in [c for c in ["title", "current_phase", "assignee"] if c in alerts.columns]:
            mask = mask | alerts[col].astype(str).str.contains(query, case=False, na=False)
        alerts = alerts[mask]
    max_rows = st.slider("Limite de registros", min_value=20, max_value=500, value=200, step=20, key="pipefy_alert_rows")
    st.dataframe(alerts.head(max_rows), width="stretch")
    st.download_button(
        "Exportar alertas em CSV",
        data=alerts.to_csv(index=False).encode("utf-8"),
        file_name="pipefy_alerts.csv",
        mime="text/csv",
    )

    kpis = {"total_tickets": len(filtered), "backlog_aberto": int(open_mask.sum()), "tickets_criticos": int(critical_mask.sum())}
    stories = build_storytelling_blocks(filtered.rename(columns={"category": "categoria_operacional", "priority": "ticket_priority"}), kpis)
    cols_story = st.columns(2)
    with cols_story[0]:
        render_story_block("Resumo Executivo", stories["Resumo Executivo"])
        render_story_block("Riscos Operacionais", stories["Riscos Operacionais"])
    with cols_story[1]:
        render_story_block("Insights Executivos", stories["Insights Executivos"])
        render_story_block("Ações Recomendadas", stories["Ações Recomendadas"])
    render_story_block("Oportunidades de Automação", stories["Oportunidades de Automação"])
    render_product_footer()


if __name__ == "__main__":
    st.set_page_config(page_title="Central de Automação e Operações", layout="wide")
    render_pipefy_workflow_intelligence()
