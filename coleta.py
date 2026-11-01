"""
Etapa 1 do projeto: coleta das cotações de moedas na API do Banco Central (SGS).

Gera o arquivo data/cotacoes.csv com uma coluna de data e uma coluna por moeda
(valor de venda em reais).

Como rodar:
    pip install requests pandas
    python coleta.py
"""

from datetime import date
from pathlib import Path
import time

import pandas as pd
import requests

# Códigos das séries no SGS do Banco Central (cotação de venda, em R$)
SERIES = {
    "USD": 1,       # Dólar americano
    "EUR": 21619,   # Euro
    "GBP": 21623,   # Libra esterlina
    "JPY": 21621,   # Iene japonês
}

DATA_INICIO = date(2015, 1, 1)
DATA_FIM = date.today()

# A API recusa janelas maiores que 10 anos em séries diárias.
# Buscar de 3 em 3 anos é mais rápido e evita timeout.
ANOS_POR_JANELA = 3

URL = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"


def gerar_janelas(inicio: date, fim: date, anos: int):
    """Divide o período em janelas de até `anos` anos."""
    atual = inicio
    while atual <= fim:
        proximo = date(atual.year + anos, atual.month, atual.day)
        # termina um dia antes do início da próxima janela para não duplicar
        fim_janela = min(date.fromordinal(proximo.toordinal() - 1), fim)
        yield atual, fim_janela
        atual = proximo


def buscar_serie(nome: str, codigo: int) -> pd.Series:
    """Busca uma série inteira, janela por janela, e devolve uma Series do pandas."""
    pedacos = []
    for ini, fim in gerar_janelas(DATA_INICIO, DATA_FIM, ANOS_POR_JANELA):
        params = {
            "formato": "json",
            "dataInicial": ini.strftime("%d/%m/%Y"),
            "dataFinal": fim.strftime("%d/%m/%Y"),
        }
        resposta = requests.get(URL.format(codigo=codigo), params=params, timeout=60)

        if resposta.status_code == 404:
            # sem dados nesse intervalo
            continue
        resposta.raise_for_status()

        dados = resposta.json()
        if dados:
            pedacos.append(pd.DataFrame(dados))
        print(f"  {nome}: {ini:%d/%m/%Y} a {fim:%d/%m/%Y} -> {len(dados)} registros")
        time.sleep(0.5)  # gentileza com o servidor

    if not pedacos:
        return pd.Series(name=nome, dtype=float)

    df = pd.concat(pedacos, ignore_index=True)
    df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df = df.drop_duplicates(subset="data").set_index("data").sort_index()
    return df["valor"].rename(nome)


def main():
    print(f"Coletando cotações de {DATA_INICIO:%d/%m/%Y} até {DATA_FIM:%d/%m/%Y}\n")

    series = []
    for nome, codigo in SERIES.items():
        print(f"Buscando {nome} (série {codigo})...")
        series.append(buscar_serie(nome, codigo))

    # Junta todas as moedas numa tabela só, alinhadas pela data
    tabela = pd.concat(series, axis=1).sort_index()
    tabela.index.name = "data"

    Path("data").mkdir(exist_ok=True)
    tabela.to_csv("data/cotacoes.csv")

    print("\nPronto! Arquivo salvo em data/cotacoes.csv")
    print(f"Total de dias: {len(tabela)}")
    print("\nÚltimas cotações:")
    print(tabela.tail())


if __name__ == "__main__":
    main()