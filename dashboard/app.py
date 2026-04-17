from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Ensure project root is importable even when Streamlit starts from dashboard/ cwd.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.charts import (
    avg_resolution_by_category,
    backlog_risk_distribution,
    bar_count,
    heatmap_priority_status,
    sla_evolution,
    status_distribution,
    trend_volume,
)
from dashboard.components import (
    render_badge,
    render_bullet_summary,
    render_capabilities,
    render_metric_cards,
    render_no_data,
    render_product_header,
    render_section_header,
)
from dashboard.filters import apply_global_filters, clear_global_filters, render_global_filters
from dashboard.product_copy import (
    PRODUCT_CAPABILITIES,
    executive_summary,
    insights_consulting_style,
    sla_interpretation,
)
from dashboard.pages.pipefy_workflow_intelligence import render_pipefy_workflow_intelligence
from dashboard.styles import inject_global_styles
from dashboard.utils import (
    OPEN_STATUSES,
    build_alerts,
    compute_critical_operational_count,
    compute_kpi_bundle,
    determine_operational_risk,
    enrich_with_alerts,
    format_hours,
    load_dataset,
    load_quality_summary,
)

APP_TITLE = "Central de Automação e Operações"
APP_SUBTITLE = "Produto analítico para monitoramento de workflows, SLA, backlog, gargalos operacionais e alertas automatizados."
CONTACT_EMAIL = os.getenv("PROJECT_CONTACT_EMAIL", "smaia2@gmail.com")
CONTACT_LINKEDIN = os.getenv("PROJECT_CONTACT_LINKEDIN", "https://linkedin.com/in/samuelmaia-analytics")
APP_DATA_MODE = os.getenv("APP_DATA_MODE", "auto").strip().lower()  # auto | pipefy | legacy

st.set_page_config(page_title=APP_TITLE, layout="wide")
inject_global_styles()
render_product_header(APP_TITLE, APP_SUBTITLE)

all_pages = [
    "Overview Executivo",
    "Monitoramento de SLA",
    "Backlog & Prioridades",
    "Gargalos do Workflow",
    "Alertas Automatizados",
    "Insights Executivos",
    "Inteligência Operacional com Pipefy",
    "Explorador Operacional de Cards",
]
base_df = load_dataset()
legacy_available = not base_df.empty
pipefy_only_mode = APP_DATA_MODE == "pipefy" or (APP_DATA_MODE == "auto" and not legacy_available)
if APP_DATA_MODE == "legacy" and not legacy_available:
    st.error(
        "APP_DATA_MODE=legacy definido, mas a base legada não foi encontrada. "
        "Execute `python main.py` ou altere APP_DATA_MODE para `auto`/`pipefy`."
    )
    st.stop()

pages = ["Inteligência Operacional com Pipefy"] if pipefy_only_mode else all_pages
selected_page = st.sidebar.radio("Navegação", pages)
presentation_mode = st.sidebar.toggle("Modo apresentação (portfólio)", value=False)

if selected_page == "Inteligência Operacional com Pipefy":
    if pipefy_only_mode:
        st.caption("Modo de dados: Pipefy")
    render_pipefy_workflow_intelligence()
    st.markdown("---")
    if not presentation_mode:
        render_capabilities(PRODUCT_CAPABILITIES)
        st.caption(f"Contato: {CONTACT_EMAIL} | LinkedIn: {CONTACT_LINKEDIN}")
    st.stop()

alerts_df = build_alerts(base_df)
enriched_df = enrich_with_alerts(base_df, alerts_df)
if st.sidebar.button("Limpar filtros"):
    clear_global_filters()
    st.rerun()
filter_state = render_global_filters(enriched_df)
filtered_df = apply_global_filters(enriched_df, filter_state)
filtered_alerts = alerts_df[alerts_df["ticket_id"].isin(filtered_df["ticket_id"])] if not alerts_df.empty else alerts_df
quality_summary = load_quality_summary()

if filtered_df.empty:
    render_no_data("Nenhum registro para os filtros selecionados. Ajuste os filtros globais na barra lateral.")
    st.stop()

kpis = compute_kpi_bundle(filtered_df)
sla_compliance = float(kpis.get("percentual_dentro_sla", 0.0))
risk = determine_operational_risk(sla_compliance)
critical_operational_count = compute_critical_operational_count(filtered_df)

