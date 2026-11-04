"""API de análise de sentimento — Semana 03 (FastAPI).

É aqui que o serviço do grupo nasce. O contrato definido neste arquivo
(`GET /`, `GET /health`, `POST /predict`) fica **congelado** e é reusado das
Semanas 04 a 11: a Semana 04 empacota esta mesma API em uma imagem Docker, a
Semana 07 a publica no Cloud Run e a Semana 10 a bombardeia no load test.

O modelo é treinado uma única vez, no startup (via `lifespan`), e fica em
memória — não a cada requisição.

Rodar local, a partir de `semana-03/codigo/`:

    uvicorn app.main:app --reload --port 8000

Documentação interativa: http://localhost:8000/docs
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
    title="API de Sentimento — Semana 03",
    description="Classifica o sentimento de um texto em português (positivo, negativo ou neutro).",
    version=VERSAO,
    lifespan=lifespan,
)


class PedidoPredicao(BaseModel):
    """Contrato de entrada do /predict (congelado nesta semana).

    O nome da classe vira o nome do schema no `/openapi.json` — por isso vale
    um nome que diga o papel do objeto, não o tipo do campo.
    """

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
    """Diz se o processo está de pé e se o modelo já foi carregado.

    A partir da Semana 04 esta rota passa a ser consumida por máquinas: o
    `HEALTHCHECK` do container, o `depends_on` do Compose e, na Semana 07, o
    probe do Cloud Run.
    """
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
