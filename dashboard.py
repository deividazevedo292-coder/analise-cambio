"""
Dashboard interativo da Análise de Câmbio.

Como rodar:
    pip install -r requirements.txt
    streamlit run dashboard.py
"""

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Análise de Câmbio", page_icon="📈", layout="wide")

MOEDAS = {
    "USD": "Dólar americano",
    "EUR": "Euro",
    "GBP": "Libra esterlina",
    "JPY": "Iene japonês",
}
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

@st.cache_data
def carregar_dados() -> pd.DataFrame:
    df = pd.read_csv("data/cotacoes.csv", index_col="data", parse_dates=True)
    return df[[m for m in MOEDAS if m in df.columns]].sort_index()

def formatar_real(valor: float, casas: int = 2) -> str:
    texto = f"{valor:,.{casas}f}"
    return "R$ " + texto.replace(",", "X").replace(".", ",").replace("X", ".")

df = carregar_dados()
primeiro_dia = df.index.min().date()
ultimo_dia = df.index.max().date()

# ---------------- Barra lateral: filtros ----------------
st.sidebar.header("Filtros")

moedas = st.sidebar.multiselect(
    "Moedas",
    options=list(MOEDAS),
    default=list(MOEDAS),
    format_func=lambda m: f"{m} · {MOEDAS[m]}",
)

periodo = st.sidebar.date_input(
    "Período",
    value=(primeiro_dia, ultimo_dia),
    min_value=primeiro_dia,
    max_value=ultimo_dia,
    format="DD/MM/YYYY",
)

base_100 = st.sidebar.toggle(
    "Comparar em base 100",
    value=True,
    help="Coloca todas as moedas valendo 100 no início do período, para comparar a variação de cada uma.",
)

st.sidebar.caption(
    "Fonte: API do SGS, Banco Central do Brasil. "
    f"Dados de {primeiro_dia:%d/%m/%Y} a {ultimo_dia:%d/%m/%Y}."
)

if not moedas:
    st.warning("Escolha pelo menos uma moeda na barra lateral.")
    st.stop()

# o date_input devolve só uma data enquanto a pessoa ainda está escolhendo o intervalo
if isinstance(periodo, (tuple, list)) and len(periodo) == 2:
    inicio, fim = periodo
else:
    inicio, fim = primeiro_dia, ultimo_dia

dados = df.loc[pd.Timestamp(inicio):pd.Timestamp(fim), moedas]
if dados.dropna(how="all").empty:
    st.warning("Não há cotações nesse período. Escolha outro intervalo.")
    st.stop()

# ---------------- Cabeçalho e indicadores ----------------
st.title("📈 Análise de Câmbio")
st.markdown(
    "Como o Real se comportou frente a outras moedas, com dados oficiais do Banco Central. "
    "Use os filtros na barra lateral para explorar."
)

colunas = st.columns(len(moedas))
for coluna, moeda in zip(colunas, moedas):
    serie = dados[moeda].dropna()
    if serie.empty:
        coluna.metric(MOEDAS[moeda], "sem dados")
        continue
    casas = 4 if moeda == "JPY" else 2
    variacao = (serie.iloc[-1] / serie.iloc[0] - 1) * 100
    coluna.metric(
        label=MOEDAS[moeda],
        value=formatar_real(serie.iloc[-1], casas),
        delta=f"{variacao:+.1f}% no período".replace(".", ","),
        delta_color="inverse",
        help=f"Cotação em {serie.index[-1]:%d/%m/%Y}. Vermelho significa que a moeda ficou mais cara em reais.",
    )

# ---------------- Abas ----------------
aba_evolucao, aba_volatilidade, aba_pandemia, aba_sazonal, aba_conversor = st.tabs(
    ["Evolução", "Volatilidade", "Pandemia", "Sazonalidade", "Conversor"]
)

