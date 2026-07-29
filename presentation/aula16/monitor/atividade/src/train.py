"""Estágio `train` do pipeline: treina o modelo e o serializa.

Entradas  (deps): data/prepared/train.csv
Parâmetros      : train.n_estimators, train.max_depth (params.yaml)
Saídas    (outs): models/model.pkl

O modelo serializado é um ``outs`` normal do DVC: entra no cache, vai para
o remote no ``dvc push`` e volta no tempo junto com o dado e o código no
``git checkout + dvc checkout`` — versionamento de MODELO de graça.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
import yaml
from sklearn.ensemble import RandomForestClassifier

TRAIN_PATH = Path("data/prepared/train.csv")
MODEL_PATH = Path("models/model.pkl")


def main() -> None:
    params = yaml.safe_load(Path("params.yaml").read_text())
    seed = params["base"]["seed"]
    train_params = params["train"]

    df = pd.read_csv(TRAIN_PATH)
    features = df.drop(columns=["target"])
    target = df["target"]

    model = RandomForestClassifier(
        n_estimators=train_params["n_estimators"],
        max_depth=train_params["max_depth"],
        random_state=seed,
        n_jobs=-1,
    )
    model.fit(features, target)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(
        f"train: RandomForest(n_estimators={train_params['n_estimators']}, "
        f"max_depth={train_params['max_depth']}) -> {MODEL_PATH}"
    )


if __name__ == "__main__":
    main()
