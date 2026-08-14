"""
03_train_model.py

Passo 3: Treina RandomForest (CPU) e emite metrics.json do candidato.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

from src.utils import (
    DATA_DIR,
    FEATURE_COLUMNS,
    MODEL_DIR,
    REPORT_DIR,
    TARGET_COLUMN,
    ensure_dirs,
    save_json,
)


def main() -> None:
    ensure_dirs()
    print("🚀 [Passo 3] Treinando modelo candidato (RandomForest)...")
    t0 = time.perf_counter()

    train_df = pd.read_csv(DATA_DIR / "train.csv")
    test_df = pd.read_csv(DATA_DIR / "test.csv")

    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[TARGET_COLUMN]
    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[TARGET_COLUMN]

    # Hiperparâmetros leves para caber em ~2 min no free tier
    n_estimators = int(os.environ.get("N_ESTIMATORS", "80"))
    max_depth = int(os.environ.get("MAX_DEPTH", "8"))

    model = RandomForestClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    preds = (proba >= 0.5).astype(int)

    metrics = {
        "accuracy": float(accuracy_score(y_test, preds)),
        "precision": float(precision_score(y_test, preds, zero_division=0)),
        "recall": float(recall_score(y_test, preds, zero_division=0)),
        "f1": float(f1_score(y_test, preds, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, proba)),
        "n_train": int(len(train_df)),
        "n_test": int(len(test_df)),
        "n_estimators": n_estimators,
        "max_depth": max_depth,
        "model_type": "RandomForestClassifier",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "degraded": os.environ.get("CI_DEGRADE", "0") == "1",
    }

    model_path = MODEL_DIR / "candidate.joblib"
    metrics_path = REPORT_DIR / "metrics.json"
    joblib.dump(model, model_path)
    save_json(metrics_path, metrics)

    elapsed = time.perf_counter() - t0
    print(f"✅ Modelo salvo em: {model_path}")
    print(f"✅ Métricas salvas em: {metrics_path}")
    print(
        "📊 "
        f"acc={metrics['accuracy']:.4f} | "
        f"f1={metrics['f1']:.4f} | "
        f"roc_auc={metrics['roc_auc']:.4f} "
        f"({elapsed:.1f}s)"
    )
    print("👉 Próximo: python -m src.04_evaluate_gate")


if __name__ == "__main__":
    main()
