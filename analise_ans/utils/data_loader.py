"""
utils/data_loader.py — Carregamento, cache e pré-processamento do CSV
"""
from __future__ import annotations

import pandas as pd
import streamlit as st
from pathlib import Path


CSV_PATH = Path(__file__).resolve().parents[1] / "dados_IGR_limpos.csv"


@st.cache_data(show_spinner="Carregando dados do IGR…")
def load_data(path: str | Path = CSV_PATH) -> pd.DataFrame:
    """
    Lê o CSV, converte tipos e retorna o DataFrame pronto para análise.
    Usa cache do Streamlit para evitar releitura a cada interação.
    """
    df = pd.read_csv(
        path,
        sep=";",
        dtype={
            "REGISTRO_ANS":    "int64",
            "RAZAO_SOCIAL":    "str",
            "COBERTURA":       "str",
            "IGR":             "float64",
            "QTD_RECLAMACOES": "int64",
            "QTD_BENEFICIARIOS": "int64",
            "PORTE_OPERADORA": "str",
        },
        parse_dates=["DT_ATUALIZACAO"],
    )

    # Converte colunas de período
    for col in ["COMPETENCIA", "COMPETENCIA_BENEFICIARIO"]:
        if col in df.columns:
            df[col] = pd.PeriodIndex(df[col], freq="M")

    # Normaliza strings
    str_cols = ["RAZAO_SOCIAL", "COBERTURA", "PORTE_OPERADORA"]
    for c in str_cols:
        df[c] = df[c].str.strip().str.upper()

    # Garante ordem categórica do porte
    ordem_porte = ["PEQUENO", "MÉDIO", "GRANDE"]
    df["PORTE_OPERADORA"] = pd.Categorical(
        df["PORTE_OPERADORA"], categories=ordem_porte, ordered=True
    )

    # Coluna auxiliar de ano-mês para gráficos temporais
    if "COMPETENCIA" in df.columns:
        df["ANO_MES"] = df["COMPETENCIA"].dt.to_timestamp()

    # Flag de outlier severo (z-score robusto > 3.5)
    mediana = df["IGR"].median()
    mad = (df["IGR"] - mediana).abs().median()
    df["Z_ROBUSTO"] = (df["IGR"] - mediana) / (mad if mad > 0 else 1)
    df["OUTLIER"] = df["Z_ROBUSTO"].abs() > 3.5

    return df


def get_data() -> pd.DataFrame:
    """Ponto de entrada único para obter o DataFrame em qualquer página."""
    if st.session_state.df is None:
        st.session_state.df = load_data()
        st.session_state.df_loaded = True
    return st.session_state.df


def apply_filters(
    df: pd.DataFrame,
    cobertura: str = "Todas",
    porte: str = "Todos",
    periodo_inicio=None,
    periodo_fim=None,
    excluir_zero_igr: bool = False,
) -> pd.DataFrame:
    """Aplica filtros interativos sobre o DataFrame."""
    mask = pd.Series(True, index=df.index)

    if cobertura != "Todas":
        mask &= df["COBERTURA"] == cobertura.upper()

    if porte != "Todos":
        mask &= df["PORTE_OPERADORA"] == porte.upper()

    if periodo_inicio and "ANO_MES" in df.columns:
        mask &= df["ANO_MES"] >= pd.Timestamp(periodo_inicio)

    if periodo_fim and "ANO_MES" in df.columns:
        mask &= df["ANO_MES"] <= pd.Timestamp(periodo_fim)

    if excluir_zero_igr:
        mask &= df["IGR"] > 0

    return df[mask].copy()
