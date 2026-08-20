"""Fixtures compartilhadas.

Fixtures de escopo `session` existem por um motivo prático: geração de dados e
treino são caros o bastante para dominar o tempo da suíte se repetidos a cada
teste. Teste unitário lento não é rodado — e teste não rodado não protege nada.
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.common import load_contract
from src.features import split_por_id
from src.generate_data import generate_clean
from src.model import train_model

N_ROWS = 800


@pytest.fixture(scope="session")
def contract() -> dict:
    return load_contract()


@pytest.fixture(scope="session")
def df_clean() -> pd.DataFrame:
    return generate_clean(n_rows=N_ROWS)


@pytest.fixture(scope="session")
def split(df_clean: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    return split_por_id(df_clean)


@pytest.fixture(scope="session")
def trained(split: tuple[pd.DataFrame, pd.DataFrame]):
    train, test = split
    return train_model(train, test)
