from __future__ import annotations

import pandas as pd


def compute_kpis(df: pd.DataFrame) -> dict[str, float]:
    total = len(df)
    within_sla = df["status_sla"].eq("Dentro do SLA").sum()
    out_sla = df["status_sla"].eq("SLA vencido").sum()
    backlog_open = df["ticket_status"].str.lower().isin(["open", "pending customer response"]).sum()
    critical = df["flag_demanda_critica"].sum()

    avg_resolution = float(df["tempo_de_resolucao"].dropna().mean()) if df["tempo_de_resolucao"].notna().any() else 0.0
    median_resolution = (
        float(df["tempo_de_resolucao"].dropna().median()) if df["tempo_de_resolucao"].notna().any() else 0.0
    )

    automation_candidate = (
        df["tipo_alerta"].isin(["SLA vencido", "Demanda critica", "Recorrencia cliente"]).sum()
        if "tipo_alerta" in df.columns
        else 0
    )
    automation_rate = (automation_candidate / total * 100) if total else 0
    saved_hours = automation_candidate * 0.25

    return {
        "total_tickets": float(total),
        "percentual_dentro_sla": (within_sla / total * 100) if total else 0,
        "percentual_fora_sla": (out_sla / total * 100) if total else 0,
        "tempo_medio_resolucao_horas": avg_resolution,
        "tempo_mediano_resolucao_horas": median_resolution,
        "backlog_aberto": float(backlog_open),
        "tickets_criticos": float(critical),
        "taxa_automacao_simulada": automation_rate,
        "potencial_horas_economizadas": saved_hours,
    }


def top_operational_bottlenecks(df: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    agg = (
        df.groupby("categoria_operacional", as_index=False)
        .agg(
            volume=("ticket_id", "count"),
            sla_vencido=("status_sla", lambda s: (s == "SLA vencido").sum()),
            tempo_medio=("tempo_de_resolucao", "mean"),
        )
        .sort_values(["sla_vencido", "volume"], ascending=False)
    )
    return agg.head(limit)
