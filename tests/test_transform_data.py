from __future__ import annotations

import pandas as pd

from src.transformation.transform_data import transform_tickets


def test_transform_adds_required_columns() -> None:
    df = pd.DataFrame(
        {
            "Ticket ID": [1],
            "Ticket Type": ["Technical issue"],
            "Ticket Status": ["Open"],
            "Ticket Priority": ["High"],
            "Ticket Channel": ["Chat"],
            "Ticket Description": ["issue persists again"],
            "First Response Time": ["2024-01-01 10:00:00"],
            "Time to Resolution": [None],
            "Customer Email": ["a@x.com"],
        }
    )
    result = transform_tickets(df, reference_ts=pd.Timestamp("2024-01-02 10:00:00"))
    expected = {
        "tempo_de_resolucao",
        "status_sla",
        "risco_atraso",
        "prioridade_automatica",
        "categoria_operacional",
        "flag_retrabalho",
        "flag_demanda_critica",
    }
    assert expected.issubset(set(result.columns))
    assert bool(result.loc[0, "flag_retrabalho"]) is True
