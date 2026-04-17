from __future__ import annotations

import pandas as pd


def generate_alerts(df: pd.DataFrame) -> pd.DataFrame:
    alert_df = df.copy()
    alert_df["tipo_alerta"] = "Monitorar"
    alert_df["acao_recomendada"] = "Acompanhar fila normal"

    sla_vencido = alert_df["status_sla"].eq("SLA vencido")
    critico = alert_df["flag_demanda_critica"].eq(True)
    recorrente = alert_df["cliente_recorrente"].eq(True)

    alert_df.loc[sla_vencido, "tipo_alerta"] = "SLA vencido"
    alert_df.loc[sla_vencido, "acao_recomendada"] = "Escalar para lider operacional"

    alert_df.loc[critico, "tipo_alerta"] = "Demanda critica"
    alert_df.loc[critico, "acao_recomendada"] = "Atribuicao imediata para squad especializado"

    alert_df.loc[recorrente, "tipo_alerta"] = "Recorrencia cliente"
    alert_df.loc[recorrente, "acao_recomendada"] = "Abrir analise de causa raiz"

    return alert_df[
        [
            "ticket_id",
            "customer_email",
            "ticket_status",
            "ticket_priority",
            "prioridade_automatica",
            "status_sla",
            "tipo_alerta",
            "acao_recomendada",
        ]
    ]
