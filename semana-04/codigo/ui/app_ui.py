"""Mini-UI Streamlit: o segundo serviço do Compose.

Ela não carrega modelo nenhum — só conversa com a API pelo nome do serviço
definido no docker-compose.yml (`http://api:8000`). É esse ponto que o lab
quer mostrar: dentro da network do Compose, o nome do serviço é o hostname.
"""

from __future__ import annotations

import os

import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://api:8000").rstrip("/")
TIMEOUT = 10

CORES = {"positivo": "🟢", "negativo": "🔴", "neutro": "🟡"}

st.set_page_config(page_title="Sentimento — Semana 04", page_icon="💬")
st.title("💬 Análise de sentimento")
st.caption(f"Esta UI roda em um container e chama a API em `{API_URL}`")

with st.sidebar:
    st.subheader("Saúde da API")
    if st.button("Checar /health"):
        try:
            resposta = requests.get(f"{API_URL}/health", timeout=TIMEOUT)
            resposta.raise_for_status()
            st.success(resposta.json())
        except requests.RequestException as erro:
            st.error(f"API indisponível: {erro}")

texto = st.text_area(
    "Texto para classificar",
    value="adorei o atendimento, chegou antes do prazo",
    height=120,
)

if st.button("Classificar", type="primary"):
    if not texto.strip():
        st.warning("Escreva alguma coisa antes de classificar.")
    else:
        try:
            resposta = requests.post(
                f"{API_URL}/predict",
                json={"texto": texto},
                timeout=TIMEOUT,
            )
            resposta.raise_for_status()
            dados = resposta.json()
            sentimento = dados["sentimento"]
            st.metric(
                label="Sentimento",
                value=f"{CORES.get(sentimento, '')} {sentimento}",
                delta=f"score {dados['score']:.2f}",
            )
            st.json(dados)
        except requests.HTTPError as erro:
            st.error(f"A API recusou a requisição ({erro.response.status_code})")
            st.code(erro.response.text)
        except requests.RequestException as erro:
            st.error(f"Não consegui falar com a API: {erro}")
