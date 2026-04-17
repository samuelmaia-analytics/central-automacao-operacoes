from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.utils.helpers import ensure_directory


@dataclass(frozen=True)
class RunMetadata:
    run_id: str
    snapshot_date: str
    source_path: str
    source_hash: str
    records: int
    generated_at_utc: str
    partition_path: str
    incremental_by_watermark: bool = False
    previous_watermark: str | None = None
    applied_cutoff: str | None = None
    max_watermark_loaded: str | None = None


def build_source_hash(source_path: Path) -> str:
    hasher = hashlib.sha256()
    with source_path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            hasher.update(chunk)
    return hasher.hexdigest()


def build_run_id() -> str:
    return datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")


def build_snapshot_date(reference_ts: pd.Timestamp | None = None) -> str:
    ts = reference_ts or pd.Timestamp.utcnow()
    return ts.strftime("%Y-%m-%d")


def persist_partition_snapshot(
    analytics_df: pd.DataFrame,
    alerts_df: pd.DataFrame,
    versioned_root_dir: Path,
    snapshot_date: str,
    run_id: str,
) -> Path:
    partition_dir = versioned_root_dir / f"snapshot_date={snapshot_date}" / f"run_id={run_id}"
    ensure_directory(partition_dir)
    analytics_df.to_parquet(partition_dir / "analytics_tickets.parquet", index=False)
    alerts_df.to_parquet(partition_dir / "operational_alerts.parquet", index=False)
    return partition_dir


def persist_manifests(metadata: RunMetadata, latest_manifest_file: Path, history_file: Path) -> None:
    ensure_directory(latest_manifest_file.parent)
    latest_manifest_file.write_text(json.dumps(asdict(metadata), ensure_ascii=True, indent=2), encoding="utf-8")
    with history_file.open("a", encoding="utf-8") as out:
        out.write(json.dumps(asdict(metadata), ensure_ascii=True) + "\n")
