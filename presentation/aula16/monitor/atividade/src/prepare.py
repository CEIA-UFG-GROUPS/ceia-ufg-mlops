"""Estágio `prepare` do pipeline: divide o dado bruto em treino e teste.

Lê os hiperparâmetros do ``params.yaml`` — NUNCA hardcoded no script.
É isso que permite ao DVC saber que uma mudança em ``prepare.test_size``
invalida este estágio (e os seguintes), enquanto uma mudança em
``train.n_estimators`` não o afeta.

Entradas  (deps): data/raw/data.csv
Saídas    (outs): data/prepared/train.csv, data/prepared/test.csv
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml
from sklearn.model_selection import train_test_split

RAW_PATH = Path("data/raw/data.csv")
OUT_DIR = Path("data/prepared")


def main() -> None:
    params = yaml.safe_load(Path("params.yaml").read_text())
    test_size = params["prepare"]["test_size"]
    seed = params["base"]["seed"]

    df = pd.read_csv(RAW_PATH)
    train_df, test_df = train_test_split(
        df,
        test_size=test_size,
        random_state=seed,
        stratify=df["target"],  # mantém a proporção de classes nos dois splits
    )

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(OUT_DIR / "train.csv", index=False)
    test_df.to_csv(OUT_DIR / "test.csv", index=False)
    print(f"prepare: {len(train_df)} treino / {len(test_df)} teste (test_size={test_size})")


if __name__ == "__main__":
    main()
