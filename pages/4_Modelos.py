import streamlit as st

st.set_page_config(page_title="Modelos | Brasil 2050", page_icon="🧠", layout="wide")
st.title("Avaliação dos modelos de projeção")
st.info("Esta página será preenchida após a Sprint de modelagem. Não há métricas ou previsões carregadas ainda.")

st.markdown("""
### Resultados que serão apresentados
- Valores observados x valores previstos.
- Comparação entre modelos e baseline.
- MAE, RMSE e MAPE (quando a métrica for adequada à série).
- Resíduos e diagnóstico dos erros.
- Horizonte de previsão e intervalos de confiança, quando disponíveis.

**Importante:** os modelos financeiros do INSS devem ser avaliados com validação temporal, sem embaralhar os meses aleatoriamente.
""")
