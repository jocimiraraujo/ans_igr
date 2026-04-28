"""
utils/config.py — Configurações globais do projeto
"""

PAGE_CONFIG = dict(
    page_title="IGR - Análise · ANS",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

THEME = {
    # Cores principais
    "primary":       "#1E3A5F",
    "primary_dark":  "#122540",
    "primary_light": "#3A6EA5",
    "accent":        "#2ECC71",

    # Texto
    "text_primary":  "#1A202C",
    "text_muted":    "#718096",

    # Fundos
    "sidebar_bg":    "#F7F9FC",
    "sidebar_text":  "#1E3A5F",
    "card_bg":       "#FFFFFF",
    "page_bg":       "#F0F4F8",
    "border":        "#E2E8F0",

    # Status
    "success":       "#059669",
    "success_bg":    "#ECFDF5",
    "warning":       "#D97706",
    "warn_bg":       "#FFFBEB",
    "danger":        "#DC2626",
    "danger_bg":     "#FEF2F2",
    "info_bg":       "#EFF6FF",

    # Paleta de portes
    "grande":        "#1D6954",
    "medio":         "#4C1D95",
    "pequeno":       "#78350F",

    # Paleta de cobertura
    "medica":        "#1E3A5F",
    "odonto":        "#0E7490",
}

# Paleta Plotly alinhada ao tema
PLOTLY_COLORS = {
    "GRANDE":  "#059669",
    "MÉDIO":   "#7C3AED",
    "PEQUENO": "#D97706",
    "ASSISTÊNCIA MÉDICA":          "#1E3A5F",
    "EXCLUSIVAMENTE ODONTOLÓGICA": "#0E7490",
}

PLOTLY_TEMPLATE = "plotly_white"

# Limites ANS de referência (por 100 mil beneficiários)
ANS_METAS = {
    "ASSISTÊNCIA MÉDICA":          {"meta": 30.0, "alerta": 60.0},
    "EXCLUSIVAMENTE ODONTOLÓGICA": {"meta": 5.0,  "alerta": 15.0},
}
