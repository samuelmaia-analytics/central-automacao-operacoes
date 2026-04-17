from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd


def get_last_watermark(db_path: Path, table_name: str, watermark_column: str) -> pd.Timestamp | None:
    if not db_path.exists():
        return None

    query = f"SELECT MAX({watermark_column}) AS max_watermark FROM {table_name}"
    try:
        with duckdb.connect(str(db_path)) as conn:
            result = conn.execute(query).fetchone()
    except duckdb.Error:
        return None

    if not result or result[0] is None:
        return None
    return pd.Timestamp(result[0])


def apply_watermark_filter(
    df: pd.DataFrame,
    watermark_column: str,
    last_watermark: pd.Timestamp | None,
    lookback_hours: int = 0,
) -> tuple[pd.DataFrame, pd.Timestamp | None]:
    if last_watermark is None:
        return df, None

    if watermark_column not in df.columns:
        raise ValueError(f"Coluna de watermark ausente: {watermark_column}")

    lookback = max(0, int(lookback_hours))
    cutoff = last_watermark - pd.Timedelta(hours=lookback)

    column_ts = pd.to_datetime(df[watermark_column], errors="coerce")
    filtered = df[column_ts.notna() & (column_ts > cutoff)].copy()
    return filtered, cutoff
