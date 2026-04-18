from __future__ import annotations

from pathlib import Path

from integrations.pipefy.pipefy_pipeline import PIPEFY_OUTPUT_FILE, run_pipefy_pipeline


def test_pipefy_pipeline_runs_in_mock_mode() -> None:
    df = run_pipefy_pipeline(use_mock=True)

    assert not df.empty
    assert "automation_alert" in df.columns
    assert "recommended_action" in df.columns
    assert set(df["source_system"].unique()) == {"pipefy"}
    assert Path(PIPEFY_OUTPUT_FILE).exists()
