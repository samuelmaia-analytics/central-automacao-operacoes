from __future__ import annotations

from datetime import datetime

import pandas as pd

from src.analytics.insights import build_automatic_insights
from src.analytics.kpis import top_operational_bottlenecks
from src.quality.data_quality import QualitySummary


def generate_markdown_report(df: pd.DataFrame, kpis: dict[str, float], quality: QualitySummary | None = None) -> str:
    bottlenecks = top_operational_bottlenecks(df, limit=5)
    alerts = df[df["flag_demanda_critica"]].head(10)[
        ["ticket_id", "ticket_status", "status_sla", "prioridade_automatica"]
    ]
    insights = build_automatic_insights(df)

    lines = [
        "# Relatório Executivo - Plataforma de Análise e Automação Operacional",
        "",
        f"Data de geracao: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        "",
        "## Resumo executivo",
        f"- Total de tickets/processos: {int(kpis['total_tickets'])}",
        f"- Percentual dentro do SLA: {kpis['percentual_dentro_sla']:.2f}%",
        f"- Percentual fora do SLA: {kpis['percentual_fora_sla']:.2f}%",
        f"- Backlog aberto: {int(kpis['backlog_aberto'])}",
        f"- Tickets criticos: {int(kpis['tickets_criticos'])}",
        "",
        "## Gargalos operacionais",
    ]
    for _, row in bottlenecks.iterrows():
        line = (
            f"- {row['categoria_operacional']}: "
            f"volume={int(row['volume'])}, "
            f"sla_vencido={int(row['sla_vencido'])}, "
            f"tempo_medio={row['tempo_medio']:.2f}h"
        )
        lines.append(line)

    lines.extend(["", "## Alertas criticos (amostra)"])
    for _, row in alerts.iterrows():
        line = (
            f"- Ticket {int(row['ticket_id'])}: "
            f"status={row['ticket_status']}, "
            f"sla={row['status_sla']}, "
            f"prioridade_auto={row['prioridade_automatica']}"
        )
        lines.append(line)

    lines.extend(["", "## Insights automaticos"])
    for item in insights:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Governanca e qualidade de dados",
        ]
    )
    if quality:
        lines.extend(
            [
                f"- Registros analisados: {quality.total_registros}",
                f"- IDs duplicados: {quality.ids_duplicados}",
                f"- Linhas sem first_response_time: {quality.linhas_sem_first_response}",
                f"- Linhas com datas inconsistentes: {quality.linhas_data_inconsistente}",
            ]
        )
    lines.extend(
        [
            "",
            "## Recomendacoes de automacao",
            "- Criar roteamento automatico para demandas criticas.",
            "- Implementar monitoramento horario para tickets perto do vencimento do SLA.",
            "- Priorizar plano de reducao de recorrencia por cliente e categoria.",
            "",
            "## Proximos passos",
            "- Integrar notificacoes em Teams/Slack.",
            "- Criar score de risco preditivo para violacao de SLA.",
            "- Publicar dashboard em ambiente cloud.",
        ]
    )
    return "\n".join(lines)
