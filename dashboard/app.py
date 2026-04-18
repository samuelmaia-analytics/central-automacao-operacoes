from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(DASHBOARD_ROOT) not in sys.path:
    sys.path.insert(0, str(DASHBOARD_ROOT))
try:
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
        render_capabilities,
        render_data_source_status,
        render_footer,
        render_health_score,
        render_kpi_cards,
        render_no_data,
        render_product_header,
        render_section_header,
        render_story_section,
    )
    from dashboard.filters import apply_global_filters, clear_global_filters, render_global_filters
    from dashboard.insights import executive_story_lines
    from dashboard.pages.pipefy_workflow_intelligence import render_pipefy_workflow_intelligence
    from dashboard.product_copy import PRODUCT_CAPABILITIES
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
except Exception:
    from charts import (
        avg_resolution_by_category,
        backlog_risk_distribution,
        bar_count,
        heatmap_priority_status,
        sla_evolution,
        status_distribution,
        trend_volume,
    )
    from components import (
        render_badge,
        render_capabilities,
        render_data_source_status,
        render_footer,
        render_health_score,
        render_kpi_cards,
        render_no_data,
        render_product_header,
        render_section_header,
        render_story_section,
    )
    from filters import apply_global_filters, clear_global_filters, render_global_filters
    from insights import executive_story_lines
    from pages.pipefy_workflow_intelligence import render_pipefy_workflow_intelligence
    from product_copy import PRODUCT_CAPABILITIES
    from styles import inject_global_styles

    from utils import (
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
APP_SUBTITLE = (
    "Produto analítico para monitoramento de workflows, SLA, backlog, gargalos operacionais e alertas automatizados."
)
APP_DATA_MODE = os.getenv("APP_DATA_MODE", "auto").strip().lower()  # auto | pipefy | legacy

st.set_page_config(page_title=APP_TITLE, layout="wide")
inject_global_styles()
render_product_header(APP_TITLE, APP_SUBTITLE, show_intro=True)

all_pages = [
    "Visão Executiva",
    "Monitoramento de SLA",
    "Backlog & Prioridades",
    "Gargalos Operacionais",
    "Alertas Automatizados",
    "Insights Executivos",
    "Inteligência Operacional com Pipefy",
    "Explorador Operacional de Cards",
]
legacy_df = load_dataset()
legacy_available = not legacy_df.empty
pipefy_only_mode = APP_DATA_MODE == "pipefy" or (APP_DATA_MODE == "auto" and not legacy_available)

if APP_DATA_MODE == "legacy" and not legacy_available:
    st.error(
        "APP_DATA_MODE=legacy definido, mas a base legada não foi encontrada. "
        "Execute `python main.py` ou altere APP_DATA_MODE para `auto`/`pipefy`."
    )
    st.stop()

st.sidebar.markdown("### Navegação")
pages = ["Inteligência Operacional com Pipefy"] if pipefy_only_mode else all_pages
selected_page = st.sidebar.radio("Seções", pages)
presentation_mode = st.sidebar.toggle("Modo apresentação (portfólio)", value=False)

if selected_page == "Inteligência Operacional com Pipefy":
    if pipefy_only_mode:
        st.caption("Modo de dados: Pipefy")
    render_pipefy_workflow_intelligence(show_page_intro=False)
    st.markdown("---")
    if not presentation_mode:
        render_capabilities(PRODUCT_CAPABILITIES)
        render_footer()
    st.stop()

alerts_df = build_alerts(legacy_df)
enriched_df = enrich_with_alerts(legacy_df, alerts_df)
if st.sidebar.button("Limpar filtros"):
    clear_global_filters()
    st.rerun()
filter_state = render_global_filters(enriched_df)
filtered_df = apply_global_filters(enriched_df, filter_state)
filtered_alerts = alerts_df[alerts_df["ticket_id"].isin(filtered_df["ticket_id"])] if not alerts_df.empty else alerts_df
quality_summary = load_quality_summary()

if filtered_df.empty:
    render_no_data("Nenhum registro encontrado para os filtros atuais. Ajuste os filtros na barra lateral.")
    st.stop()

kpis = compute_kpi_bundle(filtered_df)
sla_compliance = float(kpis.get("percentual_dentro_sla", 0.0))
risk = determine_operational_risk(sla_compliance)
critical_operational_count = compute_critical_operational_count(filtered_df)
stories = executive_story_lines(filtered_df)

overdue_count = int(filtered_df["status_sla"].astype(str).str.contains("vencido", case=False, na=False).sum())
in_sla_count = int(filtered_df["status_sla"].astype(str).str.contains("dentro", case=False, na=False).sum())
unassigned_count = int(
    filtered_df.get("assigned_to", pd.Series(index=filtered_df.index, dtype="object"))
    .astype(str)
    .str.contains("unassigned|nan|none|^$", case=False, regex=True, na=False)
    .sum()
)
if "assignee" in filtered_df.columns:
    unassigned_count = int(
        filtered_df["assignee"]
        .astype(str)
        .str.contains("unassigned|nan|none|^$", case=False, regex=True, na=False)
        .sum()
    )

open_mask = filtered_df["ticket_status"].fillna("").astype(str).str.lower().isin(OPEN_STATUSES)
backlog_aberto = int(open_mask.sum())

health_score = max(
    0.0,
    min(
        100.0,
        100.0
        - (100.0 - sla_compliance) * 0.50
        - (overdue_count / max(len(filtered_df), 1) * 100.0) * 0.20
        - (critical_operational_count / max(len(filtered_df), 1) * 100.0) * 0.15
        - (backlog_aberto / max(len(filtered_df), 1) * 100.0) * 0.10
        - (unassigned_count / max(len(filtered_df), 1) * 100.0) * 0.05,
    ),
)
health_class = "Saudável" if health_score >= 80 else "Atenção" if health_score >= 60 else "Crítico"

if selected_page == "Visão Executiva":
    render_section_header(
        "Visão Executiva", "Indicadores principais para acompanhamento diário de performance operacional."
    )
    render_data_source_status(
        source="Base operacional tratada",
        status="Conectado",
        details=[
            f"Registros analisados: {len(filtered_df)}",
            f"Cards dentro do SLA: {in_sla_count}",
        ],
    )
    cards = [
        {
            "title": "Total de cards/processos",
            "value": f"{int(kpis['total_tickets'])}",
            "description": "Volume operacional monitorado no período filtrado.",
            "status": "neutro",
            "icon": "📌",
        },
        {
            "title": "SLA dentro do prazo",
            "value": f"{kpis['percentual_dentro_sla']:.1f}%",
            "description": "Percentual de demandas dentro do prazo operacional definido.",
            "status": "saudavel" if sla_compliance >= 85 else "atencao",
            "icon": "⏱️",
        },
        {
            "title": "Backlog aberto",
            "value": f"{backlog_aberto}",
            "description": "Cards em andamento ou aguardando resposta.",
            "status": "atencao" if backlog_aberto > len(filtered_df) * 0.3 else "neutro",
            "icon": "📚",
        },
        {
            "title": "Demandas críticas",
            "value": f"{critical_operational_count}",
            "description": "Casos com alta prioridade e risco operacional.",
            "status": "critico" if critical_operational_count > 0 else "saudavel",
            "icon": "🚨",
        },
        {
            "title": "Cards vencidos",
            "value": f"{overdue_count}",
            "description": "Volume com SLA já vencido no recorte atual.",
            "status": "critico" if overdue_count else "saudavel",
            "icon": "⚠️",
        },
        {
            "title": "Tempo médio de resolução",
            "value": format_hours(kpis["tempo_medio_resolucao_horas"]),
            "description": "Tempo médio para encerramento das demandas.",
            "status": "neutro",
            "icon": "🕒",
        },
        {
            "title": "Cards sem responsável",
            "value": f"{unassigned_count}",
            "description": "Demandas sem owner definido para execução.",
            "status": "atencao" if unassigned_count else "saudavel",
            "icon": "👥",
        },
        {
            "title": "Potencial de horas economizadas",
            "value": f"{kpis['potencial_horas_economizadas']:.1f}h",
            "description": "Estimativa de ganho com automações recomendadas.",
            "status": "neutro",
            "icon": "⚙️",
        },
    ]
    render_kpi_cards(cards, cols=4)

    render_section_header("Índice de Saúde Operacional")
    factors = [
        f"SLA dentro do prazo: {sla_compliance:.1f}%",
        f"Cards vencidos: {overdue_count}",
        f"Demandas críticas: {critical_operational_count}",
        f"Backlog aberto: {backlog_aberto}",
        f"Cards sem responsável: {unassigned_count}",
    ]
    recommendation = (
        "Priorizar cards vencidos e rebalancear backlog por prioridade."
        if health_class != "Saudável"
        else "Manter governança de fila e monitoramento contínuo de SLA."
    )
    render_health_score(health_score, health_class, factors, recommendation)
    render_badge(f"Classificação atual: {health_class}", level=risk)

    c1, c2 = st.columns(2)
    with c1:
        st.caption("Este gráfico mostra a evolução de volume ao longo do período.")
        st.plotly_chart(trend_volume(filtered_df), width="stretch")
    with c2:
        st.caption("Este gráfico mostra a composição do fluxo por status atual.")
        st.plotly_chart(status_distribution(filtered_df), width="stretch")

    render_story_section("Resumo Executivo", stories["resumo"])
    render_story_section("Riscos Operacionais", stories["riscos"])
    render_story_section("Oportunidades de Automação", stories["oportunidades"])

    if quality_summary:
        st.caption(
            "Qualidade da base: "
            f"IDs duplicados={quality_summary.get('ids_duplicados', 0)} | "
            f"Datas inconsistentes={quality_summary.get('linhas_data_inconsistente', 0)}"
        )
elif selected_page == "Monitoramento de SLA":
    render_section_header("Monitoramento de SLA", "Compliance temporal, evolução de risco e desempenho por categoria.")
    cards = [
        {
            "title": "Dentro do SLA",
            "value": f"{kpis['percentual_dentro_sla']:.1f}%",
            "description": "Chamados concluídos dentro do prazo.",
            "status": "saudavel" if kpis["percentual_dentro_sla"] >= 85 else "atencao",
            "icon": "✅",
        },
        {
            "title": "Fora do SLA",
            "value": f"{kpis['percentual_fora_sla']:.1f}%",
            "description": "Indicador de impacto por atraso.",
            "status": "critico" if kpis["percentual_fora_sla"] >= 20 else "atencao",
            "icon": "⛔",
        },
        {
            "title": "Tempo mediano",
            "value": format_hours(kpis["tempo_mediano_resolucao_horas"]),
            "description": "Tempo típico de resolução.",
            "status": "neutro",
            "icon": "📈",
        },
    ]
    render_kpi_cards(cards, cols=3)
    render_badge(f"Risco operacional: {risk.title()}", level=risk)

    c1, c2 = st.columns(2)
    with c1:
        st.caption("Este gráfico acompanha a tendência de compliance de SLA no período.")
        st.plotly_chart(sla_evolution(filtered_df), width="stretch")
    with c2:
        st.caption("Este gráfico mostra a distribuição dos status de SLA.")
        st.plotly_chart(bar_count(filtered_df, "status_sla", "SLA por status"), width="stretch")

    c3, c4 = st.columns(2)
    with c3:
        st.caption("Este gráfico mostra quais categorias concentram maior risco de prazo.")
        st.plotly_chart(
            bar_count(filtered_df, "categoria_operacional", "SLA por categoria", orientation="h"),
            width="stretch",
        )
    with c4:
        st.caption("Este gráfico compara SLA entre diferentes prioridades.")
        st.plotly_chart(bar_count(filtered_df, "ticket_priority", "SLA por prioridade"), width="stretch")

elif selected_page == "Backlog & Prioridades":
    render_section_header(
        "Backlog & Prioridades", "Volume em aberto, risco de atraso e distribuição da fila operacional."
    )
    backlog = filtered_df[open_mask]
    if backlog.empty:
        render_no_data("Não há backlog aberto no recorte filtrado.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            st.caption("Este gráfico mostra a pressão de backlog por prioridade.")
            st.plotly_chart(bar_count(backlog, "ticket_priority", "Backlog por prioridade"), width="stretch")
        with c2:
            st.caption("Este gráfico mostra em quais categorias o backlog está concentrado.")
            st.plotly_chart(
                bar_count(backlog, "categoria_operacional", "Backlog por categoria", orientation="h"),
                width="stretch",
            )
        c3, c4 = st.columns(2)
        with c3:
            st.caption("Este gráfico destaca a distribuição de risco no backlog.")
            st.plotly_chart(backlog_risk_distribution(backlog), width="stretch")
        with c4:
            st.caption("Este gráfico cruza prioridade e status para apoiar priorização.")
            st.plotly_chart(heatmap_priority_status(backlog), width="stretch")

        rank_cols = [
            c
            for c in ["ticket_id", "ticket_priority", "prioridade_automatica", "risco_atraso", "idade_ticket_horas"]
            if c in backlog.columns
        ]
        render_section_header("Fila priorizada", "Cards ordenados por criticidade e tempo em aberto.")
        ranked = backlog.sort_values(["flag_demanda_critica", "idade_ticket_horas"], ascending=[False, False])
        st.dataframe(ranked[rank_cols].head(300), width="stretch")

elif selected_page == "Gargalos Operacionais":
    render_section_header("Gargalos do Workflow", "Mapeamento dos pontos de maior acúmulo e atraso operacional.")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Este gráfico mostra onde o volume operacional está concentrado.")
        st.plotly_chart(
            bar_count(filtered_df, "categoria_operacional", "Volume por categoria", orientation="h"),
            width="stretch",
        )
    delayed = filtered_df[filtered_df["status_sla"].astype(str).str.contains("vencido|risco", case=False, na=False)]
    with c2:
        st.caption("Este gráfico destaca categorias com maior pressão de SLA.")
        st.plotly_chart(
            bar_count(delayed, "categoria_operacional", "Atrasos por categoria", orientation="h"),
            width="stretch",
        )
    st.caption("Este gráfico compara tempo médio de resolução entre categorias.")
    st.plotly_chart(avg_resolution_by_category(filtered_df), width="stretch")

elif selected_page == "Alertas Automatizados":
    render_section_header("Alertas Automatizados", "Fila de atuação com severidade, risco e ação recomendada.")
    if filtered_alerts.empty:
        render_no_data("Não há alertas para o recorte atual.")
    else:
        sla_alerts_count = int(
            filtered_alerts["tipo_alerta"].astype(str).str.contains("SLA", case=False, na=False).sum()
        )
        unassigned_alert_count = (
            int(
                filtered_df.get("assignee", pd.Series(index=filtered_df.index))
                .astype(str)
                .str.contains("Unassigned", case=False, na=False)
                .sum()
            )
            if "assignee" in filtered_df.columns
            else 0
        )
        sev_counts = (
            filtered_alerts["severidade"].value_counts().to_dict() if "severidade" in filtered_alerts.columns else {}
        )
        cards = [
            {
                "title": "Total de alertas",
                "value": f"{len(filtered_alerts)}",
                "description": "Alertas ativos no recorte atual.",
                "status": "neutro",
                "icon": "🔔",
            },
            {
                "title": "Alertas críticos",
                "value": f"{int(sev_counts.get('alta', 0))}",
                "description": "Demandam resposta imediata.",
                "status": "critico" if int(sev_counts.get("alta", 0)) > 0 else "saudavel",
                "icon": "🚨",
            },
            {
                "title": "Alertas de SLA",
                "value": f"{sla_alerts_count}",
                "description": "Alertas associados a risco/vencimento de SLA.",
                "status": "atencao",
                "icon": "⏱️",
            },
            {
                "title": "Sem responsável",
                "value": f"{unassigned_alert_count}",
                "description": "Cards sem owner para execução.",
                "status": "atencao",
                "icon": "👤",
            },
        ]
        render_kpi_cards(cards, cols=4)
        st.caption("Este gráfico mostra os principais tipos de alerta operacional.")
        st.plotly_chart(bar_count(filtered_alerts, "tipo_alerta", "Tipos de alerta", orientation="h"), width="stretch")
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
            "Exportar alertas CSV",
            data=filtered_alerts.to_csv(index=False).encode("utf-8"),
            file_name="alertas_automatizados.csv",
            mime="text/csv",
        )

elif selected_page == "Insights Executivos":
    render_section_header("Insights Executivos", "Leitura analítica orientada a decisão executiva.")
    render_story_section("Resumo Executivo", stories["resumo"])
    render_story_section("Insights Executivos", stories["insights"])
    render_story_section("Ações Recomendadas", stories["acoes"])
    render_story_section("Riscos Operacionais", stories["riscos"])
    render_story_section("Oportunidades de Automação", stories["oportunidades"])

elif selected_page == "Explorador Operacional de Cards":
    render_section_header(
        "Explorador Operacional de Cards", "Consulta operacional com busca, seleção de colunas e exportação."
    )
    available_cols = filtered_df.columns.tolist()
    default_cols = [
        c
        for c in ["ticket_id", "ticket_status", "ticket_priority", "categoria_operacional", "status_sla"]
        if c in available_cols
    ]
    selected_cols = st.multiselect("Colunas", available_cols, default=default_cols or available_cols[:10])
    search_text = st.text_input("Busca textual")
    max_rows = st.slider("Limite de registros", min_value=50, max_value=2000, value=500, step=50)
    data = filtered_df.copy()
    if search_text:
        mask = pd.Series(False, index=data.index)
        for col in selected_cols[:12]:
            mask = mask | data[col].astype(str).str.contains(search_text, case=False, na=False)
        data = data[mask]
    sort_col = st.selectbox("Ordenar por", options=selected_cols if selected_cols else available_cols)
    if sort_col:
        data = data.sort_values(sort_col, ascending=False, na_position="last")
    st.dataframe(data[selected_cols].head(max_rows) if selected_cols else data.head(max_rows), width="stretch")
    st.download_button(
        "Exportar dados filtrados (CSV)",
        data=data.to_csv(index=False).encode("utf-8"),
        file_name="explorador_cards.csv",
        mime="text/csv",
    )

st.markdown("---")
if not presentation_mode:
    render_capabilities(PRODUCT_CAPABILITIES)
    render_footer()