with aba_evolucao:
    if base_100:
        grafico = dados.apply(lambda s: s / s.dropna().iloc[0] * 100 if s.notna().any() else s)
        st.subheader("Evolução das moedas (início do período = 100)")
        st.caption("Acima de 100: a moeda ficou mais cara em reais. Abaixo de 100: ficou mais barata.")
    else:
        grafico = dados
        st.subheader("Cotação de venda em reais (R$)")
        if "JPY" in moedas and len(moedas) > 1:
            st.caption("Dica: o iene vale centavos, então ele fica achatado neste modo. Ative a base 100 para comparar.")
    st.line_chart(grafico, y_label="Índice" if base_100 else "R$")

with aba_volatilidade:
    st.subheader("Volatilidade anual (%)")
    st.caption(
        "Desvio padrão das variações diárias, anualizado. Quanto maior, mais a moeda oscilou naquele ano."
    )
    retornos = dados.pct_change(fill_method=None)
    vol = retornos.groupby(retornos.index.year).std() * (252 ** 0.5) * 100
    vol.index = vol.index.astype(str)
    st.bar_chart(vol, stack=False, y_label="%")

    ranking = (retornos.std() * (252 ** 0.5) * 100).sort_values(ascending=False)
    st.markdown(
        "**No período escolhido:** "
        + " · ".join(f"{m} {v:.1f}%".replace(".", ",") for m, v in ranking.items())
    )

with aba_pandemia:
    st.subheader("O dólar durante a pandemia de 2020")
    usd = df["USD"].dropna()
    janela = usd["2019-10-01":"2021-06-30"]
    antes = usd[:"2020-02-28"].iloc[-1]
    pico_data = usd["2020"].idxmax()
    pico = usd["2020"].max()

    c1, c2, c3 = st.columns(3)
    c1.metric("Fim de fev/2020", formatar_real(antes))
    c2.metric(f"Pico em {pico_data:%d/%m/%Y}", formatar_real(pico))
    c3.metric("Alta até o pico", f"{(pico / antes - 1) * 100:.1f}%".replace(".", ","))
    st.line_chart(janela, y_label="R$")
    st.caption("Este gráfico usa sempre o período da pandemia, independente dos filtros.")

with aba_sazonal:
    st.subheader("Existe um mês melhor para comprar dólar?")
    mensal = df["USD"].dropna().resample("ME").last().pct_change().dropna() * 100
    media = mensal.groupby(mensal.index.month).mean()
    media.index = [f"{i:02d} · {MESES[i - 1]}" for i in media.index]
    st.bar_chart(media.rename("Variação média (%)"), y_label="%")
    anos = mensal.index.year.nunique()
    st.info(
        f"São só {anos} anos de dados, ou seja, cerca de {anos} observações por mês. "
        "Uma média puxada por poucos anos atípicos pode parecer um padrão sem ser."
    )

with aba_conversor:
    st.subheader("Conversor com a última cotação")
    st.caption("Complemento do projeto Banco Multimoedas: converte reais usando a cotação mais recente da base.")
    c1, c2 = st.columns(2)
    valor = c1.number_input("Valor em reais (R$)", min_value=0.0, value=1000.0, step=100.0)
    moeda = c2.selectbox("Converter para", list(MOEDAS), format_func=lambda m: f"{m} · {MOEDAS[m]}")
    cotacao = df[moeda].dropna()
    convertido = valor / cotacao.iloc[-1]
    st.metric(
        f"Você recebe ({moeda})",
        f"{convertido:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        help=f"Cotação de {cotacao.index[-1]:%d/%m/%Y}: {formatar_real(cotacao.iloc[-1], 4)}",
    )

st.divider()
st.caption(
    "Projeto de Deivid Azevedo Dantas · "
    "[Código no GitHub](https://github.com/deividazevedo292-coder/analise-cambio) · "
    "[LinkedIn](https://www.linkedin.com/in/deivid-azevedo-4b5709344/)"
)
