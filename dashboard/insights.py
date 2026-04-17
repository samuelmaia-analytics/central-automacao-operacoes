from __future__ import annotations

import pandas as pd


def build_operational_health(df: pd.DataFrame, kpis: dict[str, float]) -> dict[str, object]:
    total = max(1, int(kpis.get("total_tickets", 0)))
    sla_ok = float(kpis.get("percentual_dentro_sla", 0.0))
    backlog = int(kpis.get("backlog_aberto", 0))
    critical = int(kpis.get("tickets_criticos", 0))
    overdue = int(df["status_sla"].astype(str).str.contains("vencido", case=False, na=False).sum()) if "status_sla" in df.columns else 0
    unassigned = (
        int(df["assignee"].astype(str).isin(["Unassigned"]).sum()) if "assignee" in df.columns else 0
    )

    backlog_pct = backlog / total * 100
    critical_pct = critical / total * 100
    overdue_pct = overdue / total * 100
    unassigned_pct = unassigned / total * 100

    score = int(
        max(
            0,
            min(
                100,
                sla_ok * 0.45
                + (100 - overdue_pct) * 0.20
                + (100 - critical_pct) * 0.15
                + (100 - backlog_pct) * 0.10
                + (100 - unassigned_pct) * 0.10,
            ),
        )
    )
    if score >= 80:
        classification = "Saudável"
    elif score >= 60:
        classification = "Atenção"
    else:
        classification = "Crítico"

    drivers = [
        f"Conformidade de SLA: {sla_ok:.1f}%",
        f"Cards vencidos: {overdue}",
        f"Demandas críticas: {critical}",
        f"Backlog aberto: {backlog}",
        f"Cards sem responsável: {unassigned}",
    ]
    recommendation = "Priorizar cards vencidos e redistribuir backlog nas fases com maior concentração."
    explanation = "Score composto por SLA, backlog, criticidade, vencimentos e atribuição."
    return {
        "score": score,
        "classification": classification,
        "explanation": explanation,
        "drivers": drivers,
        "recommendation": recommendation,
    }


def build_storytelling_blocks(df: pd.DataFrame, kpis: dict[str, float]) -> dict[str, list[str]]:
    if df.empty:
        base = ["Sem dados suficientes para gerar narrativas operacionais."]
        return {
            "Resumo Executivo": base,
            "Insights Executivos": base,
            "Ações Recomendadas": base,
            "Riscos Operacionais": base,
            "Oportunidades de Automação": base,
        }

    total = max(1, int(kpis.get("total_tickets", len(df))))
    top_category = (
        str(df["categoria_operacional"].value_counts().index[0]) if "categoria_operacional" in df.columns else "N/D"
    )
    overdue = int(df["status_sla"].astype(str).str.contains("vencido", case=False, na=False).sum()) if "status_sla" in df.columns else 0
    risk = int(df["status_sla"].astype(str).str.contains("risco", case=False, na=False).sum()) if "status_sla" in df.columns else 0
    critical = int(kpis.get("tickets_criticos", 0))
    top_priority = str(df["ticket_priority"].mode().iloc[0]) if "ticket_priority" in df.columns and not df["ticket_priority"].dropna().empty else "N/D"
    backlog = int(kpis.get("backlog_aberto", 0))

    summary = [
        f"O volume operacional analisado no período é de {total} registros.",
        f"A categoria com maior concentração de demandas é {top_category}.",
        f"A prioridade mais recorrente no backlog atual é {top_priority}.",
    ]
    insights = [
        f"Existem {overdue} registros com SLA vencido e {risk} em risco.",
        f"O backlog aberto está em {backlog} demandas, com {critical} itens críticos.",
        "A distribuição atual indica necessidade de balanceamento entre filas de atendimento.",
    ]
    recommendations = [
        "Priorizar imediatamente os itens com SLA vencido e criticidade alta.",
        "Reforçar triagem inicial para reduzir acúmulo em fases de maior carga.",
        "Aplicar políticas de atribuição automática para reduzir cards sem responsável.",
    ]
    risks = [
        "Risco de deterioração de SLA caso o backlog crítico permaneça concentrado.",
        "Risco de retrabalho por baixa padronização em rotas de atendimento.",
        "Risco de baixa previsibilidade operacional sem atualização frequente dos cards.",
    ]
    opportunities = [
        "Automatizar classificação de prioridade para reduzir tempo de triagem.",
        "Implementar alertas preventivos para cards próximos do vencimento.",
        "Criar ações sugeridas por fase para acelerar tomada de decisão de liderança.",
    ]
    return {
        "Resumo Executivo": summary,
        "Insights Executivos": insights,
        "Ações Recomendadas": recommendations,
        "Riscos Operacionais": risks,
        "Oportunidades de Automação": opportunities,
    }

