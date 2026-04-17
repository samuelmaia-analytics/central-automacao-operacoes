from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from src.database.duckdb_pipeline import upsert_incremental_to_duckdb


def test_upsert_incremental_is_idempotent(tmp_path: Path) -> None:
    db_path = tmp_path / "test.duckdb"
    df = pd.DataFrame(
        {
            "ticket_id": [1, 2, 3],
            "status_sla": ["Dentro do SLA", "SLA vencido", "Dentro do SLA"],
            "ticket_status": ["Closed", "Open", "Closed"],
            "flag_demanda_critica": [False, True, False],
            "tempo_de_resolucao": [2.0, 12.0, 3.0],
        }
    )

    upsert_incremental_to_duckdb(
        df=df,
        db_path=db_path,
        snapshot_date="2026-04-16",
        run_id="run_1",
        source_hash="abc",
    )
    upsert_incremental_to_duckdb(
        df=df,
        db_path=db_path,
        snapshot_date="2026-04-16",
        run_id="run_2",
        source_hash="abc",
    )

    with duckdb.connect(str(db_path)) as conn:
        loaded = conn.execute("SELECT COUNT(*) FROM analytics_tickets").fetchone()[0]
    assert loaded == 3
