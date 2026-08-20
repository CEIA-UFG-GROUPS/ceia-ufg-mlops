"""Testes pós-treino: comportamento, não média.

Um modelo pode ter ROC AUC aceitável e ainda responder que aumentar o
`score_credito` aumenta o risco de inadimplência. Acurácia agregada não vê
isso; teste comportamental vê.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from src.model import behavioral_checks, curva_por_score, perfil_base, train_model


def test_desempenho_minimo(trained, contract):
    limiar = contract["gate"]["min_roc_auc"]
    assert trained.roc_auc >= limiar, f"roc_auc={trained.roc_auc:.4f} < {limiar}"


def test_expectativa_direcional_do_score(trained):
    """Score maior ⇒ risco menor, monotonicamente."""
    riscos = [p for _, p in curva_por_score(trained)]
    assert all(a > b for a, b in zip(riscos, riscos[1:])), riscos


def test_expectativa_direcional_do_endividamento(trained):
    baixo = trained.predict_proba(perfil_base(taxa_endividamento=0.05))[0]
    alto = trained.predict_proba(perfil_base(taxa_endividamento=0.95))[0]
    assert alto > baixo


def test_invariancia_a_ordem_do_lote(trained):
    """Predição de uma linha não pode depender das vizinhas no lote."""
    lote = pd.concat(
        [perfil_base(score_credito=s) for s in (400, 700, 820)], ignore_index=True
    )
    direto = trained.predict_proba(lote)
    invertido = trained.predict_proba(lote.iloc[::-1].reset_index(drop=True))[::-1]
    np.testing.assert_allclose(direto, invertido, atol=1e-12)


def test_funcionalidade_minima(trained):
    """Casos que qualquer humano da área classificaria sem hesitar."""
    bom = trained.predict_proba(
        perfil_base(score_credito=830, taxa_endividamento=0.05, num_consultas_90d=0)
    )[0]
    ruim = trained.predict_proba(
        perfil_base(score_credito=320, taxa_endividamento=0.90, num_consultas_90d=20)
    )[0]
    assert ruim > bom
    assert 0.0 <= bom <= 1.0 and 0.0 <= ruim <= 1.0


def test_treino_e_reprodutivel(split):
    """Mesma semente, mesmos dados ⇒ mesmas predições, bit a bit."""
    train, test = split
    a = train_model(train, test, seed=42)
    b = train_model(train, test, seed=42)
    amostra = perfil_base(score_credito=555)
    np.testing.assert_array_equal(a.predict_proba(amostra), b.predict_proba(amostra))
    assert a.roc_auc == pytest.approx(b.roc_auc, abs=1e-12)


def test_behavioral_checks_expoe_evidencia_para_o_gate(trained):
    """O gate e o teste consomem a mesma função — evidência não pode divergir."""
    checks = behavioral_checks(trained)
    assert set(checks) == {
        "expectativa_direcional",
        "invariancia_ordem",
        "funcionalidade_minima",
    }
    assert all(c["pass"] for c in checks.values())
    assert len(checks["expectativa_direcional"]["curva"]) == 5
