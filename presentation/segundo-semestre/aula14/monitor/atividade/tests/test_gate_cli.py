"""Regressão crítica: o gate precisa QUEBRAR o CI quando reprova.

Relatório vermelho com `exit 0` é o antipadrão que esta aula ataca. Se este
teste sumir, o pipeline volta a mentir sem que ninguém perceba.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["GX_ANALYTICS_ENABLED"] = "false"
    env["DO_NOT_TRACK"] = "1"
    return subprocess.run(
        [sys.executable, "-m", *args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture(scope="module", autouse=True)
def _datasets():
    """Gera os dois CSVs uma vez para os testes de CLI.

    Usa o tamanho padrão (4000 linhas) de propósito: assim a suíte deixa em
    `data/` exatamente os arquivos que a demonstração da aula usa, sem
    surpresa de contagem de linhas entre `./run_tests.sh` e o gate manual.
    """
    for variant in ("clean", "corrupted"):
        done = _run("src.generate_data", "--variant", variant)
        assert done.returncode == 0, done.stdout + done.stderr


def test_gate_passa_com_dataset_limpo():
    done = _run("src.run_gate", "--dataset", "clean")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "[PASS]" in done.stdout


def test_gate_falha_e_retorna_exit_nao_zero_com_dataset_corrompido():
    done = _run("src.run_gate", "--dataset", "corrupted")
    assert done.returncode != 0, done.stdout + done.stderr
    assert "[FAIL]" in done.stdout


def test_validate_data_tambem_propaga_exit_code():
    assert _run("src.validate_data", "--dataset", "clean").returncode == 0
    assert _run("src.validate_data", "--dataset", "corrupted").returncode != 0


def test_gate_escreve_relatorio_auditavel():
    _run("src.run_gate", "--dataset", "corrupted")
    payload = json.loads((ROOT / "reports" / "gate_report_corrupted.json").read_text("utf-8"))
    assert payload["overall_pass"] is False
    assert payload["stages"]["contrato_de_dados"]["pass"] is False
    assert payload["data_validation"]["failures"], "relatório sem a causa da reprovação"
    # Sem dados válidos, não se reporta métrica de modelo como se fosse confiável.
    assert payload["model"] is None
