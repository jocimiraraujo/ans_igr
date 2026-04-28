"""
components/charts.py — Funções de gráficos Plotly reutilizáveis
Alinhadas com o tema e estratégias de análise do IGR.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.config import PLOTLY_COLORS, PLOTLY_TEMPLATE, THEME


# ── Boxplot ─────────────────────────────────────────────────────────────────

def boxplot_por_grupo(
    df: pd.DataFrame,
    grupo: str,
    coluna: str = "IGR",
    log_scale: bool = False,
    titulo: str = "",
) -> go.Figure:
    """
    Boxplot comparativo por grupo com pontos de outliers identificados.
    Implementa escala log opcional e fences de Tukey.
    """
    color_map = PLOTLY_COLORS

    fig = px.box(
        df,
        x=grupo,
        y=coluna,
        color=grupo,
        color_discrete_map=color_map,
        points="outliers",
        hover_data=["RAZAO_SOCIAL", coluna, "QTD_BENEFICIARIOS"],
        template=PLOTLY_TEMPLATE,
        title=titulo or f"Distribuição do {coluna} por {grupo}",
        labels={coluna: f"{coluna} (por 100 mil beneficiários)", grupo: ""},
        category_orders={grupo: ["PEQUENO", "MÉDIO", "GRANDE"]},
    )

    if log_scale:
        fig.update_yaxes(type="log", title_text=f"{coluna} (escala log)")

    fig.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font_family="Inter",
        title_font_size=15,
        margin=dict(t=50, b=40, l=50, r=20),
    )
    fig.update_traces(boxmean=True)  # Mostra média além da mediana
    return fig


def violin_por_grupo(
    df: pd.DataFrame,
    grupo: str,
    coluna: str = "IGR",
    titulo: str = "",
) -> go.Figure:
    """Violin plot com boxplot interno — mostra densidade + quartis."""
    fig = px.violin(
        df,
        x=grupo,
        y=coluna,
        color=grupo,
        color_discrete_map=PLOTLY_COLORS,
        box=True,
        points="outliers",
        template=PLOTLY_TEMPLATE,
        title=titulo or f"Violin: {coluna} por {grupo}",
        labels={coluna: f"{coluna} (por 100 mil beneficiários)", grupo: ""},
        category_orders={grupo: ["PEQUENO", "MÉDIO", "GRANDE"]},
    )
    fig.update_layout(
        showlegend=False,
        font_family="Inter",
        margin=dict(t=50, b=40, l=50, r=20),
    )
    return fig


# ── Histograma ───────────────────────────────────────────────────────────────

def histograma_igr(
    df: pd.DataFrame,
    coluna: str = "IGR",
    grupo: str | None = None,
    log_scale: bool = False,
    titulo: str = "",
) -> go.Figure:
    """Histograma com curva KDE opcional e separação por grupo."""
    if grupo:
        fig = px.histogram(
            df, x=coluna, color=grupo,
            color_discrete_map=PLOTLY_COLORS,
            barmode="overlay", opacity=0.7,
            nbins=60,
            template=PLOTLY_TEMPLATE,
            title=titulo or f"Distribuição do {coluna}",
            marginal="box",
        )
    else:
        fig = px.histogram(
            df, x=coluna, nbins=60,
            color_discrete_sequence=[THEME["primary"]],
            template=PLOTLY_TEMPLATE,
            title=titulo or f"Distribuição do {coluna}",
            marginal="box",
        )

    if log_scale:
        fig.update_xaxes(type="log")

    fig.update_layout(
        font_family="Inter",
        margin=dict(t=50, b=40, l=50, r=20),
        bargap=0.05,
    )
    return fig


# ── Scatter ──────────────────────────────────────────────────────────────────

def scatter_correlacao(
    df: pd.DataFrame,
    x: str,
    y: str = "IGR",
    cor: str | None = None,
    log_x: bool = False,
    log_y: bool = False,
    titulo: str = "",
    trendline: bool = True,
) -> go.Figure:
    """Scatter com linha de tendência e coloração por grupo."""
    kwargs = dict(
        x=x, y=y,
        color=cor,
        color_discrete_map=PLOTLY_COLORS if cor else None,
        opacity=0.6,
        template=PLOTLY_TEMPLATE,
        title=titulo or f"{y} × {x}",
        hover_data=["RAZAO_SOCIAL"],
    )
    if trendline:
        kwargs["trendline"] = "ols"

    fig = px.scatter(df.sample(min(5000, len(df)), random_state=42), **kwargs)

    if log_x:
        fig.update_xaxes(type="log")
    if log_y:
        fig.update_yaxes(type="log")

    fig.update_layout(
        font_family="Inter",
        margin=dict(t=50, b=40, l=50, r=20),
    )
    return fig


# ── Heatmap de correlação ────────────────────────────────────────────────────

def heatmap_correlacao(corr_matrix: pd.DataFrame, titulo: str = "Matriz de Correlação de Spearman") -> go.Figure:
    """Heatmap da matriz de correlação."""
    fig = go.Figure(go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.index.tolist(),
        colorscale="RdBu",
        zmid=0,
        text=corr_matrix.round(2).values,
        texttemplate="%{text}",
        showscale=True,
    ))
    fig.update_layout(
        title=titulo,
        template=PLOTLY_TEMPLATE,
        font_family="Inter",
        margin=dict(t=60, b=40, l=120, r=40),
        height=400,
    )
    return fig


# ── Série temporal ────────────────────────────────────────────────────────────

def linha_temporal(
    df: pd.DataFrame,
    y: str = "IGR",
    grupo: str | None = None,
    agg: str = "median",
    titulo: str = "",
) -> go.Figure:
    """
    Evolução temporal do IGR agregado por mês.
    agg: 'median' ou 'mean'
    """
    agg_fn = "median" if agg == "median" else "mean"

    if grupo:
        df_agg = (
            df.groupby(["ANO_MES", grupo], observed=True)[y]
            .agg(agg_fn)
            .reset_index()
        )
        fig = px.line(
            df_agg, x="ANO_MES", y=y, color=grupo,
            color_discrete_map=PLOTLY_COLORS,
            markers=True,
            template=PLOTLY_TEMPLATE,
            title=titulo or f"Evolução do {y} ao longo do tempo",
            labels={y: f"{agg_fn.capitalize()} do {y}", "ANO_MES": "Competência"},
        )
    else:
        df_agg = df.groupby("ANO_MES")[y].agg(agg_fn).reset_index()
        fig = px.line(
            df_agg, x="ANO_MES", y=y,
            markers=True,
            color_discrete_sequence=[THEME["primary"]],
            template=PLOTLY_TEMPLATE,
            title=titulo or f"Evolução do {y} ao longo do tempo",
            labels={y: f"{agg_fn.capitalize()} do {y}", "ANO_MES": "Competência"},
        )

    fig.update_layout(
        font_family="Inter",
        margin=dict(t=50, b=40, l=50, r=20),
    )
    return fig


# ── Barras comparativas ───────────────────────────────────────────────────────

def barras_medianas(
    df: pd.DataFrame,
    grupo: str,
    coluna: str = "IGR",
    titulo: str = "",
    top_n: int | None = None,
) -> go.Figure:
    """Barras horizontais das medianas por grupo, ordenadas."""
    resumo = (
        df.groupby(grupo, observed=True)[coluna]
        .median()
        .reset_index()
        .sort_values(coluna, ascending=True)
    )
    if top_n:
        resumo = resumo.tail(top_n)

    cores = [PLOTLY_COLORS.get(str(g), THEME["primary"]) for g in resumo[grupo]]

    fig = go.Figure(go.Bar(
        x=resumo[coluna],
        y=resumo[grupo].astype(str),
        orientation="h",
        marker_color=cores,
        text=resumo[coluna].round(1),
        textposition="outside",
    ))
    fig.update_layout(
        title=titulo or f"Mediana do {coluna} por {grupo}",
        template=PLOTLY_TEMPLATE,
        font_family="Inter",
        xaxis_title=f"Mediana do {coluna}",
        yaxis_title="",
        margin=dict(t=50, b=40, l=160, r=60),
    )
    return fig


# ── QQ-Plot ───────────────────────────────────────────────────────────────────

def qq_plot(serie: pd.Series, titulo: str = "QQ-Plot (verificação de normalidade)") -> go.Figure:
    """QQ-Plot para verificar normalidade visualmente."""
    from scipy.stats import probplot
    osm, osr = probplot(serie.dropna(), dist="norm")
    theoretical, sample = osm
    slope, intercept, _ = osr

    x_line = np.array([theoretical[0], theoretical[-1]])
    y_line = slope * x_line + intercept

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=theoretical, y=sample,
        mode="markers",
        marker=dict(color=THEME["primary"], size=3, opacity=0.4),
        name="Dados",
    ))
    fig.add_trace(go.Scatter(
        x=x_line, y=y_line,
        mode="lines",
        line=dict(color=THEME["danger"], width=2),
        name="Linha Normal",
    ))
    fig.update_layout(
        title=titulo,
        xaxis_title="Quantis Teóricos (Normal)",
        yaxis_title="Quantis Observados (IGR)",
        template=PLOTLY_TEMPLATE,
        font_family="Inter",
        margin=dict(t=50, b=40, l=60, r=20),
    )
    return fig
