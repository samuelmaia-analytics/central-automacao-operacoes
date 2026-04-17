from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import requests

PIPEFY_GRAPHQL_ENDPOINT = "https://api.pipefy.com/graphql"
SAMPLE_FILE = Path(__file__).resolve().parents[2] / "data" / "samples" / "pipefy_cards_sample.json"


class PipefyError(Exception):
    """Base error for Pipefy integration."""


class PipefyTokenError(PipefyError):
    """Raised when token is missing for API mode."""


class PipefyAuthenticationError(PipefyError):
    """Raised when token is invalid or unauthorized."""


class PipefyConnectionError(PipefyError):
    """Raised when API is unavailable."""


class PipefyGraphQLError(PipefyError):
    """Raised when GraphQL returns business errors."""


class PipefyClient:
    def __init__(
        self,
        token: str | None = None,
        endpoint: str = PIPEFY_GRAPHQL_ENDPOINT,
        timeout_seconds: int = 20,
        use_mock: bool = False,
        sample_file: Path = SAMPLE_FILE,
    ) -> None:
        env_token = os.getenv("PIPEFY_TOKEN", "").strip()
        self.token = (token or env_token).strip()
        self.endpoint = endpoint
        self.timeout_seconds = timeout_seconds
        self.sample_file = sample_file
        self.use_mock = use_mock or not self.token

    def execute_query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.use_mock:
            return self._load_mock_payload()
        if not self.token:
            raise PipefyTokenError("PIPEFY_TOKEN ausente para execucao em modo API.")
        return self._execute_api_query(query=query, variables=variables)

    def _execute_api_query(self, query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = {"query": query, "variables": variables or {}}
        headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}
        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=headers,
                timeout=self.timeout_seconds,
            )
        except requests.RequestException as exc:
            raise PipefyConnectionError(f"Falha de conexao com Pipefy: {exc}") from exc

        if response.status_code in {401, 403}:
            raise PipefyAuthenticationError("Falha de autenticacao no Pipefy. Verifique PIPEFY_TOKEN.")
        if response.status_code >= 400:
            raise PipefyConnectionError(f"Erro HTTP {response.status_code} ao consultar Pipefy.")

        try:
            body = response.json()
        except ValueError as exc:
            raise PipefyConnectionError("Resposta invalida da API Pipefy (JSON malformado).") from exc

        errors = body.get("errors") if isinstance(body, dict) else None
        if errors:
            raise PipefyGraphQLError(f"Erro GraphQL retornado pelo Pipefy: {errors}")
        if not isinstance(body, dict):
            raise PipefyConnectionError("Resposta inesperada da API Pipefy.")
        return body

    def _load_mock_payload(self) -> dict[str, Any]:
        if not self.sample_file.exists():
            raise FileNotFoundError(f"Arquivo mock nao encontrado: {self.sample_file}")
        with self.sample_file.open("r", encoding="utf-8") as fp:
            return json.load(fp)

