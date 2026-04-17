from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
OUTPUTS_DIR = DATA_DIR / "outputs"
MANIFESTS_DIR = OUTPUTS_DIR / "manifests"
REPORTS_DIR = PROJECT_ROOT / "reports"
SQL_DIR = PROJECT_ROOT / "sql"
DB_PATH = OUTPUTS_DIR / "operations_analytics.duckdb"

RAW_DATASET_FILE = RAW_DIR / "customer_support_tickets.csv"
PROCESSED_DATASET_FILE = PROCESSED_DIR / "tickets_enriched.parquet"
PROCESSED_DATASET_CSV = PROCESSED_DIR / "tickets_enriched.csv"
VERSIONED_PROCESSED_DIR = PROCESSED_DIR / "snapshots"
ALERTS_OUTPUT_FILE = OUTPUTS_DIR / "operational_alerts.csv"
REPORT_OUTPUT_FILE = REPORTS_DIR / "executive_report.md"
DATA_QUALITY_OUTPUT_FILE = OUTPUTS_DIR / "data_quality_summary.json"
LATEST_RUN_MANIFEST_FILE = MANIFESTS_DIR / "latest_run.json"
RUN_HISTORY_FILE = MANIFESTS_DIR / "run_history.jsonl"

RAW_REQUIRED_COLUMNS = {
    "Ticket ID",
    "Ticket Type",
    "Ticket Status",
    "Ticket Priority",
    "Ticket Channel",
    "Ticket Description",
    "First Response Time",
    "Time to Resolution",
}

PRIORITY_SLA_HOURS = {
    "critical": 24,
    "high": 48,
    "medium": 72,
    "low": 96,
}

CRITICAL_WAITING_HOURS = 12


@dataclass(frozen=True)
class Settings:
    project_root: Path = PROJECT_ROOT
    raw_dataset_file: Path = RAW_DATASET_FILE
    processed_dataset_file: Path = PROCESSED_DATASET_FILE
    processed_dataset_csv: Path = PROCESSED_DATASET_CSV
    versioned_processed_dir: Path = VERSIONED_PROCESSED_DIR
    alerts_output_file: Path = ALERTS_OUTPUT_FILE
    report_output_file: Path = REPORT_OUTPUT_FILE
    data_quality_output_file: Path = DATA_QUALITY_OUTPUT_FILE
    latest_run_manifest_file: Path = LATEST_RUN_MANIFEST_FILE
    run_history_file: Path = RUN_HISTORY_FILE
    db_path: Path = DB_PATH
