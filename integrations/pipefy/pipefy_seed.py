from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any

import pandas as pd

from integrations.pipefy.pipefy_client import PipefyClient, PipefyGraphQLError
from integrations.pipefy.pipefy_queries import (
    create_card_mutation,
    get_pipe_metadata_query,
    move_card_to_phase_mutation,
    update_card_assignee_mutation,
    update_card_field_mutation,
)

CATEGORIES = ["Suporte", "Financeiro", "Comercial", "Dados", "Operações", "Sistemas", "Cadastro"]
PRIORITIES = ["Baixa", "Média", "Alta", "Crítica"]
BASE_TITLES = [
    "Revisar solicitação operacional",
    "Ajustar cadastro de cliente",
    "Validar fluxo de atendimento",
    "Corrigir inconsistência de dados",
    "Atualizar processo interno",
    "Tratar demanda pendente",
    "Analisar ticket crítico",
]


@dataclass(frozen=True)
class SeedCard:
    title: str
    due_date: str
    phase_bucket: str
    category: str
    priority: str


def _build_seed_cards(seed_count: int = 30) -> list[SeedCard]:
    cards: list[SeedCard] = []
    now = pd.Timestamp.utcnow().tz_localize(None)
    for idx in range(seed_count):
        category = CATEGORIES[idx % len(CATEGORIES)]
        priority = PRIORITIES[idx % len(PRIORITIES)]
        base_title = BASE_TITLES[idx % len(BASE_TITLES)]
        due_offset_days = (idx % 10) - 3  # include overdue/risk/ok
        due_date = (now + pd.Timedelta(days=due_offset_days, hours=8)).isoformat() + "Z"
        if idx % 7 == 0:
            phase_bucket = "done"
        elif idx % 3 == 0:
            phase_bucket = "doing"
        else:
            phase_bucket = "start"
        title = f"[{category}] {base_title} | Prioridade: {priority} | Seed {idx + 1:02d}"
        cards.append(
            SeedCard(
                title=title,
                due_date=due_date,
                phase_bucket=phase_bucket,
                category=category,
                priority=priority,
            )
        )
    return cards


def _select_phase_targets(phases: list[dict[str, Any]]) -> dict[str, str | None]:
    if not phases:
        return {"start": None, "doing": None, "done": None}

    first = str(phases[0].get("id"))
    second = str(phases[1].get("id")) if len(phases) >= 2 else first
    third = str(phases[-1].get("id")) if len(phases) >= 3 else second
    return {"start": first, "doing": second, "done": third}


def seed_pipefy_cards(pipe_id: str, seed_count: int = 30, randomize: bool = False) -> int:
    client = PipefyClient(use_mock=False)
    pipe_meta = client.execute_query(get_pipe_metadata_query(), {"pipe_id": pipe_id})
    phases = pipe_meta.get("data", {}).get("pipe", {}).get("phases", [])
    users = pipe_meta.get("data", {}).get("pipe", {}).get("users", [])
    fields = pipe_meta.get("data", {}).get("pipe", {}).get("start_form_fields", [])
    phase_targets = _select_phase_targets(phases if isinstance(phases, list) else [])
    first_user_id = str(users[0].get("id")) if isinstance(users, list) and users else None

    field_map: dict[str, str] = {}
    if isinstance(fields, list):
        for field in fields:
            if not isinstance(field, dict):
                continue
            label = str(field.get("label", "")).strip().lower()
            field_id = str(field.get("id", "")).strip()
            if not field_id:
                continue
            if label in {"categoria", "category"}:
                field_map["categoria"] = field_id
            if label in {"prioridade", "priority"}:
                field_map["prioridade"] = field_id

    cards = _build_seed_cards(seed_count=seed_count)
    if randomize:
        random.shuffle(cards)

    created = 0
    moved = 0

    def _safe_move(card_id: str, destination_phase_id: str | None) -> bool:
        if not destination_phase_id:
            return False
        move_payload = {"input": {"card_id": str(card_id), "destination_phase_id": str(destination_phase_id)}}
        try:
            client.execute_query(move_card_to_phase_mutation(), move_payload)
            return True
        except PipefyGraphQLError:
            return False

    for item in cards:
        payload = {
            "input": {
                "pipe_id": pipe_id,
                "title": item.title,
                "due_date": item.due_date,
            }
        }
        response = client.execute_query(create_card_mutation(), payload)
        card_id = response.get("data", {}).get("createCard", {}).get("card", {}).get("id")
        if not card_id:
            continue
        created += 1
        if first_user_id and created % 3 != 0:
            try:
                client.execute_query(
                    update_card_assignee_mutation(),
                    {"input": {"id": str(card_id), "assignee_ids": [first_user_id]}},
                )
            except PipefyGraphQLError:
                pass

        if field_map.get("categoria"):
            try:
                client.execute_query(
                    update_card_field_mutation(),
                    {
                        "input": {
                            "card_id": str(card_id),
                            "field_id": field_map["categoria"],
                            "new_value": [item.category],
                        }
                    },
                )
            except PipefyGraphQLError:
                pass
        if field_map.get("prioridade"):
            try:
                client.execute_query(
                    update_card_field_mutation(),
                    {
                        "input": {
                            "card_id": str(card_id),
                            "field_id": field_map["prioridade"],
                            "new_value": [item.priority],
                        }
                    },
                )
            except PipefyGraphQLError:
                pass

        if item.phase_bucket == "start":
            continue
        if item.phase_bucket == "doing":
            if _safe_move(str(card_id), phase_targets.get("doing")):
                moved += 1
            continue
        if item.phase_bucket == "done":
            moved_to_doing = _safe_move(str(card_id), phase_targets.get("doing"))
            moved_to_done = _safe_move(str(card_id), phase_targets.get("done"))
            if moved_to_doing or moved_to_done:
                moved += 1
    print(f"Seed criado no Pipefy: {created} cards | Movimentados de fase: {moved}")
    return created
