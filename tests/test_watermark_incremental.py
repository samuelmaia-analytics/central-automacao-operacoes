from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from src.incremental.watermark import apply_watermark_filter, get_last_watermark


def test_apply_watermark_filter_returns_only_new_rows() -> None:
    df = pd.DataFrame(
        {
            "ticket_id": [1, 2, 3],
            "first_response_time": pd.to_datetime(
                ["2026-01-01 00:00:00", "2026-01-02 00:00:00", "2026-01-03 00:00:00"]
            ),
        }
    )
    filtered, cutoff = apply_watermark_filter(
        df=df,
        watermark_column="first_response_time",
        last_watermark=pd.Timestamp("2026-01-02 00:00:00"),
        lookback_hours=0,
    )
    assert cutoff == pd.Timestamp("2026-01-02 00:00:00")
    assert filtered["ticket_id"].tolist() == [3]


def test_get_last_watermark_from_duckdb(tmp_path: Path) -> None:
    db_path = tmp_path / "wm.duckdb"
    with duckdb.connect(str(db_path)) as conn:
        conn.execute("CREATE TABLE analytics_tickets (first_response_time TIMESTAMP)")
        conn.execute("INSERT INTO analytics_tickets VALUES ('2026-01-01 00:00:00'), ('2026-01-03 00:00:00')")
    value = get_last_watermark(db_path, "analytics_tickets", "first_response_time")
    assert value == pd.Timestamp("2026-01-03 00:00:00")
