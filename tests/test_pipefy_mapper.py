from __future__ import annotations

import json
from pathlib import Path

from integrations.pipefy.pipefy_mapper import map_pipefy_cards_to_dataframe


def test_pipefy_mapper_maps_sample_cards() -> None:
    sample_path = Path("data/samples/pipefy_cards_sample.json")
    raw = json.loads(sample_path.read_text(encoding="utf-8"))
    df = map_pipefy_cards_to_dataframe(raw)

    assert len(df) >= 30
    assert "ticket_id" in df.columns
    assert "source_system" in df.columns
    assert set(df["source_system"].unique()) == {"pipefy"}


def test_pipefy_mapper_handles_missing_fields() -> None:
    raw = {
        "cards": [
            {
                "id": "X-1",
                "title": "Card sem campos",
                "current_phase": {"name": "Nova solicitação"},
                "created_at": "2026-04-10T10:00:00Z",
            }
        ]
    }
    df = map_pipefy_cards_to_dataframe(raw)

    assert len(df) == 1
    assert df.loc[0, "assignee"] == "Unassigned"
    assert df.loc[0, "category"] == "General"
    assert df.loc[0, "priority"] in {"Baixa", "Média", "Alta", "Crítica"}
