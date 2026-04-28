"""
pages/por_cobertura.py — Análise do IGR por Tipo de Cobertura
"""
import streamlit as st
from utils.data_loader import get_data, apply_filters
from components.ui import page_header, section_title, info_box, warn_box, footer
from components.charts import boxplot_por_grupo, violin_por_grupo, histograma_igr
from analysis.estatistica_descritiva import resumo_por_grupo
from analysis.correlacoes import teste_mann_whitney
from utils.config import ANS_METAS


def render():
    page_header(
        title="Análise por Tipo de Cobertura",
        subtitle="Comparação entre Assistência Médica e Cobertura Exclusivamente Odontológica",
        icon="🩺",
    )

    df = get_data()

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Filtros**")
    portes = ["Todos"] + \
        sorted(df["PORTE_OPERADORA"].dropna().unique().tolist())
    porte = st.sidebar.selectbox("Porte", portes, key="cob_porte")
    excluir_zero = st.sidebar.checkbox("Excluir IGR = 0", key="cob_zero")

    df_f = apply_filters(df, porte=porte, excluir_zero_igr=excluir_zero)

    if df_f.empty:
        st.warning("Nenhum dado com os filtros selecionados.")
        return

    warn_box(
        "A ANS define <b>metas separadas</b> para Assistência Médica e Odontológico. "
        "Não compare os valores de IGR entre coberturas diretamente — as escalas são diferentes."
    )

    # ── Metas por cobertura ──────────────────────────────────────────────────
    section_title("Metas ANS por Cobertura")
    cols = st.columns(2)
    for i, (cobertura_nome, vals) in enumerate(ANS_METAS.items()):
        igr_cob = df_f[df_f["COBERTURA"] == cobertura_nome]["IGR"]
        mediana_atual = igr_cob.median() if not igr_cob.empty else None

        with cols[i]:
            status = ""
            cor = "#059669"
            if mediana_atual is not None:
                if mediana_atual <= vals["meta"]:
                    status = "✅ Abaixo da meta"
                    cor = "#059669"
                elif mediana_atual <= vals["alerta"]:
                    status = "⚠️ Em atenção"
                    cor = "#D97706"
                else:
                    status = "🔴 Crítico"
                    cor = "#DC2626"

            st.markdown(f"""
            <div class="metric-card">
              <div class="label">{cobertura_nome}</div>
              <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-top:10px;">
                <div>
                  <div style="font-size:11px; color:#718096;">Mediana atual</div>
                  <div style="font-size:28px; font-weight:700; color:{cor};">
                    {f"{mediana_atual:.2f}" if mediana_atual else "—"}
                  </div>
                </div>
                <div style="text-align:right; font-size:12px; color:#718096;">
                  Meta: ≤ {vals['meta']}<br>
                  Alerta: ≤ {vals['alerta']}<br>
                  <b style="color:{cor};">{status}</b>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Resumo estatístico ───────────────────────────────────────────────────
    section_title("Estatísticas por Cobertura")
    resumo = resumo_por_grupo(df_f, grupo="COBERTURA")
    st.dataframe(resumo, use_container_width=True, hide_index=True)

    # ── Visualizações ────────────────────────────────────────────────────────
    section_title("Distribuição Comparativa do IGR")
    tipo_viz = st.radio("Visualização:", [
                        "Boxplot", "Violin", "Histograma sobrepost"], horizontal=True)

    if tipo_viz == "Boxplot":
        fig = boxplot_por_grupo(
            df_f, "COBERTURA", titulo="Boxplot do IGR por Cobertura")
        st.plotly_chart(fig, use_container_width=True)
    elif tipo_viz == "Violin":
        fig = violin_por_grupo(
            df_f, "COBERTURA", titulo="Violin do IGR por Cobertura")
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig = histograma_igr(df_f, grupo="COBERTURA",
                             titulo="Histograma do IGR por Cobertura")
        st.plotly_chart(fig, use_container_width=True)

    # ── Boxplot por porte × cobertura ────────────────────────────────────────
    section_title("IGR por Porte × Cobertura")
    import plotly.graph_objects as go
    from utils.config import PLOTLY_COLORS, PLOTLY_TEMPLATE

    ordem_porte = ["PEQUENO", "MÉDIO", "GRANDE"]
    ordem_idx = {porte_nome: idx for idx, porte_nome in enumerate(ordem_porte)}
    resumo_box = (
        df_f.dropna(subset=["PORTE_OPERADORA", "COBERTURA", "IGR"])
        .groupby(["PORTE_OPERADORA", "COBERTURA"], observed=True)["IGR"]
        .agg(
            N="count",
            media="mean",
            minimo="min",
            q1=lambda s: s.quantile(0.25),
            mediana="median",
            q3=lambda s: s.quantile(0.75),
            maximo="max",
        )
        .reset_index()
    )

    if resumo_box.empty:
        st.warning(
            "Nenhum dado disponível para montar o gráfico por porte e cobertura.")
    else:
        resumo_box["PORTE_OPERADORA"] = resumo_box["PORTE_OPERADORA"].astype(
            str)
        resumo_box["iqr"] = resumo_box["q3"] - resumo_box["q1"]
        resumo_box["lowerfence"] = resumo_box.apply(
            lambda row: max(row["minimo"], row["q1"] - 1.5 * row["iqr"]),
            axis=1,
        )
        resumo_box["upperfence"] = resumo_box.apply(
            lambda row: min(row["maximo"], row["q3"] + 1.5 * row["iqr"]),
            axis=1,
        )

        resumo_exibicao = resumo_box[[
            "PORTE_OPERADORA", "COBERTURA", "N", "media", "q1", "mediana", "q3"
        ]].copy()
        resumo_exibicao["_ordem"] = resumo_exibicao["PORTE_OPERADORA"].map(
            ordem_idx)
        resumo_exibicao = resumo_exibicao.sort_values(
            ["_ordem", "COBERTURA"]).drop(columns="_ordem")
        resumo_exibicao.columns = [
            "Porte", "Cobertura", "N", "Média", "Q1", "Mediana", "Q3"
        ]
        st.dataframe(
            resumo_exibicao,
            use_container_width=True,
            hide_index=True,
        )

        fig2 = go.Figure()
        for cobertura_nome in sorted(resumo_box["COBERTURA"].unique()):
            sub = resumo_box[resumo_box["COBERTURA"] == cobertura_nome].copy()
            sub["ordem"] = sub["PORTE_OPERADORA"].map(ordem_idx)
            sub = sub.sort_values("ordem")

            fig2.add_trace(go.Box(
                name=cobertura_nome,
                x=sub["PORTE_OPERADORA"],
                q1=sub["q1"],
                median=sub["mediana"],
                q3=sub["q3"],
                lowerfence=sub["lowerfence"],
                upperfence=sub["upperfence"],
                mean=sub["media"],
                boxmean=True,
                marker_color=PLOTLY_COLORS.get(cobertura_nome),
                customdata=sub[["N", "media"]],
                hovertemplate=(
                    "Porte: %{x}<br>"
                    "Cobertura: " + cobertura_nome + "<br>"
                    "N: %{customdata[0]}<br>"
                    "Média: %{customdata[1]:.2f}<br>"
                    "Q1: %{q1:.2f}<br>"
                    "Mediana: %{median:.2f}<br>"
                    "Q3: %{q3:.2f}<br>"
                    "<extra></extra>"
                ),
            ))

        fig2.update_layout(
            title="IGR por Porte de Operadora, estratificado por Cobertura",
            template=PLOTLY_TEMPLATE,
            font_family="Inter",
            boxmode="group",
            xaxis_title="Porte da Operadora",
            yaxis_title="IGR",
            legend_title_text="Cobertura",
            height=520,
            margin=dict(t=60, b=40, l=60, r=20),
        )
        fig2.update_yaxes(rangemode="tozero")
        st.plotly_chart(fig2, use_container_width=True)
        st.caption(
            "Boxplot renderizado com quartis pré-calculados para evitar travamento com muitos registros.")

    # ── Teste Mann-Whitney ───────────────────────────────────────────────────
    section_title("Teste Mann-Whitney: Médica vs Odontológica")
    try:
        coberturas = df_f["COBERTURA"].unique().tolist()
        if len(coberturas) >= 2:
            mw = teste_mann_whitney(
                df_f, "IGR", "COBERTURA", coberturas[0], coberturas[1])
            col1, col2, col3, col4 = st.columns(4)
            col1.metric(f"Mediana {coberturas[0][:12]}...", mw["Mediana A"])
            col2.metric(f"Mediana {coberturas[1][:12]}...", mw["Mediana B"])
            col3.metric("p-valor", mw["p-valor"])
            col4.metric("Significativo?", mw["Significativo (α=0.05)"])
            st.info(f"📌 {mw['Conclusão']}")
        else:
            info_box("Apenas uma cobertura disponível com os filtros atuais.")
    except Exception as e:
        st.warning(f"Não foi possível executar o teste: {e}")

    footer()
