import os
from io import BytesIO
from datetime import datetime

import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="Crypto Filter Pro",
    page_icon="📊",
    layout="wide"
)

WATCHLIST_FILE = "watchlist.csv"

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

    .mini-card {
        background-color: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="main-title">📊 Crypto Filter Pro</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Scanner de criptomoedas com score avançado, risco, tendência, comparador, watchlist e exportação.</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="info-box">
    Este app é uma ferramenta de filtragem e estudo. Ele não é recomendação de investimento.
    </div>
    """,
    unsafe_allow_html=True
)

meme_terms = [
    "doge", "shib", "pepe", "inu", "floki", "bonk",
    "meme", "cat", "dog", "baby", "elon", "trump",
    "maga", "wojak", "moon", "safe", "frog", "pump",
    "hamster", "kitty", "pug", "ape", "chad", "based",
    "cum", "donald", "biden", "putin", "obama",
    "toad", "goat", "moonshot", "rocket", "lambo",
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
    return "Fraca"


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

    return score.clip(lower=0, upper=100).round(2)


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

    return "Moderado"


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
    motivos = []

    score = row["Score"]
    market_cap = row["Market cap"]
    volume = row["Volume 24h"]
    v24 = row["Variação 24h %"]
    v7 = row["Variação 7d %"]
    v30 = row["Variação 30d %"]
    tendencia = row["Tendência"]

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


def resumo_final(row):
    selo = row["Selo de qualidade"]
    risco = row["Nível de risco"]
    tendencia = row["Tendência"]

    if selo == "Alta qualidade":
        return "Passou com bom equilíbrio entre score, risco e tendência. Vale estudar com mais atenção."

    if selo == "Boa oportunidade":
        return "Mostra bons sinais, mas ainda precisa de confirmação com análise externa."

    if selo == "Observar":
        return "Tem pontos interessantes, mas ainda não está forte o suficiente para destaque."

    if risco == "Alto":
        return "Apresenta risco elevado pelos critérios do filtro. Exige bastante cautela."

    if tendencia == "Baixa":
        return "Tendência negativa no momento. Melhor acompanhar antes de considerar."

    return "Não se destacou nos critérios principais do filtro."


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


def preparar_df_final(df):
    return df[
        [
            "Ranking interno",
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
            "Motivo",
            "Resumo final"
        ]
    ].copy()


def formatar_df_visual(df_final):
    df_visual = df_final.copy()

    if df_visual.empty:
        return df_visual

    if "Preço" in df_visual.columns:
        df_visual["Preço"] = df_visual["Preço"].apply(formatar_dolar)

    if "Market cap" in df_visual.columns:
        df_visual["Market cap"] = df_visual["Market cap"].apply(formatar_numero)

    if "Volume 24h" in df_visual.columns:
        df_visual["Volume 24h"] = df_visual["Volume 24h"].apply(formatar_numero)

    for coluna in ["Variação 24h %", "Variação 7d %", "Variação 30d %"]:
        if coluna in df_visual.columns:
            df_visual[coluna] = pd.to_numeric(df_visual[coluna], errors="coerce").round(2)

    return df_visual.reset_index(drop=True)


def carregar_watchlist():
    colunas = [
        "Data adicionada",
        "Ranking interno",
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
        "Motivo",
        "Resumo final"
    ]

    if os.path.exists(WATCHLIST_FILE):
        try:
            return pd.read_csv(WATCHLIST_FILE)
        except Exception:
            return pd.DataFrame(columns=colunas)

    return pd.DataFrame(columns=colunas)


def salvar_watchlist(df_watchlist):
    df_watchlist.to_csv(WATCHLIST_FILE, index=False, encoding="utf-8-sig")


def exportar_excel(df_final, df_top, df_risco_alto, df_tendencia_alta, df_watchlist):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_final.to_excel(writer, index=False, sheet_name="Resultado completo")
        df_top.to_excel(writer, index=False, sheet_name="Top oportunidades")
        df_risco_alto.to_excel(writer, index=False, sheet_name="Risco alto")
        df_tendencia_alta.to_excel(writer, index=False, sheet_name="Tendência alta")

        if not df_watchlist.empty:
            df_watchlist.to_excel(writer, index=False, sheet_name="Watchlist")

    return output.getvalue()


with st.sidebar:
    st.header("⚙️ Filtros")

    perfil = st.selectbox(
        "Modo de perfil",
        ["Conservador", "Moderado", "Agressivo", "Personalizado"]
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

    market_cap_min = st.number_input(
        "Market cap mínimo",
        min_value=0,
        value=market_cap_padrao,
        step=10_000_000
    )

    volume_min = st.number_input(
        "Volume 24h mínimo",
        min_value=0,
        value=volume_padrao,
        step=1_000_000
    )

    ranking_max = st.number_input(
        "Ranking máximo",
        min_value=1,
        value=ranking_padrao,
        step=10
    )

    variacao_min = st.number_input(
        "Variação 24h mínima %",
        value=variacao_min_padrao,
        step=1.0
    )

    variacao_max = st.number_input(
        "Variação 24h máxima %",
        value=variacao_max_padrao,
        step=1.0
    )

    score_min = st.slider(
        "Score mínimo",
        min_value=0,
        max_value=100,
        value=score_padrao
    )

    st.divider()

    busca = st.text_input(
        "Buscar moeda ou símbolo",
        placeholder="Ex: BTC, SOL, Ethereum..."
    )

    filtro_classificacao = st.selectbox(
        "Classificação",
        ["Todas", "Excelente", "Boa", "Média", "Fraca"]
    )

    filtro_risco = st.selectbox(
        "Nível de risco",
        ["Todos", "Baixo", "Moderado", "Médio", "Alto"]
    )

    filtro_tendencia = st.selectbox(
        "Tendência",
        ["Todas", "Alta", "Neutra", "Baixa", "Instável"]
    )

    ordenar_por = st.selectbox(
        "Ordenar por",
        [
            "Score",
            "Ranking interno",
            "Ranking",
            "Market cap",
            "Volume 24h",
            "Variação 24h %",
            "Variação 7d %",
            "Variação 30d %"
        ]
    )

    ordem = st.selectbox(
        "Ordem",
        ["Maior para menor", "Menor para maior"]
    )

    limite_resultados = st.slider(
        "Quantidade máxima de resultados",
        min_value=10,
        max_value=200,
        value=50,
        step=10
    )

    st.divider()

    remover_stablecoins = st.checkbox("Remover stablecoins", value=True)
    top_oportunidades = st.checkbox("Mostrar apenas Top oportunidades", value=False)
    limpeza_pesada = st.checkbox("Ativar limpeza pesada", value=False)

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

    filtrar = st.button("🔎 Filtrar criptomoedas", use_container_width=True)


if "df_resultado" not in st.session_state:
    st.session_state["df_resultado"] = pd.DataFrame()

if "total_analisadas" not in st.session_state:
    st.session_state["total_analisadas"] = 0


if filtrar:
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

            moedas.append(
                {
                    "Ranking": item.get("rank"),
                    "Moeda": nome,
                    "Símbolo": simbolo,
                    "Preço": quote.get("price"),
                    "Market cap": quote.get("market_cap"),
                    "Volume 24h": quote.get("volume_24h"),
                    "Variação 24h %": quote.get("percent_change_24h"),
                    "Variação 7d %": quote.get("percent_change_7d"),
                    "Variação 30d %": quote.get("percent_change_30d"),
                    "Memecoin": parece_memecoin(nome, simbolo)
                }
            )

        df = pd.DataFrame(moedas)

        colunas_numericas = [
            "Ranking",
            "Preço",
            "Market cap",
            "Volume 24h",
            "Variação 24h %",
            "Variação 7d %",
            "Variação 30d %"
        ]

        for coluna in colunas_numericas:
            df[coluna] = pd.to_numeric(df[coluna], errors="coerce")

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

        if not df.empty:
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
            df["Alertas de risco"] = df.apply(gerar_alertas_risco, axis=1)
            df["Nível de risco"] = df.apply(nivel_risco, axis=1)
            df["Selo de qualidade"] = df.apply(gerar_selo, axis=1)
            df["Motivo"] = df.apply(gerar_motivo, axis=1)
            df["Resumo final"] = df.apply(resumo_final, axis=1)

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

            if not df.empty:
                df = df.sort_values(by="Score", ascending=False)
                df["Ranking interno"] = range(1, len(df) + 1)

                ascendente = True if ordem == "Menor para maior" else False

                df = df.sort_values(
                    by=ordenar_por,
                    ascending=ascendente
                )

                df = df.head(limite_resultados)

        st.session_state["df_resultado"] = df
        st.session_state["total_analisadas"] = total_analisadas


df = st.session_state["df_resultado"]
total_analisadas = st.session_state["total_analisadas"]

if df.empty:
    st.info("Use os filtros na barra lateral e clique em **Filtrar criptomoedas** para começar.")
else:
    df_final = preparar_df_final(df)
    df_final_formatado = formatar_df_visual(df_final)

    tab_scanner, tab_analise, tab_watchlist, tab_comparador, tab_exportacao = st.tabs(
        [
            "📊 Scanner",
            "🔍 Análise individual",
            "⭐ Watchlist",
            "⚖️ Comparador",
            "📁 Exportação"
        ]
    )

    with tab_scanner:
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

        st.markdown('<div class="section-title">Resultado</div>', unsafe_allow_html=True)
        st.dataframe(
            df_final_formatado,
            use_container_width=True,
            hide_index=True
        )

    with tab_analise:
        st.markdown('<div class="section-title">Análise individual</div>', unsafe_allow_html=True)

        moeda_escolhida = st.selectbox(
            "Escolha uma moeda para análise rápida",
            df["Moeda"].tolist()
        )

        linha = df[df["Moeda"] == moeda_escolhida].iloc[0]

        a1, a2, a3, a4 = st.columns(4)
        a1.metric("Ranking interno", int(linha["Ranking interno"]))
        a2.metric("Score", linha["Score"])
        a3.metric("Risco", linha["Nível de risco"])
        a4.metric("Tendência", linha["Tendência"])

        a5, a6, a7, a8 = st.columns(4)
        a5.metric("Ranking global", int(linha["Ranking"]))
        a6.metric("Variação 24h", f'{round(linha["Variação 24h %"], 2)}%')
        a7.metric("Variação 7d", f'{round(linha["Variação 7d %"], 2)}%')
        a8.metric("Variação 30d", f'{round(linha["Variação 30d %"], 2)}%')

        st.markdown(
            f"""
            <div class="mini-card">
            <b>Moeda:</b> {linha["Moeda"]} ({linha["Símbolo"]})<br>
            <b>Selo de qualidade:</b> {linha["Selo de qualidade"]}<br>
            <b>Motivo:</b> {linha["Motivo"]}<br>
            <b>Alertas:</b> {linha["Alertas de risco"]}<br>
            <b>Resumo final:</b> {linha["Resumo final"]}
            </div>
            """,
            unsafe_allow_html=True
        )

    with tab_watchlist:
        st.markdown('<div class="section-title">⭐ Watchlist</div>', unsafe_allow_html=True)

        df_watchlist = carregar_watchlist()

        moedas_watchlist = st.multiselect(
            "Selecione moedas do resultado para salvar na watchlist",
            df["Moeda"].tolist()
        )

        col_watch_1, col_watch_2 = st.columns(2)

        with col_watch_1:
            if st.button("⭐ Adicionar à watchlist", use_container_width=True):
                if len(moedas_watchlist) == 0:
                    st.warning("Selecione pelo menos uma moeda.")
                else:
                    df_selecionadas = df[df["Moeda"].isin(moedas_watchlist)].copy()
                    df_selecionadas = preparar_df_final(df_selecionadas)
                    df_selecionadas.insert(0, "Data adicionada", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

                    df_watchlist = carregar_watchlist()

                    if not df_watchlist.empty:
                        simbolos_existentes = set(df_watchlist["Símbolo"].astype(str).tolist())
                        df_selecionadas = df_selecionadas[
                            ~df_selecionadas["Símbolo"].astype(str).isin(simbolos_existentes)
                        ]

                    if df_selecionadas.empty:
                        st.info("Essas moedas já estão na watchlist.")
                    else:
                        df_watchlist = pd.concat([df_watchlist, df_selecionadas], ignore_index=True)
                        salvar_watchlist(df_watchlist)
                        st.success("Moeda(s) adicionada(s) à watchlist.")

        with col_watch_2:
            if st.button("🗑️ Limpar watchlist", use_container_width=True):
                salvar_watchlist(pd.DataFrame(columns=carregar_watchlist().columns))
                st.success("Watchlist limpa.")

        df_watchlist = carregar_watchlist()

        if df_watchlist.empty:
            st.info("Sua watchlist ainda está vazia.")
        else:
            remover_moedas = st.multiselect(
                "Remover moedas da watchlist",
                df_watchlist["Moeda"].dropna().unique().tolist()
            )

            if st.button("Remover selecionadas", use_container_width=True):
                if len(remover_moedas) > 0:
                    df_watchlist = df_watchlist[~df_watchlist["Moeda"].isin(remover_moedas)]
                    salvar_watchlist(df_watchlist)
                    st.success("Moeda(s) removida(s).")
                    df_watchlist = carregar_watchlist()

            st.dataframe(
                formatar_df_visual(df_watchlist),
                use_container_width=True,
                hide_index=True
            )

            watchlist_csv = df_watchlist.to_csv(index=False).encode("utf-8-sig")

            st.download_button(
                label="⬇️ Baixar watchlist em CSV",
                data=watchlist_csv,
                file_name="watchlist_crypto_filter.csv",
                mime="text/csv",
                use_container_width=True
            )

    with tab_comparador:
        st.markdown('<div class="section-title">Comparador de moedas</div>', unsafe_allow_html=True)

        moedas_comparar = st.multiselect(
            "Selecione moedas para comparar",
            df["Moeda"].tolist(),
            default=df.sort_values(by="Score", ascending=False)["Moeda"].head(2).tolist()
        )

        if len(moedas_comparar) > 0:
            df_comparacao = df[df["Moeda"].isin(moedas_comparar)][
                [
                    "Moeda",
                    "Símbolo",
                    "Ranking interno",
                    "Ranking",
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
                    "Selo de qualidade"
                ]
            ].copy()

            st.dataframe(
                formatar_df_visual(df_comparacao),
                use_container_width=True,
                hide_index=True
            )

            st.markdown('<div class="section-title">Gráfico comparativo de Score</div>', unsafe_allow_html=True)

            df_comp_grafico = df_comparacao.set_index("Símbolo")
            st.bar_chart(df_comp_grafico["Score"])
        else:
            st.info("Selecione pelo menos uma moeda para comparar.")

    with tab_exportacao:
        st.markdown('<div class="section-title">Exportação</div>', unsafe_allow_html=True)

        df_top = df_final[df_final["Selo de qualidade"].isin(["Alta qualidade", "Boa oportunidade"])].copy()
        df_risco_alto = df_final[df_final["Nível de risco"] == "Alto"].copy()
        df_tendencia_alta = df_final[df_final["Tendência"] == "Alta"].copy()
        df_watchlist = carregar_watchlist()

        csv = df_final_formatado.to_csv(index=False).encode("utf-8-sig")

        col_csv, col_excel = st.columns(2)

        with col_csv:
            st.download_button(
                label="⬇️ Baixar resultado em CSV",
                data=csv,
                file_name="resultado_crypto_filter.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col_excel:
            excel = exportar_excel(
                df_final,
                df_top,
                df_risco_alto,
                df_tendencia_alta,
                df_watchlist
            )

            st.download_button(
                label="⬇️ Baixar Excel com abas",
                data=excel,
                file_name="resultado_crypto_filter.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        st.markdown("### Abas incluídas no Excel")
        st.write("- Resultado completo")
        st.write("- Top oportunidades")
        st.write("- Risco alto")
        st.write("- Tendência alta")
        st.write("- Watchlist, se houver moedas salvas")