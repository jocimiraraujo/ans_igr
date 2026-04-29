"""
pages/about_igr.py — Página explicativa: O que é o IGR e como se aplica
"""
import streamlit as st
from components.ui import page_header, section_title, info_box, warn_box, success_box, footer
from utils.config import THEME, ANS_METAS


def render():
    page_header(
        title="O que é o Índice Geral de Reclamações?",
        subtitle="Entenda o IGR, sua fórmula, interpretação e como ele se aplica à regulação da ANS",
        icon="📖",
    )

    # ── Definição ────────────────────────────────────────────────────────────
    section_title("Definição")
    st.markdown("""
    O **Índice Geral de Reclamações (IGR)** é um indicador produzido pela
    **Agência Nacional de Saúde Suplementar (ANS)** que mede o número médio de
    reclamações de beneficiários de planos privados de saúde que recorreram à ANS
    em um período de **doze meses** (ano-base), tendo como referência cada
    **100.000 beneficiários** do universo analisado.

    O IGR é um dos principais instrumentos de transparência regulatória do setor
    de saúde suplementar no Brasil, sendo divulgado publicamente e utilizado
    como critério em processos regulatórios.
    """)

    info_box(
        "O IGR integra o Programa de Monitoramento da Qualidade dos Planos de Saúde "
        "(PMAQ) e é uma das métricas utilizadas no Índice de Desempenho da Saúde "
        "Suplementar (IDSS)."
    )

    # ── Fórmula ──────────────────────────────────────────────────────────────
    section_title("Fórmula de Cálculo")
    st.markdown("""
    O cálculo do IGR segue a seguinte lógica:
    """)

    st.latex(r"""
    IGR = \frac{\text{Número de Reclamações no Ano-Base}}
               {\text{Número de Beneficiários no Universo Analisado}}
    \times 100.000
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
          <div class="label">Numerador</div>
          <div style="font-size:14px; color:{THEME['text_primary']}; margin-top:8px;">
            Total de reclamações recebidas nos <b>12 meses</b> do ano-base,
            registradas no sistema da ANS por beneficiários do plano.
          </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
          <div class="label">Denominador</div>
          <div style="font-size:14px; color:{THEME['text_primary']}; margin-top:8px;">
            Universo de <b>beneficiários analisados</b> no período
            correspondente à competência beneficiário.
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Regras metodológicas ─────────────────────────────────────────────────
    section_title("Regras Metodológicas da ANS")
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("""
        **✅ O que está incluído:**
        - Reclamações recebidas nos 12 meses do ano-base
        - Reclamações médico-hospitalares (Assistência Médica)
        - Reclamações exclusivamente odontológicas (coberturas odonto)
        """)
    with col_b:
        st.markdown("""
        **❌ O que está excluído:**
        - Reclamações fora do período do ano-base
        - Cancelamentos e solicitações de informação
        - Operadoras com menos de X beneficiários (limiar mínimo)
        """)

    warn_box(
        "O indicador diferencia as reclamações <b>médico-hospitalares</b> das "
        "<b>exclusivamente odontológicas</b>, estabelecendo metas específicas "
        "para cada subgrupo. Não é correto comparar IGR médico com IGR odonto diretamente."
    )

    # ── Interpretação ────────────────────────────────────────────────────────
    section_title("Como Interpretar o IGR")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div style="background:#ECFDF5; border-radius:12px; padding:20px; text-align:center; border:1px solid #6EE7B7;">
          <div style="font-size:32px; font-weight:700; color:#059669;">🟢</div>
          <div style="font-size:16px; font-weight:600; color:#065F46; margin:8px 0;">IGR Baixo</div>
          <div style="font-size:13px; color:#065F46; opacity:.8;">
            Poucos beneficiários recorreram à ANS.<br>
            <b>Maior satisfação</b> com a operadora.
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="background:#FFFBEB; border-radius:12px; padding:20px; text-align:center; border:1px solid #FCD34D;">
          <div style="font-size:32px; font-weight:700; color:#D97706;">🟡</div>
          <div style="font-size:16px; font-weight:600; color:#78350F; margin:8px 0;">IGR Médio</div>
          <div style="font-size:13px; color:#78350F; opacity:.8;">
            Volume de reclamações em patamar de <b>atenção</b>.<br>Monitoramento recomendado.
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="background:#FEF2F2; border-radius:12px; padding:20px; text-align:center; border:1px solid #FCA5A5;">
          <div style="font-size:32px; font-weight:700; color:#DC2626;">🔴</div>
          <div style="font-size:16px; font-weight:600; color:#7F1D1D; margin:8px 0;">IGR Alto</div>
          <div style="font-size:13px; color:#7F1D1D; opacity:.8;">
            Muitos beneficiários reclamaram.<br>
            <b>Pior avaliação</b> da operadora pela ANS.
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Metas de referência ──────────────────────────────────────────────────
    section_title("Metas e Limiares de Referência")
    for cobertura, valores in ANS_METAS.items():
        st.markdown(f"""
        <div class="metric-card">
          <div class="label">{cobertura}</div>
          <div style="display:flex; gap:32px; margin-top:10px;">
            <div>
              <span style="font-size:11px; color:{THEME['text_muted']};">META (bom desempenho)</span><br>
              <span style="font-size:22px; font-weight:700; color:{THEME['success']};">≤ {valores['meta']}</span>
            </div>
            <div>
              <span style="font-size:11px; color:{THEME['text_muted']};">ALERTA</span><br>
              <span style="font-size:22px; font-weight:700; color:{THEME['warning']};">≤ {valores['alerta']}</span>
            </div>
            <div>
              <span style="font-size:11px; color:{THEME['text_muted']};">CRÍTICO</span><br>
              <span style="font-size:22px; font-weight:700; color:{THEME['danger']};">&gt; {valores['alerta']}</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Limitações ───────────────────────────────────────────────────────────
    section_title("Limitações e Cuidados na Análise")
    st.markdown("""
    | Limitação | Impacto | Recomendação |
    |-----------|---------|--------------|
    | **Operadoras pequenas** têm IGR volátil | Uma reclamação pode multiplicar o IGR | Usar z-score robusto para comparar |
    | **Subnotificação** pode existir em algumas regiões | IGR = 0 pode ser ausência de dado | Verificar QTD_BENEFICIARIOS |
    | **Distribuição assimétrica** à direita | Média não representa o setor | Usar **mediana** e **IQR** |
    | **Outliers severos** distorcem modelos | Regressão OLS pode ser inválida | Usar **regressão quantílica** |
    | **Mistura de tipos** de cobertura | Médico ≠ Odonto em escala | Sempre estratificar por COBERTURA |
    """)

    success_box(
        "Para uma análise correta, sempre estratifique por <b>COBERTURA</b> antes de comparar operadoras, "
        "e use <b>mediana + IQR</b> como medidas centrais em vez de média e desvio-padrão."
    )

    footer()
