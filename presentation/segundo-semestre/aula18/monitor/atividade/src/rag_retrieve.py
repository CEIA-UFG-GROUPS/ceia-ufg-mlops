"""Ângulo 2026 — feature store como vector DB: busca semântica na base de conhecimento.

O feature store guarda embeddings como uma feature (`kb_docs:embedding`) e serve
busca por similaridade via `retrieve_online_documents_v2`. É o padrão de
recuperação por trás de um assistente/agente de atendimento (RAG).

⚠️  A busca vetorial no online store sqlite do Feast 0.65 exige **Python 3.10**
    (a extensão sqlite_vec só é carregada nessa versão). No Docker a imagem já é
    python:3.10-slim. Localmente, use Python 3.10 ou rode este passo no container.

Pré-requisitos: `feast apply` e `feast materialize-incremental`.
"""

from __future__ import annotations

import sys

from feast import FeatureStore

from common import FEATURE_REPO, embed

QUERY = "não reconheço uma cobrança no meu cartão, o que faço?"
TOP_K = 3


def main() -> None:
    store = FeatureStore(repo_path=str(FEATURE_REPO))
    query_vec = embed(QUERY)

    try:
        result = store.retrieve_online_documents_v2(
            features=["kb_docs:content", "kb_docs:embedding"],
            query=query_vec,
            top_k=TOP_K,
        ).to_dict()
    except Exception as exc:  # noqa: BLE001
        print(f"Falha na busca vetorial: {type(exc).__name__}: {exc}")
        print("Provável causa: sqlite_vec não carregado (use Python 3.10 ou o Docker).")
        sys.exit(1)

    print(f"Consulta: {QUERY!r}\nDocumentos mais relevantes (top {TOP_K}):")
    for i, content in enumerate(result["content"], 1):
        print(f"  {i}. {content}")


if __name__ == "__main__":
    main()
