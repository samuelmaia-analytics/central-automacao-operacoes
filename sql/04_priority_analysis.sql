SELECT
    prioridade_automatica,
    COUNT(*) AS volume,
    SUM(CASE WHEN flag_demanda_critica THEN 1 ELSE 0 END) AS criticos,
    SUM(CASE WHEN status_sla = 'SLA vencido' THEN 1 ELSE 0 END) AS sla_vencido,
    AVG(tempo_de_resolucao) AS tempo_medio_resolucao
FROM analytics_tickets
GROUP BY prioridade_automatica
ORDER BY criticos DESC, volume DESC;
