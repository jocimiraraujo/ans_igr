"""
pages/modelagem.py — Modelagem estatística: regressão log-linear e quantílica
"""
import streamlit as st
import numpy as np
import pandas as pd
from utils.data_loader import get_data, apply_filters
from components.ui import page_header, section_title, info_box, warn_box, footer
from analysis.modelagem import (
    regressao_log_linear, regressao_quantilica,
    ranking_percentilico, analise_tukey, zscore_robusto
)
from analysis.estatistica_descritiva import detectar_outliers
import plotly.express as px
from utils.config import PLOTLY_COLORS, PLOTLY_TEMPLATE


def render():
    page_header(
        title="Modelagem Estatística",
        subtitle="Regressão quantílica, log-linear, ranking percentílico e análise de outliers",
        icon="🎯",
    )

    df = get_data()

    st.sidebar.markdown("---")
    excluir_zero = st.sidebar.checkbox("Excluir IGR = 0", key="mod_zero")
    df_f = apply_filters(df, excluir_zero_igr=excluir_zero)

    # ── Fences de Tukey ──────────────────────────────────────────────────────
    section_title("Análise de Outliers — Fences de Tukey")

    warn_box(
        "Use os fences de Tukey para classificar operadoras. "
        "Outliers <b>severos</b> (acima de Q3 + 3×IQR) merecem investigação regulatória prioritária."
    )

    col1, col2 = st.columns(2)
    for i, cob in enumerate(df_f["COBERTURA"].unique()[:2]):
        sub = df_f[df_f["COBERTURA"] == cob]["IGR"]
        tukey = analise_tukey(sub)
        with [col1, col2][i]:
            st.markdown(f"**{cob}**")
            for k, v in tukey.items():
                st.markdown(f"- **{k}:** {v}")

    # ── Z-score robusto ───────────────────────────────────────────────────────
    section_title("Z-Score Robusto por Cobertura")
    info_box("z = (IGR − Mediana) / MAD. Valores |z| &gt; 3,5 = outlier severo.")

    df_z = df_f.copy()
    df_z["Z_ROB"] = df_z.groupby("COBERTURA", observed=True)["IGR"].transform(zscore_robusto).round(2)
    df_outliers = df_z[df_z["Z_ROB"].abs() > 3.5].sort_values("Z_ROB", ascending=False)

    st.markdown(f"**{len(df_outliers)} outliers severos** identificados no dataset filtrado.")
    if not df_outliers.empty:
        cols_show = ["RAZAO_SOCIAL", "PORTE_OPERADORA", "COBERTURA",
                     "IGR", "QTD_RECLAMACOES", "Z_ROB"]
        cols_show = [c for c in cols_show if c in df_outliers.columns]
        st.dataframe(df_outliers[cols_show].head(30), use_container_width=True, hide_index=True)

    # ── Ranking percentílico ──────────────────────────────────────────────────
    section_title("Ranking Percentílico das Operadoras")
    info_box(
        "Percentil alto = IGR mais alto = pior desempenho. "
        "'Crítico (p90-100)' indica as 10% piores operadoras dentro de cada cobertura."
    )

    df_rank = ranking_percentilico(df_f)
    rank_dist = df_rank["CLASSIFICACAO"].value_counts().reset_index()
    rank_dist.columns = ["Classificação", "N"]

    col_a, col_b = st.columns(2)
    with col_a:
        fig_rank = px.bar(
            rank_dist.sort_values("Classificação"),
            x="Classificação", y="N",
            color="Classificação",
            color_discrete_sequence=["#059669", "#34D399", "#FCD34D", "#F97316", "#DC2626"],
            template=PLOTLY_TEMPLATE,
            title="Distribuição das Classificações de Desempenho",
        )
        fig_rank.update_layout(showlegend=False, font_family="Inter")
        st.plotly_chart(fig_rank, use_container_width=True)

    with col_b:
        st.markdown("**Top 20 — Operadoras Críticas (pior IGR)**")
        criticas = (
            df_rank[df_rank["CLASSIFICACAO"] == "Crítico (p90-100)"]
            .sort_values("IGR", ascending=False)
            [["RAZAO_SOCIAL", "COBERTURA", "PORTE_OPERADORA", "IGR", "PERCENTIL"]]
            .head(20)
        )
        if not criticas.empty:
            st.dataframe(criticas, use_container_width=True, hide_index=True)

    # ── Regressão log-linear ──────────────────────────────────────────────────
    section_title("Regressão Log-Linear: log(IGR+1) ~ Porte + Cobertura")
    warn_box(
        "A transformação log(IGR+1) aproxima normalidade e permite usar OLS. "
        "Os coeficientes representam o efeito sobre o <b>log do IGR</b> — multiplique por e^β para obter o efeito multiplicativo no IGR original."
    )

    if st.button("Executar Regressão Log-Linear"):
        with st.spinner("Ajustando modelo OLS…"):
            resultado = regressao_log_linear(df_f)

        if "erro" in resultado:
            st.error(resultado["erro"])
        else:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("R²", resultado["R²"])
            col2.metric("R² Ajustado", resultado["R² Ajustado"])
            col3.metric("F-statistic", resultado["F-statistic"])
            col4.metric("N observações", resultado["n_obs"])

            st.markdown("**Coeficientes do modelo:**")
            st.dataframe(resultado["coeficientes"], use_container_width=True)

            with st.expander("Ver resumo completo do modelo"):
                st.text(resultado["resumo_texto"])

    # ── Regressão quantílica ──────────────────────────────────────────────────
    section_title("Regressão Quantílica (Mediana)")
    info_box(
        "A regressão quantílica na mediana (q=0.5) modela o IGR <b>típico</b>, "
        "sendo completamente robusta a outliers — sem necessidade de removê-los."
    )

    quantil = st.slider("Quantil alvo:", min_value=0.10, max_value=0.90,
                        value=0.50, step=0.05)

    if st.button("Executar Regressão Quantílica"):
        with st.spinner(f"Ajustando regressão quantílica (q={quantil})…"):
            resultado_q = regressao_quantilica(df_f, quantil=quantil)

        if "erro" in resultado_q:
            st.error(resultado_q["erro"])
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Quantil", resultado_q["quantil"])
            col2.metric("Pseudo-R²", resultado_q["pseudo_R²"])
            col3.metric("N observações", resultado_q["n_obs"])

            st.markdown("**Coeficientes:**")
            st.dataframe(resultado_q["coeficientes"], use_container_width=True)

            with st.expander("Ver resumo completo"):
                st.text(resultado_q["resumo_texto"])

    footer()
