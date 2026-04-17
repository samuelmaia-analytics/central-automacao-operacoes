from __future__ import annotations

import argparse
import logging
from pathlib import Path

import pandas as pd

from src.analytics.kpis import compute_kpis
from src.automation.alert_generator import generate_alerts
from src.automation.report_generator import generate_markdown_report
from src.config.settings import (
    Settings,
)
from src.database.duckdb_pipeline import insert_run_audit, upsert_incremental_to_duckdb
from src.incremental.watermark import apply_watermark_filter, get_last_watermark
from src.ingestion.load_data import ingest_dataset
from src.quality.data_quality import build_quality_summary, save_quality_summary
from src.transformation.transform_data import transform_tickets
from src.utils.helpers import ensure_directory
from src.utils.logging_utils import configure_logging
from src.versioning.data_versioning import (
    RunMetadata,
    build_run_id,
    build_snapshot_date,
    build_source_hash,
    persist_manifests,
    persist_partition_snapshot,
)

LOGGER = logging.getLogger(__name__)


def run_pipeline(
    input_path: Path | None = None,
    reference_ts: pd.Timestamp | None = None,
    incremental_by_watermark: bool = False,
    watermark_column: str = "first_response_time",
    watermark_lookback_hours: int = 0,
) -> None:
    settings = Settings()
    ensure_directory(settings.processed_dataset_file.parent)
    ensure_directory(settings.alerts_output_file.parent)
    ensure_directory(settings.report_output_file.parent)
    ensure_directory(settings.versioned_processed_dir)
    ensure_directory(settings.latest_run_manifest_file.parent)

    source = input_path or settings.raw_dataset_file
    source_hash = build_source_hash(source)
    run_id = build_run_id()
    snapshot_date = build_snapshot_date(reference_ts)

    LOGGER.info("Iniciando ingestao do dataset: %s", source)
    raw_df = ingest_dataset(source)

    LOGGER.info("Aplicando transformacoes e regras de negocio")
    transformed_df = transform_tickets(raw_df, reference_ts=reference_ts)
    previous_watermark: pd.Timestamp | None = None
    applied_cutoff: pd.Timestamp | None = None
    if incremental_by_watermark:
        previous_watermark = get_last_watermark(settings.db_path, "analytics_tickets", watermark_column)
        transformed_df, applied_cutoff = apply_watermark_filter(
            transformed_df,
            watermark_column=watermark_column,
            last_watermark=previous_watermark,
            lookback_hours=watermark_lookback_hours,
        )
        LOGGER.info(
            "Modo incremental watermark ativo | coluna=%s | watermark_anterior=%s | cutoff=%s | registros=%s",
            watermark_column,
            previous_watermark,
            applied_cutoff,
            len(transformed_df),
        )

    transformed_df.to_parquet(settings.processed_dataset_file, index=False)
    transformed_df.to_csv(settings.processed_dataset_csv, index=False)
    LOGGER.info("Dataset tratado salvo em: %s", settings.processed_dataset_file)

    alerts_df = generate_alerts(transformed_df)
    alerts_df.to_csv(settings.alerts_output_file, index=False)

    analytics_df = transformed_df.merge(
        alerts_df[["ticket_id", "tipo_alerta", "acao_recomendada"]],
        on="ticket_id",
        how="left",
    )
    partition_path = persist_partition_snapshot(
        analytics_df=analytics_df,
        alerts_df=alerts_df,
        versioned_root_dir=settings.versioned_processed_dir,
        snapshot_date=snapshot_date,
        run_id=run_id,
    )
    kpis = compute_kpis(analytics_df)
    quality = build_quality_summary(analytics_df)

    report_content = generate_markdown_report(analytics_df, kpis, quality=quality)
    settings.report_output_file.write_text(report_content, encoding="utf-8")

    max_watermark_loaded: pd.Timestamp | None = None
    if not analytics_df.empty and watermark_column in analytics_df.columns:
        max_watermark_loaded = pd.to_datetime(analytics_df[watermark_column], errors="coerce").max()

    if not analytics_df.empty:
        upsert_incremental_to_duckdb(
            df=analytics_df,
            db_path=settings.db_path,
            snapshot_date=snapshot_date,
            run_id=run_id,
            source_hash=source_hash,
        )
    else:
        LOGGER.info("Nenhum registro novo para carga no DuckDB nesta execucao.")

    insert_run_audit(
        db_path=settings.db_path,
        run_id=run_id,
        snapshot_date=snapshot_date,
        source_hash=source_hash,
        source_path=str(source),
        records_loaded=len(analytics_df),
        max_watermark_loaded=max_watermark_loaded,
    )
    save_quality_summary(quality, settings.data_quality_output_file)
    run_metadata = RunMetadata(
        run_id=run_id,
        snapshot_date=snapshot_date,
        source_path=str(source),
        source_hash=source_hash,
        records=len(analytics_df),
        generated_at_utc=pd.Timestamp.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        partition_path=str(partition_path),
        incremental_by_watermark=incremental_by_watermark,
        previous_watermark=str(previous_watermark) if previous_watermark is not None else None,
        applied_cutoff=str(applied_cutoff) if applied_cutoff is not None else None,
        max_watermark_loaded=str(max_watermark_loaded) if max_watermark_loaded is not None else None,
    )
    persist_manifests(
        metadata=run_metadata,
        latest_manifest_file=settings.latest_run_manifest_file,
        history_file=settings.run_history_file,
    )
    LOGGER.info("Resumo de qualidade salvo em: %s", settings.data_quality_output_file)
    LOGGER.info("Pipeline executado com sucesso | run_id=%s | snapshot_date=%s", run_id, snapshot_date)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pipeline de automacao operacional e analytics")
    parser.add_argument("--input", type=Path, help="Caminho para CSV de entrada")
    parser.add_argument(
        "--reference-ts",
        type=str,
        help="Timestamp de referencia ISO-8601 para calculo de idade do ticket",
    )
    parser.add_argument("--log-level", default="INFO", help="Nivel de log: DEBUG, INFO, WARNING, ERROR")
    parser.add_argument(
        "--incremental-by-watermark",
        action="store_true",
        help="Carrega apenas registros com timestamp maior que watermark salvo no DuckDB",
    )
    parser.add_argument(
        "--watermark-column",
        default="first_response_time",
        help="Coluna de timestamp para watermark incremental",
    )
    parser.add_argument(
        "--watermark-lookback-hours",
        type=int,
        default=0,
        help="Janela de reprocessamento (horas) para capturar atraso de ingestao",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    configure_logging(args.log_level)
    reference_ts = pd.Timestamp(args.reference_ts) if args.reference_ts else None
    run_pipeline(
        input_path=args.input,
        reference_ts=reference_ts,
        incremental_by_watermark=args.incremental_by_watermark,
        watermark_column=args.watermark_column,
        watermark_lookback_hours=args.watermark_lookback_hours,
    )


if __name__ == "__main__":
    main()
