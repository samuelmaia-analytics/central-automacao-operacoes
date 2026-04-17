from __future__ import annotations

import numpy as np
import pandas as pd

from src.automation.priority_rules import classify_priority_automatically, is_critical_demand
from src.automation.sla_rules import calculate_sla_risk, classify_sla_status, get_sla_hours
from src.utils.helpers import to_snake_case


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [to_snake_case(col) for col in normalized.columns]
    return normalized


def _derive_operational_category(ticket_type: str) -> str:
    ticket_type = str(ticket_type).lower()
    if "technical" in ticket_type:
        return "incidente_tecnico"
    if "billing" in ticket_type:
        return "financeiro"
    if "product" in ticket_type:
        return "duvida_produto"
    if "refund" in ticket_type:
        return "pos_venda"
    return "operacional_geral"


def _detect_rework(description: str) -> bool:
    text = str(description).lower()
    keywords = ["again", "still", "persist", "intermittent", "same issue", "repeat"]
    return any(keyword in text for keyword in keywords)


def transform_tickets(df: pd.DataFrame, reference_ts: pd.Timestamp | None = None) -> pd.DataFrame:
    transformed = _normalize_columns(df)
    reference_ts = reference_ts or pd.Timestamp.utcnow().tz_localize(None)

    transformed["ticket_status"] = transformed["ticket_status"].fillna("unknown").str.strip()
    transformed["ticket_priority"] = transformed["ticket_priority"].fillna("medium").str.strip().str.lower()
    transformed["ticket_type"] = transformed["ticket_type"].fillna("operational")
    transformed["ticket_channel"] = transformed["ticket_channel"].fillna("unknown")

    transformed["first_response_time"] = pd.to_datetime(transformed["first_response_time"], errors="coerce")
    transformed["time_to_resolution"] = pd.to_datetime(transformed["time_to_resolution"], errors="coerce")

    transformed["tempo_de_resolucao"] = (
        transformed["time_to_resolution"] - transformed["first_response_time"]
    ).dt.total_seconds() / 3600
    transformed.loc[transformed["tempo_de_resolucao"] < 0, "tempo_de_resolucao"] = np.nan
    transformed["idade_ticket_horas"] = (reference_ts - transformed["first_response_time"]).dt.total_seconds() / 3600
    transformed["sla_horas"] = transformed["ticket_priority"].apply(get_sla_hours)
    transformed["status_sla"] = transformed.apply(
        lambda row: classify_sla_status(
            resolution_hours=row["tempo_de_resolucao"],
            sla_hours=int(row["sla_horas"]),
            is_open=str(row["ticket_status"]).lower() in {"open", "pending customer response"},
        ),
        axis=1,
    )
    transformed["risco_atraso"] = transformed.apply(
        lambda row: calculate_sla_risk(row["idade_ticket_horas"], int(row["sla_horas"])),
        axis=1,
    )
    transformed["prioridade_automatica"] = transformed.apply(
        lambda row: classify_priority_automatically(
            original_priority=row["ticket_priority"],
            status=row["ticket_status"],
            age_hours=row["idade_ticket_horas"],
        ),
        axis=1,
    )
    transformed["categoria_operacional"] = transformed["ticket_type"].apply(_derive_operational_category)
    transformed["flag_retrabalho"] = transformed["ticket_description"].apply(_detect_rework)
    transformed["flag_demanda_critica"] = transformed.apply(
        lambda row: is_critical_demand(row["prioridade_automatica"], row["status_sla"]),
        axis=1,
    )

    grouped = transformed.groupby("customer_email")["ticket_id"].transform("count")
    transformed["cliente_recorrente"] = grouped >= 3
    transformed["status_sla"] = np.where(
        transformed["status_sla"].eq("SLA em risco") & transformed["cliente_recorrente"],
        "SLA em risco - recorrencia",
        transformed["status_sla"],
    )
    return transformed
