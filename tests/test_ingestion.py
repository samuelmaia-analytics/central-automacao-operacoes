from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.ingestion.load_data import ingest_dataset


def test_ingest_raises_on_duplicated_ticket_id(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "Ticket ID": [1, 1],
            "Ticket Type": ["Technical issue", "Technical issue"],
            "Ticket Status": ["Open", "Open"],
            "Ticket Priority": ["High", "High"],
            "Ticket Channel": ["Chat", "Chat"],
            "Ticket Description": ["a", "b"],
            "First Response Time": ["2024-01-01", "2024-01-01"],
            "Time to Resolution": [None, None],
        }
    )
    file_path = tmp_path / "dup.csv"
    df.to_csv(file_path, index=False)
    with pytest.raises(ValueError, match="Ticket ID duplicado"):
        ingest_dataset(file_path)
