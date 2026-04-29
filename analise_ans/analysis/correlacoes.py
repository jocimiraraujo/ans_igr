"""
analysis/correlacoes.py — Correlações e testes de hipótese não-paramétricos
Implementa Spearman, Kendall, Mann-Whitney, Kruskal-Wallis e Dunn.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats
try:
    from scikit_posthocs import posthoc_dunn
    HAS_POSTHOCS = True
except ImportError:
    HAS_POSTHOCS = False


def correlacao_spearman(
    df: pd.DataFrame, x: str, y: str
) -> dict:
    """Correlação de Spearman entre duas variáveis numéricas."""
    sub = df[[x, y]].dropna()
    rho, p = stats.spearmanr(sub[x], sub[y])
    return {
        "Variável X": x,
        "Variável Y": y,
        "Método": "Spearman",
        "ρ (rho)": round(rho, 4),
        "p-valor": round(p, 6),
        "Significativo (α=0.05)": "Sim ✓" if p < 0.05 else "Não ✗",
        "Força": _forca_correlacao(rho),
    }


def correlacao_kendall(df: pd.DataFrame, x: str, y: str) -> dict:
    """Correlação de Kendall (mais conservadora, melhor para amostras pequenas)."""
    sub = df[[x, y]].dropna()
    tau, p = stats.kendalltau(sub[x], sub[y])
    return {
        "Variável X": x,
        "Variável Y": y,
        "Método": "Kendall",
        "τ (tau)": round(tau, 4),
        "p-valor": round(p, 6),
        "Significativo (α=0.05)": "Sim ✓" if p < 0.05 else "Não ✗",
        "Força": _forca_correlacao(tau),
    }


def matriz_correlacao_spearman(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    """Matriz de correlação de Spearman para múltiplas colunas."""
    sub = df[colunas].dropna()
    corr, _ = stats.spearmanr(sub)
    if len(colunas) == 2:
        # scipy retorna escalar para 2 variáveis
        mat = np.array([[1.0, corr], [corr, 1.0]])
    else:
        mat = corr
    return pd.DataFrame(mat, index=colunas, columns=colunas).round(4)


def teste_mann_whitney(
    df: pd.DataFrame, coluna: str, grupo_col: str, grupo_a: str, grupo_b: str
) -> dict:
    """
    Mann-Whitney U — compara dois grupos independentes.
    Alternativa não-paramétrica ao teste t.
    """
    a = df[df[grupo_col] == grupo_a][coluna].dropna()
    b = df[df[grupo_col] == grupo_b][coluna].dropna()
    stat, p = stats.mannwhitneyu(a, b, alternative="two-sided")
    return {
        "Teste": "Mann-Whitney U",
        "Grupo A": f"{grupo_a} (n={len(a)})",
        "Grupo B": f"{grupo_b} (n={len(b)})",
        "Mediana A": round(a.median(), 2),
        "Mediana B": round(b.median(), 2),
        "U-Statistic": round(stat, 2),
        "p-valor": round(p, 6),
        "Significativo (α=0.05)": "Sim ✓" if p < 0.05 else "Não ✗",
        "Conclusão": (
            f"Há diferença significativa entre {grupo_a} e {grupo_b}."
            if p < 0.05
            else f"Não há diferença significativa entre {grupo_a} e {grupo_b}."
        ),
    }


def teste_kruskal_wallis(
    df: pd.DataFrame, coluna: str, grupo_col: str
) -> dict:
    """
    Kruskal-Wallis H — compara 3+ grupos independentes.
    Alternativa não-paramétrica à ANOVA.
    """
    grupos = [
        g[coluna].dropna().values
        for _, g in df.groupby(grupo_col, observed=True)
        if len(g) > 0
    ]
    nomes = [
        str(n) for n, g in df.groupby(grupo_col, observed=True)
        if len(g) > 0
    ]
    stat, p = stats.kruskal(*grupos)
    return {
        "Teste": "Kruskal-Wallis H",
        "Grupos": ", ".join(nomes),
        "H-Statistic": round(stat, 4),
        "p-valor": round(p, 6),
        "Significativo (α=0.05)": "Sim ✓" if p < 0.05 else "Não ✗",
        "Conclusão": (
            "Pelo menos um grupo tem distribuição de IGR diferente dos demais."
            if p < 0.05
            else "Não há diferença significativa entre os grupos."
        ),
    }


def teste_dunn_posthoc(
    df: pd.DataFrame, coluna: str, grupo_col: str
) -> pd.DataFrame | None:
    """
    Teste post-hoc de Dunn com correção de Bonferroni.
    Usado após Kruskal-Wallis significativo.
    """
    if not HAS_POSTHOCS:
        return None
    result = posthoc_dunn(
        df, val_col=coluna, group_col=grupo_col, p_adjust="bonferroni"
    )
    return result.round(4)


def _forca_correlacao(r: float) -> str:
    r = abs(r)
    if r >= 0.7:
        return "Forte"
    if r >= 0.4:
        return "Moderada"
    if r >= 0.2:
        return "Fraca"
    return "Desprezível"
