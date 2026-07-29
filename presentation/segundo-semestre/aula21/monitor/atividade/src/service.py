"""Serviço de inferência com BentoML + ONNX Runtime e adaptive batching.

Este é o "servidor de modelo" da prática. Três decisões de projeto
importam aqui (e são o conteúdo da aula):

1. **Runtime enxuto**: o serviço NÃO depende do PyTorch. Ele carrega o
   grafo ONNX quantizado com o ONNX Runtime — menos memória, menos
   dependências, inicialização mais rápida (pense no cold start!).

2. **Adaptive batching** (``batchable=True``): cada cliente envia UMA
   requisição individual, mas o BentoML segura as requisições por até
   ``max_latency_ms`` e as funde em um único batch antes de chamar o
   modelo. É o trade-off central da aula: um pouco de latência a mais
   em troca de muito mais throughput.

3. **Modelo carregado UMA vez** no ``__init__`` do serviço — nunca por
   requisição.

Servir localmente (após rodar ``python -m src.export_onnx``)::

    bentoml serve src.service:SentimentService --port 3000

Testar::

    curl -X POST http://localhost:3000/classify \
         -H 'Content-Type: application/json' \
         -d '{"texts": ["what a great class!"]}'

O diretório do modelo pode ser trocado via variável de ambiente
``MODEL_DIR`` (padrão: ``models/onnx-int8``).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import bentoml
import numpy as np
import onnxruntime as ort
from transformers import AutoTokenizer

MODEL_DIR = Path(os.environ.get("MODEL_DIR", "models/onnx-int8"))
MAX_SEQ_LEN = 128


def _softmax(logits: np.ndarray) -> np.ndarray:
    exp = np.exp(logits - logits.max(axis=-1, keepdims=True))
    return exp / exp.sum(axis=-1, keepdims=True)


@bentoml.service(
    resources={"cpu": "2"},
    traffic={"timeout": 30},
)
class SentimentService:
    """Classificação de sentimento servida sobre ONNX Runtime (INT8)."""

    def __init__(self) -> None:
        if not MODEL_DIR.exists():
            raise RuntimeError(
                f"Modelo não encontrado em '{MODEL_DIR}'. "
                "Rode antes: python -m src.export_onnx --output-dir models"
            )

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
        self.session = ort.InferenceSession(
            str(MODEL_DIR / "model.onnx"),
            providers=["CPUExecutionProvider"],
        )
        # Só alimentamos as entradas que o grafo realmente declara
        # (o tokenizer pode produzir campos extras, ex.: token_type_ids).
        self.input_names = {i.name for i in self.session.get_inputs()}

        # Mapeamento de índices para rótulos, vindo do config do modelo.
        config_path = MODEL_DIR / "config.json"
        id2label = {}
        if config_path.exists():
            config = json.loads(config_path.read_text())
            id2label = {int(k): v for k, v in config.get("id2label", {}).items()}
        self.id2label = id2label or {0: "NEGATIVE", 1: "POSITIVE"}

    @bentoml.api(
        batchable=True,       # <- funde requisições concorrentes em um batch
        max_batch_size=32,    # teto do batch dinâmico
        max_latency_ms=20,    # tempo máximo de espera para formar o batch
    )
    def classify(self, texts: list[str]) -> list[dict]:
        """Classifica uma lista de textos (o batch é montado pelo BentoML)."""
        encoded = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=MAX_SEQ_LEN,
            return_tensors="np",
        )
        feeds = {
            name: array.astype(np.int64)
            for name, array in encoded.items()
            if name in self.input_names
        }
        logits = self.session.run(None, feeds)[0]
        probs = _softmax(logits)

        predictions = probs.argmax(axis=-1)
        return [
            {
                "label": self.id2label[int(pred)],
                "score": round(float(probs[i, pred]), 4),
            }
            for i, pred in enumerate(predictions)
        ]
