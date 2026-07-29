"""Estágio `evaluate` do pipeline: avalia o modelo no conjunto de teste.

Entradas  (deps): models/model.pkl, data/prepared/test.csv
Saídas          : eval/metrics.json  (metrics do DVC — comparável com
                  `dvc metrics show/diff`)
                  eval/predictions.csv (plots do DVC — matriz de confusão
                  com `dvc plots show`)

As duas saídas são declaradas com ``cache: false`` no dvc.yaml: são
pequenas e textuais, então versioná-las DIRETO no Git dá diffs legíveis
em code review ("este PR muda a accuracy de 0.91 para 0.94").
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

TEST_PATH = Path("data/prepared/test.csv")
MODEL_PATH = Path("models/model.pkl")
EVAL_DIR = Path("eval")


def main() -> None:
    df = pd.read_csv(TEST_PATH)
    features = df.drop(columns=["target"])
    target = df["target"]

    model = joblib.load(MODEL_PATH)
    predictions = model.predict(features)

    metrics = {
        "accuracy": round(float(accuracy_score(target, predictions)), 4),
        "precision": round(float(precision_score(target, predictions)), 4),
        "recall": round(float(recall_score(target, predictions)), 4),
        "f1": round(float(f1_score(target, predictions)), 4),
    }

    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    (EVAL_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")

    # Pares (real, previsto) para a matriz de confusão do `dvc plots`.
    pd.DataFrame({"actual": target, "predicted": predictions}).to_csv(
        EVAL_DIR / "predictions.csv", index=False
    )

    print(f"evaluate: {json.dumps(metrics)}")


if __name__ == "__main__":
    main()
