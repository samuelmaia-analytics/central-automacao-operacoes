# Arquitetura do Projeto

## Objetivo
Descrever a arquitetura técnica da solução de dados e automação operacional, com foco em rastreabilidade, modularidade e consumo executivo.

## Escopo
- Pipeline de ingestão, transformação, automação, analytics e persistência local.
- Camada de dashboard analítico em Streamlit.
- Documentação de governança, privacidade e regras de negócio.

## Entradas
- Dataset CSV em `data/raw/customer_support_tickets.csv`.
- Regras de negócio definidas em `src/automation/`.
- Queries SQL em `sql/`.

## Saídas
- Dados tratados em `data/processed/`.
- Snapshots versionados em `data/processed/snapshots/`.
- Outputs operacionais e de qualidade em `data/outputs/`.
- Dashboard em `dashboard/app.py`.
- Relatório executivo em `reports/executive_report.md`.

## Riscos
- Acoplamento excessivo entre camadas de transformação e visualização.
- Divergência de cálculo entre Python e SQL.
- Crescimento de volume sem otimização de consultas.

## Controles
- Separação por módulos (`ingestion`, `transformation`, `automation`, `analytics`, `database`, `quality`, `versioning`).
- SQL analítico no DuckDB para KPIs auditáveis.
- Testes automatizados e lint no CI.
- Versionamento por `run_id`, `snapshot_date` e `source_hash`.

## Fluxo arquitetural
```text
Dataset Raw
  -> Ingestão
  -> Transformação
  -> Regras de Automação
  -> Camada Analítica
     -> DuckDB + SQL -> Dashboard Streamlit
     -> Relatório Executivo
     -> Qualidade e Governança
```
