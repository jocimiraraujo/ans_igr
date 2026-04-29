"""
pages/home.py — Página inicial com visão geral e KPIs do dataset
"""
import streamlit as st
import pandas as pd
from utils.data_loader import get_data
from components.ui import page_header, metric_card, section_title, info_box, footer
from utils.config import THEME


def render():
    page_header(
        title="Análise IGR · ANS",
        subtitle="Análise estatística do Índice Geral de Reclamações · Disciplina: Algoritmo II · Autor: Jocimir Araujo",
        icon="🏥",
    )

    # ── Carrega dados ────────────────────────────────────────────────────────
    try:
        df = get_data()
        dados_ok = True
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.info("Certifique-se de que **dados_IGR_limpos.csv** está na pasta do projeto.")
        dados_ok = False

    # ── Sobre o projeto ──────────────────────────────────────────────────────
    section_title("Sobre o Projeto")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("""
        Este painel analisa o **Índice Geral de Reclamações (IGR)** da Agência Nacional
        de Saúde Suplementar (ANS), aplicando métodos de **estatística descritiva robusta**
        adequados à natureza assimétrica dos dados e à presença de outliers.

        **Metodologia implementada:**
        - Medidas robustas: Mediana, IQR, MAD e Média Aparada
        - Visualizações: Boxplot, Violin, QQ-Plot, Histograma, Série temporal
        - Testes não-paramétricos: Kruskal-Wallis, Mann-Whitney, Dunn post-hoc
        - Correlações: Spearman ρ e Kendall τ
        - Modelagem: Regressão log-linear e Regressão Quantílica
        - Detecção de outliers: Tukey (fences) e Z-score Robusto
        """)

    with col2:
        st.markdown(f"""
        <div style="background:{THEME['info_bg']}; border-radius:12px; padding:20px; border:1px solid {THEME['border']};">
          <div style="font-size:13px; color:{THEME['text_muted']}; margin-bottom:12px; font-weight:600;">INFORMAÇÕES ACADÊMICAS</div>
          <div style="font-size:14px; margin-bottom:8px;"><b>Disciplina:</b> Algoritmo II</div>
          <div style="font-size:14px; margin-bottom:8px;"><b>Autor:</b> Jocimir Araujo</div>
          <div style="font-size:14px; margin-bottom:8px;"><b>Fonte:</b> ANS</div>
          <div style="font-size:14px;"><b>Dataset:</b> dados_IGR_limpos.csv</div>
        </div>
        """, unsafe_allow_html=True)

    # ── KPIs principais ──────────────────────────────────────────────────────
    if dados_ok:
        section_title("Visão Geral do Dataset")
        c1, c2, c3, c4 = st.columns(4)

        with c1:
            metric_card("Total de Registros", f"{len(df):,}".replace(",", "."), "dados_IGR_limpos.csv")
        with c2:
            n_op = df["REGISTRO_ANS"].nunique()
            metric_card("Operadoras Únicas", f"{n_op:,}".replace(",", "."))
        with c3:
            mediana = df["IGR"].median()
            metric_card("Mediana do IGR", f"{mediana:.2f}",
                       "por 100 mil beneficiários")
        with c4:
            n_out = df["OUTLIER"].sum()
            pct_out = n_out / len(df) * 100
            metric_card("Outliers (Z-rob > 3.5)", f"{n_out:,}".replace(",", "."),
                       f"≈ {pct_out:.1f}% do total", delta_good=False)

        c5, c6, c7, c8 = st.columns(4)
        with c5:
            metric_card("IGR Máximo", f"{df['IGR'].max():.2f}")
        with c6:
            metric_card("IQR do IGR", f"{df['IGR'].quantile(0.75) - df['IGR'].quantile(0.25):.2f}")
        with c7:
            n_per = df["COMPETENCIA"].nunique() if "COMPETENCIA" in df.columns else "—"
            metric_card("Competências (meses)", str(n_per))
        with c8:
            coberturas = df["COBERTURA"].nunique()
            metric_card("Tipos de Cobertura", str(coberturas))

        # ── Tabela de amostra ────────────────────────────────────────────────
        section_title("Amostra dos Dados")
        info_box(
            "Interpretação do IGR: quanto <b>menor</b> o valor, <b>maior</b> a satisfação "
            "dos beneficiários. Quanto <b>maior</b> o IGR, pior tende a ser a avaliação da operadora."
        )

        colunas_exibir = ["REGISTRO_ANS", "RAZAO_SOCIAL", "COBERTURA",
                          "IGR", "QTD_RECLAMACOES", "QTD_BENEFICIARIOS", "PORTE_OPERADORA"]
        st.dataframe(
            df[colunas_exibir].head(20),
            use_container_width=True,
            hide_index=True,
        )

        # ── Distribuição por porte ───────────────────────────────────────────
        section_title("Composição do Dataset")
        col_a, col_b = st.columns(2)

        with col_a:
            import plotly.express as px
            porte_cnt = df["PORTE_OPERADORA"].value_counts().reset_index()
            porte_cnt.columns = ["Porte", "Registros"]
            from utils.config import PLOTLY_COLORS, PLOTLY_TEMPLATE
            fig = px.pie(porte_cnt, names="Porte", values="Registros",
                         color="Porte", color_discrete_map=PLOTLY_COLORS,
                         title="Registros por Porte", template=PLOTLY_TEMPLATE,
                         hole=0.45)
            fig.update_layout(font_family="Inter")
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            cob_cnt = df["COBERTURA"].value_counts().reset_index()
            cob_cnt.columns = ["Cobertura", "Registros"]
            fig2 = px.pie(cob_cnt, names="Cobertura", values="Registros",
                          color="Cobertura", color_discrete_map=PLOTLY_COLORS,
                          title="Registros por Cobertura", template=PLOTLY_TEMPLATE,
                          hole=0.45)
            fig2.update_layout(font_family="Inter")
            st.plotly_chart(fig2, use_container_width=True)

    footer()
