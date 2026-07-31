"""Servidor MCP de MLOps — expõe um modelo de ML para agentes de IA.

Este servidor transforma um modelo de detecção de fraude (e seus metadados)
em capacidades que QUALQUER cliente MCP consegue descobrir e usar: Claude Code,
Cursor, VS Code (Copilot), Windsurf, Claude Desktop, um agente conversacional
próprio ou o cliente Python de `agent_client.py`.

Ele oferece as três primitivas de servidor do MCP:

    - Tools     (ações que o MODELO decide chamar): predict, list_models,
                get_model_card
    - Resources (dados read-only que a APLICAÇÃO injeta como contexto):
                o model card e o schema do dataset
    - Prompts   (templates que o USUÁRIO invoca): investigate_alert

Transportes:
    - stdio            (padrão)   -> cliente sobe o servidor como subprocesso
    - streamable-http  (remoto)   -> servidor de rede compartilhado (Docker)

Controle via variáveis de ambiente:
    MCP_TRANSPORT = stdio | streamable-http   (padrão: stdio)
    MCP_HOST      = 0.0.0.0                    (só para streamable-http)
    MCP_PORT      = 8000                       (só para streamable-http)

⚠️  stdio: NUNCA use print() para stdout — isso corrompe as mensagens JSON-RPC.
    Todo log vai para stderr (logging já faz isso por padrão).
"""

from __future__ import annotations

import json
import logging
import os
import sys
from pathlib import Path

import joblib
from mcp.server.fastmcp import FastMCP

# Logs SEMPRE em stderr (obrigatório no transporte stdio).
logging.basicConfig(level=logging.INFO, stream=sys.stderr)
logger = logging.getLogger("mlops-mcp")

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

mcp = FastMCP(
    "mlops-fraud",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", "8000")),
)


def _load_artifacts() -> tuple[object | None, dict]:
    """Carrega modelo + model card do disco (ou avisa que faltou treinar)."""
    model_path = MODELS_DIR / "model.pkl"
    card_path = MODELS_DIR / "model_card.json"
    if not model_path.exists() or not card_path.exists():
        logger.warning(
            "Artefatos não encontrados em %s. Rode `python src/train_model.py` "
            "antes de subir o servidor.",
            MODELS_DIR,
        )
        return None, {}
    model = joblib.load(model_path)
    card = json.loads(card_path.read_text(encoding="utf-8"))
    logger.info("Modelo '%s' v%s carregado.", card.get("name"), card.get("version"))
    return model, card


_MODEL, _CARD = _load_artifacts()


# --------------------------------------------------------------------------- #
# TOOLS — o modelo (LLM) decide quando chamar. Ações com schema tipado.
# --------------------------------------------------------------------------- #
@mcp.tool()
def predict(
    amount: float,
    hour_of_day: int,
    num_tx_last_hour: int,
    account_age_days: int,
    is_foreign: int,
    distance_from_home_km: float,
) -> dict:
    """Avalia o risco de fraude de UMA transação com o modelo em produção.

    Args:
        amount: Valor da transação em R$.
        hour_of_day: Hora do dia da transação (0-23).
        num_tx_last_hour: Nº de transações da conta na última hora.
        account_age_days: Idade da conta em dias.
        is_foreign: 1 se a transação é no exterior, 0 caso contrário.
        distance_from_home_km: Distância do local usual do cliente, em km.

    Returns:
        dict com o rótulo previsto, a probabilidade de fraude e a versão do modelo.
    """
    if _MODEL is None:
        return {"error": "Modelo não carregado. Rode src/train_model.py primeiro."}

    features = [[
        amount, hour_of_day, num_tx_last_hour,
        account_age_days, is_foreign, distance_from_home_km,
    ]]
    proba = float(_MODEL.predict_proba(features)[0][1])
    threshold = float(_CARD.get("threshold", 0.5))
    return {
        "is_fraud": bool(proba >= threshold),
        "fraud_probability": round(proba, 4),
        "threshold": threshold,
        "model": f"{_CARD.get('name')}:{_CARD.get('version')}",
    }


@mcp.tool()
def list_models() -> list[dict]:
    """Lista os modelos disponíveis neste servidor (mini "model registry")."""
    if not _CARD:
        return []
    return [
        {
            "name": _CARD["name"],
            "version": _CARD["version"],
            "stage": _CARD["stage"],
            "task": _CARD["task"],
            "f1": _CARD["metrics"]["f1"],
        }
    ]


@mcp.tool()
def get_model_card(name: str = "fraud-detector") -> dict:
    """Retorna o model card completo (métricas, features, limitações) de um modelo."""
    if not _CARD or name != _CARD.get("name"):
        return {"error": f"Modelo '{name}' não encontrado."}
    return _CARD


# --------------------------------------------------------------------------- #
# RESOURCES — a aplicação injeta como contexto (read-only, sem efeito colateral).
# --------------------------------------------------------------------------- #
@mcp.resource("model://{name}/card")
def model_card_resource(name: str) -> str:
    """Model card como recurso legível por URI (ex.: model://fraud-detector/card)."""
    if not _CARD or name != _CARD.get("name"):
        return json.dumps({"error": f"Modelo '{name}' não encontrado."})
    return json.dumps(_CARD, indent=2, ensure_ascii=False)


@mcp.resource("dataset://schema")
def dataset_schema() -> str:
    """Schema das features de entrada esperadas pelo modelo."""
    schema = {
        "features": _CARD.get("features", []),
        "target": _CARD.get("target"),
        "description": "Ordem e nomes das features aceitas pela tool `predict`.",
    }
    return json.dumps(schema, indent=2, ensure_ascii=False)


# --------------------------------------------------------------------------- #
# PROMPTS — o usuário invoca (ex.: slash command). Orquestram tools + resources.
# --------------------------------------------------------------------------- #
@mcp.prompt()
def investigate_alert(
    amount: float, hour_of_day: int, distance_from_home_km: float
) -> str:
    """Template guiando o agente a investigar um alerta de transação suspeita."""
    return (
        "Você é um analista antifraude. Investigue a transação abaixo:\n"
        f"- valor: R$ {amount}\n"
        f"- hora: {hour_of_day}h\n"
        f"- distância do local usual: {distance_from_home_km} km\n\n"
        "1. Leia o recurso `model://fraud-detector/card` para entender o modelo.\n"
        "2. Chame a tool `predict` com os dados da transação.\n"
        "3. Explique a decisão citando a probabilidade e as limitações do modelo."
    )


if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    logger.info("Iniciando servidor MCP no transporte '%s'.", transport)
    mcp.run(transport=transport)
