from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from unittest.mock import MagicMock

import pandas as pd
import pytest

import main
from src.config.settings import Settings
from src.ingestion.load_data import ingest_dataset
from src.quality.data_quality import build_quality_summary, require_publishable_data


def candidate():
    return pd.DataFrame(
        {
            "ticket_id": [1, 2],
            "first_response_time": pd.to_datetime(["2026-01-02", None]),
            "time_to_resolution": pd.to_datetime(["2026-01-03", None]),
        }
    )


@pytest.mark.parametrize("defect", ["duplicate", "null", "empty", "chronology", "missing"])
def test_quality_refusal_preserves_published_files_and_database(tmp_path, monkeypatch, defect):
    df = candidate()
    if defect == "duplicate":
        df["ticket_id"] = [1, 1]
    elif defect == "null":
        df.loc[0, "ticket_id"] = None
    elif defect == "empty":
        df["ticket_id"] = ["", "2"]
    elif defect == "missing":
        df = df.drop(columns="ticket_id")
    else:
        df.loc[0, "time_to_resolution"] = pd.Timestamp("2026-01-01")
    settings = replace(Settings(), **{name: tmp_path / name for name in Settings.__dataclass_fields__})
    preserved = [
        settings.processed_dataset_file,
        settings.processed_dataset_csv,
        settings.alerts_output_file,
        settings.report_output_file,
        settings.latest_run_manifest_file,
        settings.db_path,
        settings.data_quality_output_file,
    ]
    for path in preserved:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"previous approved publication")
    monkeypatch.setattr(main, "Settings", lambda: settings)
    monkeypatch.setattr(main, "build_source_hash", lambda _: "source-hash")
    monkeypatch.setattr(main, "ingest_dataset", lambda _: df)
    monkeypatch.setattr(main, "transform_tickets", lambda *args, **kwargs: df)
    watermark = MagicMock()
    monkeypatch.setattr(main, "get_last_watermark", watermark)
    with pytest.raises(ValueError, match="Publicacao bloqueada"):
        main.run_pipeline(incremental_by_watermark=True)
    watermark.assert_not_called()
    assert all(path.read_bytes() == b"previous approved publication" for path in preserved)
    assert not list(settings.versioned_processed_dir.rglob("*.parquet"))


def test_missing_response_is_reported_but_allowed():
    df = candidate()
    summary = build_quality_summary(df)
    assert summary.linhas_sem_first_response == 1
    require_publishable_data(df, summary)


@pytest.mark.parametrize(
    "field,value",
    [
        ("Ticket ID", None),
        ("Ticket ID", "  "),
        ("First Response Time", "invalid-time"),
        ("Time to Resolution", "invalid-time"),
    ],
)
def test_ingestion_rejects_invalid_evidence_without_writing(tmp_path: Path, field, value):
    row = {
        "Ticket ID": 1,
        "Ticket Type": "technical",
        "Ticket Status": "Open",
        "Ticket Priority": "high",
        "Ticket Channel": "email",
        "Ticket Description": "issue",
        "First Response Time": "2026-01-01",
        "Time to Resolution": "2026-01-02",
    }
    row[field] = value
    source, output = tmp_path / "source.csv", tmp_path / "output.csv"
    pd.DataFrame([row]).to_csv(source, index=False)
    with pytest.raises(ValueError, match="Dataset invalido"):
        ingest_dataset(source, output)
    assert not output.exists()
