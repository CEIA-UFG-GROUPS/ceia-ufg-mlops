"""Fixtures compartilhadas pelos testes."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> Iterator[TestClient]:
    """Cliente HTTP de teste, chamando a API em processo (sem subir o uvicorn).

    O `with` é obrigatório: é ele que dispara o `lifespan` do FastAPI e, com
    isso, o treino do modelo no startup. Sem o `with`, `estado["modelo"]`
    continua `None` e todo `/predict` estoura.
    """
    with TestClient(app) as cliente:
        yield cliente
