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
    '<div class="subtitle">Scanner de criptomoedas com anti-memecoin, score avançado, risco, tendência e análise individual.</div>',
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

st.markdown('<div class="section-title">Modo de perfil</div>', unsafe_allow_html=True)

perfil = st.selectbox(
    "Escolha o perfil do filtro",
    [
        "Conservador",
        "Moderado",
        "Agressivo",
        "Personalizado"
    ]
)

if perfil == "Conservador":
    market_cap_padrao = 1_000_000_000
    volume_padrao = 100_000_000
    ranking_padrao = 100
    variacao_min_padrao = -10.0
    variacao_max_padrao = 15.0
    score_padrao = 70
elif perfil == "Moderado":
    market_cap_padrao = 300_000_000
    volume_padrao = 30_000_000
    ranking_padrao = 200
    variacao_min_padrao = -20.0
    variacao_max_padrao = 30.0
    score_padrao = 50
elif perfil == "Agressivo":
    market_cap_padrao = 50_000_000
    volume_padrao = 5_000_000
    ranking_padrao = 500
    variacao_min_padrao = -40.0
    variacao_max_padrao = 80.0
    score_padrao = 30
else:
    market_cap_padrao = 100_000_000
    volume_padrao = 10_000_000
    ranking_padrao = 250
    variacao_min_padrao = -100.0
    variacao_max_padrao = 100.0
    score_padrao = 0

st.markdown('<div class="section-title">Filtros principais</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    market_cap_min = st.number_input(
        "Market cap mínimo",
        min_value=0,
        value=market_cap_padrao,
        step=10_000_000
    )

with col2:
    volume_min = st.number_input(
        "Volume 24h mínimo",
        min_value=0,
        value=volume_padrao,
        step=1_000_000
    )

with col3:
    ranking_max = st.number_input(
        "Ranking máximo",
        min_value=1,
        value=ranking_padrao,
        step=10
    )

col4, col5, col6 = st.columns(3)

with col4:
    variacao_min = st.number_input(
        "Variação 24h mínima %",
        value=variacao_min_padrao,
        step=1.0
    )

with col5:
    variacao_max = st.number_input(
        "Variação 24h máxima %",
        value=variacao_max_padrao,
        step=1.0
    )

with col6:
    score_min = st.slider(
        "Score mínimo",
        min_value=0,
        max_value=100,
        value=score_padrao
    )

st.markdown('<div class="section-title">Busca, tendência, risco e organização</div>', unsafe_allow_html=True)

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
            "Variação 24h %",
            "Variação 7d %",
            "Variação 30d %"
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

col10, col11, col12 = st.columns(3)

with col10:
    filtro_classificacao = st.selectbox(
        "Filtrar por classificação",
        [
            "Todas",
            "Excelente",
            "Boa",
            "Média",
            "Fraca"
        ]
    )

with col11:
    filtro_risco = st.selectbox(
        "Filtrar por nível de risco",
        [
            "Todos",
            "Baixo",
            "Moderado",
            "Médio",
            "Alto"
        ]
    )

with col12:
    filtro_tendencia = st.selectbox(
        "Filtrar por tendência",
        [
            "Todas",
            "Alta",
            "Neutra",
            "Baixa",
            "Instável"
        ]
    )

col13, col14, col15 = st.columns(3)

with col13:
    remover_stablecoins = st.checkbox(
        "Remover stablecoins",
        value=True
    )

with col14:
    top_oportunidades = st.checkbox(
        "Mostrar apenas Top oportunidades",
        value=False
    )

with col15:
    limpeza_pesada = st.checkbox(
        "Ativar limpeza pesada",
        value=False
    )

limite_resultados = st.slider(
    "Quantidade máxima de resultados",
    min_value=10,
    max_value=200,
    value=50,
    step=10
)

tipo_grafico = st.selectbox(
    "Gráfico visual",
    [
        "Score",
        "Volume 24h",
        "Market cap",
        "Variação 24h %",
        "Variação 7d %",
        "Variação 30d %"
    ]
)

