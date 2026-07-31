"""Configurações e utilidades compartilhadas pelo lab."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

# Dimensão do embedding. DEVE bater com `vector_length` na FeatureView (definitions.py).
EMBED_DIM = 8

# Caminho do feature repo (onde vivem feature_store.yaml e definitions.py).
FEATURE_REPO = Path(__file__).resolve().parent.parent / "feature_repo"
DATA_DIR = FEATURE_REPO / "data"
MODELS_DIR = FEATURE_REPO.parent / "models"

# Features do modelo de fraude (na ordem esperada pelo treino/serving).
CUSTOMER_FEATURES = [
    "customer_stats:avg_tx_amount_30d",
    "customer_stats:num_tx_30d",
    "customer_stats:account_age_days",
    "customer_stats:chargeback_rate",
]

# Vetorizador determinístico (sem download de modelo pesado). Em produção, use
# um modelo de embeddings de verdade (ex.: sentence-transformers) — aqui o foco
# é o feature store armazenando/servindo embeddings, não a qualidade do encoder.
_vectorizer = HashingVectorizer(n_features=EMBED_DIM, alternate_sign=False, norm="l2")


def embed(text: str) -> list[float]:
    """Transforma um texto num embedding de dimensão EMBED_DIM (determinístico)."""
    vec = _vectorizer.transform([text]).toarray()[0]
    return [round(float(x), 6) for x in vec.astype(np.float32)]
