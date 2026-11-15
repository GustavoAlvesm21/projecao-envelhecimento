import streamlit as st
import plotly.express as px
from utils.data import load_population

st.set_page_config(page_title="Comparação por UF | Brasil 2050", page_icon="🗺️", layout="wide")
st.title("Comparação entre Unidades da Federação")
st.caption("Comparação dos indicadores demográficos entre estados.")

df = load_population()
if df is None:
    st.warning("Exporte a base do IBGE para `data/projecao_ibge.csv`. Veja o README.")
    st.stop()

years = sorted(df["ANO"].dropna().unique())
year = st.select_slider("Ano", options=years, value=2025 if 2025 in years else years[0])
states = df[(df["ANO"] == year) & (~df["SIGLA"].astype(str).str.upper().isin(["BR"]))]
states = states.copy()
states["PERC_65_MAIS"] = states["65+_T"] / states["POP_T"] * 100
states["DEPENDENCIA"] = states["65+_T"] / states["15-64_T"] * 100

metric = st.radio("Indicador", ["População 65+ (%)", "Razão de dependência"], horizontal=True)
if metric == "População 65+ (%)":
    y, title = "PERC_65_MAIS", "Percentual da população com 65 anos ou mais"
else:
    y, title = "DEPENDENCIA", "Idosos por 100 pessoas em idade ativa"

states = states.sort_values(y, ascending=False)
fig = px.bar(states, x="SIGLA", y=y, hover_name="LOCAL",
             title=f"{title} — {year}",
             labels={"SIGLA": "UF", y: metric})
st.plotly_chart(fig, use_container_width=True)
st.dataframe(states[["SIGLA", "LOCAL", "POP_T", "PERC_65_MAIS", "DEPENDENCIA"]],
             use_container_width=True, hide_index=True)
