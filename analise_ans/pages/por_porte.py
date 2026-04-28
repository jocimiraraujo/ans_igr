"""
pages/por_porte.py — Análise do IGR por Porte de Operadora
"""
import streamlit as st
from utils.data_loader import get_data, apply_filters
from components.ui import page_header, section_title, info_box, warn_box, footer
from components.charts import boxplot_por_grupo, violin_por_grupo, barras_medianas
from analysis.estatistica_descritiva import resumo_por_grupo
from analysis.correlacoes import teste_kruskal_wallis, teste_mann_whitney


def render():
    page_header(
        title="Análise por Porte de Operadora",
        subtitle="Comparação estatística do IGR entre operadoras Pequenas, Médias e Grandes",
        icon="📦",
    )

    df = get_data()

    # Filtro de cobertura no sidebar
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Filtros**")
    coberturas = ["Todas"] + sorted(df["COBERTURA"].dropna().unique().tolist())
    cobertura = st.sidebar.selectbox("Cobertura", coberturas, key="porte_cob")
    excluir_zero = st.sidebar.checkbox("Excluir IGR = 0", key="porte_zero")

    df_f = apply_filters(df, cobertura=cobertura, excluir_zero_igr=excluir_zero)

    if df_f.empty:
        st.warning("Nenhum dado com os filtros selecionados.")
        return

    info_box(
        "Operadoras <b>pequenas</b> têm IGR mais volátil: poucas reclamações absolutas "
        "representam valores extremos por 100 mil. Operadoras <b>grandes</b> tendem a ter "
        "IGR estruturalmente mais alto por complexidade operacional."
    )

    # ── Resumo por porte ─────────────────────────────────────────────────────
    section_title("Estatísticas Robustas por Porte")
    resumo = resumo_por_grupo(df_f, grupo="PORTE_OPERADORA")
    st.dataframe(resumo, use_container_width=True, hide_index=True)

    # ── Boxplot + Violin ─────────────────────────────────────────────────────
    section_title("Visualizações Comparativas")

    tipo_viz = st.radio(
        "Tipo de gráfico:",
        ["Boxplot", "Violin Plot", "Barras (Medianas)"],
        horizontal=True,
    )

    log_scale = st.checkbox("Aplicar escala logarítmica", value=False)

    if tipo_viz == "Boxplot":
        fig = boxplot_por_grupo(
            df_f, "PORTE_OPERADORA", log_scale=log_scale,
            titulo="Boxplot do IGR por Porte de Operadora"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "Linha central = mediana | X = média | Pontos fora dos whiskers = outliers (Tukey). "
            "Whiskers: Q1−1,5×IQR a Q3+1,5×IQR."
        )

    elif tipo_viz == "Violin Plot":
        fig = violin_por_grupo(
            df_f, "PORTE_OPERADORA",
            titulo="Violin Plot do IGR por Porte de Operadora"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "O Violin mostra a densidade completa da distribuição. "
            "Regiões mais largas = maior concentração de operadoras naquele valor de IGR."
        )

    else:
        fig = barras_medianas(df_f, "PORTE_OPERADORA",
                              titulo="Mediana do IGR por Porte")
        st.plotly_chart(fig, use_container_width=True)

    # ── Testes estatísticos ──────────────────────────────────────────────────
    section_title("Testes de Hipótese Não-Paramétricos")

    warn_box(
        "Como o IGR não segue distribuição normal (confirmado pelo Shapiro-Wilk), "
        "usamos o <b>Kruskal-Wallis</b> (3 grupos) e <b>Mann-Whitney</b> (2 grupos) "
        "em vez de ANOVA e teste t."
    )

    # Kruskal-Wallis
    kw = teste_kruskal_wallis(df_f, coluna="IGR", grupo_col="PORTE_OPERADORA")
    st.markdown("**Kruskal-Wallis H — IGR difere entre os portes?**")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("H-Statistic", kw["H-Statistic"])
    col2.metric("p-valor", kw["p-valor"])
    col3.metric("Significativo?", kw["Significativo (α=0.05)"])
    col4.metric("Grupos", kw["Grupos"].count(",") + 1)
    st.info(f"📌 {kw['Conclusão']}")

    # Mann-Whitney pairwise
    section_title("Comparações Pareadas — Mann-Whitney U")

    pares = [
        ("GRANDE", "MÉDIO"),
        ("GRANDE", "PEQUENO"),
        ("MÉDIO", "PEQUENO"),
    ]
    cols = st.columns(3)
    for i, (a, b) in enumerate(pares):
        try:
            mw = teste_mann_whitney(df_f, "IGR", "PORTE_OPERADORA", a, b)
            with cols[i]:
                st.markdown(f"""
                <div class="metric-card">
                  <div class="label">{a} vs {b}</div>
                  <div style="font-size:13px; margin-top:8px;">
                    <b>Mediana {a}:</b> {mw['Mediana A']}<br>
                    <b>Mediana {b}:</b> {mw['Mediana B']}<br>
                    <b>p-valor:</b> {mw['p-valor']}<br>
                    <b>Sig.:</b> {mw['Significativo (α=0.05)']}
                  </div>
                </div>
                """, unsafe_allow_html=True)
        except Exception:
            with cols[i]:
                st.warning(f"Dados insuficientes para {a} vs {b}")

    footer()
