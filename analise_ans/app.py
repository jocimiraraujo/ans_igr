"""
Análise do Índice Geral de Reclamações (IGR) - ANS
Disciplina: Algoritmo II
Autor: Jocimir Araujo
"""

import streamlit as st
from utils.config import PAGE_CONFIG, THEME
from utils.session import init_session_state

# ── Configuração da página ──────────────────────────────────────────────────
st.set_page_config(**PAGE_CONFIG)

init_session_state()

# ── CSS Global ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
  }}

  /* Sidebar */
  [data-testid="stSidebar"] {{
    background: {THEME['sidebar_bg']};
    border-right: 1px solid {THEME['border']};
  }}
  [data-testid="stSidebar"] * {{
    color: {THEME['sidebar_text']} !important;
  }}
  [data-testid="stSidebar"] .stRadio label {{
    font-size: 14px;
    padding: 6px 0;
  }}
  [data-testid="stSidebarNav"] {{
    display: none;
  }}

  /* Cards métricas */
  .metric-card {{
    background: {THEME['card_bg']};
    border: 1px solid {THEME['border']};
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
  }}
  .metric-card .label {{
    font-size: 12px;
    color: {THEME['text_muted']};
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: .05em;
    margin-bottom: 4px;
  }}
  .metric-card .value {{
    font-size: 28px;
    font-weight: 700;
    color: {THEME['text_primary']};
    line-height: 1.1;
  }}
  .metric-card .delta {{
    font-size: 12px;
    margin-top: 4px;
  }}
  .delta-good {{ color: {THEME['success']}; }}
  .delta-bad  {{ color: {THEME['danger']}; }}

  /* Page header */
  .page-header {{
    background: linear-gradient(135deg, {THEME['primary']} 0%, {THEME['primary_dark']} 100%);
    border-radius: 16px;
    padding: 32px 36px;
    margin-bottom: 28px;
    color: white;
  }}
  .page-header h1 {{ font-size: 26px; font-weight: 700; margin: 0 0 6px; color: white; }}
  .page-header p  {{ font-size: 14px; opacity: .85; margin: 0; color: white; }}

  /* Section titles */
  .section-title {{
    font-size: 16px;
    font-weight: 600;
    color: {THEME['text_primary']};
    margin: 24px 0 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid {THEME['primary']};
  }}

  /* Info boxes */
  .info-box {{
    background: {THEME['info_bg']};
    border-left: 4px solid {THEME['primary']};
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    font-size: 14px;
    color: {THEME['text_primary']};
    margin: 12px 0;
  }}
  .warn-box {{
    background: {THEME['warn_bg']};
    border-left: 4px solid {THEME['warning']};
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    font-size: 14px;
    color: {THEME['text_primary']};
    margin: 12px 0;
  }}
  .success-box {{
    background: {THEME['success_bg']};
    border-left: 4px solid {THEME['success']};
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    font-size: 14px;
    color: {THEME['text_primary']};
    margin: 12px 0;
  }}

  /* Tabelas */
  .dataframe {{ font-size: 13px !important; }}

  /* Tags de porte */
  .badge {{
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
  }}
  .badge-grande  {{ background:#D1FAE5; color:#065F46; }}
  .badge-medio   {{ background:#EDE9FE; color:#4C1D95; }}
  .badge-pequeno {{ background:#FEF3C7; color:#78350F; }}

  /* Sidebar nav label */
  .nav-label {{
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: .08em;
    opacity: .6;
    margin: 16px 0 6px;
    padding: 0 4px;
  }}

  /* Footer */
  footer {{ visibility: hidden; }}
  .custom-footer {{
    text-align: center;
    font-size: 12px;
    color: {THEME['text_muted']};
    padding: 24px 0 8px;
    border-top: 1px solid {THEME['border']};
    margin-top: 40px;
  }}
</style>
""", unsafe_allow_html=True)

# ── Navegação lateral ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 8px 0 20px;">
      <div style="font-size:20px; font-weight:700; color:#1E3A5F;">🏥 Análise IGR</div>
      <div style="font-size:12px; opacity:.7; margin-top:2px;">ANS · Algoritmo II</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nav-label">Menu</div>', unsafe_allow_html=True)

    pagina = st.radio(
        label="Menu de páginas",
        options=[
            "🏠  Início",
            "📖  O que é o IGR?",
            "📊  Estatística Descritiva",
            "📦  Análise por Porte",
            "🩺  Análise por Cobertura",
            "📈  Evolução Temporal",
            "🔗  Correlações",
            "🎯  Modelagem Estatística",
            "🔍  Buscar Operadora",
        ],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("""
    <div style="font-size:12px; opacity:.65; line-height:1.6;">
      <b>Disciplina:</b> Algoritmo II<br>
      <b>Autor:</b> Jocimir Araujo<br>
      <b>Fonte:</b> ANS · dados_IGR_limpos.csv
    </div>
    """, unsafe_allow_html=True)

# ── Roteador de páginas ─────────────────────────────────────────────────────
if pagina == "🏠  Início":
    from pages.home import render
    render()
elif pagina == "📖  O que é o IGR?":
    from pages.about_igr import render
    render()
elif pagina == "📊  Estatística Descritiva":
    from pages.descritiva import render
    render()
elif pagina == "📦  Análise por Porte":
    from pages.por_porte import render
    render()
elif pagina == "🩺  Análise por Cobertura":
    from pages.por_cobertura import render
    render()
elif pagina == "📈  Evolução Temporal":
    from pages.temporal import render
    render()
elif pagina == "🔗  Correlações":
    from pages.correlacoes import render
    render()
elif pagina == "🎯  Modelagem Estatística":
    from pages.modelagem import render
    render()
elif pagina == "🔍  Buscar Operadora":
    from pages.busca import render
    render()
