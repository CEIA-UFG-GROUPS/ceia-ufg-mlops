"""Definições do feature store (o que o `feast apply` registra no registry).

Contém as três peças centrais de um feature store:
    - Entity        : a chave de negócio (customer, doc)
    - Data source   : de onde vêm os valores (Parquet offline)
    - Feature View  : o "contrato" de um grupo de features servidas online/offline
    - Feature Service: um pacote de features versionado, consumido por um modelo
"""

from datetime import timedelta
from pathlib import Path

from feast import Entity, FeatureService, FeatureView, Field, FileSource
from feast.types import Array, Float32, Int64, String

# Dimensão do embedding — DEVE bater com common.EMBED_DIM (src/common.py).
EMBED_DIM = 8

DATA = Path(__file__).resolve().parent / "data"

# --------------------------------------------------------------------------- #
# Entities — a chave primária pela qual as features são buscadas.
# --------------------------------------------------------------------------- #
customer = Entity(name="customer", join_keys=["customer_id"])
doc = Entity(name="doc", join_keys=["doc_id"])

# --------------------------------------------------------------------------- #
# Data sources (offline) — os Parquets gerados por generate_data.py.
# --------------------------------------------------------------------------- #
customer_source = FileSource(
    name="customer_stats_source",
    path=str(DATA / "customer_stats.parquet"),
    timestamp_field="event_timestamp",
    created_timestamp_column="created",
)
kb_source = FileSource(
    name="kb_docs_source",
    path=str(DATA / "kb_docs.parquet"),
    timestamp_field="event_timestamp",
)

# --------------------------------------------------------------------------- #
# Feature Views — o esquema das features, servidas tanto offline quanto online.
# --------------------------------------------------------------------------- #
customer_stats_fv = FeatureView(
    name="customer_stats",
    entities=[customer],
    ttl=timedelta(days=90),
    schema=[
        Field(name="avg_tx_amount_30d", dtype=Float32),
        Field(name="num_tx_30d", dtype=Int64),
        Field(name="account_age_days", dtype=Int64),
        Field(name="chargeback_rate", dtype=Float32),
    ],
    online=True,
    source=customer_source,
    tags={"team": "antifraude"},
)

# Ângulo 2026: o feature store também guarda EMBEDDINGS e faz busca vetorial —
# a convergência feature store + vector DB para casos real-time/RAG.
kb_docs_fv = FeatureView(
    name="kb_docs",
    entities=[doc],
    ttl=timedelta(days=3650),
    schema=[
        Field(name="content", dtype=String),
        Field(
            name="embedding",
            dtype=Array(Float32),
            vector_index=True,          # indexa para busca por similaridade
            vector_length=EMBED_DIM,
            vector_search_metric="L2",
        ),
    ],
    online=True,
    source=kb_source,
    tags={"team": "atendimento"},
)

# --------------------------------------------------------------------------- #
# Feature Service — o pacote versionado que um modelo consome (v1).
# --------------------------------------------------------------------------- #
fraud_model_v1 = FeatureService(name="fraud_model_v1", features=[customer_stats_fv])
