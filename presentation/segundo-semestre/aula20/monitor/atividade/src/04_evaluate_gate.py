"""
04_evaluate_gate.py

Passo 4: Compara métricas do candidato com a baseline e falha (exit != 0)
se houver regressão além do limiar configurável (GATE_THRESHOLD).
"""

from __future__ import annotations

import os
import sys
from typing import Any

from src.utils import (
    BASELINE_DIR,
    DEFAULT_GATE_THRESHOLD,
    PRIMARY_METRIC,
    REPORT_DIR,
    ensure_dirs,
    load_json,
    save_json,
)


def compare_metrics(
    candidate: dict[str, Any],
    baseline: dict[str, Any],
    threshold: float,
    primary: str = PRIMARY_METRIC,
) -> dict[str, Any]:
    keys = ["accuracy", "precision", "recall", "f1", "roc_auc"]
    diffs: dict[str, float] = {}
    for key in keys:
        diffs[key] = float(candidate[key]) - float(baseline[key])

    primary_drop = -diffs[primary]  # positivo = piorou
    passed = primary_drop <= threshold

    return {
        "passed": passed,
        "primary_metric": primary,
        "threshold": threshold,
        "primary_drop": primary_drop,
        "candidate": {k: candidate[k] for k in keys},
        "baseline": {k: baseline[k] for k in keys},
        "diffs": diffs,
        "message": (
            f"OK: Δ{primary}={diffs[primary]:+.4f} (queda máx. permitida={threshold:.4f})"
            if passed
            else f"REGRESSÃO: queda de {primary}={primary_drop:.4f} > limiar {threshold:.4f}"
        ),
    }


def main() -> None:
    ensure_dirs()
    print("🚀 [Passo 4] Avaliando quality gate (candidato vs baseline)...")

    metrics_path = REPORT_DIR / "metrics.json"
    baseline_path = BASELINE_DIR / "baseline_metrics.json"
    result_path = REPORT_DIR / "gate_result.json"

    if not metrics_path.exists():
        print("❌ metrics.json ausente. Execute: python -m src.03_train_model")
        sys.exit(1)
    if not baseline_path.exists():
        print(f"❌ Baseline ausente em {baseline_path}")
        sys.exit(1)

    threshold = float(os.environ.get("GATE_THRESHOLD", str(DEFAULT_GATE_THRESHOLD)))
    candidate = load_json(metrics_path)
    baseline = load_json(baseline_path)
    result = compare_metrics(candidate, baseline, threshold=threshold)
    save_json(result_path, result)

    print(f"📌 Métrica primária: {result['primary_metric']}")
    print(f"📌 Limiar de regressão: {threshold:.4f}")
    for key, delta in result["diffs"].items():
        sign = "+" if delta >= 0 else ""
        print(
            f"   {key:10s}  baseline={result['baseline'][key]:.4f}  "
            f"candidato={result['candidate'][key]:.4f}  Δ={sign}{delta:.4f}"
        )

    if result["passed"]:
        print(f"✅ Gate de modelo OK — {result['message']}")
        print("👉 Próximo: python -m src.05_write_pr_comment")
        sys.exit(0)

    print(f"❌ Gate de modelo FALHOU — {result['message']}")
    print("👉 O comentário de PR (model-diff) ainda será gerado no passo 5.")
    # Exit 1 para bloquear merge / falhar o check required
    sys.exit(1)


if __name__ == "__main__":
    main()
