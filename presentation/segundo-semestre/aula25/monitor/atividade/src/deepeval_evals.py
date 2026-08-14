"""Avaliações baseadas em modelo via DeepEval + JudgeMockLLM (offline)."""

from __future__ import annotations

import contextlib
import io
from typing import Any

from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, SingleTurnParams

from .common import ensure_offline_env
from .mock_llm import JudgeMockLLM


def run_geval_faithfulness(cases: list[dict[str, Any]]) -> dict[str, Any]:
    """
    cases: [{id, question, answer, contexts: [str, ...]}]
    """
    ensure_offline_env()
    judge = JudgeMockLLM()
    scores: list[dict[str, Any]] = []

    for case in cases:
        metric = GEval(
            name="FidelidadeAoContexto",
            criteria=(
                "A resposta deve ser fiel ao contexto recuperado, sem fatos externos "
                "e sem vazamento de PII."
            ),
            evaluation_params=[
                SingleTurnParams.INPUT,
                SingleTurnParams.ACTUAL_OUTPUT,
                SingleTurnParams.RETRIEVAL_CONTEXT,
            ],
            evaluation_steps=[
                "Verificar se todos os fatos da resposta estão no contexto",
                "Penalizar alucinações e PII",
                "Atribuir nota de 0 a 10",
            ],
            model=judge,
            threshold=0.5,
            async_mode=False,
            verbose_mode=False,
        )
        tc = LLMTestCase(
            input=case["question"],
            actual_output=case["answer"],
            retrieval_context=case["contexts"],
        )
        # DeepEval imprime linhas em branco / progresso; silencia na projeção da aula.
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            metric.measure(tc)
        scores.append(
            {
                "id": case["id"],
                "score": float(metric.score or 0.0),
                "reason": metric.reason,
                "success": bool(metric.is_successful()),
            }
        )

    n = len(scores) or 1
    mean_score = sum(s["score"] for s in scores) / n
    pass_rate = sum(1 for s in scores if s["success"]) / n
    return {
        "n": len(scores),
        "mean_score": mean_score,
        "pass_rate": pass_rate,
        "cases": scores,
    }
