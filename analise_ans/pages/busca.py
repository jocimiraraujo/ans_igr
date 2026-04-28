"""
pages/busca.py — Busca e perfil individual de operadoras
"""
import streamlit as st
import numpy as np
import plotly.express as px
from utils.data_loader import get_data
from components.ui import page_header, section_title, info_box, warn_box, metric_card, footer
from analysis.modelagem import ranking_percentilico, analise_tukey
from utils.config import PLOTLY_COLORS, PLOTLY_TEMPLATE, ANS_METAS


def render():
    page_header(
        title="Buscar Operadora",
        subtitle="Perfil detalhado, histórico e classificação de desempenho de uma operadora específica",
        icon="🔍",
    )

    df = get_data()
    df_rank = ranking_percentilico(df)

    # ── Busca ────────────────────────────────────────────────────────────────
    section_title("Selecionar Operadora")
    busca = st.text_input("Digite parte do nome ou o Registro ANS:", placeholder="Ex: Unimed, Bradesco, 5711…")

    if not busca:
        info_box("Digite um nome ou registro para buscar a operadora.")
        footer()
        return

    # Filtra por nome ou registro
    mask = (
        df_rank["RAZAO_SOCIAL"].str.contains(busca.upper(), na=False) |
        df_rank["REGISTRO_ANS"].astype(str).str.contains(busca, na=False)
    )
    resultados = df_rank[mask][["REGISTRO_ANS", "RAZAO_SOCIAL", "PORTE_OPERADORA"]].drop_duplicates()

    if resultados.empty:
        st.warning("Nenhuma operadora encontrada. Tente outro termo.")
        footer()
        return

    opcoes = resultados.apply(
        lambda r: f"{r['REGISTRO_ANS']} — {r['RAZAO_SOCIAL']} ({r['PORTE_OPERADORA']})", axis=1
    ).tolist()

    escolha = st.selectbox("Operadoras encontradas:", opcoes)
    registro = int(escolha.split("—")[0].strip())

    df_op = df_rank[df_rank["REGISTRO_ANS"] == registro].copy()

    if df_op.empty:
        st.warning("Sem dados para esta operadora.")
        footer()
        return

    # ── Cabeçalho da operadora ───────────────────────────────────────────────
    nome = df_op["RAZAO_SOCIAL"].iloc[0]
    porte = df_op["PORTE_OPERADORA"].iloc[0]

    st.markdown(f"""
    <div class="page-header" style="margin-top:12px;">
      <h1 style="font-size:20px;">🏢 {nome}</h1>
      <p>Registro ANS: {registro} · Porte: {porte}</p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPIs por cobertura ───────────────────────────────────────────────────
    section_title("Desempenho por Cobertura")
    for _, row in df_op.groupby("COBERTURA", observed=True).agg(
        IGR_med=("IGR", "median"),
        IGR_max=("IGR", "max"),
        N=("IGR", "count"),
        Percentil=("PERCENTIL", "mean"),
        Classif=("CLASSIFICACAO", lambda x: x.mode()[0] if len(x) > 0 else "—"),
        Reclamacoes=("QTD_RECLAMACOES", "sum"),
    ).reset_index().iterrows():
        meta = ANS_METAS.get(row["COBERTURA"], {})
        limite = meta.get("alerta", 9999)
        status = "✅ OK" if row["IGR_med"] <= meta.get("meta", 9999) else (
            "⚠️ Atenção" if row["IGR_med"] <= limite else "🔴 Crítico"
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card(f"IGR Mediano ({row['COBERTURA'][:15]}…)", f"{row['IGR_med']:.2f}", status)
        with col2:
            metric_card("Percentil no setor", f"{row['Percentil']:.1f}%",
                        row["Classif"], delta_good=row["Percentil"] < 50)
        with col3:
            metric_card("Máximo observado", f"{row['IGR_max']:.2f}")
        with col4:
            metric_card("Total de Reclamações", f"{int(row['Reclamacoes']):,}".replace(",", "."))

    # ── Evolução temporal ────────────────────────────────────────────────────
    if "ANO_MES" in df_op.columns:
        section_title("Evolução do IGR ao Longo do Tempo")
        df_temp = df_op.groupby(["ANO_MES", "COBERTURA"], observed=True)["IGR"].median().reset_index()

        fig = px.line(
            df_temp, x="ANO_MES", y="IGR", color="COBERTURA",
            color_discrete_map=PLOTLY_COLORS,
            markers=True,
            template=PLOTLY_TEMPLATE,
            title=f"Evolução do IGR — {nome}",
            labels={"IGR": "IGR Mediano", "ANO_MES": "Competência"},
        )
        # Linhas de referência ANS
        for cob, vals in ANS_METAS.items():
            fig.add_hline(y=vals["meta"], line_dash="dot",
                          line_color="#059669", opacity=0.5,
                          annotation_text=f"Meta {cob[:6]}: {vals['meta']}")
            fig.add_hline(y=vals["alerta"], line_dash="dash",
                          line_color="#D97706", opacity=0.5,
                          annotation_text=f"Alerta {cob[:6]}: {vals['alerta']}")

        fig.update_layout(font_family="Inter")
        st.plotly_chart(fig, use_container_width=True)

    # ── Posição no setor ─────────────────────────────────────────────────────
    section_title("Posição no Setor")
    for cob in df_op["COBERTURA"].unique():
        df_setor = df_rank[df_rank["COBERTURA"] == cob].copy()
        igr_op = df_op[df_op["COBERTURA"] == cob]["IGR"].median()
        pct = df_op[df_op["COBERTURA"] == cob]["PERCENTIL"].mean()

        if np.isnan(igr_op):
            continue

        st.markdown(f"**{cob}**")
        fig_hist = px.histogram(
            df_setor, x="IGR", nbins=60,
            color_discrete_sequence=["#CBD5E0"],
            template=PLOTLY_TEMPLATE,
            title=f"Distribuição do IGR no setor — {cob}",
        )
        fig_hist.add_vline(
            x=igr_op, line_color="#DC2626", line_width=2,
            annotation_text=f"{nome[:20]}… (IGR={igr_op:.1f}, p{pct:.0f})",
            annotation_position="top right",
        )
        fig_hist.update_layout(font_family="Inter",
                               xaxis_title="IGR", yaxis_title="Frequência")
        st.plotly_chart(fig_hist, use_container_width=True)

    # ── Tabela completa ───────────────────────────────────────────────────────
    section_title("Histórico Completo")
    cols_show = ["COMPETENCIA", "COBERTURA", "IGR", "QTD_RECLAMACOES",
                 "QTD_BENEFICIARIOS", "PERCENTIL", "CLASSIFICACAO"]
    cols_show = [c for c in cols_show if c in df_op.columns]
    st.dataframe(
        df_op[cols_show].sort_values("COMPETENCIA" if "COMPETENCIA" in df_op.columns else "IGR",
                                     ascending=False),
        use_container_width=True,
        hide_index=True,
    )

    footer()
