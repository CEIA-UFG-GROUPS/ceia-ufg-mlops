"""
05_write_pr_comment.py

Passo 5: Gera reports/pr_comment.md com tabela markdown de model-diff.
Isto é o que o CML fazia com `cml comment create` — aqui, com tooling plain.
Sempre gera o arquivo (mesmo se o gate falhou), para o workflow postar no PR.
"""

from __future__ import annotations

import sys
from pathlib import Path

from src.utils import REPORT_DIR, ensure_dirs, load_json


def build_markdown(gate: dict, metrics: dict) -> str:
    status = "✅ APROVADO" if gate["passed"] else "❌ BLOQUEADO"
    rows = []
    for key in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
        base = gate["baseline"][key]
        cand = gate["candidate"][key]
        delta = gate["diffs"][key]
        sign = "+" if delta >= 0 else ""
        rows.append(f"| `{key}` | {base:.4f} | {cand:.4f} | {sign}{delta:.4f} |")

    table = "\n".join(rows)
    degrade_note = (
        "\n> ⚠️ Treino executado com `CI_DEGRADE=1` (rótulos corrompidos de propósito).\n"
        if metrics.get("degraded")
        else ""
    )

    return f"""## 📊 Model Diff Report — Aula 20 (CI/CD for ML)

**Status do quality gate:** {status}

{degrade_note}
| Métrica | Baseline | Candidato | Δ |
|---|---:|---:|---:|
{table}

- **Métrica primária:** `{gate["primary_metric"]}`
- **Queda observada:** `{gate["primary_drop"]:.4f}`
- **Limiar (`GATE_THRESHOLD`):** `{gate["threshold"]:.4f}`
- **Mensagem:** {gate["message"]}

---
<sub>Gerado automaticamente pelo pipeline CD4ML do lab (substituto pedagógico do antigo `cml comment create`).</sub>
"""


def main() -> None:
    ensure_dirs()
    print("🚀 [Passo 5] Gerando comentário markdown de model-diff para o PR...")

    gate_path = REPORT_DIR / "gate_result.json"
    metrics_path = REPORT_DIR / "metrics.json"
    out_path = REPORT_DIR / "pr_comment.md"

    if not gate_path.exists():
        print("❌ gate_result.json ausente. Execute: python -m src.04_evaluate_gate")
        sys.exit(1)
    if not metrics_path.exists():
        print("❌ metrics.json ausente.")
        sys.exit(1)

    gate = load_json(gate_path)
    metrics = load_json(metrics_path)
    md = build_markdown(gate, metrics)
    out_path.write_text(md, encoding="utf-8")

    print(f"✅ Comentário salvo em: {out_path}")
    print("--- preview ---")
    print(md)
    print("👉 Próximo: python -m src.06_security_scan")


if __name__ == "__main__":
    main()
