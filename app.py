import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Crypto Filter Pro",
    page_icon="📊",
    layout="wide"
)

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 18px;
        color: #B0B0B0;
        margin-bottom: 25px;
    }

    .info-box {
        background-color: rgba(255, 193, 7, 0.12);
        border-left: 5px solid #FFC107;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 25px;
        font-size: 15px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-title">📊 Crypto Filter Pro</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="subtitle">Filtro inteligente de criptomoedas com exclusão automática de memecoins e stablecoins.</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="info-box">
    Este app é apenas uma ferramenta de filtragem e estudo. 
    Ele não é recomendação de investimento.
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="section-title">Filtros principais</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    market_cap_min = st.number_input(
        "Market cap mínimo",
        min_value=0,
        value=100_000_000,
        step=10_000_000
    )

with col2:
    volume_min = st.number_input(
        "Volume 24h mínimo",
        min_value=0,
        value=10_000_000,
        step=1_000_000
    )

with col3:
    ranking_max = st.number_input(
        "Ranking máximo",
        min_value=1,
        value=250,
        step=10
    )

col4, col5, col6 = st.columns(3)

with col4:
    variacao_min = st.number_input(
        "Variação 24h mínima %",
        value=-100.0,
        step=1.0
    )

with col5:
    variacao_max = st.number_input(
        "Variação 24h máxima %",
        value=100.0,
        step=1.0
    )

with col6:
    score_min = st.slider(
        "Score mínimo",
        min_value=0,
        max_value=100,
        value=0
    )

st.markdown('<div class="section-title">Busca e organização</div>', unsafe_allow_html=True)

col7, col8, col9 = st.columns(3)

with col7:
    busca = st.text_input(
        "Buscar moeda ou símbolo",
        placeholder="Ex: BTC, SOL, Ethereum..."
    )

with col8:
    ordenar_por = st.selectbox(
        "Ordenar por",
        [
            "Score",
            "Ranking",
            "Market cap",
            "Volume 24h",
            "Variação 24h %"
        ]
    )

with col9:
    ordem = st.selectbox(
        "Ordem",
        [
            "Maior para menor",
            "Menor para maior"
        ]
    )

limite_resultados = st.slider(
    "Quantidade máxima de resultados",
    min_value=10,
    max_value=200,
    value=50,
    step=10
)

remover_stablecoins = st.checkbox(
    "Remover stablecoins",
    value=True
)

meme_terms = [
    "doge", "shib", "pepe", "inu", "floki", "bonk",
    "meme", "cat", "dog", "baby", "elon", "trump",
    "maga", "wojak", "moon", "safe", "frog", "pump"
]

stablecoins = [
    "USDT", "USDC", "DAI", "FDUSD", "TUSD", "USDD",
    "USDE", "PYUSD", "BUSD", "GUSD", "LUSD", "FRAX",
    "USDP", "EURS", "SUSD", "USD0", "RLUSD"
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


def classificar_score(score):
    if score >= 85:
        return "Excelente"
    elif score >= 70:
        return "Boa"
    elif score >= 50:
        return "Média"
    else:
        return "Fraca"


def gerar_motivo(row):
    score = row["Score"]
    market_cap = row["Market cap"]
    volume = row["Volume 24h"]
    variacao = row["Variação 24h %"]

    motivos = []

    if score >= 85:
        motivos.append("score forte")
    elif score >= 70:
        motivos.append("score bom")
    elif score >= 50:
        motivos.append("score moderado")
    else:
        motivos.append("score fraco")

    if market_cap >= 10_000_000_000:
        motivos.append("market cap alto")
    elif market_cap >= 1_000_000_000:
        motivos.append("market cap relevante")
    else:
        motivos.append("market cap menor")

    if volume >= 1_000_000_000:
        motivos.append("volume muito forte")
    elif volume >= 100_000_000:
        motivos.append("bom volume")
    else:
        motivos.append("volume mais baixo")

    if variacao >= 10:
        motivos.append("alta forte em 24h")
    elif variacao >= 3:
        motivos.append("alta moderada em 24h")
    elif variacao <= -10:
        motivos.append("queda forte em 24h")
    elif variacao <= -3:
        motivos.append("queda moderada em 24h")
    else:
        motivos.append("variação estável")

    return ", ".join(motivos).capitalize() + "."


def formatar_dolar(valor):
    try:
        return f"US$ {valor:,.2f}"
    except Exception:
        return valor


def formatar_numero(valor):
    try:
        return f"US$ {valor:,.0f}"
    except Exception:
        return valor


if st.button("🔎 Filtrar criptomoedas", use_container_width=True):
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
                    "Preço": preco,
                    "Market cap": market_cap,
                    "Volume 24h": volume_24h,
                    "Variação 24h %": variacao_24h,
                    "Memecoin": parece_memecoin(nome, simbolo)
                }
            )

        df = pd.DataFrame(moedas)

        df["Ranking"] = pd.to_numeric(df["Ranking"], errors="coerce")
        df["Market cap"] = pd.to_numeric(df["Market cap"], errors="coerce")
        df["Volume 24h"] = pd.to_numeric(df["Volume 24h"], errors="coerce")
        df["Preço"] = pd.to_numeric(df["Preço"], errors="coerce")
        df["Variação 24h %"] = pd.to_numeric(df["Variação 24h %"], errors="coerce")

        df = df.dropna(subset=["Ranking", "Market cap", "Volume 24h"])

        total_analisadas = len(df)

        df = df[
            (df["Market cap"] >= market_cap_min) &
            (df["Volume 24h"] >= volume_min) &
            (df["Ranking"] <= ranking_max) &
            (df["Variação 24h %"] >= variacao_min) &
            (df["Variação 24h %"] <= variacao_max) &
            (df["Memecoin"] == False)
        ]

        if remover_stablecoins:
            df = df[~df["Símbolo"].isin(stablecoins)]

        if busca.strip() != "":
            busca_normalizada = busca.strip().lower()

            df = df[
                df["Moeda"].str.lower().str.contains(busca_normalizada, na=False) |
                df["Símbolo"].str.lower().str.contains(busca_normalizada, na=False)
            ]

        if df.empty:
            st.warning("Nenhuma moeda passou nos filtros escolhidos.")

        else:
            df["Score"] = (
                (df["Market cap"].rank(pct=True) * 45) +
                (df["Volume 24h"].rank(pct=True) * 40) +
                (df["Variação 24h %"].fillna(0).rank(pct=True) * 15)
            ).round(2)

            df["Classificação"] = df["Score"].apply(classificar_score)
            df["Motivo"] = df.apply(gerar_motivo, axis=1)

            df = df[df["Score"] >= score_min]

            if df.empty:
                st.warning("Nenhuma moeda passou no score mínimo escolhido.")

            else:
                ascendente = True if ordem == "Menor para maior" else False

                df = df.sort_values(
                    by=ordenar_por,
                    ascending=ascendente
                )

                df = df.head(limite_resultados)

                total_filtradas = len(df)
                melhor_score = df["Score"].max()
                melhor_moeda = df.sort_values(by="Score", ascending=False).iloc[0]["Moeda"]

                excelentes = len(df[df["Classificação"] == "Excelente"])
                boas = len(df[df["Classificação"] == "Boa"])

                st.markdown('<div class="section-title">Resumo do filtro</div>', unsafe_allow_html=True)

                m1, m2, m3, m4 = st.columns(4)

                m1.metric("Moedas analisadas", total_analisadas)
                m2.metric("Moedas aprovadas", total_filtradas)
                m3.metric("Melhor score", melhor_score)
                m4.metric("Melhor moeda", melhor_moeda)

                m5, m6 = st.columns(2)
                m5.metric("Classificação excelente", excelentes)
                m6.metric("Classificação boa", boas)

                st.markdown('<div class="section-title">Resultado</div>', unsafe_allow_html=True)

                df_final = df[
                    [
                        "Ranking",
                        "Moeda",
                        "Símbolo",
                        "Preço",
                        "Market cap",
                        "Volume 24h",
                        "Variação 24h %",
                        "Score",
                        "Classificação",
                        "Motivo"
                    ]
                ].copy()

                df_final["Preço"] = df_final["Preço"].apply(formatar_dolar)
                df_final["Market cap"] = df_final["Market cap"].apply(formatar_numero)
                df_final["Volume 24h"] = df_final["Volume 24h"].apply(formatar_numero)
                df_final["Variação 24h %"] = df_final["Variação 24h %"].round(2)

                df_final = df_final.reset_index(drop=True)

                st.dataframe(
                    df_final,
                    use_container_width=True,
                    hide_index=True
                )

                csv = df_final.to_csv(index=False).encode("utf-8-sig")

                st.download_button(
                    label="⬇️ Baixar resultado em CSV",
                    data=csv,
                    file_name="resultado_crypto_filter.csv",
                    mime="text/csv",
                    use_container_width=True
                )