"""
Script 2: Gateway de tráfego que implementa as três estratégias de deploy
estudadas na aula, escolhida via variável de ambiente DEPLOY_STRATEGY:

- "blue_green": 100% do tráfego vai para o ambiente ACTIVE_COLOR (blue=champion,
  green=canary). Trocar essa variável e reiniciar o gateway simula o corte
  atômico de tráfego de um Blue-Green Deployment.
- "canary": uma fração (CANARY_PERCENT) do tráfego é roteada para o modelo
  candidato, o resto continua no champion.
- "shadow": 100% do tráfego real é respondido pelo champion; uma cópia de cada
  requisição é espelhada (em paralelo) para o modelo shadow, cuja resposta é
  descartada e apenas usada para medir divergência.
"""

import os
import random

import httpx
from fastapi import FastAPI

app = FastAPI(title="Gateway de Estratégias de Deploy - Aula 22")

CHAMPION_URL = os.environ.get("CHAMPION_URL", "http://model-champion:8000")
CANARY_URL = os.environ.get("CANARY_URL", "http://model-canary:8000")

STRATEGY = os.environ.get("DEPLOY_STRATEGY", "canary")  # canary | blue_green | shadow
CANARY_PERCENT = int(os.environ.get("CANARY_PERCENT", "10"))
ACTIVE_COLOR = os.environ.get("ACTIVE_COLOR", "blue")  # blue -> champion, green -> canary

# Estado simples em memória para acompanhar a taxa de divergência do Shadow Deployment
_divergencias: list[bool] = []


@app.get("/health")
def health():
    return {"status": "ok", "strategy": STRATEGY}


@app.post("/predict")
async def predict(payload: dict):
    async with httpx.AsyncClient(timeout=5.0) as client:

        if STRATEGY == "blue_green":
            alvo = CHAMPION_URL if ACTIVE_COLOR == "blue" else CANARY_URL
            resp = await client.post(f"{alvo}/predict", json=payload)
            body = resp.json()
            body["_gateway_strategy"] = "blue_green"
            body["_gateway_active_color"] = ACTIVE_COLOR
            return body

        if STRATEGY == "canary":
            usar_canary = random.randint(1, 100) <= CANARY_PERCENT
            alvo = CANARY_URL if usar_canary else CHAMPION_URL
            resp = await client.post(f"{alvo}/predict", json=payload)
            body = resp.json()
            body["_gateway_strategy"] = "canary"
            body["_gateway_canary_percent"] = CANARY_PERCENT
            body["_gateway_routed_to"] = "canary" if usar_canary else "champion"
            return body

        if STRATEGY == "shadow":
            resp_producao = await client.post(f"{CHAMPION_URL}/predict", json=payload)
            body = resp_producao.json()
            body["_gateway_strategy"] = "shadow"

            # A chamada ao modelo sombra NUNCA deve afetar a resposta retornada ao usuário.
            try:
                resp_shadow = await client.post(f"{CANARY_URL}/predict", json=payload)
                shadow_body = resp_shadow.json()
                divergiu = shadow_body.get("prediction") != body.get("prediction")
                _divergencias.append(divergiu)
                if divergiu:
                    print(
                        f"[SHADOW] Divergência detectada! "
                        f"champion={body.get('prediction')} shadow={shadow_body.get('prediction')}"
                    )
            except Exception as exc:  # noqa: BLE001 - falha no shadow nunca deve propagar
                print(f"[SHADOW] Falha ao chamar o modelo sombra (resposta ao usuário não é afetada): {exc}")

            return body

        return {"error": f"Estratégia de deploy desconhecida: {STRATEGY}"}


@app.get("/shadow/stats")
def shadow_stats():
    """Métrica de divergência acumulada entre champion e shadow (apenas relevante em STRATEGY=shadow)."""
    if not _divergencias:
        return {"total_comparacoes": 0, "taxa_divergencia": None}
    taxa = sum(_divergencias) / len(_divergencias)
    return {"total_comparacoes": len(_divergencias), "taxa_divergencia": round(taxa, 4)}
