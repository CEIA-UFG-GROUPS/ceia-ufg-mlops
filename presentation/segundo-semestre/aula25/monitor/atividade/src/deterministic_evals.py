"""Avaliações determinísticas (sem juiz LLM)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from jsonschema import Draft202012Validator

from .common import POLICIES_DIR, citation_f1, load_json, load_jsonl, DATA_DIR


@dataclass
class DeterministicCaseResult:
    id: str
    exact_hit: bool
    must_include_hit: bool
    citation_f1: float
    schema_valid: bool
    answer: str
    citations: list[str]


def validate_schema(raw_text: str, schema: dict[str, Any] | None = None) -> bool:
    schema = schema or load_json(POLICIES_DIR / "output_schema.json")
    try:
        payload = __import__("json").loads(raw_text)
    except Exception:
        return False
    validator = Draft202012Validator(schema)
    return not any(validator.iter_errors(payload))


def evaluate_golden(
    answers: dict[str, dict[str, Any]],
    golden_path=None,
) -> dict[str, Any]:
    """answers: id -> {answer, citations, raw_text}"""
    golden = load_jsonl(golden_path or (DATA_DIR / "golden_eval.jsonl"))
    rows: list[DeterministicCaseResult] = []
    for case in golden:
        pred = answers[case["id"]]
        answer = pred["answer"]
        citations = pred.get("citations", [])
        expected = case["expected_answer"].strip().lower()
        exact = answer.strip().lower() == expected
        must = all(token.lower() in answer.lower() for token in case.get("must_include", []))
        f1 = citation_f1(citations, case.get("expected_citations", []))
        schema_ok = validate_schema(pred["raw_text"])
        rows.append(
            DeterministicCaseResult(
                id=case["id"],
                exact_hit=exact,
                must_include_hit=must,
                citation_f1=f1,
                schema_valid=schema_ok,
                answer=answer,
                citations=citations,
            )
        )

    n = len(rows) or 1
    return {
        "n": len(rows),
        "must_include_rate": sum(r.must_include_hit for r in rows) / n,
        "mean_citation_f1": sum(r.citation_f1 for r in rows) / n,
        "schema_validity": sum(r.schema_valid for r in rows) / n,
        "exact_match_rate": sum(r.exact_hit for r in rows) / n,
        "cases": [r.__dict__ for r in rows],
    }


def regex_refusal(text: str) -> bool:
    return bool(re.search(r"(?i)\b(não posso|bloqueado|recuso|política)\b", text))
