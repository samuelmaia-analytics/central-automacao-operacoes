from __future__ import annotations

from src.automation.sla_rules import calculate_sla_risk, classify_sla_status, get_sla_hours


def test_get_sla_hours_defaults() -> None:
    assert get_sla_hours("critical") == 24
    assert get_sla_hours("unknown") == 72


def test_classify_sla_status() -> None:
    assert classify_sla_status(10, 24, False) == "Dentro do SLA"
    assert classify_sla_status(30, 24, False) == "SLA vencido"
    assert classify_sla_status(None, 24, True) == "SLA em risco"


def test_calculate_sla_risk() -> None:
    assert calculate_sla_risk(10, 24) == "Baixo"
    assert calculate_sla_risk(20, 24) == "Medio"
    assert calculate_sla_risk(30, 24) == "Alto"
