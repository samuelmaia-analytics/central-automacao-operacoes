from __future__ import annotations

import os
import unicodedata
import re
from typing import Any

import pandas as pd

TARGET_COLUMNS = [
    "ticket_id",
    "title",
    "source_system",
    "category",
    "priority",
    "status",
    "current_phase",
    "assignee",
    "created_at",
    "updated_at",
    "due_date",
    "closed_at",
    "days_open",
    "sla_status",
    "risk_level",
    "automation_alert",
    "recommended_action",
    "card_url",
]

OPEN_PHASE_NAMES = {
    "nova solicitacao",
    "triagem",
    "em analise",
    "em execucao",
    "aguardando cliente",
}

CLOSED_PHASE_NAMES = {"resolvido", "cancelado"}
VALID_PRIORITIES = {"Baixa", "Média", "Alta", "Crítica"}
VALID_CATEGORIES = {"Suporte", "Financeiro", "Comercial", "Dados", "Operações", "Sistemas", "Cadastro"}


def _norm(value: Any) -> str:
    text = str(value or "").strip().lower()
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return " ".join(normalized.split())


def _parse_date(value: Any) -> pd.Timestamp | pd.NaT:
    if value in (None, "", "null"):
        return pd.NaT
    return pd.to_datetime(value, errors="coerce", utc=True).tz_convert(None)


def _extract_cards(raw_data: dict[str, Any] | list[dict[str, Any]]) -> list[dict[str, Any]]:
    if isinstance(raw_data, list):
        return raw_data
    if not isinstance(raw_data, dict):
        return []

    cards = raw_data.get("cards")
    if isinstance(cards, list):
        return cards

    data_cards = raw_data.get("data", {}).get("pipe", {}).get("cards", {})
    if isinstance(data_cards, list):
        return data_cards

    edges = data_cards.get("edges") if isinstance(data_cards, dict) else None
    if isinstance(edges, list):
        return [edge.get("node", {}) for edge in edges if isinstance(edge, dict)]

    top_cards = raw_data.get("data", {}).get("cards", {})
    top_edges = top_cards.get("edges") if isinstance(top_cards, dict) else None
    if isinstance(top_edges, list):
        return [edge.get("node", {}) for edge in top_edges if isinstance(edge, dict)]

    return []


def _extract_field_value(card: dict[str, Any], candidates: set[str]) -> str:
    fields = card.get("fields", [])
    if not isinstance(fields, list):
        return ""
    for item in fields:
        if not isinstance(item, dict):
            continue
        name = _norm(item.get("name") or item.get("field") or item.get("key"))
        if name in candidates:
            return str(item.get("value", "")).strip()
    return ""


def _infer_category(card: dict[str, Any], phase_name: str) -> str:
    field_category = _extract_field_value(card, {"categoria", "category", "tipo"})
    if field_category in VALID_CATEGORIES:
        return field_category

    labels = card.get("labels") or []
    for label in labels:
        name = str((label or {}).get("name", "")).strip()
        if name in VALID_CATEGORIES:
            return name

    phase_norm = _norm(phase_name)
    title = str(card.get("title", ""))
    match = re.search(r"\[([^\]]+)\]", title)
    if match:
        possible = match.group(1).strip()
        if possible in VALID_CATEGORIES:
            return possible
    if "cliente" in phase_norm:
        return "Suporte"
    if "analise" in phase_norm:
        return "Dados"
    if "execucao" in phase_norm:
        return "Operações"
    return "General"


def _infer_priority(card: dict[str, Any], due_date: pd.Timestamp | pd.NaT, category: str, phase_name: str) -> str:
    priority = _extract_field_value(card, {"prioridade", "priority", "urgencia", "urgência"})
    if priority in VALID_PRIORITIES:
        return priority

    title = str(card.get("title", ""))
    match = re.search(r"Prioridade:\s*([A-Za-zÀ-ÿ]+)", title)
    if match:
        possible = match.group(1).strip().capitalize()
        if possible in VALID_PRIORITIES:
            return possible

    now = pd.Timestamp.utcnow().tz_localize(None)
    if pd.notna(due_date):
        if due_date < now:
            return "Crítica"
        if due_date <= (now + pd.Timedelta(days=2)):
            return "Alta"

    phase_norm = _norm(phase_name)
    if phase_norm in {"nova solicitacao", "triagem"} and category in {"Financeiro", "Sistemas"}:
        return "Alta"
    if category in {"Dados", "Operações"}:
        return "Média"
    return "Baixa"


