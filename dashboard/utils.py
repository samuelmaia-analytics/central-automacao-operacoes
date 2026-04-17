from __future__ import annotations

import json
from pathlib import Path

import duckdb
import pandas as pd
import streamlit as st

from src.analytics.kpis import compute_kpis
from src.config.settings import DATA_QUALITY_OUTPUT_FILE, PROCESSED_DATASET_CSV, SQL_DIR

OPEN_STATUSES = {"open", "pending customer response"}


@st.cache_data(show_spinner=False)
def load_dataset(path: Path = PROCESSED_DATASET_CSV) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    df = pd.read_csv(path)
    for col in ["first_response_time", "time_to_resolution", "date_of_purchase"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


@st.cache_data(show_spinner=False)
def load_quality_summary(path: Path = DATA_QUALITY_OUTPUT_FILE) -> dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_alerts(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["ticket_id", "tipo_alerta", "severidade", "acao_recomendada"])

    data = df.copy()
    data["tipo_alerta"] = "Monitoramento"
    data["severidade"] = "baixa"
    data["acao_recomendada"] = "Acompanhar rotina operacional"

    status_sla = data.get("status_sla", pd.Series(index=data.index, dtype="object")).fillna("").str.lower()
    prioridade = data.get("prioridade_automatica", pd.Series(index=data.index, dtype="object")).fillna("").str.lower()
    recorrente = data.get("cliente_recorrente", pd.Series(False, index=data.index))
    status = data.get("ticket_status", pd.Series("", index=data.index)).fillna("").str.lower()
    idade = pd.to_numeric(data.get("idade_ticket_horas", pd.Series(index=data.index)), errors="coerce")
    sla_horas = pd.to_numeric(data.get("sla_horas", pd.Series(index=data.index)), errors="coerce")

    m_sla_vencido = status_sla.eq("sla vencido")
    m_sla_risco = status_sla.str.contains("risco", na=False)
    m_critico = prioridade.eq("critical")
    m_backlog_elevado = status.isin(OPEN_STATUSES) & (idade > (sla_horas * 0.75))
    m_recorrencia = recorrente.eq(True)

    data.loc[m_sla_vencido, ["tipo_alerta", "severidade", "acao_recomendada"]] = [
        "SLA vencido",
        "alta",
        "Priorizar atendimento imediato e escalonamento",
    ]
    data.loc[m_sla_risco & ~m_sla_vencido, ["tipo_alerta", "severidade", "acao_recomendada"]] = [
        "SLA em risco",
        "media",
        "Redistribuir demanda e revisar fila",
    ]
    data.loc[m_critico & ~m_sla_vencido, ["tipo_alerta", "severidade", "acao_recomendada"]] = [
        "Prioridade crítica",
        "alta",
        "Atribuir célula especializada",
    ]
    data.loc[m_backlog_elevado & ~m_sla_vencido, ["tipo_alerta", "severidade", "acao_recomendada"]] = [
        "Backlog elevado",
        "media",
        "Automatizar triagem e rebalancear capacidade",
    ]
    data.loc[m_recorrencia & ~m_sla_vencido, ["tipo_alerta", "severidade", "acao_recomendada"]] = [
        "Recorrência",
        "media",
        "Abrir investigação de causa raiz",
    ]

    cols = [
        "ticket_id",
        "customer_email",
        "ticket_status",
        "ticket_priority",
        "prioridade_automatica",
        "categoria_operacional",
        "status_sla",
        "risco_atraso",
        "tipo_alerta",
        "severidade",
        "acao_recomendada",
    ]
    present = [c for c in cols if c in data.columns]
    return data[present].copy()


def enrich_with_alerts(df: pd.DataFrame, alerts: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    if alerts.empty or "ticket_id" not in alerts.columns:
        return df.assign(severidade=pd.NA, tipo_alerta=pd.NA, acao_recomendada=pd.NA)
    add_cols = [c for c in ["ticket_id", "tipo_alerta", "severidade", "acao_recomendada"] if c in alerts.columns]
    return df.merge(alerts[add_cols], on="ticket_id", how="left")


def compute_kpi_bundle(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {
            "total_tickets": 0.0,
            "percentual_dentro_sla": 0.0,
            "percentual_fora_sla": 0.0,
            "tempo_medio_resolucao_horas": 0.0,
            "tempo_mediano_resolucao_horas": 0.0,
            "backlog_aberto": 0.0,
            "tickets_criticos": 0.0,
            "taxa_automacao_simulada": 0.0,
            "potencial_horas_economizadas": 0.0,
        }
    try:
        sql_kpis = (SQL_DIR / "02_kpis_operacionais.sql").read_text(encoding="utf-8")
        with duckdb.connect(":memory:") as conn:
            conn.register("analytics_tickets", df)
            kpi_row = conn.execute(sql_kpis).fetchone()
            auto_row = conn.execute(
                """
                SELECT
                    SUM(
                        CASE
                            WHEN tipo_alerta IN ('SLA vencido', 'Demanda critica', 'Recorrencia cliente')
                            THEN 1 ELSE 0
                        END
                    ) AS automation_candidate
                FROM analytics_tickets
                """
            ).fetchone()

        total = float(kpi_row[0] or 0)
        automation_candidate = float((auto_row[0] or 0) if auto_row else 0)
        automation_rate = (automation_candidate / total * 100) if total else 0.0
        return {
            "total_tickets": total,
            "percentual_dentro_sla": float(kpi_row[1] or 0),
            "percentual_fora_sla": float(kpi_row[2] or 0),
            "tempo_medio_resolucao_horas": float(kpi_row[3] or 0),
            "tempo_mediano_resolucao_horas": float(kpi_row[4] or 0),
            "backlog_aberto": float(kpi_row[5] or 0),
            "tickets_criticos": float(kpi_row[6] or 0),
            "taxa_automacao_simulada": automation_rate,
            "potencial_horas_economizadas": automation_candidate * 0.25,
        }
    except Exception:
        return compute_kpis(df)


def determine_operational_risk(sla_compliance: float) -> str:
    if sla_compliance >= 85:
        return "saudavel"
    if sla_compliance >= 70:
        return "atencao"
    return "critico"


def format_hours(value: float) -> str:
    return f"{value:.1f}h"


def compute_critical_operational_count(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    try:
        with duckdb.connect(":memory:") as conn:
            conn.register("analytics_tickets", df)
            row = conn.execute(
                """
                SELECT
                    SUM(
                        CASE
                            WHEN lower(coalesce(ticket_status, '')) IN ('open', 'pending customer response')
                             AND (
                                lower(coalesce(status_sla, '')) LIKE '%vencido%'
                                OR lower(coalesce(status_sla, '')) LIKE '%risco%'
                                OR lower(coalesce(prioridade_automatica, '')) = 'critical'
                             )
                            THEN 1 ELSE 0
                        END
                    ) AS critical_operational
                FROM analytics_tickets
                """
            ).fetchone()
        return int((row[0] or 0) if row else 0)
    except Exception:
        status_open = df["ticket_status"].fillna("").astype(str).str.lower().isin(OPEN_STATUSES)
        status_sla = df["status_sla"].fillna("").astype(str).str.lower()
        priority_auto = df["prioridade_automatica"].fillna("").astype(str).str.lower()
        critical_mask = status_open & (
            status_sla.str.contains("vencido|risco", na=False) | priority_auto.eq("critical")
        )
        return int(critical_mask.sum())
