from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parents[1] / "data/transformed_data"

@st.cache_data
def load_population():
    path = DATA_DIR / "projecao_ibge.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce").astype("Int64")
    return df

@st.cache_data
def load_finances():
    path = DATA_DIR / "financas_inss.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    df["ANO"] = pd.to_numeric(df["ANO"], errors="coerce").astype(int)
    df["MES_NUM"] = pd.to_numeric(df["MES_NUM"], errors="coerce").astype(int)
    return df

def brazil_rows(df):
    sigla = df["SIGLA"].astype(str).str.strip().str.upper()
    local = df["LOCAL"].astype(str).str.strip().str.casefold()
    return df[(sigla == "BR") | (local == "Brasil")].copy()

def format_brl(value):
    return "R$ " + f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
