"""
utils/session.py — Gerenciamento do estado da sessão Streamlit
"""
import streamlit as st


def init_session_state():
    defaults = {
        "df_loaded": False,
        "df":        None,
        "filtro_cobertura": "Todas",
        "filtro_porte":     "Todos",
        "filtro_periodo":   None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
