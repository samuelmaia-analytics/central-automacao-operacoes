from __future__ import annotations

import pandas as pd


def _top_value(df: pd.DataFrame, column: str, fallback: str = "Não identificado") -> str:
    if column not in df.columns or df[column].dropna().empty:
        return fallback
    return str(df[column].value_counts().idxmax())


def executive_story_lines(df: pd.DataFrame) -> dict[str, list[str]]:
    if df.empty:
        no_data = ["Sem dados suficientes para gerar análise automática no recorte atual."]
        return {
            "resumo": no_data,
            "insights": no_data,
            "acoes": no_data,
            "riscos": no_data,
            "oportunidades": no_data,
        }

    total = len(df)
    phase_col = "current_phase" if "current_phase" in df.columns else "categoria_operacional"
    priority_col = "priority" if "priority" in df.columns else "ticket_priority"
    status_col = "status" if "status" in df.columns else "ticket_status"
    sla_col = "sla_status" if "sla_status" in df.columns else "status_sla"
    risk_col = "risk_level" if "risk_level" in df.columns else "risco_atraso"
    assignee_col = "assignee" if "assignee" in df.columns else ""

    top_phase = _top_value(df, phase_col)
    top_priority = _top_value(df, priority_col)
    top_risk = _top_value(df, risk_col, fallback="Risco não mapeado")
    overdue = int(df[sla_col].astype(str).str.contains("vencido", case=False, na=False).sum()) if sla_col in df.columns else 0
    at_risk = int(df[sla_col].astype(str).str.contains("risco", case=False, na=False).sum()) if sla_col in df.columns else 0
    unresolved = (
        int(df[status_col].astype(str).str.contains("open|aberto|pending", case=False, na=False).sum())
        if status_col in df.columns
        else 0
    )
    unassigned = (
        int(df[assignee_col].astype(str).str.contains("unassigned", case=False, na=False).sum())
        if assignee_col and assignee_col in df.columns
        else 0
    )
    phase_conc = 0.0
    if phase_col in df.columns and not df[phase_col].dropna().empty:
        phase_conc = float(df[phase_col].value_counts(normalize=True).iloc[0] * 100)

    resumo = [
        f"O recorte atual possui {total} cards/processos monitorados.",
        f"A fase com maior concentração é {top_phase}, representando {phase_conc:.1f}% do volume.",
        f"A prioridade mais recorrente é {top_priority}.",
    ]
    insights = [
        f"Há {overdue} cards com SLA vencido e {at_risk} em risco de vencimento.",
        f"O maior risco operacional está em {top_risk}.",
        f"O backlog aberto atual é de {unresolved} cards.",
    ]
    riscos = [
        f"{overdue} cards com SLA vencido exigem atuação imediata.",
        f"{unassigned} cards sem responsável elevam risco de atraso." if unassigned else "Não há cards sem responsável no recorte atual.",
        f"A concentração em {top_phase} sugere gargalo de workflow.",
    ]
    oportunidades = [
        "Automatizar triagem inicial para reduzir acúmulo em fases de entrada.",
        "Aplicar roteamento por prioridade para reduzir risco de SLA.",
        "Acompanhar fila crítica com checkpoint diário de execução.",
    ]
    acao = "Priorizar atendimento dos cards vencidos e redistribuir demanda da fase mais congestionada."
    if unassigned > 0:
        acao = "Atribuir responsáveis imediatamente e escalar cards com SLA vencido para liderança."
    acoes = [
        acao,
        "Revisar capacidade por responsável e redistribuir backlog crítico.",
        "Criar regra automática de alerta para cards sem atualização recente.",
    ]
    return {
        "resumo": resumo,
        "insights": insights,
        "acoes": acoes,
        "riscos": riscos,
        "oportunidades": oportunidades,
    }
