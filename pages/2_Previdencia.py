import streamlit as st
import plotly.express as px
from utils.data import load_finances

st.set_page_config(page_title="Previdência | Brasil 2050", page_icon="🏛️", layout="wide")
st.title("Análise previdenciária")
st.caption("Séries mensais do INSS — 2020 a 2025.")

df = load_finances()
if df is None or df.empty:
    st.warning("Exporte os DataFrames FINANCAS_INSS_2020 a FINANCAS_INSS_2025 para `data/financas_inss.csv`. Veja o README.")
    st.stop()

df = df.copy()
df["DATA"] = df["ANO"].astype(str) + "-" + df["MES_NUM"].astype(str).str.zfill(2)
df = df.sort_values(["ANO", "MES_NUM"])

years = sorted(df["ANO"].unique())
selected_years = st.multiselect("Anos", years, default=years)
view = df[df["ANO"].isin(selected_years)]

fig1 = px.line(view, x="DATA", y=["Arrecadacao_Liquida", "Total_Beneficios"],
               markers=True, title="Arrecadação líquida x total de benefícios",
               labels={"DATA": "Mês", "value": "Valor", "variable": "Série"})
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.bar(view, x="DATA", y="Resultado_Primario",
              title="Resultado primário mensal",
              labels={"DATA": "Mês", "Resultado_Primario": "Resultado"})
fig2.add_hline(y=0, line_width=1)
st.plotly_chart(fig2, use_container_width=True)

st.dataframe(view, use_container_width=True, hide_index=True)
st.caption("A linha 'Total' foi excluída na preparação para evitar duplicação dos valores mensais.")
