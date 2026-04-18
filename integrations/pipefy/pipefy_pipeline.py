from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import pandas as pd

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - fallback for environments without python-dotenv

    def load_dotenv() -> bool:
        return False


from integrations.pipefy.pipefy_client import (
    PipefyAuthenticationError,
    PipefyClient,
    PipefyConnectionError,
    PipefyGraphQLError,
    PipefyTokenError,
)
from integrations.pipefy.pipefy_mapper import map_pipefy_cards_to_dataframe
from integrations.pipefy.pipefy_queries import get_cards_query, get_organization_pipes_query
from integrations.pipefy.pipefy_seed import seed_pipefy_cards
from src.automation.pipefy_rules import apply_pipefy_automation_rules
from src.utils.helpers import ensure_directory

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PIPEFY_OUTPUT_FILE = PROJECT_ROOT / "data" / "processed" / "pipefy_cards_processed.csv"


def _is_true(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y"}


def run_pipefy_pipeline(
    pipe_id: str | None = None,
    use_mock: bool = False,
    seed_if_empty: bool = False,
    seed_count: int = 30,
) -> pd.DataFrame:
    load_dotenv()
    pipe_id = pipe_id or os.getenv("PIPEFY_PIPE_ID", "").strip()
    token = os.getenv("PIPEFY_TOKEN", "").strip()
    env_mock = _is_true(os.getenv("USE_PIPEFY_MOCK", "false"))
    should_use_mock = use_mock or env_mock or not token

    raw_data: dict[str, object]
    if should_use_mock:
        client = PipefyClient(use_mock=True)
        raw_data = client.execute_query(query="")
    else:
        if not pipe_id:
            print("PIPEFY_PIPE_ID ausente. Alternando para modo mock.")
            client = PipefyClient(use_mock=True)
            raw_data = client.execute_query(query="")
        else:
            try:
                client = PipefyClient(token=token, use_mock=False)
                raw_data = client.execute_query(
                    query=get_cards_query(),
                    variables={"pipe_id": pipe_id},
                )
            except (PipefyTokenError, PipefyAuthenticationError, PipefyConnectionError, PipefyGraphQLError) as exc:
                print(f"Falha na API Pipefy ({exc}). Alternando para modo mock.")
                client = PipefyClient(use_mock=True)
                raw_data = client.execute_query(query="")

    mapped_df = map_pipefy_cards_to_dataframe(raw_data)
    if not should_use_mock and pipe_id and mapped_df.empty and seed_if_empty:
        try:
            created = seed_pipefy_cards(pipe_id=pipe_id, seed_count=seed_count)
            print(f"Pipe vazio detectado. Seed automático criado: {created} cards.")
            client = PipefyClient(token=token, use_mock=False)
            raw_data = client.execute_query(
                query=get_cards_query(),
                variables={"pipe_id": pipe_id},
            )
            mapped_df = map_pipefy_cards_to_dataframe(raw_data)
        except (PipefyTokenError, PipefyAuthenticationError, PipefyConnectionError, PipefyGraphQLError) as exc:
            print(f"Falha no seed automático do Pipefy ({exc}).")
    final_df = apply_pipefy_automation_rules(mapped_df)

    ensure_directory(PIPEFY_OUTPUT_FILE.parent)
    final_df.to_csv(PIPEFY_OUTPUT_FILE, index=False)
    return final_df


def list_pipefy_pipes(organization_id: str) -> pd.DataFrame:
    load_dotenv()
    token = os.getenv("PIPEFY_TOKEN", "").strip()
    if not token:
        raise PipefyTokenError("PIPEFY_TOKEN ausente. Nao e possivel listar pipes reais.")
    client = PipefyClient(token=token, use_mock=False)
    payload: dict[str, Any] = client.execute_query(
        query=get_organization_pipes_query(),
        variables={"organization_id": organization_id},
    )
    pipes = payload.get("data", {}).get("organization", {}).get("pipes", [])
    if not isinstance(pipes, list):
        return pd.DataFrame(columns=["pipe_id", "pipe_name"])
    rows = []
    for pipe in pipes:
        if not isinstance(pipe, dict):
            continue
        rows.append({"pipe_id": str(pipe.get("id", "")), "pipe_name": str(pipe.get("name", ""))})
    return pd.DataFrame(rows)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Pipeline de integracao Pipefy para analytics operacional")
    parser.add_argument("--pipe-id", help="ID do Pipe no Pipefy")
    parser.add_argument("--organization-id", help="ID da organizacao Pipefy")
    parser.add_argument("--list-pipes", action="store_true", help="Lista pipes da organizacao e encerra")
    parser.add_argument("--use-mock", action="store_true", help="Forca execucao com dados mock")
    parser.add_argument("--seed-if-empty", action="store_true", help="Cria cards automáticos se pipe estiver vazio")
    parser.add_argument("--seed-count", type=int, default=30, help="Quantidade de cards a criar no seed automático")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    if args.list_pipes:
        org_id = args.organization_id or os.getenv("PIPEFY_ORGANIZATION_ID", "").strip()
        if not org_id:
            raise ValueError("Informe --organization-id ou PIPEFY_ORGANIZATION_ID para listar pipes.")
        pipes_df = list_pipefy_pipes(organization_id=org_id)
        print(pipes_df.to_string(index=False) if not pipes_df.empty else "Nenhum pipe encontrado.")
        return
    df = run_pipefy_pipeline(
        pipe_id=args.pipe_id,
        use_mock=args.use_mock,
        seed_if_empty=args.seed_if_empty,
        seed_count=args.seed_count,
    )
    print(f"Pipeline Pipefy concluido. Registros processados: {len(df)} | Saida: {PIPEFY_OUTPUT_FILE}")


if __name__ == "__main__":
    main()
