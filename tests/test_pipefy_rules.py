from __future__ import annotations

import pandas as pd

from src.automation.pipefy_rules import apply_pipefy_automation_rules


def _base_df() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "ticket_id": "1",
                "title": "Vencido",
                "priority": "Alta",
                "status": "open",
                "current_phase": "Triagem",
                "assignee": "Ana",
                "created_at": "2026-04-01T10:00:00",
                "updated_at": "2026-04-10T10:00:00",
                "due_date": "2026-04-12T10:00:00",
            },
            {
                "ticket_id": "2",
                "title": "Risco",
                "priority": "Média",
                "status": "open",
                "current_phase": "Em análise",
                "assignee": "Bruno",
                "created_at": "2026-04-10T10:00:00",
                "updated_at": "2026-04-16T10:00:00",
                "due_date": "2026-04-18T10:00:00",
            },
            {
                "ticket_id": "3",
                "title": "Sem dono",
                "priority": "Baixa",
                "status": "open",
                "current_phase": "Em execução",
                "assignee": "Unassigned",
                "created_at": "2026-04-11T10:00:00",
                "updated_at": "2026-04-11T10:00:00",
                "due_date": "2026-04-22T10:00:00",
            },
        ]
    )


def test_pipefy_rules_sla_overdue_and_risk() -> None:
    df = apply_pipefy_automation_rules(_base_df(), reference_ts=pd.Timestamp("2026-04-17 12:00:00"))
    assert df.loc[df["ticket_id"] == "1", "sla_status"].item() == "SLA vencido"
    assert df.loc[df["ticket_id"] == "2", "sla_status"].item() == "SLA em risco"


def test_pipefy_rules_unassigned_and_recommendation() -> None:
    df = apply_pipefy_automation_rules(_base_df(), reference_ts=pd.Timestamp("2026-04-17 12:00:00"))
    row = df[df["ticket_id"] == "3"].iloc[0]
    assert row["automation_alert"] == "Sem responsável"
    assert row["recommended_action"] == "Atribuir responsável"