meme_terms = [
    "doge", "shib", "pepe", "inu", "floki", "bonk",
    "meme", "cat", "dog", "baby", "elon", "trump",
    "maga", "wojak", "moon", "safe", "frog", "pump",
    "hamster", "kitty", "pug", "ape", "chad", "based",
    "cum", "elon", "donald", "biden", "putin", "obama",
    "toad", "goat", "moonshot", "rocket", "lambo", "wife",
    "millionaire", "rich", "degen", "waifu"
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


def classificar_tendencia(v24, v7, v30):
    v24 = 0 if pd.isna(v24) else v24
    v7 = 0 if pd.isna(v7) else v7
    v30 = 0 if pd.isna(v30) else v30

    if abs(v24) >= 35 or abs(v7) >= 50 or abs(v30) >= 100:
        return "Instável"

    if v24 > 0 and v7 > 0 and v30 > 0:
        return "Alta"

    if v24 < 0 and v7 < 0 and v30 < 0:
        return "Baixa"

    if v7 > 0 and v30 > 0:
        return "Alta"

    if v7 < 0 and v30 < 0:
        return "Baixa"

    return "Neutra"


def classificar_score(score):
    if score >= 85:
        return "Excelente"
    elif score >= 70:
        return "Boa"
    elif score >= 50:
        return "Média"
    else:
        return "Fraca"


def gerar_selo(row):
    score = row["Score"]
    risco = row["Nível de risco"]
    tendencia = row["Tendência"]

    if score >= 80 and risco in ["Baixo", "Moderado"] and tendencia == "Alta":
        return "Alta qualidade"

    if score >= 70 and risco in ["Baixo", "Moderado"] and tendencia in ["Alta", "Neutra"]:
        return "Boa oportunidade"

    if score >= 50 and risco != "Alto":
        return "Observar"

    if risco == "Alto":
        return "Risco elevado"

    return "Evitar por enquanto"


def gerar_motivo(row):
    score = row["Score"]
    market_cap = row["Market cap"]
    volume = row["Volume 24h"]
    v24 = row["Variação 24h %"]
    v7 = row["Variação 7d %"]
    v30 = row["Variação 30d %"]
    tendencia = row["Tendência"]

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

    if tendencia == "Alta":
        motivos.append("tendência positiva")
    elif tendencia == "Baixa":
        motivos.append("tendência negativa")
    elif tendencia == "Instável":
        motivos.append("movimento instável")
    else:
        motivos.append("tendência neutra")

    if v24 >= 15 or v7 >= 30 or v30 >= 60:
        motivos.append("forte valorização recente")
    elif v24 <= -15 or v7 <= -30 or v30 <= -60:
        motivos.append("queda relevante recente")

    return ", ".join(motivos).capitalize() + "."


def gerar_alertas_risco(row):
    alertas = []

    ranking = row["Ranking"]
    market_cap = row["Market cap"]
    volume = row["Volume 24h"]
    v24 = row["Variação 24h %"]
    v7 = row["Variação 7d %"]
    v30 = row["Variação 30d %"]
    score = row["Score"]
    tendencia = row["Tendência"]

    if ranking > 300:
        alertas.append("ranking distante")

    if market_cap < 100_000_000:
        alertas.append("market cap muito baixo")
    elif market_cap < 300_000_000:
        alertas.append("market cap menor")

    if volume < 10_000_000:
        alertas.append("volume baixo")
    elif volume < 30_000_000:
        alertas.append("volume moderado")

    if v24 >= 30:
        alertas.append("alta muito forte em 24h")
    elif v24 <= -30:
        alertas.append("queda muito forte em 24h")

    if v7 >= 50:
        alertas.append("alta muito forte em 7d")
    elif v7 <= -50:
        alertas.append("queda muito forte em 7d")

    if v30 >= 100:
        alertas.append("alta extrema em 30d")
    elif v30 <= -70:
        alertas.append("queda extrema em 30d")

    if tendencia == "Instável":
        alertas.append("tendência instável")

    if score < 50:
        alertas.append("score fraco")

    if len(alertas) == 0:
        return "Sem alerta grave"

    return ", ".join(alertas).capitalize() + "."


def nivel_risco(row):
    alertas = row["Alertas de risco"]

    if alertas == "Sem alerta grave":
        return "Baixo"

    quantidade_alertas = alertas.count(",") + 1

    if quantidade_alertas >= 4:
        return "Alto"
    elif quantidade_alertas >= 2:
        return "Médio"
    else:
        return "Moderado"


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


def calcular_score_avancado(df):
    df = df.copy()

    market_score = df["Market cap"].rank(pct=True) * 25
    volume_score = df["Volume 24h"].rank(pct=True) * 25

    ranking_maximo = df["Ranking"].max()
    ranking_minimo = df["Ranking"].min()

    if ranking_maximo == ranking_minimo:
        ranking_score = pd.Series([15] * len(df), index=df.index)
    else:
        ranking_score = (1 - ((df["Ranking"] - ranking_minimo) / (ranking_maximo - ranking_minimo))) * 15

    v24_score = df["Variação 24h %"].fillna(0).rank(pct=True) * 10
    v7_score = df["Variação 7d %"].fillna(0).rank(pct=True) * 10
    v30_score = df["Variação 30d %"].fillna(0).rank(pct=True) * 10

    tendencia_bonus = df["Tendência"].map(
        {
            "Alta": 5,
            "Neutra": 2,
            "Baixa": -5,
            "Instável": -8
        }
    ).fillna(0)

    penalidade_volatilidade = (
        (df["Variação 24h %"].abs() > 35).astype(int) * 5 +
        (df["Variação 7d %"].abs() > 60).astype(int) * 5 +
        (df["Variação 30d %"].abs() > 120).astype(int) * 5
    )

    score = (
        market_score +
        volume_score +
        ranking_score +
        v24_score +
        v7_score +
        v30_score +
        tendencia_bonus -
        penalidade_volatilidade
    )

    score = score.clip(lower=0, upper=100).round(2)

    return score


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
            variacao_7d = quote.get("percent_change_7d")
            variacao_30d = quote.get("percent_change_30d")

            moedas.append(
                {
                    "Ranking": item.get("rank"),
                    "Moeda": nome,
                    "Símbolo": simbolo,
                    "Preço": preco,
                    "Market cap": market_cap,
                    "Volume 24h": volume_24h,
                    "Variação 24h %": variacao_24h,
                    "Variação 7d %": variacao_7d,
                    "Variação 30d %": variacao_30d,
                    "Memecoin": parece_memecoin(nome, simbolo)
                }
            )

        df = pd.DataFrame(moedas)

        df["Ranking"] = pd.to_numeric(df["Ranking"], errors="coerce")
        df["Market cap"] = pd.to_numeric(df["Market cap"], errors="coerce")
        df["Volume 24h"] = pd.to_numeric(df["Volume 24h"], errors="coerce")
        df["Preço"] = pd.to_numeric(df["Preço"], errors="coerce")
        df["Variação 24h %"] = pd.to_numeric(df["Variação 24h %"], errors="coerce")
        df["Variação 7d %"] = pd.to_numeric(df["Variação 7d %"], errors="coerce")
        df["Variação 30d %"] = pd.to_numeric(df["Variação 30d %"], errors="coerce")

        df["Variação 24h %"] = df["Variação 24h %"].fillna(0)
        df["Variação 7d %"] = df["Variação 7d %"].fillna(0)
        df["Variação 30d %"] = df["Variação 30d %"].fillna(0)

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

        if limpeza_pesada:
            df = df[
                (df["Market cap"] >= 100_000_000) &
                (df["Volume 24h"] >= 10_000_000) &
                (df["Ranking"] <= 500) &
                (df["Variação 24h %"].between(-30, 50)) &
                (df["Variação 7d %"].between(-50, 80)) &
                (df["Variação 30d %"].between(-70, 150))
            ]

        if busca.strip() != "":
            busca_normalizada = busca.strip().lower()

            df = df[
                df["Moeda"].str.lower().str.contains(busca_normalizada, na=False) |
                df["Símbolo"].str.lower().str.contains(busca_normalizada, na=False)
            ]

        if df.empty:
            st.warning("Nenhuma moeda passou nos filtros escolhidos.")

        else:
            df["Tendência"] = df.apply(
                lambda row: classificar_tendencia(
                    row["Variação 24h %"],
                    row["Variação 7d %"],
                    row["Variação 30d %"]
                ),
                axis=1
            )

            df["Score"] = calcular_score_avancado(df)
            df["Classificação"] = df["Score"].apply(classificar_score)
            df["Motivo"] = df.apply(gerar_motivo, axis=1)
            df["Alertas de risco"] = df.apply(gerar_alertas_risco, axis=1)
            df["Nível de risco"] = df.apply(nivel_risco, axis=1)
            df["Selo de qualidade"] = df.apply(gerar_selo, axis=1)

            df = df[df["Score"] >= score_min]

            if filtro_classificacao != "Todas":
                df = df[df["Classificação"] == filtro_classificacao]

            if filtro_risco != "Todos":
                df = df[df["Nível de risco"] == filtro_risco]

            if filtro_tendencia != "Todas":
                df = df[df["Tendência"] == filtro_tendencia]

            if top_oportunidades:
                df = df[
                    (df["Score"] >= 70) &
                    (df["Nível de risco"].isin(["Baixo", "Moderado"])) &
                    (df["Tendência"].isin(["Alta", "Neutra"])) &
                    (df["Market cap"] >= 300_000_000) &
                    (df["Volume 24h"] >= 30_000_000)
                ]

            if df.empty:
                st.warning("Nenhuma moeda passou nos filtros escolhidos.")

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
                medias = len(df[df["Classificação"] == "Média"])
                fracas = len(df[df["Classificação"] == "Fraca"])

                risco_baixo = len(df[df["Nível de risco"] == "Baixo"])
                risco_moderado = len(df[df["Nível de risco"] == "Moderado"])
                risco_medio = len(df[df["Nível de risco"] == "Médio"])
                risco_alto = len(df[df["Nível de risco"] == "Alto"])

                tendencia_alta = len(df[df["Tendência"] == "Alta"])
                tendencia_neutra = len(df[df["Tendência"] == "Neutra"])
                tendencia_baixa = len(df[df["Tendência"] == "Baixa"])
                tendencia_instavel = len(df[df["Tendência"] == "Instável"])

                st.markdown('<div class="section-title">Resumo do filtro</div>', unsafe_allow_html=True)

                m1, m2, m3, m4 = st.columns(4)

                m1.metric("Moedas analisadas", total_analisadas)
                m2.metric("Moedas aprovadas", total_filtradas)
                m3.metric("Melhor score", melhor_score)
                m4.metric("Melhor moeda", melhor_moeda)

                m5, m6, m7, m8 = st.columns(4)
                m5.metric("Excelentes", excelentes)
                m6.metric("Boas", boas)
                m7.metric("Médias", medias)
                m8.metric("Fracas", fracas)

                r1, r2, r3, r4 = st.columns(4)
                r1.metric("Risco baixo", risco_baixo)
                r2.metric("Risco moderado", risco_moderado)
                r3.metric("Risco médio", risco_medio)
                r4.metric("Risco alto", risco_alto)

                t1, t2, t3, t4 = st.columns(4)
                t1.metric("Tendência alta", tendencia_alta)
                t2.metric("Tendência neutra", tendencia_neutra)
                t3.metric("Tendência baixa", tendencia_baixa)
                t4.metric("Tendência instável", tendencia_instavel)

                st.markdown('<div class="section-title">Gráfico visual</div>', unsafe_allow_html=True)

                df_grafico = df.sort_values(by=tipo_grafico, ascending=False).head(10)
                df_grafico = df_grafico.set_index("Símbolo")

                st.bar_chart(df_grafico[tipo_grafico])

                st.markdown('<div class="section-title">Análise individual</div>', unsafe_allow_html=True)

                moeda_escolhida = st.selectbox(
                    "Escolha uma moeda para análise rápida",
                    df["Moeda"].tolist()
                )

                linha = df[df["Moeda"] == moeda_escolhida].iloc[0]

                a1, a2, a3, a4 = st.columns(4)
                a1.metric("Símbolo", linha["Símbolo"])
                a2.metric("Score", linha["Score"])
                a3.metric("Risco", linha["Nível de risco"])
                a4.metric("Tendência", linha["Tendência"])

                st.write(f"**Selo de qualidade:** {linha['Selo de qualidade']}")
                st.write(f"**Motivo:** {linha['Motivo']}")
                st.write(f"**Alertas:** {linha['Alertas de risco']}")

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
                        "Variação 7d %",
                        "Variação 30d %",
                        "Score",
                        "Classificação",
                        "Tendência",
                        "Nível de risco",
                        "Selo de qualidade",
                        "Alertas de risco",
                        "Motivo"
                    ]
                ].copy()

                df_final["Preço"] = df_final["Preço"].apply(formatar_dolar)
                df_final["Market cap"] = df_final["Market cap"].apply(formatar_numero)
                df_final["Volume 24h"] = df_final["Volume 24h"].apply(formatar_numero)
                df_final["Variação 24h %"] = df_final["Variação 24h %"].round(2)
                df_final["Variação 7d %"] = df_final["Variação 7d %"].round(2)
                df_final["Variação 30d %"] = df_final["Variação 30d %"].round(2)

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