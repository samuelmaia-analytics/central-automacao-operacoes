# LGPD & Privacy

## Objetivo
Documentar diretrizes de privacidade e aderência referencial à LGPD no contexto deste projeto analítico.

## Escopo
- Tratamento de dados operacionais e campos potencialmente identificáveis.
- Exposição de dados em dashboard, exportações e relatórios.

## Entradas
- Campos do dataset bruto (incluindo `customer_name`, `customer_email`).
- Regras de exibição e exportação no dashboard.

## Saídas
- Recomendações práticas de minimização de dados.
- Diretrizes para uso seguro em ambiente corporativo.

## Riscos
- Exposição de PII em telas e exportações.
- Compartilhamento indevido de dados fora do propósito.
- Ausência de controle de acesso em ambiente produtivo.

## Controles
- Minimização de PII em visão executiva.
- Preferência por agregações para gestão.
- Revisão periódica de campos exportáveis no Explorador Operacional de Cards.
- Recomendações de pseudonimização, IAM e trilha de auditoria para produção.
