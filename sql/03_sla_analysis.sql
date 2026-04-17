SELECT
    categoria_operacional,
    COUNT(*) AS volume_total,
    SUM(CASE WHEN status_sla = 'SLA vencido' THEN 1 ELSE 0 END) AS volume_sla_vencido,
    ROUND(SUM(CASE WHEN status_sla = 'SLA vencido' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS perc_sla_vencido,
    AVG(tempo_de_resolucao) AS tempo_medio_resolucao
FROM analytics_tickets
GROUP BY categoria_operacional
ORDER BY perc_sla_vencido DESC, volume_total DESC;
