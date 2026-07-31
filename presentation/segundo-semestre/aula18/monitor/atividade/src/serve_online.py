"""Inferência online: busca as features FRESCAS no online store e prediz.

Mesma definição de feature usada no treino (get_historical_features) e aqui
(get_online_features) → é isso que elimina o training-serving skew: uma única
definição, servida nos dois mundos.

Pré-requisitos: `feast apply`, `train.py` e `feast materialize-incremental`.
"""

from __future__ import annotations

import joblib
from feast import FeatureStore

from common import CUSTOMER_FEATURES, FEATURE_REPO, MODELS_DIR

# Clientes a pontuar em tempo real (só a chave; as features vêm do online store).
ENTITY_ROWS = [{"customer_id": 3}, {"customer_id": 17}, {"customer_id": 42}]


def main() -> None:
    store = FeatureStore(repo_path=str(FEATURE_REPO))
    bundle = joblib.load(MODELS_DIR / "fraud_model.pkl")
    model, feature_cols = bundle["model"], bundle["features"]

    online = store.get_online_features(
        features=CUSTOMER_FEATURES,
        entity_rows=ENTITY_ROWS,
    ).to_dict()

    for i, row in enumerate(ENTITY_ROWS):
        x = [[online[c][i] for c in feature_cols]]
        proba = float(model.predict_proba(x)[0][1])
        print(
            f"customer_id={row['customer_id']:>3} | "
            f"features={ {c: online[c][i] for c in feature_cols} } | "
            f"fraud_probability={proba:.3f}"
        )


if __name__ == "__main__":
    main()
