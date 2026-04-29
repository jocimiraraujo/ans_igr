"""
pages/correlacoes.py — Análise de correlações Spearman e Kendall
"""
import streamlit as st
import pandas as pd
import numpy as np
from utils.data_loader import get_data, apply_filters
from components.ui import page_header, section_title, info_box, warn_box, footer
from components.charts import scatter_correlacao, heatmap_correlacao
from analysis.correlacoes import (
    correlacao_spearman, correlacao_kendall, matriz_correlacao_spearman
)


def render():
    page_header(
        title="Análise de Correlações",
        subtitle="Correlações de Spearman e Kendall entre IGR e variáveis do dataset",
        icon="🔗",
    )

    df = get_data()

    st.sidebar.markdown("---")
    coberturas = ["Todas"] + sorted(df["COBERTURA"].unique().tolist())
    cobertura = st.sidebar.selectbox("Cobertura", coberturas, key="corr_cob")
    portes = ["Todos"] + sorted(df["PORTE_OPERADORA"].dropna().unique().tolist())
    porte = st.sidebar.selectbox("Porte", portes, key="corr_porte")
    excluir_zero = st.sidebar.checkbox("Excluir IGR = 0", key="corr_zero")

    df_f = apply_filters(df, cobertura=cobertura, porte=porte, excluir_zero_igr=excluir_zero)

    if df_f.empty:
        st.warning("Nenhum dado com os filtros selecionados.")
        return

    warn_box(
        "Como o IGR não é normalmente distribuído, utilizamos <b>Spearman ρ</b> (mais comum) "
        "e <b>Kendall τ</b> (mais conservador, melhor para amostras pequenas). "
        "Não use Pearson diretamente no IGR bruto."
    )

    # ── Correlações individuais ───────────────────────────────────────────────
    section_title("Correlações com o IGR")

    pares = [
        ("QTD_RECLAMACOES", "IGR"),
        ("QTD_BENEFICIARIOS", "IGR"),
        ("QTD_RECLAMACOES", "QTD_BENEFICIARIOS"),
    ]

    resultados_sp = []
    resultados_kd = []
    for x, y in pares:
        try:
            resultados_sp.append(correlacao_spearman(df_f, x, y))
            resultados_kd.append(correlacao_kendall(df_f, x, y))
        except Exception:
            pass

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Spearman ρ**")
        st.dataframe(pd.DataFrame(resultados_sp), use_container_width=True, hide_index=True)
    with col2:
        st.markdown("**Kendall τ**")
        st.dataframe(pd.DataFrame(resultados_kd), use_container_width=True, hide_index=True)

    info_box(
        "Interpretação da força: |r| ≥ 0,7 = Forte | 0,4–0,7 = Moderada | "
        "0,2–0,4 = Fraca | &lt; 0,2 = Desprezível"
    )

    # ── Matriz de correlação ──────────────────────────────────────────────────
    section_title("Matriz de Correlação de Spearman")
    colunas_num = ["IGR", "QTD_RECLAMACOES", "QTD_BENEFICIARIOS"]
    try:
        mat = matriz_correlacao_spearman(df_f, colunas_num)
        fig_heat = heatmap_correlacao(mat)
        st.plotly_chart(fig_heat, use_container_width=True)
    except Exception as e:
        st.warning(f"Não foi possível calcular a matriz: {e}")

    # ── Scatter plots ─────────────────────────────────────────────────────────
    section_title("Gráficos de Dispersão")

    opcoes_scatter = {
        "IGR × QTD_RECLAMACOES": ("QTD_RECLAMACOES", "IGR"),
        "IGR × QTD_BENEFICIARIOS": ("QTD_BENEFICIARIOS", "IGR"),
        "log(IGR) × log(QTD_BENEFICIARIOS)": ("QTD_BENEFICIARIOS", "IGR"),
    }
    escolha = st.selectbox("Selecione o par de variáveis:", list(opcoes_scatter.keys()))
    x_var, y_var = opcoes_scatter[escolha]
    usar_log = "log" in escolha

    cor_grupo = st.radio("Colorir por:", ["PORTE_OPERADORA", "COBERTURA", "Nenhum"], horizontal=True)
    cor = None if cor_grupo == "Nenhum" else cor_grupo

    fig_sc = scatter_correlacao(
        df_f, x=x_var, y=y_var, cor=cor,
        log_x=usar_log, log_y=usar_log,
        titulo=f"Dispersão: {y_var} × {x_var}",
        trendline=True,
    )
    st.plotly_chart(fig_sc, use_container_width=True)
    st.caption("Linha de tendência calculada por OLS após amostragem de até 5.000 pontos.")

    # ── Log-transformação ─────────────────────────────────────────────────────
    section_title("Efeito da Transformação Logarítmica")
    col_a, col_b = st.columns(2)
    with col_a:
        sp_original = correlacao_spearman(df_f, "QTD_BENEFICIARIOS", "IGR")
        st.metric("Spearman ρ — IGR bruto", sp_original["ρ (rho)"],
                  f"p = {sp_original['p-valor']}")
    with col_b:
        df_log = df_f.copy()
        df_log["LOG_IGR"] = np.log1p(df_log["IGR"])
        sp_log = correlacao_spearman(df_log, "QTD_BENEFICIARIOS", "LOG_IGR")
        st.metric("Spearman ρ — log(IGR+1)", sp_log["ρ (rho)"],
                  f"p = {sp_log['p-valor']}")
    info_box(
        "Aplicar log(IGR+1) comprime a cauda direita, tornando a relação mais linear "
        "e viabilizando regressão OLS. O Spearman não muda pois é baseado em postos."
    )

    footer()
