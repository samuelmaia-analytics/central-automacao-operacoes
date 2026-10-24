from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd


@dataclass(frozen=True)
class QualitySummary:
    total_registros: int
    colunas: int
    ids_duplicados: int
    linhas_sem_first_response: int
    linhas_data_inconsistente: int
    top_5_percentual_nulos: dict[str, float]


def build_quality_summary(df: pd.DataFrame) -> QualitySummary:
    null_ratio = (df.isna().mean() * 100).sort_values(ascending=False).head(5)
    duplicated_ids = int(df["ticket_id"].duplicated().sum()) if "ticket_id" in df.columns else 0
    sem_first_response = int(df["first_response_time"].isna().sum()) if "first_response_time" in df.columns else 0

    linhas_data_inconsistente = 0
    if {"first_response_time", "time_to_resolution"}.issubset(df.columns):
        invalid = (
            df["first_response_time"].notna()
            & df["time_to_resolution"].notna()
            & (df["time_to_resolution"] < df["first_response_time"])
        )
        linhas_data_inconsistente = int(invalid.sum())

    return QualitySummary(
        total_registros=int(len(df)),
        colunas=int(df.shape[1]),
        ids_duplicados=duplicated_ids,
        linhas_sem_first_response=sem_first_response,
        linhas_data_inconsistente=linhas_data_inconsistente,
        top_5_percentual_nulos={k: round(float(v), 2) for k, v in null_ratio.items()},
    )


def save_quality_summary(summary: QualitySummary, output_path: Path) -> None:
    output_path.write_text(json.dumps(asdict(summary), ensure_ascii=True, indent=2), encoding="utf-8")


def require_publishable_data(df: pd.DataFrame, summary: QualitySummary) -> None:
    """Block critical integrity failures before any analytical output is written.

    Missing first response is allowed for tickets still awaiting service; it is
    reported as a quality/coverage indicator rather than silently discarded.
    """
    failures = []
    if "ticket_id" not in df.columns:
        failures.append("ticket_id ausente")
    elif df["ticket_id"].isna().any() or df["ticket_id"].astype(str).str.strip().eq("").any():
        failures.append("ticket_id nulo ou vazio")
    if summary.ids_duplicados:
        failures.append("ticket_id duplicado")
    if summary.linhas_data_inconsistente:
        failures.append("resolucao anterior a primeira resposta")
    if failures:
        raise ValueError("Publicacao bloqueada por qualidade: " + "; ".join(failures))
