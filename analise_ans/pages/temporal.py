"""
pages/temporal.py — Evolução temporal do IGR
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.data_loader import get_data, apply_filters
from components.ui import page_header, section_title, info_box, footer
from components.charts import linha_temporal
from utils.config import PLOTLY_COLORS, PLOTLY_TEMPLATE


def render():
    page_header(
        title="Evolução Temporal do IGR",
        subtitle="Tendências mensais do índice ao longo das competências disponíveis",
        icon="📈",
    )

    df = get_data()
    if "ANO_MES" not in df.columns:
        st.error("Coluna COMPETENCIA não disponível para análise temporal.")
        return

    # ── Filtros ───────────────────────────────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Filtros**")
    coberturas = ["Todas"] + sorted(df["COBERTURA"].unique().tolist())
    cobertura = st.sidebar.selectbox("Cobertura", coberturas, key="temp_cob")
    portes = ["Todos"] + sorted(df["PORTE_OPERADORA"].dropna().unique().tolist())
    porte = st.sidebar.selectbox("Porte", portes, key="temp_porte")

    df_f = apply_filters(df, cobertura=cobertura, porte=porte)

    if df_f.empty:
        st.warning("Nenhum dado com os filtros selecionados.")
        return

    # ── Série temporal geral ─────────────────────────────────────────────────
    section_title("Evolução Mensal do IGR — Geral")
    agg_escolha = st.radio("Agregação:", ["Mediana (robusta)", "Média"], horizontal=True)
    agg = "median" if "Mediana" in agg_escolha else "mean"

    fig_geral = linha_temporal(df_f, agg=agg,
                               titulo=f"{agg_escolha} do IGR por Competência")
    st.plotly_chart(fig_geral, use_container_width=True)
    info_box(
        "Picos isolados em determinados meses podem indicar eventos regulatórios, "
        "crises pontuais ou mudanças na metodologia de coleta da ANS."
    )

    # ── Por porte ────────────────────────────────────────────────────────────
    section_title("Evolução por Porte de Operadora")
    fig_porte = linha_temporal(df_f, grupo="PORTE_OPERADORA", agg=agg,
                               titulo=f"{agg_escolha} do IGR por Porte ao longo do tempo")
    st.plotly_chart(fig_porte, use_container_width=True)

    # ── Por cobertura ─────────────────────────────────────────────────────────
    section_title("Evolução por Tipo de Cobertura")
    fig_cob = linha_temporal(df_f, grupo="COBERTURA", agg=agg,
                             titulo=f"{agg_escolha} do IGR por Cobertura ao longo do tempo")
    st.plotly_chart(fig_cob, use_container_width=True)

    # ── Heatmap mensal ────────────────────────────────────────────────────────
    section_title("Heatmap: IGR Mediano por Porte × Mês")
    try:
        pivot = (
            df_f.groupby(["ANO_MES", "PORTE_OPERADORA"], observed=True)["IGR"]
            .median()
            .reset_index()
            .pivot(index="PORTE_OPERADORA", columns="ANO_MES", values="IGR")
        )
        pivot.columns = [str(c)[:7] for c in pivot.columns]

        fig_heat = px.imshow(
            pivot,
            color_continuous_scale="RdYlGn_r",
            aspect="auto",
            title="Mediana do IGR por Porte × Competência (Verde = menor IGR)",
            template=PLOTLY_TEMPLATE,
            labels={"color": "Mediana IGR"},
        )
        fig_heat.update_layout(
            font_family="Inter",
            margin=dict(t=60, b=40, l=100, r=20),
            xaxis_title="Competência",
            yaxis_title="Porte",
        )
        st.plotly_chart(fig_heat, use_container_width=True)
    except Exception as e:
        st.info(f"Heatmap não disponível: {e}")

    # ── Tabela mensal ─────────────────────────────────────────────────────────
    section_title("Tabela Mensal Resumida")
    tabela = (
        df_f.groupby("ANO_MES")["IGR"]
        .agg(["count", "median", "mean", lambda x: x.quantile(0.25),
              lambda x: x.quantile(0.75), "max"])
        .round(2)
        .reset_index()
    )
    tabela.columns = ["Competência", "N", "Mediana", "Média", "Q1", "Q3", "Máximo"]
    tabela["Competência"] = tabela["Competência"].astype(str).str[:7]
    st.dataframe(tabela, use_container_width=True, hide_index=True)

    footer()
