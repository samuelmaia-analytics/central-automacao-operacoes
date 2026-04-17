# Pipefy Integration Module

Esta pasta implementa a camada de integração operacional com Pipefy:

- `pipefy_client.py`: cliente GraphQL com suporte a token e fallback mock.
- `pipefy_queries.py`: queries GraphQL para captura de cards.
- `pipefy_mapper.py`: mapeamento para schema analítico padronizado.
- `pipefy_pipeline.py`: execução ponta a ponta da ingestão -> regras -> CSV processado.

Execução:

```bash
python -m integrations.pipefy.pipefy_pipeline
```

