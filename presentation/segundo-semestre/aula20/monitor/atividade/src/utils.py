"""Utilitários compartilhados do lab de CI/CD para ML (Aula 20)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
REPORT_DIR = BASE_DIR / "reports"
REGISTRY_DIR = BASE_DIR / "registry"
BASELINE_DIR = BASE_DIR / "baselines"

FEATURE_COLUMNS = [
    "idade",
    "renda_anual",
    "score_credito",
    "taxa_endividamento",
    "num_consultas_90d",
]
TARGET_COLUMN = "fraude"
REQUIRED_COLUMNS = FEATURE_COLUMNS + [TARGET_COLUMN]

# Limiares de regressão (candidato vs baseline). Ajuste via env GATE_THRESHOLD.
DEFAULT_GATE_THRESHOLD = float(os.environ.get("GATE_THRESHOLD", "0.02"))
PRIMARY_METRIC = "f1"


def ensure_dirs() -> None:
    for path in (DATA_DIR, MODEL_DIR, REPORT_DIR, REGISTRY_DIR, BASELINE_DIR):
        path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
