import streamlit as st
import plotly.express as px
from utils.data import load_population, brazil_rows

st.set_page_config(page_title="Demografia | Brasil 2050", page_icon="👥", layout="wide")
st.title("Análise demográfica")
st.caption("Projeções populacionais do IBGE — 2000 a 2070.")

df = load_population()
if df is None:
    st.warning("Exporte `PROJECAO_2024` para `data/projecao_ibge.csv`. Veja o README.")
    st.stop()

years = sorted(df["ANO"].dropna().unique())
ufs = sorted(df.loc[~df["SIGLA"].astype(str).str.upper().isin(["BR"]), "LOCAL"].dropna().unique())
selected_local = st.selectbox("Localidade", ["Brasil"] + ufs)
if selected_local == "Brasil":
    data = brazil_rows(df)
else:
    data = df[df["LOCAL"] == selected_local].copy()

data = data.sort_values("ANO")
if data.empty:
    st.error("Não foram encontrados registros para essa localidade.")
    st.stop()

data["PERC_65_MAIS_CALC"] = data["65+_T"] / data["POP_T"] * 100
data["DEPENDENCIA_65_MAIS"] = data["65+_T"] / data["15-64_T"] * 100

c1, c2, c3 = st.columns(3)
last = data.iloc[-1]
c1.metric("População em 2070", f'{last["POP_T"]:,.0f}'.replace(",", "."))
c2.metric("População 65+ em 2070", f'{last["PERC_65_MAIS_CALC"]:.2f}%')
c3.metric("Dependência de IDOSOS em 2070", f'{last["DEPENDENCIA_65_MAIS"]:.2f}', help="Pessoas com 65+ para cada 100 pessoas de 15 a 64 anos.")

fig1 = px.line(data, x="ANO", y="PERC_65_MAIS_CALC", markers=True,
               title="% da população com 65 anos ou mais",
               labels={"ANO": "Ano", "PERC_65_MAIS_CALC": "População 65+ (%)"})
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(data, x="ANO", y="DEPENDENCIA_65_MAIS", markers=True,
               title="Razão de dependência de idosos",
               labels={"ANO": "Ano", "DEPENDENCIA_65_MAIS": "Idosos por 100 pessoas de 15 a 64 anos"})
st.plotly_chart(fig2, use_container_width=True)

st.markdown("#### Dados da localidade")
st.dataframe(data[["ANO", "POP_T", "65+_T", "15-64_T", "PERC_65_MAIS_CALC", "DEPENDENCIA_65_MAIS"]],
             use_container_width=True, hide_index=True)
