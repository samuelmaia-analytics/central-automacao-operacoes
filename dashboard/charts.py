from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

COLORWAY = ["#1d4ed8", "#0ea5e9", "#16a34a", "#f59e0b", "#dc2626", "#7c3aed", "#334155"]


def _apply_executive_layout(fig: go.Figure) -> go.Figure:
    fig.update_layout(
        template="plotly_white",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        font={"color": "#0f172a", "size": 13},
        title={"font": {"color": "#0f172a", "size": 18}},
        legend={"font": {"color": "#334155", "size": 12}},
        legend_title_text="",
        margin={"l": 14, "r": 14, "t": 46, "b": 10},
        hoverlabel={"bgcolor": "#ffffff", "font": {"color": "#111827"}},
        height=330,
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#e2e8f0",
        zeroline=False,
        title_font={"color": "#334155", "size": 13},
        tickfont={"color": "#475569", "size": 12},
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="#e2e8f0",
        zeroline=False,
        title_font={"color": "#334155", "size": 13},
        tickfont={"color": "#475569", "size": 12},
    )
    return fig


def _empty_figure(title: str) -> go.Figure:
    fig = go.Figure()
    fig.update_layout(title=title, height=340)
    fig.add_annotation(text="Sem dados para exibição", showarrow=False, x=0.5, y=0.5, xref="paper", yref="paper")
    return _apply_executive_layout(fig)


def trend_volume(df: pd.DataFrame) -> go.Figure:
    if df.empty or "first_response_time" not in df.columns:
        return _empty_figure("Tendência de volume por período")
    tmp = df[df["first_response_time"].notna()].copy()
    if tmp.empty:
        return _empty_figure("Tendência de volume por período")
    trend = (
        tmp.assign(periodo=tmp["first_response_time"].dt.date).groupby("periodo", as_index=False)["ticket_id"].count()
    )
    fig = px.line(
        trend,
        x="periodo",
        y="ticket_id",
        title="Tendência de volume por período",
        markers=True,
        color_discrete_sequence=[COLORWAY[1]],
    )
    fig.update_layout(yaxis_title="Volume", xaxis_title="Período")
    return _apply_executive_layout(fig)


def status_distribution(df: pd.DataFrame) -> go.Figure:
    if df.empty or "ticket_status" not in df.columns:
        return _empty_figure("Distribuição por status")
    data = df.groupby("ticket_status", as_index=False)["ticket_id"].count().rename(columns={"ticket_id": "volume"})
    fig = px.pie(
        data,
        names="ticket_status",
        values="volume",
        hole=0.58,
        title="Distribuição por status",
        color_discrete_sequence=COLORWAY,
    )
    fig.update_traces(hovertemplate="Status=%{label}<br>Volume=%{value}<br>Percentual=%{percent}<extra></extra>")
    fig.update_traces(textfont={"color": "#ffffff", "size": 16})
    return _apply_executive_layout(fig)


def bar_count(df: pd.DataFrame, col: str, title: str, orientation: str = "v") -> go.Figure:
    if df.empty or col not in df.columns:
        return _empty_figure(title)
    data = df.groupby(col, as_index=False)["ticket_id"].count().sort_values("ticket_id", ascending=(orientation == "v"))
    fig = px.bar(
        data,
        x=("ticket_id" if orientation == "h" else col),
        y=(col if orientation == "h" else "ticket_id"),
        orientation=orientation,
        title=title,
        color_discrete_sequence=[COLORWAY[0]],
    )
    fig.update_layout(xaxis_title="", yaxis_title="Volume")
    return _apply_executive_layout(fig)


def sla_evolution(df: pd.DataFrame) -> go.Figure:
    if df.empty or "first_response_time" not in df.columns or "status_sla" not in df.columns:
        return _empty_figure("Evolução de SLA")
    tmp = df[df["first_response_time"].notna()].copy()
    if tmp.empty:
        return _empty_figure("Evolução de SLA")
    grouped = (
        tmp.assign(
            periodo=tmp["first_response_time"].dt.date,
            dentro=tmp["status_sla"].eq("Dentro do SLA").astype(int),
        )
        .groupby("periodo", as_index=False)["dentro"]
        .mean()
    )
    grouped["compliance_pct"] = grouped["dentro"] * 100
    fig = px.line(
        grouped,
        x="periodo",
        y="compliance_pct",
        title="Evolução de SLA (%)",
        markers=True,
        color_discrete_sequence=[COLORWAY[0]],
    )
    fig.update_layout(yaxis_title="% Dentro do SLA", xaxis_title="Período")
    return _apply_executive_layout(fig)


def heatmap_priority_status(df: pd.DataFrame) -> go.Figure:
    title = "Matriz Prioridade x Status"
    if df.empty or "ticket_priority" not in df.columns or "ticket_status" not in df.columns:
        return _empty_figure(title)
    matrix = pd.crosstab(df["ticket_priority"], df["ticket_status"])
    if matrix.empty:
        return _empty_figure(title)
    fig = px.imshow(matrix, text_auto=True, aspect="auto", title=title, color_continuous_scale="Blues")
    fig.update_layout(xaxis_title="Status", yaxis_title="Prioridade")
    return _apply_executive_layout(fig)


def avg_resolution_by_category(df: pd.DataFrame) -> go.Figure:
    title = "Tempo médio de resolução por categoria"
    if df.empty or "categoria_operacional" not in df.columns or "tempo_de_resolucao" not in df.columns:
        return _empty_figure(title)
    data = (
        df.groupby("categoria_operacional", as_index=False)["tempo_de_resolucao"]
        .mean()
        .sort_values("tempo_de_resolucao", ascending=False)
    )
    fig = px.bar(
        data,
        x="tempo_de_resolucao",
        y="categoria_operacional",
        orientation="h",
        title=title,
        color_discrete_sequence=[COLORWAY[2]],
    )
    fig.update_layout(xaxis_title="Horas", yaxis_title="Categoria")
    return _apply_executive_layout(fig)


def backlog_risk_distribution(df: pd.DataFrame) -> go.Figure:
    title = "Backlog por risco de atraso"
    if df.empty:
        return _empty_figure(title)

    order = ["Baixo", "Medio", "Alto"]
    if "risco_atraso" not in df.columns:
        return _empty_figure(title)

    counts = (
        df["risco_atraso"]
        .fillna("Indefinido")
        .replace({"Médio": "Medio"})
        .value_counts()
        .reindex(order, fill_value=0)
        .reset_index()
    )
    counts.columns = ["risco_atraso", "volume"]

    fig = px.bar(
        counts,
        x="risco_atraso",
        y="volume",
        title=title,
        category_orders={"risco_atraso": order},
        color="risco_atraso",
        color_discrete_map={"Baixo": "#0f766e", "Medio": "#f59e0b", "Alto": "#ef4444"},
    )
    fig.update_layout(xaxis_title="Risco", yaxis_title="Volume", showlegend=False)
    return _apply_executive_layout(fig)
