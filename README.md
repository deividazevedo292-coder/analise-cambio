# 📈 Análise de Câmbio: o Real frente a outras moedas (2015–2026)

Projeto de análise de dados que coleta, trata e analisa o histórico de cotações do Real brasileiro em relação a quatro moedas, usando dados oficiais do **Banco Central do Brasil**.

> Projeto complementar ao [Banco Multimoedas](https://github.com/deividazevedo292-coder/banco-multimoedas), meu sistema de conversão de moedas em Python. Lá eu converto valores; aqui eu analiso como essas moedas se comportaram ao longo dos anos.

---

## 🎯 Objetivo

Entender o comportamento do câmbio no Brasil nos últimos dez anos e responder perguntas como:

- Qual moeda mais se valorizou frente ao Real desde 2015?
- Qual moeda foi a mais volátil?
- Como o Real reagiu a momentos de crise, como a pandemia de 2020?
- Existe algum padrão sazonal, como meses em que o dólar costuma estar mais barato?

## 🗂️ Dados

| Moeda | Código | Série no SGS (Banco Central) |
|---|---|---|
| Dólar americano | USD | 1 |
| Euro | EUR | 21619 |
| Libra esterlina | GBP | 21623 |
| Iene japonês | JPY | 21621 |

- **Fonte:** API pública do SGS (Sistema Gerenciador de Séries Temporais) do Banco Central
- **Período:** janeiro de 2015 até a data da coleta
- **Frequência:** diária (dias úteis)
- **Valor:** cotação de venda, em reais
- **Observação:** o peso argentino chegou a ser incluído, mas a validação dos dados mostrou que a série usada (21637) não era a cotação diária da moeda, e sim um indicador mensal. Por isso ele foi retirado da análise.

A API limita consultas de séries diárias a janelas de no máximo 10 anos, então o script de coleta busca os dados em blocos de 3 anos e junta tudo ao final.

## 🛠️ Tecnologias

- Python
- pandas
- requests
- matplotlib
- Jupyter Notebook

## ▶️ Como executar

```bash
# instalar as dependências
pip install -r requirements.txt

# coletar os dados
python coleta.py
```

O resultado é salvo em `data/cotacoes.csv`. Depois, abra o `analise.ipynb` no Jupyter ou no VS Code e execute todas as células.

## 📁 Estrutura do projeto

```
analise-cambio/
├── coleta.py          # coleta das cotações na API do Banco Central
├── data/
│   └── cotacoes.csv   # dados coletados
├── analise.ipynb      # análise exploratória e conclusões
├── requirements.txt   # dependências do projeto
└── README.md
```

## 🚧 Status

- [x] Coleta automatizada dos dados via API
- [x] Limpeza e tratamento
- [x] Análise exploratória
- [x] Visualizações
- [x] Conclusões
- [ ] Dashboard interativo *(próxima etapa)*

## 💡 Principais conclusões

Entre 2015 e 2026, o Real perdeu valor frente a todas as moedas analisadas, com o dólar dobrando de preço. A instabilidade do câmbio se concentrou em momentos de crise, como 2015 e a pandemia de 2020, quando o dólar subiu 32% em menos de três meses. Já a ideia de que existe um “mês certo” para comprar dólar não se sustenta: a aparente sazonalidade é explicada por poucos anos atípicos. Durante o projeto, a validação dos dados também mostrou que uma das séries inicialmente usadas não correspondia ao peso argentino, e ela foi retirada da análise.

## 👤 Autor

**Deivid Azevedo Dantas**
Estudante de Análise e Desenvolvimento de Sistemas no Centro Universitário FMU

[LinkedIn](https://www.linkedin.com/in/deivid-azevedo-4b5709344/)