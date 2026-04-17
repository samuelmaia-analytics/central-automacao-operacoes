from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from src.utils.helpers import ensure_directory


def persist_to_duckdb(df: pd.DataFrame, db_path: Path, table_name: str = "analytics_tickets") -> None:
    ensure_directory(db_path.parent)
    with duckdb.connect(str(db_path)) as conn:
        conn.execute(f"CREATE OR REPLACE TABLE {table_name} AS SELECT * FROM df")


def upsert_incremental_to_duckdb(
    df: pd.DataFrame,
    db_path: Path,
    snapshot_date: str,
    run_id: str,
    source_hash: str,
    table_name: str = "analytics_tickets",
) -> None:
    ensure_directory(db_path.parent)
    load_df = df.copy()
    load_df["snapshot_date"] = snapshot_date
    load_df["run_id"] = run_id
    load_df["source_hash"] = source_hash
    load_df["ingested_at"] = pd.Timestamp.utcnow().tz_localize(None)

    with duckdb.connect(str(db_path)) as conn:
        conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} AS
            SELECT * FROM load_df LIMIT 0
            """
        )
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS snapshot_date DATE")
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS run_id VARCHAR")
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS source_hash VARCHAR")
        conn.execute(f"ALTER TABLE {table_name} ADD COLUMN IF NOT EXISTS ingested_at TIMESTAMP")
        conn.execute(f"DELETE FROM {table_name} WHERE snapshot_date IS NULL")
        conn.execute(
            f"""
            DELETE FROM {table_name}
            WHERE snapshot_date = ? AND source_hash = ?
            """,
            [snapshot_date, source_hash],
        )
        conn.register("load_df", load_df)
        conn.execute(
            f"""
            INSERT INTO {table_name}
            SELECT * FROM load_df
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id VARCHAR,
                snapshot_date DATE,
                source_hash VARCHAR,
                source_path VARCHAR,
                records_loaded BIGINT,
                loaded_at TIMESTAMP
            )
            """
        )


def insert_run_audit(
    db_path: Path,
    run_id: str,
    snapshot_date: str,
    source_hash: str,
    source_path: str,
    records_loaded: int,
    max_watermark_loaded: pd.Timestamp | None = None,
) -> None:
    with duckdb.connect(str(db_path)) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id VARCHAR,
                snapshot_date DATE,
                source_hash VARCHAR,
                source_path VARCHAR,
                records_loaded BIGINT,
                max_watermark_loaded TIMESTAMP,
                loaded_at TIMESTAMP
            )
            """
        )
        conn.execute("ALTER TABLE pipeline_runs ADD COLUMN IF NOT EXISTS max_watermark_loaded TIMESTAMP")
        conn.execute(
            """
            DELETE FROM pipeline_runs
            WHERE run_id = ?
            """,
            [run_id],
        )
        conn.execute(
            """
            INSERT INTO pipeline_runs (
                run_id,
                snapshot_date,
                source_hash,
                source_path,
                records_loaded,
                max_watermark_loaded,
                loaded_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                run_id,
                snapshot_date,
                source_hash,
                source_path,
                records_loaded,
                max_watermark_loaded,
                pd.Timestamp.utcnow().tz_localize(None),
            ],
        )


def run_sql_file(db_path: Path, sql_path: Path) -> None:
    with duckdb.connect(str(db_path)) as conn:
        sql = sql_path.read_text(encoding="utf-8")
        conn.execute(sql)
