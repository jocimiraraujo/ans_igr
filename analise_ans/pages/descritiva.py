"""
pages/descritiva.py — Estatística Descritiva completa do IGR
"""
import streamlit as st
import numpy as np
from utils.data_loader import get_data, apply_filters
from components.ui import page_header, section_title, info_box, warn_box, filter_sidebar, footer
from components.charts import histograma_igr, qq_plot, boxplot_por_grupo
from analysis.estatistica_descritiva import resumo_robusto, teste_normalidade, detectar_outliers


def render():
    page_header(
        title="Estatística Descritiva",
        subtitle="Medidas robustas, distribuição e diagnóstico de normalidade do IGR",
        icon="📊",
    )

    df = get_data()
    filtros = filter_sidebar(df)
    df_f = apply_filters(df, **filtros)

    if df_f.empty:
        st.warning("Nenhum dado com os filtros selecionados.")
        return

    warn_box(
        "O IGR tem distribuição fortemente <b>assimétrica à direita</b> (cauda positiva longa). "
        "Por isso, <b>Mediana e IQR</b> são as medidas preferidas sobre Média e Desvio-Padrão."
    )

    # ── Tabela de resumo robusto ─────────────────────────────────────────────
    section_title("Resumo Estatístico Robusto")
    resumo = resumo_robusto(df_f["IGR"], nome="IGR")
    st.dataframe(resumo, use_container_width=True, hide_index=True)

    # ── Teste de normalidade ─────────────────────────────────────────────────
    section_title("Teste de Normalidade")
    resultado_norm = teste_normalidade(df_f["IGR"].sample(min(5000, len(df_f)), random_state=42))
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Teste", resultado_norm["Teste"])
    col2.metric("Estatística", resultado_norm["Estatística"])
    col3.metric("p-valor", resultado_norm["p-valor"])
    col4.metric("Normal?", resultado_norm["Distribuição Normal?"])

    info_box(
        "p-valor &lt; 0,05 rejeita a hipótese de normalidade. Isso justifica o uso de métodos "
        "<b>não-paramétricos</b> (Spearman, Kruskal-Wallis, Mann-Whitney) em toda a análise."
    )

    # ── Histograma + QQ-Plot ─────────────────────────────────────────────────
    section_title("Distribuição do IGR")
    col_h, col_q = st.columns(2)

    escala_log = st.checkbox("Escala logarítmica no histograma", value=False)
    with col_h:
        fig_hist = histograma_igr(
            df_f, log_scale=escala_log,
            titulo="Histograma do IGR com margem boxplot"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_q:
        fig_qq = qq_plot(df_f["IGR"].sample(min(3000, len(df_f)), random_state=42))
        st.plotly_chart(fig_qq, use_container_width=True)

    st.caption(
        "No QQ-Plot, pontos alinhados à linha diagonal = distribuição normal. "
        "A dispersão crescente nas caudas confirma assimetria e presença de outliers."
    )

    # ── Boxplot geral ────────────────────────────────────────────────────────
    section_title("Boxplot Geral do IGR")
    fig_box = boxplot_por_grupo(df_f, "PORTE_OPERADORA",
                                titulo="Boxplot do IGR por Porte de Operadora")
    st.plotly_chart(fig_box, use_container_width=True)

    # ── Tabela de outliers ───────────────────────────────────────────────────
    section_title("Outliers Detectados (Z-score Robusto > 3,5)")
    df_out = detectar_outliers(df_f, metodo="zscore_robusto", limiar=3.5)

    if df_out.empty:
        st.success("Nenhum outlier severo detectado com os filtros atuais.")
    else:
        st.warning(f"{len(df_out)} outliers severos detectados.")
        colunas = ["RAZAO_SOCIAL", "COBERTURA", "PORTE_OPERADORA",
                   "IGR", "QTD_RECLAMACOES", "QTD_BENEFICIARIOS", "Z_ROBUSTO"]
        colunas_disp = [c for c in colunas if c in df_out.columns]
        st.dataframe(
            df_out[colunas_disp].sort_values("Z_ROBUSTO", ascending=False).head(50),
            use_container_width=True,
            hide_index=True,
        )

    footer()
