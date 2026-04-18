from __future__ import annotations

import argparse
import os

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover

    def load_dotenv() -> bool:
        return False


from integrations.pipefy.pipefy_seed import seed_pipefy_cards


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Seed automático de cards no Pipefy")
    parser.add_argument("--pipe-id", help="ID do Pipe no Pipefy")
    parser.add_argument("--count", type=int, default=30, help="Quantidade de cards para criar")
    parser.add_argument("--randomize", action="store_true", help="Embaralha o lote antes de criar")
    return parser


def main() -> None:
    load_dotenv()
    args = _build_parser().parse_args()
    pipe_id = args.pipe_id or os.getenv("PIPEFY_PIPE_ID", "").strip()
    if not pipe_id:
        raise ValueError("Informe --pipe-id ou PIPEFY_PIPE_ID para executar seed no Pipefy.")
    created = seed_pipefy_cards(pipe_id=pipe_id, seed_count=args.count, randomize=args.randomize)
    print(f"Seed Pipefy concluído. Cards criados: {created} | pipe_id={pipe_id}")


if __name__ == "__main__":
    main()
