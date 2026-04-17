from __future__ import annotations

import pandas as pd

from src.analytics.kpis import compute_kpis


def test_compute_kpis_basic() -> None:
    df = pd.DataFrame(
        {
            "ticket_id": [1, 2, 3],
            "status_sla": ["Dentro do SLA", "SLA vencido", "SLA vencido"],
            "ticket_status": ["Closed", "Open", "Pending Customer Response"],
            "flag_demanda_critica": [False, True, True],
            "tempo_de_resolucao": [2.0, 10.0, None],
            "tipo_alerta": ["Monitorar", "SLA vencido", "Demanda critica"],
        }
    )
    kpis = compute_kpis(df)
    assert kpis["total_tickets"] == 3
    assert round(kpis["percentual_fora_sla"], 2) == 66.67
    assert kpis["backlog_aberto"] == 2
