SELECT
    COUNT(*) AS total_tickets,
    AVG(CASE WHEN status_sla = 'Dentro do SLA' THEN 1 ELSE 0 END) * 100 AS percentual_dentro_sla,
    AVG(CASE WHEN status_sla = 'SLA vencido' THEN 1 ELSE 0 END) * 100 AS percentual_fora_sla,
    AVG(tempo_de_resolucao) AS tempo_medio_resolucao_horas,
    MEDIAN(tempo_de_resolucao) AS tempo_mediano_resolucao_horas,
    SUM(CASE WHEN lower(ticket_status) IN ('open', 'pending customer response') THEN 1 ELSE 0 END) AS backlog_aberto,
    SUM(CASE WHEN flag_demanda_critica THEN 1 ELSE 0 END) AS tickets_criticos
FROM analytics_tickets;