if selected_page == "Overview Executivo":
    render_section_header("Visão executiva", "Métricas-chave e sinais de risco para decisão diária.")
    metrics = [
        ("Total de Tickets/Processos", f"{int(kpis['total_tickets'])}"),
        ("Conformidade de SLA", f"{kpis['percentual_dentro_sla']:.1f}%"),
        ("Backlog Aberto", f"{int(kpis['backlog_aberto'])}"),
        ("Tickets Críticos", f"{critical_operational_count}"),
        ("Tempo Médio de Resolução", format_hours(kpis["tempo_medio_resolucao_horas"])),
        ("Potencial de Horas Economizadas", f"{kpis['potencial_horas_economizadas']:.1f}h"),
    ]
    render_metric_cards(metrics, cols=3)

    col_a, col_b = st.columns([1.3, 1.0])
    col_a.plotly_chart(trend_volume(filtered_df), width="stretch")
    col_b.plotly_chart(status_distribution(filtered_df), width="stretch")

    render_section_header("Resumo executivo automático")
    render_bullet_summary(executive_summary(filtered_df, kpis, critical_count=critical_operational_count))
    render_section_header("Índice de Saúde Operacional")
    render_badge(f"Nível atual: {risk.title()}", level=risk)
    if quality_summary:
        st.caption(
            "Qualidade da base completa monitorada: "
            f"IDs duplicados={quality_summary.get('ids_duplicados', 0)} | "
            f"Datas inconsistentes={quality_summary.get('linhas_data_inconsistente', 0)}"
        )

elif selected_page == "Monitoramento de SLA":
    render_section_header("Monitoramento de SLA", "Compliance temporal, dispersão e casos críticos.")
    render_metric_cards(
        [
            ("Dentro do SLA", f"{kpis['percentual_dentro_sla']:.1f}%"),
            ("Fora do SLA", f"{kpis['percentual_fora_sla']:.1f}%"),
            ("Tempo Mediano", format_hours(kpis["tempo_mediano_resolucao_horas"])),
        ],
        cols=3,
    )
    render_badge(f"Risco {risk.title()}", level=risk)
    st.caption(sla_interpretation(sla_compliance))

    col_a, col_b = st.columns(2)
    col_a.plotly_chart(sla_evolution(filtered_df), width="stretch")
    col_b.plotly_chart(bar_count(filtered_df, "status_sla", "SLA por status"), width="stretch")

    col_c, col_d = st.columns(2)
    col_c.plotly_chart(
        bar_count(filtered_df, "categoria_operacional", "SLA por categoria", orientation="h"),
        width="stretch",
    )
    col_d.plotly_chart(bar_count(filtered_df, "ticket_priority", "SLA por prioridade"), width="stretch")

    critical_cols = [
        c for c in ["ticket_id", "ticket_status", "status_sla", "prioridade_automatica"] if c in filtered_df.columns
    ]
    critical_cases = filtered_df[
        filtered_df["status_sla"].astype(str).str.contains("vencido|risco", case=False, na=False)
    ]
    render_section_header("Casos mais críticos")
    st.dataframe(critical_cases[critical_cols].head(200), width="stretch")

elif selected_page == "Backlog & Prioridades":
    render_section_header("Backlog & Prioridades", "Capacidade operacional, aging e priorização da fila.")
    status = filtered_df["ticket_status"].fillna("").astype(str).str.lower()
    backlog = filtered_df[status.isin(OPEN_STATUSES)]

    col_a, col_b = st.columns(2)
    col_a.plotly_chart(bar_count(backlog, "ticket_priority", "Backlog por prioridade"), width="stretch")
    col_b.plotly_chart(
        bar_count(backlog, "categoria_operacional", "Backlog por categoria", orientation="h"),
        width="stretch",
    )

    col_c, col_d = st.columns(2)
    col_c.plotly_chart(backlog_risk_distribution(backlog), width="stretch")
    col_d.plotly_chart(heatmap_priority_status(backlog), width="stretch")
    if "risco_atraso" in backlog.columns and backlog["risco_atraso"].nunique(dropna=True) <= 1:
        col_c.caption("No recorte atual, o backlog está concentrado em uma única faixa de risco.")

    render_section_header("Ranking de demandas críticas")
    rank_cols = [
        c
        for c in ["ticket_id", "ticket_priority", "prioridade_automatica", "risco_atraso", "idade_ticket_horas"]
        if c in backlog.columns
    ]
    ranked = backlog.sort_values(["flag_demanda_critica", "idade_ticket_horas"], ascending=[False, False])
    st.dataframe(ranked[rank_cols].head(200), width="stretch")

    render_section_header("Tabela operacional")
    query = st.text_input("Busca (ticket, cliente, categoria, status)", value="")
    data = backlog.copy()
    if query:
        search_cols = [
            c
            for c in ["ticket_id", "customer_email", "customer_name", "categoria_operacional", "ticket_status"]
            if c in data.columns
        ]
        mask = pd.Series(False, index=data.index)
        for col in search_cols:
            mask = mask | data[col].astype(str).str.contains(query, case=False, na=False)
        data = data[mask]
    show_cols = [
        c
        for c in [
            "ticket_id",
            "customer_email",
            "ticket_status",
            "ticket_priority",
            "categoria_operacional",
            "status_sla",
        ]
        if c in data.columns
    ]
    st.dataframe(data[show_cols].head(500), width="stretch")

