# 🏥 IGR Análise — ANS

**Disciplina:** Algoritmo II  
**Autor:** Jocimir Araujo  
**Fonte de dados:** Agência Nacional de Saúde Suplementar (ANS)

---

## O que é o projeto

Painel interativo em **Streamlit** para análise estatística do
**Índice Geral de Reclamações (IGR)** da ANS, utilizando métodos adequados à natureza assimétrica dos dados.

---

## Estrutura do projeto

```
analise_ans/
│
├── app.py                          # Ponto de entrada — roteador de páginas
│
├── pages/                          # Uma página por módulo de análise
│   ├── home.py                     # Dashboard inicial com KPIs
│   ├── about_igr.py                # Explicação educativa do IGR
│   ├── descritiva.py               # Estatística descritiva completa
│   ├── por_porte.py                # Análise por porte de operadora
│   ├── por_cobertura.py            # Análise por tipo de cobertura
│   ├── temporal.py                 # Evolução temporal (série temporal)
│   ├── correlacoes.py              # Correlações Spearman e Kendall
│   ├── modelagem.py                # Regressão log-linear e quantílica
│   └── busca.py                    # Perfil individual de operadoras
│
├── components/                     # Componentes reutilizáveis
│   ├── ui.py                       # Cards, headers, badges, footer
│   └── charts.py                   # Gráficos Plotly padronizados
│
├── analysis/                       # Módulos de análise estatística pura
│   ├── estatistica_descritiva.py   # Mediana, IQR, MAD, assimetria, Shapiro
│   ├── correlacoes.py              # Spearman, Kendall, Mann-Whitney, Kruskal
│   └── modelagem.py                # Regressão, ranking, Tukey, z-robusto
│
├── utils/
│   ├── config.py                   # Tema, cores, metas ANS
│   ├── data_loader.py              # Carregamento, cache, filtros
│   └── session.py                  # Estado da sessão Streamlit
│
├── requirements.txt
└── README.md
```

---

## Como executar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Colocar o arquivo CSV na pasta do projeto
# dados_IGR_limpos.csv → mesma pasta que app.py

# 3. Rodar o Streamlit
cd analise_ans
streamlit run app.py
```

---

## Metodologia estatística

| Pergunta analítica | Método |
|---|---|
| IGR típico do setor | Mediana + IQR |
| Distribuição normal? | Shapiro-Wilk / KS-test |
| Grandes diferem de pequenas? | Kruskal-Wallis + Dunn |
| Médico vs. odonto | Mann-Whitney U |
| Quem são os outliers? | Tukey fences + Z-score robusto |
| IGR correlaciona com beneficiários? | Spearman ρ |
| Modelar IGR com preditores | Regressão log-linear (OLS) |
| Modelar sem remover outliers | Regressão Quantílica (q=0.5) |
| Ranking de desempenho | Percentil por cobertura |

---

## Colunas do dataset

| Coluna | Tipo | Descrição |
|---|---|---|
| REGISTRO_ANS | int64 | Identificador único da operadora |
| RAZAO_SOCIAL | str | Nome da operadora |
| COBERTURA | str | Assistência Médica ou Exclusivamente Odontológico |
| IGR | float64 | Índice Geral de Reclamações (por 100 mil beneficiários) |
| QTD_RECLAMACOES | int64 | Total de reclamações no período |
| QTD_BENEFICIARIOS | int64 | Total de beneficiários analisados |
| PORTE_OPERADORA | str | PEQUENO, MÉDIO ou GRANDE |
| COMPETENCIA | period[M] | Mês de referência do IGR |
| COMPETENCIA_BENEFICIARIO | period[M] | Mês de referência dos beneficiários |
| DT_ATUALIZACAO | datetime | Data de atualização do registro |

---

## Interpretação do IGR

> **Quanto menor o IGR, maior a satisfação dos beneficiários.**  
> **Quanto maior o IGR, pior tende a ser a avaliação da operadora.**

| Cobertura | Meta (bom) | Alerta | Crítico |
|---|---|---|---|
| Assistência Médica | ≤ 30 | ≤ 60 | > 60 |
| Exclusivamente Odontológico | ≤ 5 | ≤ 15 | > 15 |
