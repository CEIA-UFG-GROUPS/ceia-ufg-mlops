"""Testes do endpoint `POST /predict`.

Esta é a suíte que o GitHub Actions roda a cada push e a cada pull request.
Se um destes testes falhar, o merge na `main` fica bloqueado.

Os testes estão agrupados em quatro blocos, e cada bloco protege uma coisa
diferente:

1. status codes       — a API responde o que o HTTP manda responder?
2. formato da resposta — o contrato combinado na Semana 03 continua de pé?
3. comportamento       — o modelo acerta os casos óbvios?
4. endpoints de apoio  — `/health` e `/` seguem vivos?
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# 1. Status codes
# ---------------------------------------------------------------------------


def test_predict_responde_200(client: TestClient) -> None:
    resposta = client.post("/predict", json={"texto": "entrega rápida e tudo certo"})

    assert resposta.status_code == 200


def test_predict_sem_campo_texto_responde_422(client: TestClient) -> None:
    """Pydantic rejeita o corpo antes de a requisição chegar no modelo."""
    resposta = client.post("/predict", json={})

    assert resposta.status_code == 422


def test_predict_texto_vazio_responde_422(client: TestClient) -> None:
    """`min_length=1` no schema barra string vazia."""
    resposta = client.post("/predict", json={"texto": ""})

    assert resposta.status_code == 422


def test_predict_texto_longo_demais_responde_422(client: TestClient) -> None:
    """`max_length=1000` protege a API de payload abusivo."""
    resposta = client.post("/predict", json={"texto": "a" * 1001})

    assert resposta.status_code == 422


def test_predict_tipo_errado_responde_422(client: TestClient) -> None:
    resposta = client.post("/predict", json={"texto": 42})

    assert resposta.status_code == 422


def test_predict_nao_aceita_get(client: TestClient) -> None:
    """`/predict` é POST. GET tem que devolver 405, não 404."""
    resposta = client.get("/predict")

    assert resposta.status_code == 405


# ---------------------------------------------------------------------------
# 2. Formato da resposta — o contrato que outros times consomem
# ---------------------------------------------------------------------------


def test_predict_chaves_da_resposta(client: TestClient) -> None:
    """Nem chave a menos (quebra quem consome) nem a mais (vaza detalhe interno)."""
    resposta = client.post("/predict", json={"texto": "produto muito bom"})

    assert set(resposta.json()) == {"texto", "sentimento", "score", "modelo"}


def test_predict_tipos_da_resposta(client: TestClient) -> None:
    corpo = client.post("/predict", json={"texto": "produto muito bom"}).json()

    assert isinstance(corpo["texto"], str)
    assert isinstance(corpo["sentimento"], str)
    assert isinstance(corpo["score"], float)
    assert isinstance(corpo["modelo"], str)


def test_predict_devolve_o_texto_enviado(client: TestClient) -> None:
    texto = "adorei o atendimento, chegou antes do prazo"

    corpo = client.post("/predict", json={"texto": texto}).json()

    assert corpo["texto"] == texto


def test_predict_score_dentro_do_intervalo(client: TestClient) -> None:
    corpo = client.post("/predict", json={"texto": "entrega rápida e tudo certo"}).json()

    assert 0.0 <= corpo["score"] <= 1.0


def test_predict_sentimento_e_uma_das_tres_classes(client: TestClient) -> None:
    corpo = client.post("/predict", json={"texto": "qualquer coisa"}).json()

    assert corpo["sentimento"] in {"positivo", "negativo", "neutro"}


def test_predict_identifica_o_modelo(client: TestClient) -> None:
    """Saber qual modelo respondeu é o começo de qualquer investigação."""
    corpo = client.post("/predict", json={"texto": "produto muito bom"}).json()

    assert corpo["modelo"] == "tfidf+logreg"


def test_predict_responde_json(client: TestClient) -> None:
    resposta = client.post("/predict", json={"texto": "produto muito bom"})

    assert resposta.headers["content-type"].startswith("application/json")


# ---------------------------------------------------------------------------
# 3. Comportamento do modelo
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "texto",
    [
        "adorei o atendimento, chegou antes do prazo",
        "produto excelente, recomendo demais",
        "muito bom, superou as expectativas",
        "entrega rápida e tudo certo",
    ],
)
def test_predict_classifica_positivo(client: TestClient, texto: str) -> None:
    corpo = client.post("/predict", json={"texto": texto}).json()

    assert corpo["sentimento"] == "positivo"


@pytest.mark.parametrize(
    "texto",
    [
        "péssimo, veio quebrado e atrasado",
        "atendimento horrível, ninguém responde",
        "não recomendo, serviço decepcionante",
        "odiei, produto ruim",
    ],
)
def test_predict_classifica_negativo(client: TestClient, texto: str) -> None:
    corpo = client.post("/predict", json={"texto": texto}).json()

    assert corpo["sentimento"] == "negativo"


def test_predict_classifica_neutro_quando_nao_tem_sinal(client: TestClient) -> None:
    """Texto sem carga de opinião cai abaixo do limiar e vira `neutro`.

    Admitir incerteza é um comportamento do produto, não um bug — por isso
    está testado.
    """
    corpo = client.post(
        "/predict", json={"texto": "o pacote tem dimensões 20x30x10 centímetros"}
    ).json()

    assert corpo["sentimento"] == "neutro"


def test_predict_e_deterministico(client: TestClient) -> None:
    """Mesma entrada, mesma saída. Se isso quebrar, nada mais aqui vale."""
    texto = "adorei o atendimento, chegou antes do prazo"

    primeira = client.post("/predict", json={"texto": texto}).json()
    segunda = client.post("/predict", json={"texto": texto}).json()

    assert primeira == segunda


# ---------------------------------------------------------------------------
# 4. Endpoints de apoio
# ---------------------------------------------------------------------------


def test_health_responde_200_com_modelo_carregado(client: TestClient) -> None:
    """É este endpoint que o HEALTHCHECK do container e o CI consultam."""
    resposta = client.get("/health")
    corpo = resposta.json()

    assert resposta.status_code == 200
    assert corpo["status"] == "ok"
    assert corpo["modelo_carregado"] is True


def test_raiz_aponta_para_a_documentacao(client: TestClient) -> None:
    resposta = client.get("/")

    assert resposta.status_code == 200
    assert resposta.json()["docs"] == "/docs"


def test_openapi_disponivel(client: TestClient) -> None:
    """O schema OpenAPI é o contrato publicado — se ele some, quebra integração."""
    resposta = client.get("/openapi.json")

    assert resposta.status_code == 200
    assert "/predict" in resposta.json()["paths"]
