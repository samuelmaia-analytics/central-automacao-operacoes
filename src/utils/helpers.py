from __future__ import annotations

import re
from pathlib import Path


def ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def to_snake_case(value: str) -> str:
    value = value.strip().replace("/", " ")
    value = re.sub(r"[^0-9a-zA-Z]+", "_", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"_+", "_", value)
    return value.strip("_").lower()
