from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config.settings import RAW_REQUIRED_COLUMNS
from src.utils.helpers import ensure_directory


def load_csv_dataset(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def validate_required_columns(df: pd.DataFrame, required_columns: set[str] | None = None) -> None:
    required = required_columns or RAW_REQUIRED_COLUMNS
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Dataset invalido. Colunas obrigatorias ausentes: {missing}")


def ingest_dataset(input_path: Path, output_path: Path | None = None) -> pd.DataFrame:
    df = load_csv_dataset(input_path)
    validate_required_columns(df)
    if "Ticket ID" in df.columns and df["Ticket ID"].duplicated().any():
        raise ValueError("Dataset invalido. Ha Ticket ID duplicado no arquivo bruto.")
    if df["Ticket ID"].isna().any() or df["Ticket ID"].astype(str).str.strip().eq("").any():
        raise ValueError("Dataset invalido. Ticket ID nulo ou vazio.")
    for column in ("First Response Time", "Time to Resolution"):
        values = df[column]
        present = values.notna() & values.astype(str).str.strip().ne("")
        parsed = pd.to_datetime(values, errors="coerce")
        if (present & parsed.isna()).any():
            raise ValueError(f"Dataset invalido. Timestamp nao interpretavel em {column}.")
    if output_path:
        ensure_directory(output_path.parent)
        df.to_csv(output_path, index=False)
    return df
