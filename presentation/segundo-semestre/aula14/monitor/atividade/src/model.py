"""Modelo mínimo e as checagens comportamentais que rodam depois do treino.

A distinção que a aula quer fixar:

* **teste pré-treino** roda sem modelo — valida dados e transformações;
* **teste pós-treino** roda sobre o modelo já ajustado — valida *comportamento*
  (expectativa direcional, invariância, funcionalidade mínima), não o número
  agregado de acurácia.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from .common import FEATURE_COLUMNS, RANDOM_SEED
from .features import Scaler, prepare_dataset


@dataclass(frozen=True)
class TrainedModel:
    clf: LogisticRegression
    scaler: Scaler
    roc_auc: float

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """Probabilidade de inadimplência para um DataFrame contratual."""
        return self.clf.predict_proba(self.scaler.transform(df))[:, 1]


def train_model(
    train: pd.DataFrame, test: pd.DataFrame, *, leaky: bool = False, seed: int = RANDOM_SEED
) -> TrainedModel:
    x_train, y_train, x_test, y_test, scaler = prepare_dataset(train, test, leaky=leaky)
    clf = LogisticRegression(max_iter=1000, random_state=seed)
    clf.fit(x_train, y_train)
    roc_auc = float(roc_auc_score(y_test, clf.predict_proba(x_test)[:, 1]))
    return TrainedModel(clf=clf, scaler=scaler, roc_auc=roc_auc)


def perfil_base(**overrides: float) -> pd.DataFrame:
    """Cliente sintético de referência para testes comportamentais."""
    base = {
        "idade": 40,
        "renda_anual": 70000.0,
        "score_credito": 600,
        "taxa_endividamento": 0.30,
        "num_consultas_90d": 3,
    }
    base.update(overrides)
    return pd.DataFrame([base])[FEATURE_COLUMNS]


def curva_por_score(
    model: TrainedModel, scores: list[int] | None = None
) -> list[tuple[int, float]]:
    """Risco previsto variando só `score_credito` — base do teste direcional."""
    valores = scores or [300, 450, 600, 750, 850]
    return [(s, float(model.predict_proba(perfil_base(score_credito=s))[0])) for s in valores]


def behavioral_checks(model: TrainedModel) -> dict[str, dict[str, object]]:
    """Executa as checagens pós-treino e devolve um resultado serializável.

    O mesmo código é consumido pelos testes (`tests/test_model_behavior.py`) e
    pelo gate (`src/run_gate.py`): a evidência do CI e a asserção do teste não
    podem divergir.
    """
    curva = curva_por_score(model)
    riscos = [p for _, p in curva]
    direcional_ok = all(a > b for a, b in zip(riscos, riscos[1:]))

    # Invariância: reordenar as linhas não pode mudar a predição de cada linha.
    lote = pd.concat(
        [perfil_base(score_credito=s) for s in (320, 500, 700, 840)], ignore_index=True
    )
    direto = model.predict_proba(lote)
    invertido = model.predict_proba(lote.iloc[::-1].reset_index(drop=True))[::-1]
    invariancia_ok = bool(np.allclose(direto, invertido, atol=1e-12))

    # Funcionalidade mínima: perfis inequívocos precisam sair na ordem certa.
    bom = float(
        model.predict_proba(
            perfil_base(score_credito=830, taxa_endividamento=0.05, num_consultas_90d=0)
        )[0]
    )
    ruim = float(
        model.predict_proba(
            perfil_base(score_credito=320, taxa_endividamento=0.90, num_consultas_90d=20)
        )[0]
    )
    mft_ok = ruim > bom

    return {
        "expectativa_direcional": {
            "pass": bool(direcional_ok),
            "detalhe": "risco decresce quando score_credito cresce",
            "curva": [{"score_credito": s, "risco": round(p, 4)} for s, p in curva],
        },
        "invariancia_ordem": {
            "pass": invariancia_ok,
            "detalhe": "predição por linha independe da ordem do lote",
        },
        "funcionalidade_minima": {
            "pass": bool(mft_ok),
            "detalhe": "perfil ruim tem risco maior que perfil bom",
            "risco_bom": round(bom, 4),
            "risco_ruim": round(ruim, 4),
        },
    }
