# Central de Automação e Operações

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Central%20de%20Automacao%20e%20Operacoes-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pipefy](https://img.shields.io/badge/Pipefy-Integrado-4F46E5)](https://www.pipefy.com/)
[![DuckDB](https://img.shields.io/badge/DuckDB-Analytics-FECD45)](https://duckdb.org/)
[![CI](https://github.com/samuelmaia-analytics/central-automacao-operacoes/actions/workflows/ci.yml/badge.svg)](https://github.com/samuelmaia-analytics/central-automacao-operacoes/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/License-Proprietary-red)](LICENSE)

A Central de Automação e Operações é um produto analítico desenvolvido em Python, SQL e Streamlit para monitorar workflows operacionais, acompanhar SLA, identificar gargalos, priorizar demandas e gerar alertas automatizados a partir de dados operacionais e integração com Pipefy.

## Visão executiva
O projeto entrega uma esteira ponta a ponta:
- ingestão de dados reais;
- transformação e padronização com regras de negócio;
- análise operacional com métricas de SLA e eficiência;
- automação de alertas e priorização;
- dashboard executivo em Streamlit;
- relatório automático em Markdown.

## Dataset
- Nome: Customer Support Ticket Dataset
- Fonte: Kaggle
- Link: https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset
- Arquivo local: `data/raw/customer_support_tickets.csv`

## Arquitetura da solução
```text
Raw CSV
  -> Ingestão e Validação
  -> Transformação e Regras de Negócio
  -> KPIs, Insights e Alertas
     -> DuckDB + SQL -> Dashboard Streamlit
     -> Snapshots Versionados
     -> Relatório Executivo
```

## Dashboard como Produto Analítico
Nome do produto no app:
- **Central de Automação e Operações**

Seções disponíveis:
- Visão Executiva
- Monitoramento de SLA
- Backlog & Prioridades
- Gargalos Operacionais
- Alertas Automatizados
- Insights Executivos
- Inteligência Operacional com Pipefy
- Explorador Operacional de Cards

Recursos de experiência:
- filtros globais consistentes;
- botão **Limpar filtros**;
- modo apresentação para prints de portfólio;
- cards executivos com contexto de negócio;
- índice de saúde operacional (0-100) com recomendação principal;
- storytelling automático: resumo, riscos, oportunidades e ações;
- exportação CSV de alertas e dados filtrados;
- status de fonte de dados (Pipefy API ou modo demonstração);
- rodapé discreto com stack do produto.

Principais KPIs:
- total de cards/processos;
- percentual dentro do SLA;
- backlog aberto e cards vencidos;
- demandas críticas e cards sem responsável;
- tempo médio de resolução;
- potencial de horas economizadas.

## Camada de Integração Pipefy
O Pipefy foi integrado como **camada operacional** onde os processos acontecem (workflow, fases, backlog, responsáveis e prazos), enquanto Python/SQL/Streamlit permanecem como **camada de inteligência analítica** para SLA, risco, alertas e recomendações.

Por que integrar:
- conectar execução operacional com monitoramento analítico;
- simular cenário real de operação em portfólio;
- preparar o projeto para evolução de integração real via API.

Estrutura modular adicionada:
- `integrations/pipefy/pipefy_client.py`: cliente GraphQL com fallback mock.
- `integrations/pipefy/pipefy_queries.py`: query de cards por `pipe_id`.
- `integrations/pipefy/pipefy_mapper.py`: normalização de dados.
- `integrations/pipefy/pipefy_pipeline.py`: execução ponta a ponta.
- `src/automation/pipefy_rules.py`: regras de SLA, risco, gargalo e recomendação.
- `dashboard/pages/pipefy_workflow_intelligence.py`: página analítica dedicada.

KPIs gerados:
- total de cards, abertos, vencidos, em risco, críticos e sem responsável;
- tempo médio em aberto e percentual dentro do SLA;
- distribuição de cards por fase, prioridade, categoria e responsável.

Automações simuladas:
- SLA vencido / SLA em risco;
- demanda sem responsável;
- card parado;
- prioridade crítica;
- gargalo por fase;
- recomendação automática orientada à ação.

Executar pipeline Pipefy:
```bash
python -m integrations.pipefy.pipefy_pipeline
```

Executar com seed automático (cria cards no Pipefy se o pipe estiver vazio):
```bash
python -m integrations.pipefy.pipefy_pipeline --seed-if-empty --seed-count 30
```

Executar seed manual diretamente:
```bash
python -m integrations.pipefy.seed_pipefy --pipe-id 307112054 --count 30
```

Modo mock (sem token):
- padrão quando `PIPEFY_TOKEN` não existe;
- ou com `USE_PIPEFY_MOCK=true`.

Exemplo `.env`:
```bash
PIPEFY_TOKEN=your_pipefy_token_here
PIPEFY_ORGANIZATION_ID=302461931
PIPEFY_PIPE_ID=your_pipe_id_here
USE_PIPEFY_MOCK=true
APP_DATA_MODE=auto
```

Modos de dados no app (`APP_DATA_MODE`):
- `auto`: usa base legada quando disponível; caso contrário, entra em modo Pipefy.
- `pipefy`: força somente a experiência Pipefy (ideal para Streamlit Cloud).
- `legacy`: força a base legada (requer execução prévia de `python main.py`).

Listar pipes da organização via API:
```bash
python -m integrations.pipefy.pipefy_pipeline --list-pipes --organization-id 302461931
```

## Métricas e SQL
Os indicadores do dashboard são calculados com SQL (DuckDB) para rastreabilidade analítica, com fallback seguro em pandas.

KPIs principais:
- total de tickets/processos;
- percentual dentro e fora do SLA;
- backlog aberto;
- tickets críticos operacionais;
- tempo médio e mediano de resolução;
- taxa de automação simulada;
- potencial de horas economizadas.

## Governança, LGPD e conformidade
- Governança de dados: [docs/data_governance.md](docs/data_governance.md)
- LGPD e privacidade: [docs/lgpd_compliance.md](docs/lgpd_compliance.md)
- Dicionário de dados: [docs/data_dictionary.md](docs/data_dictionary.md)
- Regras de negócio: [docs/business_rules.md](docs/business_rules.md)
- Arquitetura e fluxo: [docs/project_architecture.md](docs/project_architecture.md), [docs/automation_flow.md](docs/automation_flow.md)
- Integração Pipefy: [docs/pipefy_integration.md](docs/pipefy_integration.md)
- Modelo de workflow Pipefy: [docs/pipefy_workflow_model.md](docs/pipefy_workflow_model.md)
- Regras de automação Pipefy: [docs/automation_rules_pipefy.md](docs/automation_rules_pipefy.md)

## Execução local
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
streamlit run dashboard/app.py
python -m integrations.pipefy.pipefy_pipeline
```

## Publicação no Streamlit Cloud
1. Suba o repositório no GitHub com `requirements.txt` atualizado.
2. No Streamlit Cloud, crie o app apontando para `dashboard/app.py`.
3. Configure em `Secrets`:
   - `PIPEFY_TOKEN`
   - `PIPEFY_PIPE_ID`
   - `USE_PIPEFY_MOCK`
   - `APP_DATA_MODE=pipefy` (recomendado para portfolio)
4. Faça deploy e valide a página **Inteligência Operacional com Pipefy**.

### Configuração recomendada para estabilidade
Use estes valores em **Secrets** no Streamlit Cloud:
- `APP_DATA_MODE=pipefy`
- `USE_PIPEFY_MOCK=true`
- `PIPEFY_PIPE_ID=<id_do_pipe>`
- `PIPEFY_TOKEN=<token_opcional>`

Com isso, o app sobe rápido mesmo sem API real e continua pronto para alternar para dados reais.

### Troubleshooting (Cloud)
- **Erro de import `dashboard`**: já tratado com fallback de import local no app.
- **Botão “Limpar filtros” não limpa**: implementado reset robusto por versão de chave dos widgets.
- **Filtros ilegíveis**: contraste reforçado na sidebar (campos, toggle e botões).
- **Lentidão de carregamento**: timeout da API Pipefy reduzido e filtros sem seleção padrão no primeiro load.

## Prints recomendados para portfólio
- Tela inicial com KPIs e header do produto.
- Bloco do **Índice de Saúde Operacional**.
- Página **Inteligência Operacional com Pipefy** com status de fonte de dados.
- Seção **Alertas Automatizados** com exportação CSV.
- Seção **Insights Executivos**.
- **Explorador Operacional de Cards** com filtros aplicados.

Incremental por watermark:
```bash
python main.py --incremental-by-watermark --watermark-column first_response_time --watermark-lookback-hours 6
```

## Qualidade e testes
```bash
ruff check .
pytest -q
```

## Licença
Este projeto é **privado e proprietário**. Consulte [LICENSE](LICENSE).

## Contato
- E-mail: `smaia2@gmail.com`
- LinkedIn: `https://linkedin.com/in/samuelmaia-analytics`
