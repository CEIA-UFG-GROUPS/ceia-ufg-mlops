#!/usr/bin/env bash
# Roda o ciclo completo do feature store, ponta a ponta, dentro do container.
set -euo pipefail

echo "==> 1/5  Gerando dados-fonte (offline)"
python src/generate_data.py

echo "==> 2/5  feast apply (registra features + provisiona online store)"
(cd feature_repo && feast apply)

echo "==> 3/5  Treino com join point-in-time (get_historical_features)"
python src/train.py

echo "==> 4/5  Materialize (offline -> online store)"
CT="$(date -u +%Y-%m-%dT%H:%M:%S)"
(cd feature_repo && feast materialize-incremental "$CT")

echo "==> 5/5  Serving online + busca vetorial (RAG)"
python src/serve_online.py
python src/rag_retrieve.py

echo "==> Concluído. Feature server opcional: 'feast serve' (porta 6566)."
