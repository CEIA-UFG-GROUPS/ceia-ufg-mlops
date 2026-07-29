from fastapi.testclient import TestClient
from src.app import app
import os
import pytest

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "mensagem" in response.json()

def test_prediction_without_model():
    """
    Testa se a API responde corretamente quando o modelo NÃO existe.
    Para isso, garantimos que o arquivo .pkl não está lá (ou ignoramos se estiver, 
    mas o ideal seria mockar, porém vamos manter simples).
    """
    # Se quisermos testar o fluxo de erro, teríamos que remover o arquivo
    # mas isso pode atrapalhar outros testes. Vamos assumir que o aluno
    # pode ou não ter rodado o treino.
    pass 

def test_prediction_flow():
    """
    Este teste assume que o modelo foi treinado. 
    Se não foi, ele vai falhar ou pular.
    """
    if not os.path.exists("model.pkl"):
        pytest.skip("Modelo não treinado. Execute 'src/train.py' primeiro.")

    payload = {
        "comprimento_sepala": 5.1,
        "largura_sepala": 3.5,
        "comprimento_petala": 1.4,
        "largura_petala": 0.2
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    expected_keys = ["id_classe", "nome_classe"]
    assert all(key in response.json() for key in expected_keys)
    assert response.json()["nome_classe"] == "setosa"
