"""Utilitários compartilhados da atividade da Aula 14."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_DIR = ROOT / "contracts"
DATA_DIR = ROOT / "data"
REPORTS_DIR = ROOT / "reports"

CONTRACT_PATH = CONTRACTS_DIR / "credito_v1.yaml"

FEATURE_COLUMNS = [
    "idade",
    "renda_anual",
    "score_credito",
    "taxa_endividamento",
    "num_consultas_90d",
]
TARGET_COLUMN = "inadimplente"
ID_COLUMN = "id_cliente"

RANDOM_SEED = 42


def ensure_offline_env() -> None:
    """Desliga telemetria e barra de progresso do Great Expectations.

    O lab roda offline e em CI: nada deve tentar rede nem poluir o stdout que
    o gate imprime.
    """
    os.environ.setdefault("GX_ANALYTICS_ENABLED", "false")
    os.environ.setdefault("DO_NOT_TRACK", "1")


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"YAML inválido em {path}")
    return data


def load_contract(path: Path | None = None) -> dict[str, Any]:
    """Carrega o contrato de dados versionado."""
    contract = load_yaml(path or CONTRACT_PATH)
    for key in ("name", "version", "table", "columns"):
        if key not in contract:
            raise ValueError(f"Contrato sem a chave obrigatória '{key}'")
    return contract


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2, default=str)
        fh.write("\n")
