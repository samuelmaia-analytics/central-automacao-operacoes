from __future__ import annotations

import pandas as pd

from src.config.settings import PRIORITY_SLA_HOURS


def get_sla_hours(priority: str) -> int:
    return PRIORITY_SLA_HOURS.get(str(priority).lower(), PRIORITY_SLA_HOURS["medium"])


def classify_sla_status(resolution_hours: float | None, sla_hours: int, is_open: bool) -> str:
    if resolution_hours is None or pd.isna(resolution_hours):
        return "SLA em risco" if is_open else "Sem dados"
    return "SLA vencido" if resolution_hours > sla_hours else "Dentro do SLA"


def calculate_sla_risk(age_hours: float | None, sla_hours: int) -> str:
    if age_hours is None or pd.isna(age_hours):
        return "Indefinido"
    ratio = age_hours / sla_hours if sla_hours else 0
    if ratio >= 1:
        return "Alto"
    if ratio >= 0.75:
        return "Medio"
    return "Baixo"
