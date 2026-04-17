from __future__ import annotations

import pandas as pd


def executive_summary(df: pd.DataFrame, kpis: dict[str, float], critical_count: int | None = None) -> list[str]:
    total = int(kpis.get("total_tickets", 0))
    sla_ok = kpis.get("percentual_dentro_sla", 0.0)
    backlog = int(kpis.get("backlog_aberto", 0))
    critical = int(critical_count if critical_count is not None else kpis.get("tickets_criticos", 0))
    auto = kpis.get("taxa_automacao_simulada", 0.0)

    summary = [
        f"A operação analisou {total} tickets no período filtrado.",
        f"O SLA compliance está em {sla_ok:.1f}%, com backlog aberto de {backlog} casos.",
        f"O volume crítico atual é {critical}, com potencial de automação estimado em {auto:.1f}%.",
    ]
    if not df.empty and "categoria_operacional" in df.columns:
        top_cat = df["categoria_operacional"].value_counts().index[0]
        summary.append(f"A categoria com maior pressão operacional é {top_cat}.")
    return summary


def sla_interpretation(sla_compliance: float) -> str:
    if sla_compliance >= 85:
        return "SLA em faixa saudável. Prioridade: manter estabilidade e prevenção."
    if sla_compliance >= 70:
        return "SLA em atenção. Prioridade: reduzir backlog próximo do vencimento."
    return "SLA em zona crítica. Prioridade: escalonamento imediato e replanejamento de capacidade."


def insights_consulting_style(df: pd.DataFrame, kpis: dict[str, float]) -> list[str]:
    lines: list[str] = []
    if df.empty:
        return ["Sem base filtrada suficiente para gerar insights."]

    backlog = kpis.get("backlog_aberto", 0.0)
    if backlog > (kpis.get("total_tickets", 1) * 0.25):
        lines.append("Backlog acima do limite recomendado para operação estável; existe risco de acúmulo em cadeia.")

    rec_rate = 0.0
    if "cliente_recorrente" in df.columns:
        rec_rate = df["cliente_recorrente"].mean() * 100
    if rec_rate > 8:
        lines.append("Recorrência de clientes indica falha de resolução definitiva e impacto em experiência.")

    if "tempo_de_resolucao" in df.columns and df["tempo_de_resolucao"].notna().any():
        p75 = df["tempo_de_resolucao"].quantile(0.75)
        lines.append(f"O quartil superior de resolução está em {p75:.1f}h, sugerindo fila de alta variabilidade.")

    lines.extend(
        [
            "Oportunidade de automação: roteamento automático de casos críticos e pré-triagem por categoria.",
            "Próximo passo recomendado: implantar monitor diário com metas de redução de backlog por squad.",
        ]
    )
    return lines


PRODUCT_CAPABILITIES = [
    "Monitoramento de SLA",
    "Detecção de gargalos",
    "Priorização automática",
    "Alertas operacionais",
    "Inteligência de backlog",
    "Recomendações executivas",
    "Integração com Pipefy",
]
