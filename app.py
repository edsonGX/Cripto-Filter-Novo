import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Crypto Filter Pro",
    layout="wide"
)

st.title("Crypto Filter Pro")
st.write("Filtro de criptomoedas com exclusão automática de memecoins.")

st.warning(
    "Este app é apenas uma ferramenta de filtragem e estudo. "
    "Ele não é recomendação de investimento."
)

market_cap_min = st.number_input(
    "Market cap mínimo em dólar",
    min_value=0,
    value=100_000_000,
    step=10_000_000
)

volume_min = st.number_input(
    "Volume mínimo de 24h em dólar",
    min_value=0,
    value=10_000_000,
    step=1_000_000
)

score_min = st.slider(
    "Score mínimo",
    min_value=0,
    max_value=100,
    value=0
)

meme_terms = [
    "doge", "shib", "pepe", "inu", "floki", "bonk",
    "meme", "cat", "dog", "baby", "elon", "trump",
    "maga", "wojak", "moon", "safe", "frog", "pump"
]


@st.cache_data(ttl=900)
def buscar_criptos():
    url = "https://api.coinpaprika.com/v1/tickers"

    headers = {
        "Accept": "application/json",
        "User-Agent": "CryptoFilterPro/1.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code != 200:
            return None, f"Erro da API. Código: {response.status_code}", response.text

        return response.json(), None, None

    except requests.exceptions.RequestException as erro:
        return None, "Erro de conexão com a API.", str(erro)


def parece_memecoin(nome, simbolo):
    nome = str(nome).lower()
    simbolo = str(simbolo).lower()

    for termo in meme_terms:
        if termo in nome or termo in simbolo:
            return True

    return False


if st.button("Filtrar criptomoedas"):
    data, erro, detalhe = buscar_criptos()

    if erro:
        st.error(erro)
        st.code(detalhe)
    else:
        moedas = []

        for item in data:
            quote = item.get("quotes", {}).get("USD", {})

            nome = item.get("name")
            simbolo = item.get("symbol")

            market_cap = quote.get("market_cap")
            volume_24h = quote.get("volume_24h")
            preco = quote.get("price")
            variacao_24h = quote.get("percent_change_24h")

            moedas.append(
                {
                    "Ranking": item.get("rank"),
                    "Moeda": nome,
                    "Símbolo": simbolo,
                    "Preço em dólar": preco,
                    "Market cap": market_cap,
                    "Volume 24h": volume_24h,
                    "Variação 24h %": variacao_24h,
                    "Memecoin": parece_memecoin(nome, simbolo)
                }
            )

        df = pd.DataFrame(moedas)

        df["Market cap"] = pd.to_numeric(df["Market cap"], errors="coerce")
        df["Volume 24h"] = pd.to_numeric(df["Volume 24h"], errors="coerce")
        df["Preço em dólar"] = pd.to_numeric(df["Preço em dólar"], errors="coerce")
        df["Variação 24h %"] = pd.to_numeric(df["Variação 24h %"], errors="coerce")

        df = df.dropna(subset=["Market cap", "Volume 24h"])

        df = df[
            (df["Market cap"] >= market_cap_min) &
            (df["Volume 24h"] >= volume_min) &
            (df["Memecoin"] == False)
        ]

        if df.empty:
            st.warning("Nenhuma moeda passou nos filtros escolhidos.")
        else:
            df["Score"] = (
                (df["Market cap"].rank(pct=True) * 45) +
                (df["Volume 24h"].rank(pct=True) * 40) +
                (df["Variação 24h %"].fillna(0).rank(pct=True) * 15)
            ).round(2)

            df = df[df["Score"] >= score_min]

            df = df.sort_values(by="Score", ascending=False)

            df_final = df[
                [
                    "Ranking",
                    "Moeda",
                    "Símbolo",
                    "Preço em dólar",
                    "Market cap",
                    "Volume 24h",
                    "Variação 24h %",
                    "Score"
                ]
            ]

            st.success(f"{len(df_final)} moedas encontradas.")

            st.dataframe(
                df_final,
                use_container_width=True
            )