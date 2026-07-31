"""Gera os dados-fonte (offline) que o feature store vai gerenciar.

Produz três Parquets em feature_repo/data/:
    - customer_stats.parquet : snapshots diários de features por cliente (histórico)
    - labels.parquet         : rótulos de fraude com timestamp (para treino point-in-time)
    - kb_docs.parquet        : base de conhecimento com embeddings (ângulo vector/RAG)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

from common import DATA_DIR, embed

SEED = 42
N_CUSTOMERS = 60
N_DAYS = 30


def gen_customer_stats(rng: np.random.Generator) -> pd.DataFrame:
    """Snapshots diários por cliente — é o histórico que permite o join point-in-time."""
    start = datetime.now(timezone.utc) - timedelta(days=N_DAYS)
    rows = []
    for cid in range(1, N_CUSTOMERS + 1):
        base_amount = rng.uniform(50, 500)
        age = int(rng.integers(5, 1500))
        for d in range(N_DAYS):
            ts = start + timedelta(days=d)
            rows.append(
                {
                    "customer_id": cid,
                    "avg_tx_amount_30d": round(base_amount * rng.uniform(0.7, 1.4), 2),
                    "num_tx_30d": int(rng.poisson(20)),
                    "account_age_days": age + d,
                    "chargeback_rate": round(float(rng.beta(1.2, 30)), 4),
                    "event_timestamp": ts,
                    "created": ts,
                }
            )
    return pd.DataFrame(rows)


def gen_labels(stats: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Rótulos de fraude amostrados no tempo — o entity_df do treino.

    A regra liga fraude a chargeback alto + valor alto + conta nova (mais ruído).
    """
    sample = stats.sample(n=400, random_state=SEED).copy()
    risk = (
        25.0 * sample["chargeback_rate"]                 # chargeback é o sinal mais forte
        + 2.0 * (sample["avg_tx_amount_30d"] > 350)      # ticket alto
        + 1.5 * (sample["account_age_days"] < 90)        # conta nova
    )
    risk = risk + rng.normal(0, 0.15, size=len(sample))
    prob = 1 / (1 + np.exp(-(risk - 1.6)))
    sample["is_fraud"] = (rng.uniform(0, 1, len(sample)) < prob).astype(int)
    return sample[["customer_id", "event_timestamp", "is_fraud"]].reset_index(drop=True)


def gen_kb_docs() -> pd.DataFrame:
    """Base de conhecimento de atendimento, com embeddings — para o retrieval vetorial."""
    docs = [
        "Como redefinir a senha do aplicativo do banco",
        "Passo a passo para solicitar estorno de uma compra",
        "Qual o limite do cartão e como aumentar",
        "Como bloquear o cartão em caso de perda ou roubo",
        "Contestar uma transação não reconhecida (possível fraude)",
        "Como ativar as notificações de transações no app",
        "Prazos e regras para chargeback de compras internacionais",
        "Atualizar dados cadastrais e endereço da conta",
    ]
    now = datetime.now(timezone.utc) - timedelta(days=1)
    return pd.DataFrame(
        {
            "doc_id": list(range(1, len(docs) + 1)),
            "content": docs,
            "embedding": [embed(d) for d in docs],
            "event_timestamp": [now] * len(docs),
        }
    )


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    stats = gen_customer_stats(rng)
    stats.to_parquet(DATA_DIR / "customer_stats.parquet", index=False)

    labels = gen_labels(stats, rng)
    labels.to_parquet(DATA_DIR / "labels.parquet", index=False)

    kb = gen_kb_docs()
    kb.to_parquet(DATA_DIR / "kb_docs.parquet", index=False)

    print(f"customer_stats: {stats.shape} -> {DATA_DIR / 'customer_stats.parquet'}")
    print(f"labels:         {labels.shape} (fraude={labels['is_fraud'].mean():.2%})")
    print(f"kb_docs:        {kb.shape} -> {DATA_DIR / 'kb_docs.parquet'}")


if __name__ == "__main__":
    main()
