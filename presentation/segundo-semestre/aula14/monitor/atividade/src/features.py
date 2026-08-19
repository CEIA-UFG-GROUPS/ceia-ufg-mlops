"""Transformações de feature — a *unidade* que os testes do pytest exercitam.

Funções puras, sem I/O e sem estado global: essa é a condição prática para que
um teste unitário de ML seja rápido, determinístico e capaz de apontar a linha
culpada. Tudo que precisa de arquivo fica em `run_gate.py`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .common import FEATURE_COLUMNS, TARGET_COLUMN

FAIXAS_ETARIAS = ("jovem", "adulto", "meia_idade", "senior")


def faixa_etaria(idade: int | float) -> str:
    """Discretiza idade em faixas. Fronteiras fechadas à esquerda.

    jovem [18,30) · adulto [30,45) · meia_idade [45,60) · senior [60,+)
    """
    if pd.isna(idade):
        raise ValueError("idade nula não pode ser discretizada")
    if idade < 18:
        raise ValueError(f"idade {idade} abaixo do mínimo contratual (18)")
    if idade < 30:
        return "jovem"
    if idade < 45:
        return "adulto"
    if idade < 60:
        return "meia_idade"
    return "senior"


def comprometimento_renda(divida_mensal: float, renda_mensal: float) -> float:
    """Fração da renda comprometida, saturada em [0, 1].

    Renda zero é o caso de borda clássico: dividir direto lança
    `ZeroDivisionError` em produção às 3h da manhã.
    """
    if renda_mensal <= 0:
        return 1.0
    return float(np.clip(divida_mensal / renda_mensal, 0.0, 1.0))


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Deriva features a partir das colunas contratuais.

    Idempotente: `build_features(build_features(df))` teria o mesmo resultado
    porque a função nunca sobrescreve a entrada nem depende de estado anterior.
    """
    out = df.copy()
    out["faixa_etaria"] = out["idade"].map(faixa_etaria)
    out["log_renda"] = np.log(out["renda_anual"])
    out["consultas_por_ponto_score"] = out["num_consultas_90d"] / out["score_credito"]
    return out


@dataclass(frozen=True)
class Scaler:
    """Padronização z-score com estatísticas explícitas.

    Guardar `mean_`/`std_` como dados (e não dentro de um objeto opaco) é o que
    permite ao teste de vazamento comparar os números com os do treino.
    """

    columns: tuple[str, ...]
    mean_: np.ndarray
    std_: np.ndarray

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        values = df[list(self.columns)].to_numpy(dtype=float)
        return (values - self.mean_) / self.std_


def fit_scaler(df: pd.DataFrame, columns: list[str] | None = None) -> Scaler:
    cols = tuple(columns or FEATURE_COLUMNS)
    values = df[list(cols)].to_numpy(dtype=float)
    std = values.std(axis=0, ddof=0)
    # Coluna constante zeraria o denominador.
    std = np.where(std == 0, 1.0, std)
    return Scaler(columns=cols, mean_=values.mean(axis=0), std_=std)


def prepare_dataset(
    train: pd.DataFrame,
    test: pd.DataFrame,
    *,
    leaky: bool = False,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, Scaler]:
    """Padroniza treino e teste.

    `leaky=True` reproduz o bug mais comum de pré-processamento em ML: ajustar
    o scaler sobre treino + teste juntos. A acurácia sobe um pouco, nenhum
    `assert` de schema reclama e o modelo em produção vê outra escala.
    O flag existe para o teste `test_prepare_dataset_detecta_vazamento`
    demonstrar a diferença — o caminho de produção usa `leaky=False`.
    """
    scaler_source = pd.concat([train, test], ignore_index=True) if leaky else train
    scaler = fit_scaler(scaler_source)

    x_train = scaler.transform(train)
    x_test = scaler.transform(test)
    y_train = train[TARGET_COLUMN].to_numpy(dtype=int)
    y_test = test[TARGET_COLUMN].to_numpy(dtype=int)
    return x_train, y_train, x_test, y_test, scaler


def split_por_id(
    df: pd.DataFrame, *, test_frac: float = 0.25, id_column: str = "id_cliente"
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split determinístico por hash do identificador.

    Determinístico por construção: o mesmo cliente cai sempre do mesmo lado,
    mesmo que a ordem das linhas mude ou que novas linhas cheguem — propriedade
    que `train_test_split(random_state=…)` não garante quando o dataset cresce.
    """
    if not 0.0 < test_frac < 1.0:
        raise ValueError("test_frac deve estar em (0, 1)")
    bucket = df[id_column].astype(np.int64) % 100
    limite = int(round(test_frac * 100))
    test = df[bucket < limite].reset_index(drop=True)
    train = df[bucket >= limite].reset_index(drop=True)
    return train, test
