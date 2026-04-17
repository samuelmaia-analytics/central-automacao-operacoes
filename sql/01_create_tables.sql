CREATE TABLE IF NOT EXISTS analytics_tickets (
    ticket_id BIGINT,
    ticket_status VARCHAR,
    ticket_priority VARCHAR,
    prioridade_automatica VARCHAR,
    status_sla VARCHAR,
    risco_atraso VARCHAR,
    categoria_operacional VARCHAR,
    tempo_de_resolucao DOUBLE,
    flag_demanda_critica BOOLEAN
);
