from __future__ import annotations

import pandas as pd


def build_automatic_insights(df: pd.DataFrame) -> list[str]:
    insights: list[str] = []
    if df.empty:
        return ["Sem dados para gerar insights."]

    backlog_rate = df["ticket_status"].str.lower().isin(["open", "pending customer response"]).mean() * 100
    if backlog_rate > 30:
        insights.append("Backlog aberto acima de 30% do volume total.")

    critical_rate = df["flag_demanda_critica"].mean() * 100
    if critical_rate > 20:
        insights.append("Volume de demandas criticas acima do esperado; revisar capacidade do time.")

    recurring_rate = df["cliente_recorrente"].mean() * 100
    if recurring_rate > 10:
        insights.append("Alta recorrencia por cliente; priorizar causa raiz por conta.")

    bottleneck = (
        df.groupby("categoria_operacional")["status_sla"]
        .apply(lambda s: (s == "SLA vencido").mean())
        .sort_values(ascending=False)
    )
    if not bottleneck.empty:
        insights.append(f"Maior risco de SLA na categoria: {bottleneck.index[0]}.")

    return insights or ["Operacao estavel sem alertas estruturais relevantes."]
