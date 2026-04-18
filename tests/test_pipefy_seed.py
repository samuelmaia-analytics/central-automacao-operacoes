from __future__ import annotations

from integrations.pipefy.pipefy_seed import _build_seed_cards, _select_phase_targets


def test_build_seed_cards_default_size() -> None:
    cards = _build_seed_cards(seed_count=12)
    assert len(cards) == 12
    assert any(card.phase_bucket == "done" for card in cards)
    assert all(card.title for card in cards)


def test_select_phase_targets_with_three_phases() -> None:
    phases = [
        {"id": "1", "name": "Entrada"},
        {"id": "2", "name": "Fazendo"},
        {"id": "3", "name": "Concluído"},
    ]
    targets = _select_phase_targets(phases)
    assert targets["start"] == "1"
    assert targets["doing"] == "2"
    assert targets["done"] == "3"
