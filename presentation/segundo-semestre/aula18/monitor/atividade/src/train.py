"""Treino do modelo de fraude usando o feature store (join point-in-time).

O ponto-chave: os valores de features vêm do `get_historical_features`, que faz
um join **point-in-time correct** — para cada rótulo em seu timestamp, pega o
valor da feature *como era naquele momento*, evitando data leakage.
"""

from __future__ import annotations

import joblib
import pandas as pd
from feast import FeatureStore
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

from common import CUSTOMER_FEATURES, DATA_DIR, FEATURE_REPO, MODELS_DIR

FEATURE_COLS = [f.split(":")[1] for f in CUSTOMER_FEATURES]


def main() -> None:
    store = FeatureStore(repo_path=str(FEATURE_REPO))

    # entity_df = rótulos com timestamp. É o "esqueleto" do join point-in-time.
    entity_df = pd.read_parquet(DATA_DIR / "labels.parquet")

    training_df = store.get_historical_features(
        entity_df=entity_df,
        features=CUSTOMER_FEATURES,
    ).to_df()
    print(f"Training set (após join point-in-time): {training_df.shape}")

    X = training_df[FEATURE_COLS].fillna(0.0)
    y = training_df["is_fraud"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    model = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    model.fit(X_train, y_train)

    proba = model.predict_proba(X_test)[:, 1]
    print(f"F1={f1_score(y_test, (proba >= 0.5).astype(int)):.3f} | "
          f"ROC-AUC={roc_auc_score(y_test, proba):.3f}")

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": model, "features": FEATURE_COLS}, MODELS_DIR / "fraud_model.pkl")
    print(f"Modelo salvo em {MODELS_DIR / 'fraud_model.pkl'}")


if __name__ == "__main__":
    main()
