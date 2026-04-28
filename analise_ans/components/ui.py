"""
components/ui.py — Componentes reutilizáveis de interface
"""
from __future__ import annotations
import streamlit as st
import pandas as pd


def page_header(title: str, subtitle: str, icon: str = ""):
    st.markdown(f"""
    <div class="page-header">
      <h1>{icon} {title}</h1>
      <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def metric_card(label: str, value: str, delta: str = "", delta_good: bool = True):
    delta_class = "delta-good" if delta_good else "delta-bad"
    delta_html = f'<div class="delta {delta_class}">{delta}</div>' if delta else ""
    st.markdown(f"""
    <div class="metric-card">
      <div class="label">{label}</div>
      <div class="value">{value}</div>
      {delta_html}
    </div>
    """, unsafe_allow_html=True)


def section_title(text: str):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def info_box(text: str):
    st.markdown(f'<div class="info-box">ℹ️ {text}</div>', unsafe_allow_html=True)


def warn_box(text: str):
    st.markdown(f'<div class="warn-box">⚠️ {text}</div>', unsafe_allow_html=True)


def success_box(text: str):
    st.markdown(f'<div class="success-box">✅ {text}</div>', unsafe_allow_html=True)


def porte_badge(porte: str) -> str:
    classes = {
        "GRANDE":  "badge-grande",
        "MÉDIO":   "badge-medio",
        "PEQUENO": "badge-pequeno",
    }
    cls = classes.get(porte.upper(), "badge-pequeno")
    return f'<span class="badge {cls}">{porte}</span>'


def filter_sidebar(df: pd.DataFrame) -> dict:
    """
    Sidebar de filtros reutilizável.
    Retorna dicionário com os valores selecionados.
    """
    st.sidebar.markdown("---")
    st.sidebar.markdown('<div class="nav-label">Filtros</div>', unsafe_allow_html=True)

    coberturas = ["Todas"] + sorted(df["COBERTURA"].dropna().unique().tolist())
    cobertura = st.sidebar.selectbox("Cobertura", coberturas, key="sb_cobertura")

    portes = ["Todos"] + sorted(df["PORTE_OPERADORA"].dropna().unique().tolist())
    porte = st.sidebar.selectbox("Porte", portes, key="sb_porte")

    excluir_zero = st.sidebar.checkbox(
        "Excluir IGR = 0", value=False, key="sb_excluir_zero",
        help="Remove registros sem reclamações (IGR exato = 0)"
    )

    return dict(cobertura=cobertura, porte=porte, excluir_zero_igr=excluir_zero)


def data_unavailable_warning():
    st.warning(
        "⚠️ Arquivo **dados_IGR_limpos.csv** não encontrado na pasta do projeto. "
        "Coloque o arquivo CSV na mesma pasta do `app.py` e reinicie o app.",
        icon="📂",
    )


def footer():
    st.markdown("""
    <div class="custom-footer">
      🏥 <b>IGR Analytics</b> · Disciplina: Algoritmo II · Autor: <b>Jocimir Aujo</b><br>
      Dados: Agência Nacional de Saúde Suplementar (ANS) · 2026
    </div>
    """, unsafe_allow_html=True)
