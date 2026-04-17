# Dicionário de Dados

## Objetivo
Definir os campos principais da solução e sua aplicação operacional/analítica.

## Escopo
- Colunas do dataset bruto.
- Colunas derivadas pela transformação.
- Colunas de alerta consumidas no dashboard.

## Entradas
- Fonte principal: `data/raw/customer_support_tickets.csv`
- Estrutura de colunas original do dataset público.

## Saídas
- DataFrame tratado em `data/processed/tickets_enriched.csv`.
- Tabela analítica em DuckDB.
- Base filtrável para dashboard.

## Riscos
- Mudança de schema na fonte original.
- Uso indevido de campos potencialmente identificáveis.
- Interpretação incorreta de campos derivados sem contexto de regra.

## Controles
- Validação de colunas obrigatórias na ingestão.
- Padronização de nomes e tipos na transformação.
- Documentação de campos críticos e derivados.
- Prática de minimização de PII na camada executiva.

## Campos principais
- `ticket_id`: identificador único.
- `ticket_status`: status da demanda.
- `ticket_priority`: prioridade original.
- `first_response_time`: timestamp de primeira resposta.
- `time_to_resolution`: timestamp de resolução.
- `categoria_operacional`: agrupamento por tipo de operação.
- `status_sla`: situação de SLA.
- `prioridade_automatica`: prioridade recalculada.
- `flag_demanda_critica`: criticidade operacional.
