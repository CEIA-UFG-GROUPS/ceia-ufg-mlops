"""
Script 1: serviço de modelo genérico, usado tanto para o "champion" (produção)
quanto para o "canary/shadow" (candidato). A versão e a taxa de erro simulada
são configuráveis via variáveis de ambiente, para representar dois modelos de
qualidade diferente sem duplicar código.
"""

import os
import random
import time

from fastapi import FastAPI

app = FastAPI(title="Serviço de Modelo - Aula 22 (Estratégias de Deploy)")

MODEL_VERSION = os.environ.get("MODEL_VERSION", "v1-champion")
# Taxa de erro simulada do modelo (um canário ainda não validado tende a ter mais erros)
ERROR_RATE = float(os.environ.get("ERROR_RATE", "0.05"))
LATENCY_MS = float(os.environ.get("LATENCY_MS", "20"))


@app.get("/health")
def health():
    return {"status": "ok", "version": MODEL_VERSION}


@app.post("/predict")
def predict(payload: dict):
    time.sleep(LATENCY_MS / 1000)

    features = payload.get("features", [])
    soma = sum(features) if features else 0

    # "Predição correta" simulada: soma positiva das features indica a classe 1
    predicao_correta = 1 if soma > 0 else 0

    predicao = predicao_correta
    if random.random() < ERROR_RATE:
        predicao = 1 - predicao_correta

    return {
        "prediction": predicao,
        "version": MODEL_VERSION,
        "latency_ms": LATENCY_MS,
    }
