from __future__ import annotations

from src.config.settings import CRITICAL_WAITING_HOURS


def classify_priority_automatically(original_priority: str, status: str, age_hours: float | None) -> str:
    base_priority = str(original_priority).lower()
    status_normalized = str(status).lower()

    if base_priority == "critical":
        return "critical"
    if (
        base_priority == "high"
        and status_normalized in {"open", "pending customer response"}
        and (age_hours or 0) > CRITICAL_WAITING_HOURS
    ):
        return "critical"
    if base_priority in {"high", "medium", "low"}:
        return base_priority
    return "medium"


def is_critical_demand(priority_auto: str, status_sla: str) -> bool:
    return priority_auto == "critical" or status_sla == "SLA vencido"
