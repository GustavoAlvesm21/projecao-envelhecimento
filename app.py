import streamlit as st
import plotly.express as px
from utils.data import load_population, load_finances, brazil_rows, format_brl

st.set_page_config(
    page_title="Brasil 2070 | Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("Brasil 2070")
st.subheader("Envelhecimento populacional e perspectivas previdenciárias")
st.caption("Painel exploratório com projeções demográficas do IBGE e dados financeiros do INSS.")

population = load_population()
finances = load_finances()

if population is None:
    st.info("Para começar, exporte a base do IBGE para `data/projecao_ibge.csv`. Veja as instruções no README.")
    st.stop()

br = brazil_rows(population)
if br.empty:
    st.error("Não encontrei a linha nacional. Confira se a coluna SIGLA contém 'BR' ou LOCAL contém 'Brasil'.")
    st.stop()

years = sorted(br["ANO"].dropna().unique())
default_year = 2025 if 2025 in years else years[0]
selected_year = st.select_slider("Ano de referência", options=years, value=default_year)
row = br.loc[br["ANO"] == selected_year].iloc[0]

elderly_pct = row["P_65+_T"] if "P_65+_T" in br.columns else row["65+_T"] / row["POP_T"] * 100
dependency = (row["65+_T"] + row["0-14_T"]) / row["15-64_T"] * 100
aging_index = row["65+_T"] / row["0-14_T"] * 100

c1, c2, c3, c4 = st.columns(4)
c1.metric("População total", f'{row["POP_T"]:,.0f}'.replace(",", "."))
if elderly_pct <= 1:
    elderly_pct *= 100
c2.metric("População 65+", f"{elderly_pct:.2f}%")
c3.metric("Razão de dependência TOTAL", f"{dependency:.2f}", help="Pessoas não ativas para cada 100 pessoas em idade ativa.")
if aging_index <= 1:
    aging_index *= 100
c4.metric("Índice de envelhecimento", f"{aging_index:.2f}", help="Pessoas com 65+ para cada 100 pessoas de 0 a 14 anos.")

st.divider()
left, right = st.columns(2)

with left:
    st.markdown("#### Envelhecimento populacional")
    chart = br[["ANO", "P_65+_T"]].dropna().sort_values("ANO")
    if chart["P_65+_T"].max() <= 1:
        chart["P_65+_T"] *= 100
    fig = px.line(chart, x="ANO", y="P_65+_T", markers=True,
                  labels={"ANO": "Ano", "P_65+_T": "População com 65+ (%)"})
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.markdown("#### Razão de dependência de idosos")
    chart = br[["ANO", "65+_T", "0-14_T", "15-64_T"]].dropna().copy().sort_values("ANO")
    chart["Razao"] = (chart["65+_T"] + chart["0-14_T"]) / chart["15-64_T"] * 100
    fig = px.line(chart, x="ANO", y="Razao", markers=True,
                  labels={"ANO": "Ano", "Razao": "Idosos por 100 pessoas em idade ativa"})
    fig.update_layout(margin=dict(l=10, r=10, t=20, b=10))
    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.markdown("#### Razão de dependência: jovens, idosos e total")

dep = br[["ANO", "0-14_T", "15-64_T", "65+_T"]].dropna().sort_values("ANO").copy()
dep["Jovens (0–14)"] = dep["0-14_T"] / dep["15-64_T"] * 100
dep["Idosos (65+)"] = dep["65+_T"] / dep["15-64_T"] * 100
dep["Total"] = dep["Jovens (0–14)"] + dep["Idosos (65+)"]

ano_min = int(dep.loc[dep["Total"].idxmin(), "ANO"])
ano_fim = int(dep["ANO"].max())
base = dep.set_index("ANO")
var = base.loc[ano_fim, ["Jovens (0–14)", "Idosos (65+)", "Total"]] - base.loc[ano_min, ["Jovens (0–14)", "Idosos (65+)", "Total"]]

d1, d2, d3 = st.columns(3)
d1.metric("Ano do mínimo (razão total)", ano_min, f'{base.loc[ano_min, "Total"]:.1f} por 100')
d2.metric(f"Jovens: variação {ano_min}–{ano_fim}", f'{var["Jovens (0–14)"]:+.1f} p.p.')
d3.metric(f"Idosos: variação {ano_min}–{ano_fim}", f'{var["Idosos (65+)"]:+.1f} p.p.')

fig_dep = px.line(
    dep, x="ANO", y=["Jovens (0–14)", "Idosos (65+)", "Total"], markers=True,
    labels={"ANO": "Ano", "value": "Pessoas por 100 em idade ativa (15–64)", "variable": ""},
)
fig_dep.update_layout(margin=dict(l=10, r=10, t=20, b=10))
st.plotly_chart(fig_dep, use_container_width=True)
st.caption("Razão de dependência = população do grupo etário ÷ população de 15 a 64 anos × 100.")

st.divider()
st.markdown("#### Situação financeira do INSS")
if finances is None or finances.empty:
    st.info("Os dados financeiros ainda não foram exportados. Consulte o README para gerar `data/financas_inss.csv`.")
else:
    annual = finances.groupby("ANO", as_index=False)[
        ["Arrecadacao_Liquida", "Total_Beneficios", "Resultado_Primario"]
    ].sum()
    annual = annual.sort_values("ANO")
    latest = annual.iloc[-1]
    f1, f2, f3 = st.columns(3)
    f1.metric("Arrecadação líquida (ano)", format_brl(latest["Arrecadacao_Liquida"]))
    f2.metric("Total de benefícios (ano)", format_brl(latest["Total_Beneficios"]))
    f3.metric("Resultado primário (ano)", format_brl(latest["Resultado_Primario"]))
    st.caption("Valores apresentados na mesma unidade da base original. Confirme se os dados estão em reais ou milhares de reais.")
    fig = px.line(annual, x="ANO",
                  y=["Arrecadacao_Liquida", "Total_Beneficios"],
                  markers=True,
                  labels={"ANO": "Ano", "value": "Valor", "variable": "Série"},
                  title="Arrecadação líquida x total de benefícios")
    st.plotly_chart(fig, use_container_width=True)

st.caption("Projeto acadêmico. Projeções demográficas oficiais não equivalem, isoladamente, a uma previsão do déficit previdenciário.")
