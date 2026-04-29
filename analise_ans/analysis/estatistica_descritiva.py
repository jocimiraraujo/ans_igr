"""
analysis/estatistica_descritiva.py — Estatística descritiva robusta do IGR
Implementa as estratégias discutidas: mediana, IQR, MAD, assimetria,
percentis e z-score robusto (resistentes a outliers).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def resumo_robusto(serie: pd.Series, nome: str = "IGR") -> pd.DataFrame:
    """
    Calcula estatísticas descritivas robustas para uma série numérica.
    Prioriza medidas resistentes a outliers conforme análise do IGR.
    """
    s = serie.dropna()
    q1, q2, q3 = np.percentile(s, [25, 50, 75])
    iqr = q3 - q1
    mad = np.median(np.abs(s - q2))
    fence_lo = q1 - 1.5 * iqr
    fence_hi = q3 + 1.5 * iqr
    n_outliers = ((s < fence_lo) | (s > fence_hi)).sum()
    skew = stats.skew(s)
    kurt = stats.kurtosis(s)

    return pd.DataFrame({
        "Estatística": [
            "N", "Média", "Média Aparada (10%)",
            "Mediana (Q2)", "Q1 (25%)", "Q3 (75%)", "IQR",
            "MAD", "Desvio-Padrão",
            "Mínimo", "p5", "p95", "Máximo",
            "Fence Inferior (Tukey)", "Fence Superior (Tukey)",
            "Outliers (Tukey leve)", "Assimetria (Skewness)", "Curtose",
        ],
        nome: [
            len(s),
            round(s.mean(), 4),
            round(stats.trim_mean(s, 0.10), 4),
            round(q2, 4),
            round(q1, 4),
            round(q3, 4),
            round(iqr, 4),
            round(mad, 4),
            round(s.std(), 4),
            round(s.min(), 4),
            round(np.percentile(s, 5), 4),
            round(np.percentile(s, 95), 4),
            round(s.max(), 4),
            round(fence_lo, 4),
            round(fence_hi, 4),
            int(n_outliers),
            round(skew, 4),
            round(kurt, 4),
        ],
    })


def resumo_por_grupo(
    df: pd.DataFrame,
    grupo: str,
    coluna: str = "IGR",
) -> pd.DataFrame:
    """
    Estatísticas robustas por grupo (ex: por PORTE_OPERADORA ou COBERTURA).
    Retorna DataFrame pivotado pronto para exibição.
    """
    resultados = []
    for nome_grupo, sub in df.groupby(grupo, observed=True):
        s = sub[coluna].dropna()
        if len(s) == 0:
            continue
        q1, q2, q3 = np.percentile(s, [25, 50, 75])
        iqr = q3 - q1
        mad = np.median(np.abs(s - q2))
        fence_hi = q3 + 1.5 * iqr
        n_out = (s > fence_hi).sum()
        resultados.append({
            "Grupo":             str(nome_grupo),
            "N":                 len(s),
            "Mediana":           round(q2, 2),
            "Média":             round(s.mean(), 2),
            "Média Aparada":     round(stats.trim_mean(s, 0.10), 2),
            "Q1":                round(q1, 2),
            "Q3":                round(q3, 2),
            "IQR":               round(iqr, 2),
            "MAD":               round(mad, 2),
            "Desvio-Padrão":     round(s.std(), 2),
            "p5":                round(np.percentile(s, 5), 2),
            "p95":               round(np.percentile(s, 95), 2),
            "Máximo":            round(s.max(), 2),
            "Outliers (Tukey)":  int(n_out),
        })
    return pd.DataFrame(resultados)


def detectar_outliers(
    df: pd.DataFrame,
    coluna: str = "IGR",
    metodo: str = "tukey",   # "tukey" ou "zscore_robusto"
    limiar: float = 3.5,
) -> pd.DataFrame:
    """
    Retorna subconjunto do DataFrame com outliers identificados.
    - Tukey: valor > Q3 + 1.5*IQR  (leve) ou > Q3 + 3.0*IQR (severo)
    - Z-score robusto: |z| > limiar  (recomendado para distribuições assimétricas)
    """
    s = df[coluna]
    if metodo == "tukey":
        q1, q3 = s.quantile(0.25), s.quantile(0.75)
        iqr = q3 - q1
        mask = (s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)
        df = df.copy()
        df["TIPO_OUTLIER"] = np.where(
            s > q3 + 3.0 * iqr, "Severo",
            np.where(mask, "Leve", "Normal")
        )
        return df[mask].copy()
    else:
        mediana = s.median()
        mad = (s - mediana).abs().median()
        z = (s - mediana) / (mad if mad > 0 else 1)
        mask = z.abs() > limiar
        df = df.copy()
        df["Z_ROBUSTO"] = z.round(2)
        return df[mask].copy()


def teste_normalidade(serie: pd.Series, nome: str = "IGR") -> dict:
    """Shapiro-Wilk (n<=5000) ou KS-test para amostras grandes."""
    s = serie.dropna()
    if len(s) <= 5000:
        stat, p = stats.shapiro(s.sample(min(5000, len(s)), random_state=42))
        teste = "Shapiro-Wilk"
    else:
        stat, p = stats.kstest(s, "norm", args=(s.mean(), s.std()))
        teste = "Kolmogorov-Smirnov"
    return {
        "Variável": nome,
        "Teste": teste,
        "Estatística": round(stat, 4),
        "p-valor": round(p, 6),
        "Distribuição Normal?": "Não ✗" if p < 0.05 else "Sim ✓",
    }
