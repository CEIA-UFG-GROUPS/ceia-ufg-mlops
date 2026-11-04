"""API de análise de sentimento — Semana 04 (Docker).

Mesma API da Semana 03, agora pronta para ser empacotada em uma imagem.
O modelo é treinado uma única vez, no startup, e fica em memória.

Rodar local (sem Docker), a partir de `semana-04/codigo/`:

    uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import logging
import os
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.modelo import (
    LIMIAR_NEUTRO_PADRAO,
    NOME_MODELO,
    acuracia_treino,
    classificar,
    treinar_modelo,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("api-sentimento")

VERSAO = "1.0.0"
LIMIAR_NEUTRO = float(os.getenv("LIMIAR_NEUTRO", LIMIAR_NEUTRO_PADRAO))

# Estado do processo: preenchido no startup pelo lifespan.
estado: dict[str, object] = {"modelo": None}


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Treina o modelo no startup — e não a cada requisição."""
    inicio = time.perf_counter()
    modelo = treinar_modelo()
    duracao_ms = (time.perf_counter() - inicio) * 1000
    estado["modelo"] = modelo
    logger.info(
        "modelo '%s' treinado em %.0f ms (acurácia no treino: %.2f, limiar neutro: %.2f)",
        NOME_MODELO,
        duracao_ms,
        acuracia_treino(modelo),
        LIMIAR_NEUTRO,
    )
    yield
    estado["modelo"] = None
    logger.info("encerrando a API")


app = FastAPI(
    title="API de Sentimento — Semana 04",
    description="Classifica o sentimento de um texto em português (positivo, negativo ou neutro).",
    version=VERSAO,
    lifespan=lifespan,
)


class PedidoPredicao(BaseModel):
    """Contrato de entrada do /predict (congelado na Semana 03)."""

    texto: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Texto a ser classificado.",
        examples=["adorei o atendimento, chegou antes do prazo"],
    )


class RespostaPredicao(BaseModel):
    """Contrato de saída do /predict."""

    texto: str
    sentimento: str = Field(description="positivo, negativo ou neutro")
    score: float = Field(ge=0.0, le=1.0, description="Confiança da classe vencedora")
    modelo: str


class RespostaSaude(BaseModel):
    status: str
    modelo_carregado: bool
    versao: str


@app.get("/", tags=["info"])
def raiz() -> dict[str, str]:
    """Rota de cortesia: diz para onde ir."""
    return {
        "servico": "api-sentimento",
        "versao": VERSAO,
        "docs": "/docs",
        "health": "/health",
        "predict": "POST /predict",
    }


@app.get("/health", response_model=RespostaSaude, tags=["info"])
def health() -> RespostaSaude:
    """Usada pelo HEALTHCHECK do container e pelo `depends_on` do Compose."""
    return RespostaSaude(
        status="ok",
        modelo_carregado=estado["modelo"] is not None,
        versao=VERSAO,
    )


@app.post("/predict", response_model=RespostaPredicao, tags=["predicao"])
def predict(pedido: PedidoPredicao) -> RespostaPredicao:
    """Classifica o sentimento do texto recebido."""
    modelo = estado["modelo"]
    sentimento, score = classificar(modelo, pedido.texto, LIMIAR_NEUTRO)

    logger.info("predict | sentimento=%s score=%.3f", sentimento, score)

    return RespostaPredicao(
        texto=pedido.texto,
        sentimento=sentimento,
        score=score,
        modelo=NOME_MODELO,
    )