def _status_from_phase(phase_name: str, done: Any | None = None) -> str:
    if isinstance(done, bool):
        return "closed" if done else "open"
    phase_norm = _norm(phase_name)
    if phase_norm in CLOSED_PHASE_NAMES:
        return "closed"
    if phase_norm in OPEN_PHASE_NAMES:
        return "open"
    return "open"


def _extract_assignee(card: dict[str, Any]) -> str:
    assignees = card.get("assignees") or []
    if isinstance(assignees, list) and assignees:
        first = assignees[0] or {}
        name = str(first.get("name") or first.get("email") or "").strip()
        if name:
            mask_enabled = str(os.getenv("PIPEFY_MASK_ASSIGNEE_NAMES", "true")).strip().lower() in {
                "1",
                "true",
                "yes",
                "y",
            }
            return "Responsável atribuído" if mask_enabled else name
    return "Unassigned"


def map_pipefy_cards_to_dataframe(raw_data: dict[str, Any] | list[dict[str, Any]]) -> pd.DataFrame:
    cards = _extract_cards(raw_data)
    now = pd.Timestamp.utcnow().tz_localize(None)
    rows: list[dict[str, Any]] = []

    for card in cards:
        if not isinstance(card, dict):
            continue
        phase_name = str((card.get("current_phase") or {}).get("name", "")).strip() or "Nova solicitação"
        created_at = _parse_date(card.get("created_at"))
        updated_at = _parse_date(card.get("updated_at"))
        due_date = _parse_date(card.get("due_date"))
        closed_at = _parse_date(card.get("finished_at"))
        status = _status_from_phase(phase_name, done=card.get("done"))

        category = _infer_category(card, phase_name=phase_name)
        priority = _infer_priority(card, due_date=due_date, category=category, phase_name=phase_name)
        assignee = _extract_assignee(card)

        end_date = closed_at if status == "closed" and pd.notna(closed_at) else now
        days_open = float((end_date - created_at).days) if pd.notna(created_at) else 0.0

        if pd.notna(due_date) and status != "closed" and due_date < now:
            sla_status = "SLA vencido"
        elif pd.notna(due_date) and status != "closed" and due_date <= now + pd.Timedelta(days=2):
            sla_status = "SLA em risco"
        elif pd.notna(due_date) and status == "closed" and pd.notna(closed_at) and closed_at > due_date:
            sla_status = "SLA vencido"
        else:
            sla_status = "Dentro do SLA"

        if sla_status == "SLA vencido" or priority == "Crítica":
            risk_level = "Alto"
            automation_alert = "Prioridade crítica"
            recommended_action = "Escalar para liderança"
        elif sla_status == "SLA em risco" or assignee == "Unassigned":
            risk_level = "Médio"
            automation_alert = "SLA em risco"
            recommended_action = "Priorizar atendimento"
        else:
            risk_level = "Baixo"
            automation_alert = "Monitoramento"
            recommended_action = "Encerrar ou atualizar status"

        rows.append(
            {
                "ticket_id": str(card.get("id", "")),
                "title": str(card.get("title", "")).strip() or "Sem título",
                "source_system": "pipefy",
                "category": category if category else "General",
                "priority": priority,
                "status": status,
                "current_phase": phase_name,
                "assignee": assignee,
                "created_at": created_at,
                "updated_at": updated_at,
                "due_date": due_date,
                "closed_at": closed_at,
                "days_open": days_open,
                "sla_status": sla_status,
                "risk_level": risk_level,
                "automation_alert": automation_alert,
                "recommended_action": recommended_action,
                "card_url": str(card.get("url", "") or f"https://app.pipefy.com/open-cards/{card.get('id', '')}"),
            }
        )

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=TARGET_COLUMNS)

    for col in TARGET_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    return df[TARGET_COLUMNS].copy()
