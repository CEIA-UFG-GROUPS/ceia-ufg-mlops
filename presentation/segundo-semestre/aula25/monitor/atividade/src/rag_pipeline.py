"""Pipeline RAG local mínimo (retrieval lexical + MockLLM)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .common import DATA_DIR, load_jsonl, tokenize
from .mock_llm import GenerationResult, MockLLM


@dataclass
class RAGResult:
    question: str
    contexts: list[dict[str, Any]]
    generation: GenerationResult


class LocalRAG:
    def __init__(self, kb_path=None, mode: str = "normal") -> None:
        self.docs = load_jsonl(kb_path or (DATA_DIR / "knowledge_base.jsonl"))
        self.llm = MockLLM(mode=mode)

    def retrieve(self, question: str, top_k: int = 2) -> list[dict[str, Any]]:
        q_tokens = tokenize(question)
        scored: list[tuple[float, dict[str, Any]]] = []
        for doc in self.docs:
            blob = f"{doc.get('title', '')} {doc.get('text', '')} {' '.join(doc.get('tags', []))}"
            score = len(q_tokens & tokenize(blob))
            # boost por tags literais
            for tag in doc.get("tags", []):
                if tag.lower() in question.lower():
                    score += 1.5
            scored.append((score, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [doc for score, doc in scored[:top_k] if score > 0] or [self.docs[0]]

    def answer(self, question: str, *, force_obey_injection: bool = False) -> RAGResult:
        contexts = self.retrieve(question)
        generation = self.llm.generate(
            question, contexts, force_obey_injection=force_obey_injection
        )
        return RAGResult(question=question, contexts=contexts, generation=generation)
