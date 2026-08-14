#!/usr/bin/env bash
# Executa a mesma sequência de gates do workflow GitHub Actions, localmente.
# Uso:
#   bash scripts/run_ci_local.sh              # caminho feliz (exit 0)
#   CI_DEGRADE=1 bash scripts/run_ci_local.sh # força regressão (exit != 0)
#   MODE=main bash scripts/run_ci_local.sh    # inclui registro no registry local
#   PYTHON=/usr/bin/python3 bash scripts/run_ci_local.sh  # força interpretador

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE="${MODE:-pr}"
export PYTHONPATH="${ROOT}${PYTHONPATH:+:$PYTHONPATH}"

# Resolve o interpretador de forma portátil (Ubuntu/WSL muitas vezes não têm `python`).
# Ordem: PYTHON=… (env) → venv ativo → ./.venv/bin/python → python3 → python
resolve_python() {
  if [[ -n "${PYTHON:-}" ]]; then
    if [[ -x "${PYTHON}" ]] || command -v "${PYTHON}" >/dev/null 2>&1; then
      echo "${PYTHON}"
      return 0
    fi
    echo "❌ PYTHON='${PYTHON}' definido, mas não é executável." >&2
    return 1
  fi
  if [[ -n "${VIRTUAL_ENV:-}" && -x "${VIRTUAL_ENV}/bin/python" ]]; then
    echo "${VIRTUAL_ENV}/bin/python"
    return 0
  fi
  if [[ -x "${ROOT}/.venv/bin/python" ]]; then
    echo "${ROOT}/.venv/bin/python"
    return 0
  fi
  if command -v python3 >/dev/null 2>&1; then
    command -v python3
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    command -v python
    return 0
  fi
  echo "❌ Nenhum interpretador Python encontrado." >&2
  echo "   Crie o venv e instale deps, ou exporte PYTHON=/caminho/para/python3:" >&2
  echo "   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt" >&2
  echo "   bash scripts/run_ci_local.sh" >&2
  return 1
}

PYTHON="$(resolve_python)" || exit 127

echo "════════════════════════════════════════════════════════"
echo " CI/CD local — Aula 20 (MODE=${MODE}, CI_DEGRADE=${CI_DEGRADE:-0})"
echo " Interpretador: ${PYTHON}"
echo "════════════════════════════════════════════════════════"

"${PYTHON}" -m src.01_generate_data
"${PYTHON}" -m src.02_validate_data
"${PYTHON}" -m src.03_train_model

# O gate pode falhar: ainda assim geramos o comentário (como no Actions).
set +e
"${PYTHON}" -m src.04_evaluate_gate
GATE_RC=$?
set -e

"${PYTHON}" -m src.05_write_pr_comment
"${PYTHON}" -m src.06_security_scan

if [[ "$MODE" == "main" && "$GATE_RC" -eq 0 ]]; then
  "${PYTHON}" -m src.07_register_model
elif [[ "$MODE" == "main" && "$GATE_RC" -ne 0 ]]; then
  echo "⚠️  MODE=main mas gate falhou — registro pulado."
fi

echo "════════════════════════════════════════════════════════"
if [[ "$GATE_RC" -eq 0 ]]; then
  echo " ✅ Pipeline local OK (exit 0)"
else
  echo " ❌ Pipeline local FALHOU no gate de modelo (exit ${GATE_RC})"
fi
echo "════════════════════════════════════════════════════════"
exit "$GATE_RC"
