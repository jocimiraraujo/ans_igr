"""
analysis/modelagem.py — Modelagem estatística robusta do IGR
Regressão quantílica, regressão log-linear e ranking percentílico.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def regressao_log_linear(
    df: pd.DataFrame,
    y_col: str = "IGR",
    categoricas: list[str] | None = None,
) -> dict:
    """
    Regressão linear após transformação log(IGR+1).
    Usa statsmodels OLS com variáveis dummies para colunas categóricas.
    Retorna coeficientes, R², p-valores e diagnósticos.
    """
    try:
        import statsmodels.api as sm
    except ImportError:
        return {"erro": "statsmodels não instalado. Execute: pip install statsmodels"}

    if categoricas is None:
        categoricas = ["PORTE_OPERADORA", "COBERTURA"]

    df_modelo = df[[y_col] + categoricas].dropna().copy()
    df_modelo["LOG_IGR"] = np.log1p(df_modelo[y_col])

    # Cria dummies
    X = pd.get_dummies(df_modelo[categoricas], drop_first=True, dtype=float)
    X = sm.add_constant(X)
    y = df_modelo["LOG_IGR"]

    modelo = sm.OLS(y, X).fit()

    coef = pd.DataFrame({
        "Coeficiente":   modelo.params.round(4),
        "Std Error":     modelo.bse.round(4),
        "t-stat":        modelo.tvalues.round(4),
        "p-valor":       modelo.pvalues.round(6),
        "Significativo": ["✓" if p < 0.05 else "✗" for p in modelo.pvalues],
    })

    return {
        "coeficientes": coef,
        "R²":           round(modelo.rsquared, 4),
        "R² Ajustado":  round(modelo.rsquared_adj, 4),
        "F-statistic":  round(modelo.fvalue, 2),
        "p-valor (F)":  round(modelo.f_pvalue, 6),
        "AIC":          round(modelo.aic, 2),
        "n_obs":        int(modelo.nobs),
        "resumo_texto": modelo.summary().as_text(),
    }


def regressao_quantilica(
    df: pd.DataFrame,
    y_col: str = "IGR",
    quantil: float = 0.50,
    categoricas: list[str] | None = None,
) -> dict:
    """
    Regressão quantílica (mediana por padrão).
    Robusta a outliers — modela o IGR típico, não o médio.
    """
    try:
        import statsmodels.formula.api as smf
    except ImportError:
        return {"erro": "statsmodels não instalado."}

    if categoricas is None:
        categoricas = ["PORTE_OPERADORA", "COBERTURA"]

    df_m = df[[y_col] + categoricas].dropna().copy()
    df_m["LOG_IGR"] = np.log1p(df_m[y_col])

    # Monta fórmula
    preditores = " + ".join([f"C({c})" for c in categoricas])
    formula = f"LOG_IGR ~ {preditores}"

    modelo = smf.quantreg(formula, data=df_m).fit(q=quantil, max_iter=2000)

    coef = pd.DataFrame({
        "Coeficiente": modelo.params.round(4),
        "Std Error":   modelo.bse.round(4),
        "t-stat":      modelo.tvalues.round(4),
        "p-valor":     modelo.pvalues.round(6),
        "Significativo": ["✓" if p < 0.05 else "✗" for p in modelo.pvalues],
    })

    return {
        "quantil":      quantil,
        "coeficientes": coef,
        "pseudo_R²":    round(modelo.prsquared, 4),
        "n_obs":        int(modelo.nobs),
        "resumo_texto": modelo.summary().as_text(),
    }


def ranking_percentilico(
    df: pd.DataFrame,
    grupo_col: str = "REGISTRO_ANS",
    y_col: str = "IGR",
) -> pd.DataFrame:
    """
    Calcula o percentil de cada operadora dentro do seu grupo de cobertura.
    Percentil alto = pior desempenho (IGR maior).
    """
    df_r = df.copy()
    df_r["PERCENTIL"] = df_r.groupby("COBERTURA", observed=True)[y_col].rank(pct=True).round(4) * 100
    df_r["CLASSIFICACAO"] = pd.cut(
        df_r["PERCENTIL"],
        bins=[0, 25, 50, 75, 90, 100],
        labels=["Ótimo (p0-25)", "Bom (p25-50)", "Regular (p50-75)",
                "Ruim (p75-90)", "Crítico (p90-100)"],
        include_lowest=True,
    )
    return df_r


def zscore_robusto(serie: pd.Series) -> pd.Series:
    """Z-score robusto: z = (x - mediana) / MAD. Resistente a outliers."""
    mediana = serie.median()
    mad = (serie - mediana).abs().median()
    return (serie - mediana) / (mad if mad > 0 else 1)


def analise_tukey(serie: pd.Series) -> dict:
    """Calcula fences de Tukey e classifica cada observação."""
    q1, q3 = serie.quantile(0.25), serie.quantile(0.75)
    iqr = q3 - q1
    return {
        "Q1": round(q1, 4),
        "Q3": round(q3, 4),
        "IQR": round(iqr, 4),
        "Fence Leve Inferior":  round(q1 - 1.5 * iqr, 4),
        "Fence Leve Superior":  round(q3 + 1.5 * iqr, 4),
        "Fence Severo Inferior": round(q1 - 3.0 * iqr, 4),
        "Fence Severo Superior": round(q3 + 3.0 * iqr, 4),
        "N Outliers Leves":   int(((serie < q1 - 1.5*iqr) | (serie > q3 + 1.5*iqr)).sum()),
        "N Outliers Severos": int(((serie < q1 - 3.0*iqr) | (serie > q3 + 3.0*iqr)).sum()),
    }
