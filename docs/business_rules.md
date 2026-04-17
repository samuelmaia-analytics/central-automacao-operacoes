# Regras de Negócio

## Objetivo
Formalizar as regras que sustentam cálculo de SLA, priorização automática, criticidade e alertas operacionais.

## Escopo
- Regras de SLA por prioridade.
- Regras de criticidade operacional.
- Regras de alerta com severidade e ação recomendada.

## Entradas
- `ticket_status`
- `ticket_priority`
- `prioridade_automatica`
- `first_response_time`
- `time_to_resolution`
- `idade_ticket_horas`
- `sla_horas`

## Saídas
- `status_sla`
- `risco_atraso`
- `prioridade_automatica`
- `flag_demanda_critica`
- `tipo_alerta`
- `severidade`
- `acao_recomendada`

## Riscos
- Superclassificação de criticidade em tickets já resolvidos.
- Interpretação ambígua de risco sem contexto de status.
- Variação de semântica entre regra operacional e regra analítica.

## Controles
- SLA por prioridade:
  - `critical` 24h
  - `high` 48h
  - `medium` 72h
  - `low` 96h
- Criticidade operacional no dashboard considera tickets abertos com risco/vencimento de SLA ou prioridade crítica.
- Regras de alerta explicitadas por tipo, severidade e ação recomendada.
- Revisão periódica das regras com áreas de negócio.