elif selected_page == "Gargalos do Workflow":
    render_section_header(
        "Gargalos do Workflow",
        "Categorias com carga, atraso e eficiência abaixo da meta.",
    )
    col_a, col_b = st.columns(2)
    col_a.plotly_chart(
        bar_count(filtered_df, "categoria_operacional", "Categorias com maior volume", orientation="h"),
        width="stretch",
    )
    delayed = filtered_df[filtered_df["status_sla"].astype(str).str.contains("vencido|risco", case=False, na=False)]
    col_b.plotly_chart(
        bar_count(delayed, "categoria_operacional", "Categorias com maior atraso", orientation="h"),
        width="stretch",
    )
    st.plotly_chart(avg_resolution_by_category(filtered_df), width="stretch")

    render_section_header("Top gargalos detectados")
    gargalos = (
        filtered_df.groupby("categoria_operacional", as_index=False)
        .agg(volume=("ticket_id", "count"), tempo_medio=("tempo_de_resolucao", "mean"))
        .sort_values(["volume", "tempo_medio"], ascending=False)
    )
    st.dataframe(gargalos.head(10), width="stretch")
    render_bullet_summary(
        [
            "Padronizar roteamento inicial das categorias com maior concentração de volume.",
            "Criar playbooks para reduzir variação no tempo de resolução em casos recorrentes.",
            "Aplicar automação de classificação para filas com alto backlog e criticidade.",
        ]
    )

elif selected_page == "Alertas Automatizados":
    render_section_header("Alertas Automatizados", "Motor de regras para triagem e resposta operacional.")
    sev_counts = (
        filtered_alerts["severidade"].value_counts().to_dict() if "severidade" in filtered_alerts.columns else {}
    )
    render_metric_cards(
        [
            ("Alertas Alta", f"{int(sev_counts.get('alta', 0))}"),
            ("Alertas Média", f"{int(sev_counts.get('media', 0))}"),
            ("Alertas Baixa", f"{int(sev_counts.get('baixa', 0))}"),
        ],
        cols=3,
    )
    st.plotly_chart(
        bar_count(filtered_alerts, "tipo_alerta", "Tipos de alerta", orientation="h"),
        width="stretch",
    )

    cols = [
        c
        for c in [
            "ticket_id",
            "tipo_alerta",
            "severidade",
            "acao_recomendada",
            "ticket_status",
            "prioridade_automatica",
            "status_sla",
        ]
        if c in filtered_alerts.columns
    ]
    st.dataframe(filtered_alerts[cols].head(500), width="stretch")
    st.download_button(
        "Exportar alertas (CSV)",
        data=filtered_alerts.to_csv(index=False).encode("utf-8"),
        file_name="alertas_automatizados.csv",
        mime="text/csv",
    )

elif selected_page == "Insights Executivos":
    render_section_header("Insights Executivos", "Leitura analítica para decisão executiva e melhoria contínua.")
    render_bullet_summary(insights_consulting_style(filtered_df, kpis))
    render_section_header("Potencial de ganho operacional")
    st.write(
        f"A taxa de automação simulada está em {kpis['taxa_automacao_simulada']:.1f}% com "
        f"potencial de economia de {kpis['potencial_horas_economizadas']:.1f}h no ciclo analisado."
    )
    render_section_header("Ações Recomendadas")
    render_bullet_summary(
        [
            "Implantar rotina diária de gestão do backlog por severidade e risco SLA.",
            "Automatizar abertura de ação corretiva para recorrência de cliente.",
            "Criar meta semanal de redução do tempo mediano de resolução por categoria crítica.",
        ]
    )

elif selected_page == "Explorador Operacional de Cards":
    render_section_header("Explorador Operacional de Cards", "Análise detalhada com recortes customizados e exportação.")
    available_cols = filtered_df.columns.tolist()
    selected_cols = st.multiselect("Colunas para visualização", available_cols, default=available_cols[:10])
    max_rows = st.slider("Máximo de linhas exibidas", min_value=50, max_value=2000, value=500, step=50)
    show_df = filtered_df[selected_cols].head(max_rows) if selected_cols else filtered_df.head(max_rows)
    st.dataframe(show_df, width="stretch")
    st.download_button(
        "Exportar dados filtrados (CSV)",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="data_explorer_export.csv",
        mime="text/csv",
    )
    with st.expander("Estatísticas descritivas"):
        st.dataframe(filtered_df.describe(include="all").transpose().head(40), width="stretch")

st.markdown("---")
if not presentation_mode:
    render_capabilities(PRODUCT_CAPABILITIES)
    st.caption(f"Contato: {CONTACT_EMAIL} | LinkedIn: {CONTACT_LINKEDIN}")
