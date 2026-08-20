"""Serviço de inferência mínimo — o container que a demo orquestra.

Três detalhes existem para a aula, não para o modelo:

1. `/health` (liveness) e `/ready` (readiness) são endpoints SEPARADOS. Colapsar
   os dois é o erro que produz o pico de 503 em todo deploy.
2. `STARTUP_DELAY_SECONDS` simula o tempo de carregar um modelo grande (30–90 s
   no mundo real). É o que torna a readinessProbe demonstrável em 20 segundos.
3. `MODEL_VERSION` vem do ambiente (ConfigMap), nunca da imagem — é o que
   permite trocar configuração sem rebuild.
"""

from __future__ import annotations

import os
import socket
import threading
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

MODEL_VERSION = os.getenv("MODEL_VERSION", "desconhecida")
APP_VERSION = os.getenv("APP_VERSION", "v0")
STARTUP_DELAY = float(os.getenv("STARTUP_DELAY_SECONDS", "5"))
LIMIAR = float(os.getenv("LIMIAR_APROVACAO", "0.5"))
POD_NAME = os.getenv("POD_NAME", socket.gethostname())

app = FastAPI(title="inferencia", version=APP_VERSION)

# Estado de prontidão: começa falso e vira verdadeiro só depois do "carregamento".
_pronto = threading.Event()
_vivo = threading.Event()
_vivo.set()


def _carregar_modelo() -> None:
    time.sleep(STARTUP_DELAY)
    _pronto.set()


@app.on_event("startup")
def _startup() -> None:
    threading.Thread(target=_carregar_modelo, daemon=True).start()


class Pedido(BaseModel):
    score_credito: int = Field(ge=300, le=850)
    renda_anual: float = Field(gt=0)
    taxa_endividamento: float = Field(ge=0.0, le=1.0)


@app.get("/health")
def health() -> dict[str, object]:
    """Liveness: o processo está sadio? Falhar aqui REINICIA o pod."""
    if not _vivo.is_set():
        raise HTTPException(status_code=500, detail="processo degradado")
    return {"status": "ok", "pod": POD_NAME}


@app.get("/ready")
def ready() -> dict[str, object]:
    """Readiness: já posso receber tráfego? Falhar aqui só TIRA DO SERVICE."""
    if not _pronto.is_set():
        raise HTTPException(status_code=503, detail="modelo ainda carregando")
    return {"status": "pronto", "pod": POD_NAME, "model_version": MODEL_VERSION}


@app.get("/")
def raiz() -> dict[str, object]:
    return {
        "servico": "inferencia",
        "app_version": APP_VERSION,
        "model_version": MODEL_VERSION,
        "pod": POD_NAME,
        "pronto": _pronto.is_set(),
    }


@app.post("/predict")
def predict(pedido: Pedido) -> dict[str, object]:
    if not _pronto.is_set():
        raise HTTPException(status_code=503, detail="modelo ainda carregando")

    # "Modelo": regra logística determinística. O ponto da aula é o cluster.
    z = (
        -1.1
        - 3.2 * (pedido.score_credito - 300) / 550
        + 2.6 * pedido.taxa_endividamento
        - 0.8 * ((pedido.renda_anual / 70000) - 1)
    )
    risco = 1 / (1 + pow(2.718281828459045, -z))

    return {
        "risco_inadimplencia": round(risco, 4),
        "decisao": "aprovado" if risco < LIMIAR else "negado",
        "model_version": MODEL_VERSION,
        "app_version": APP_VERSION,
        # Devolver o nome do pod é o truque que torna o load balancing VISÍVEL.
        "pod": POD_NAME,
    }


@app.post("/quebrar")
def quebrar() -> dict[str, str]:
    """Derruba a liveness de propósito — o Kubernetes reinicia o pod.

    Serve ao Ato 8 da demo: mostrar `RESTARTS` subindo sozinho.
    """
    _vivo.clear()
    return {"status": "liveness derrubada; o kubelet vai reiniciar este pod"}
