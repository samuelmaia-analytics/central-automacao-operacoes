from __future__ import annotations

import pandas as pd

from src.quality.data_quality import build_quality_summary


def test_build_quality_summary_counts_invalid_rows() -> None:
    df = pd.DataFrame(
        {
            "ticket_id": [1, 1, 2],
            "first_response_time": pd.to_datetime(["2024-01-02", None, "2024-01-03"]),
            "time_to_resolution": pd.to_datetime(["2024-01-01", None, "2024-01-05"]),
            "x": [1, None, None],
        }
    )
    summary = build_quality_summary(df)
    assert summary.ids_duplicados == 1
    assert summary.linhas_sem_first_response == 1
    assert summary.linhas_data_inconsistente == 1
