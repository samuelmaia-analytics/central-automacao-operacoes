# Governança de Dados

## Objetivo
Estabelecer diretrizes para qualidade, rastreabilidade, segurança e uso responsável dos dados operacionais.

## Escopo
- Dados brutos, processados e outputs analíticos.
- Versionamento de execução e snapshots.
- Consumo de KPIs no dashboard e relatório executivo.

## Entradas
- Dataset de tickets.
- Regras de negócio e configuração de pipeline.
- SQL analítico para cálculo de métricas.

## Saídas
- Base tratada com histórico versionado.
- Evidências de execução (`manifest`, `pipeline_runs`).
- Indicadores de qualidade de dados.

## Riscos
- Perda de rastreabilidade de execução.
- Inconsistência entre métricas de diferentes camadas.
- Exposição indevida de campos sensíveis.

## Controles
- `run_id`, `snapshot_date` e `source_hash` por execução.
- Auditoria de qualidade (`data_quality_summary.json`).
- KPIs calculados por SQL para auditabilidade.
- Política de retenção recomendada para `raw`, `processed/snapshots` e `outputs/manifests`.
- Repositório público de portfólio; não implica controle de acesso em produção.

## Ciclo de governança
```mermaid
flowchart LR
    A[Ingestão] --> B[Qualidade]
    B --> C[Versionamento]
    C --> D[Publicacao de KPIs]
    D --> E[Monitoramento]
    E --> F[Revisao de controles]
    F --> A
```


## Bloqueio antes de publicação

O fluxo `main.run_pipeline` valida o candidato completo antes do filtro incremental
ou da primeira gravação de dados, alertas, snapshots, relatórios e auditorias de sucesso.
IDs ausentes/nulos/vazios, duplicados e resolução anterior à primeira resposta
bloqueiam a execução. A ingestão também rejeita timestamps preenchidos inválidos
antes de sua conversão para valores ausentes. Ausência de primeira resposta é
permitida para representar tickets aguardando atendimento e permanece no resumo.
Esses controles não equivalem a certificação LGPD ou IAM corporativo.
