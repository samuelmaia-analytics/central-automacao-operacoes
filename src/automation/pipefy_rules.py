from __future__ import annotations

import unicodedata

import pandas as pd

OPEN_PHASES = {"nova solicitacao", "triagem", "em analise", "em execucao", "aguardando cliente"}
INITIAL_PHASES = {"nova solicitacao", "triagem", "em analise"}


def _norm(value: object) -> str:
    text = str(value or "").strip().lower()
    norm = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return " ".join(norm.split())


def _is_open_status(status: pd.Series, phase: pd.Series) -> pd.Series:
    status_open = status.astype(str).str.lower().eq("open")
    phase_open = phase.astype(str).map(_norm).isin(OPEN_PHASES)
    return status_open | phase_open


def _build_recommendation(row: pd.Series) -> str:
    alert = str(row.get("automation_alert", "Monitoramento"))
    phase = _norm(row.get("current_phase", ""))
    if "SLA vencido" in alert:
        return "Priorizar atendimento"
    if "Sem responsável" in alert:
        return "Atribuir responsável"
    if "Prioridade crítica" in alert:
        return "Escalar para liderança"
    if "Gargalo de workflow" in alert:
        return "Redistribuir demanda"
    if "Card parado" in alert:
        return "Revisar processo"
    if phase == "aguardando cliente":
        return "Aguardar retorno do cliente"
    return "Encerrar ou atualizar status"


def apply_pipefy_automation_rules(
    df: pd.DataFrame,
    reference_ts: pd.Timestamp | None = None,
    stalled_days_threshold: int = 5,
    bottleneck_ratio: float = 0.35,
) -> pd.DataFrame:
    if df.empty:
        return df.copy()

    out = df.copy()
    now = reference_ts or pd.Timestamp.utcnow().tz_localize(None)
    out["created_at"] = pd.to_datetime(out.get("created_at"), errors="coerce")
    out["updated_at"] = pd.to_datetime(out.get("updated_at"), errors="coerce")
    out["due_date"] = pd.to_datetime(out.get("due_date"), errors="coerce")
    out["closed_at"] = pd.to_datetime(out.get("closed_at"), errors="coerce")
    out["assignee"] = out.get("assignee", pd.Series(index=out.index, dtype="object")).fillna("Unassigned")
    out["priority"] = out.get("priority", pd.Series(index=out.index, dtype="object")).fillna("Média")
    out["current_phase"] = out.get("current_phase", pd.Series(index=out.index, dtype="object")).fillna(
        "Nova solicitação"
    )
    out["status"] = out.get("status", pd.Series(index=out.index, dtype="object")).fillna("open")

    open_mask = _is_open_status(out["status"], out["current_phase"])
    due = out["due_date"]
    overdue_mask = open_mask & due.notna() & (due < now)
    risk_mask = open_mask & due.notna() & due.between(now, now + pd.Timedelta(days=2), inclusive="both")

    out["sla_status"] = "Dentro do SLA"
    out.loc[overdue_mask, "sla_status"] = "SLA vencido"
    out.loc[risk_mask & ~overdue_mask, "sla_status"] = "SLA em risco"

    out["days_open"] = ((out["closed_at"].fillna(now) - out["created_at"]).dt.total_seconds() / 86400).fillna(0).round(1)
    days_since_update = ((now - out["updated_at"]).dt.total_seconds() / 86400).fillna(0)
    stalled_mask = open_mask & (days_since_update >= stalled_days_threshold)
    unassigned_mask = out["assignee"].astype(str).str.strip().isin({"", "Unassigned", "None"})
    phase_norm = out["current_phase"].astype(str).map(_norm)
    critical_priority = out["priority"].astype(str).isin({"Crítica", "Critica"})
    critical_by_context = overdue_mask & phase_norm.isin(INITIAL_PHASES)
    critical_mask = critical_priority | critical_by_context

    open_total = int(open_mask.sum())
    phase_counts = out.loc[open_mask, "current_phase"].value_counts()
    bottleneck_phases = set(
        phase_counts[(phase_counts >= 3) & ((phase_counts / open_total) >= bottleneck_ratio)].index.tolist()
    ) if open_total else set()
    bottleneck_mask = out["current_phase"].isin(bottleneck_phases)

    out["risk_level"] = "Baixo"
    out.loc[risk_mask | unassigned_mask | bottleneck_mask, "risk_level"] = "Médio"
    out.loc[overdue_mask | critical_mask, "risk_level"] = "Alto"

    out["automation_alert"] = "Monitoramento"
    out.loc[overdue_mask, "automation_alert"] = "SLA vencido"
    out.loc[risk_mask & ~overdue_mask, "automation_alert"] = "SLA em risco"
    out.loc[stalled_mask, "automation_alert"] = "Card parado"
    out.loc[unassigned_mask, "automation_alert"] = "Sem responsável"
    out.loc[critical_mask, "automation_alert"] = "Prioridade crítica"
    out.loc[bottleneck_mask, "automation_alert"] = "Gargalo de workflow"

    out["recommended_action"] = out.apply(_build_recommendation, axis=1)
    return out

