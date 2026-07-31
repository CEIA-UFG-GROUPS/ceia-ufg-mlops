"""Treina um modelo de detecção de fraude e gera o "model card".

Este script NÃO é o foco da aula — ele apenas produz os artefatos que o
servidor MCP vai expor (o `model.pkl` e o `model_card.json`). O modelo é
propositalmente pequeno: o assunto aqui é o **servidor MCP**, não o modelo.

Uso:
    python src/train_model.py

Gera em `models/`:
    - model.pkl        -> o modelo serializado (RandomForest)
    - model_card.json  -> metadados do modelo (métricas, features, versão)
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

# Diretório de saída dos artefatos (models/ ao lado de src/)
MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# Nomes das features — interpretáveis de propósito, para que um agente
# consiga "raciocinar" sobre elas ao chamar a tool `predict`.
FEATURE_NAMES = [
    "amount",                 # valor da transação (R$)
    "hour_of_day",            # hora do dia (0-23)
    "num_tx_last_hour",       # nº de transações na última hora
    "account_age_days",       # idade da conta (dias)
    "is_foreign",             # transação no exterior (0/1)
    "distance_from_home_km",  # distância do local usual (km)
]

SEED = 42


def generate_dataset(n_samples: int = 5000) -> tuple[np.ndarray, np.ndarray]:
    """Gera um dataset sintético de transações com um padrão de fraude simples.

    A regra é intencionalmente compreensível (valor alto + madrugada + conta
    nova + exterior/distância) mais um ruído — o bastante para o RandomForest
    aprender algo útil sem virar o tema da aula.
    """
    rng = np.random.default_rng(SEED)

    amount = rng.gamma(shape=2.0, scale=120.0, size=n_samples)
    hour_of_day = rng.integers(0, 24, size=n_samples)
    num_tx_last_hour = rng.poisson(lam=1.5, size=n_samples)
    account_age_days = rng.integers(1, 2000, size=n_samples)
    is_foreign = rng.binomial(1, 0.15, size=n_samples)
    distance_from_home_km = rng.exponential(scale=30.0, size=n_samples)

    # "Score de risco" latente -> probabilidade de fraude
    risk = (
        0.004 * amount
        + 0.9 * (hour_of_day < 5)
        + 0.35 * num_tx_last_hour
        + 0.9 * (account_age_days < 30)
        + 1.1 * is_foreign
        + 0.015 * distance_from_home_km
    )
    risk += rng.normal(0.0, 0.5, size=n_samples)  # ruído
    prob = 1.0 / (1.0 + np.exp(-(risk - 3.0)))
    y = (rng.uniform(0, 1, size=n_samples) < prob).astype(int)

    X = np.column_stack(
        [
            amount,
            hour_of_day,
            num_tx_last_hour,
            account_age_days,
            is_foreign,
            distance_from_home_km,
        ]
    )
    return X, y


def main() -> None:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    X, y = generate_dataset()
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SEED, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200, max_depth=8, random_state=SEED, n_jobs=-1
    )
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    preds = (proba >= 0.5).astype(int)
    metrics = {
        "f1": round(float(f1_score(y_test, preds)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, proba)), 4),
        "fraud_rate": round(float(y.mean()), 4),
    }

    joblib.dump(model, MODELS_DIR / "model.pkl")

    # O "model card" é o que dá CONTEXTO ao agente. Ele será exposto como
    # um Resource MCP (read-only) e por uma tool `get_model_card`.
    model_card = {
        "name": "fraud-detector",
        "version": "1.0.0",
        "stage": "production",
        "task": "binary-classification (fraude em transações)",
        "algorithm": "RandomForestClassifier",
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "features": FEATURE_NAMES,
        "target": "is_fraud (0 = legítima, 1 = fraude)",
        "metrics": metrics,
        "training_data": {
            "source": "sintético (train_model.py)",
            "n_samples": int(X.shape[0]),
            "seed": SEED,
        },
        "threshold": 0.5,
        "limitations": (
            "Modelo didático treinado em dados sintéticos. Não use em produção "
            "real. Sujeito a data drift e a viés do gerador sintético."
        ),
    }
    (MODELS_DIR / "model_card.json").write_text(
        json.dumps(model_card, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    print(f"Modelo salvo em {MODELS_DIR / 'model.pkl'}")
    print(f"Model card salvo em {MODELS_DIR / 'model_card.json'}")
    print(f"Métricas: {metrics}")


if __name__ == "__main__":
    main()
