import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .common import activity_root


def knowledge_base_path() -> Path:
    return activity_root() / "data" / "knowledge_base.jsonl"


def load_documents() -> list[dict[str, str]]:
    path = knowledge_base_path()
    documents = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            documents.append(json.loads(line))
    return documents


def retrieve(query: str, top_k: int = 3) -> dict[str, object]:
    documents = load_documents()
    corpus = [document["text"] for document in documents]
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), sublinear_tf=True)
    matrix = vectorizer.fit_transform(corpus + [query])
    scores = cosine_similarity(matrix[-1], matrix[:-1]).ravel()
    order = np.argsort(-scores)[:top_k]
    hits = [
        {
            "id": documents[index]["id"],
            "title": documents[index]["title"],
            "source": documents[index]["source"],
            "score": float(scores[index]),
            "text": documents[index]["text"],
        }
        for index in order
    ]
    context = "\n\n".join(f"[{hit['source']}] {hit['text']}" for hit in hits)
    prompt = (
        "Você é um assistente técnico. Responda usando somente o contexto abaixo "
        "e cite as fontes entre colchetes.\n\n"
        f"Contexto:\n{context}\n\nPergunta: {query}\nResposta:"
    )
    return {"query": query, "top_k": top_k, "hits": hits, "prompt": prompt}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True)
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = retrieve(args.query, args.top_k)
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered)


if __name__ == "__main__":
    main()
