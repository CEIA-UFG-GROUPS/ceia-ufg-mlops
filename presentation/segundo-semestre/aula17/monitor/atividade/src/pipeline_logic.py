"""
Lógica de negócio do pipeline de treinamento (Aula 17), compartilhada entre o
DAG do Airflow (dags/pipeline_treinamento_fraude.py) e o Flow do Prefect
(src/prefect_flow.py).

O objetivo didático é mostrar que o orquestrador é apenas a "cola" que agenda,
executa e recupera falhas de tarefas — a lógica de negócio em si não deveria
depender de qual ferramenta de orquestração está por trás.
"""

import json
import os
import pickle
import random
from datetime import datetime, timezone

import pandas as pd
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import train_test_split

DATA_DIR = os.environ.get("PIPELINE_DATA_DIR", "data")
MODELS_DIR = os.environ.get("PIPELINE_MODELS_DIR", "models")
F1_QUALITY_GATE = 0.85
N_FEATURES = 10


def ingerir_dados() -> str:
    """Simula a extração de um lote de transações a partir de um Data Lake."""
    os.makedirs(DATA_DIR, exist_ok=True)

    X, y = make_classification(
        n_samples=2000,
        n_features=N_FEATURES,
        n_informative=6,
        weights=[0.9, 0.1],
        random_state=42,
    )
    df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(N_FEATURES)])
    df["fraude"] = y

    caminho = os.path.join(DATA_DIR, "transacoes_raw.csv")
    df.to_csv(caminho, index=False)
    print(f"[Ingestão] {len(df)} transações extraídas e salvas em {caminho}")
    return caminho


def validar_dados(caminho_dataset: str) -> str:
    """Valida schema e qualidade mínima dos dados antes de seguir para feature engineering."""
    df = pd.read_csv(caminho_dataset)

    colunas_esperadas = {f"feature_{i}" for i in range(N_FEATURES)} | {"fraude"}
    if not colunas_esperadas.issubset(df.columns):
        raise ValueError("Schema inválido: colunas esperadas ausentes no dataset.")

    if df.isnull().sum().sum() > 0:
        raise ValueError("Dados inválidos: valores nulos encontrados no dataset.")

    # Simula a instabilidade transitória de um serviço externo de validação
    # (ex.: Great Expectations consultando um endpoint remoto), para ilustrar
    # o retry automático do orquestrador. Ative com SIMULAR_FALHA_TRANSITORIA=validacao.
    if os.environ.get("SIMULAR_FALHA_TRANSITORIA") == "validacao" and random.random() < 0.5:
        raise ConnectionError("Falha transitória simulada no serviço de validação externo.")

    print(f"[Validação] Dataset com {len(df)} linhas aprovado no schema e na checagem de nulos.")
    return caminho_dataset


def feature_engineering(caminho_dataset: str) -> str:
    """Normaliza as features numéricas e persiste o dataset pronto para treino."""
    df = pd.read_csv(caminho_dataset)
    feature_cols = [c for c in df.columns if c.startswith("feature_")]

    df[feature_cols] = (df[feature_cols] - df[feature_cols].mean()) / df[feature_cols].std()

    caminho = os.path.join(DATA_DIR, "transacoes_features.csv")
    df.to_csv(caminho, index=False)
    print(f"[Feature Engineering] Features normalizadas e salvas em {caminho}")
    return caminho


def treinar_modelo(caminho_features: str) -> dict:
    """Treina um classificador simples e retorna metadados serializáveis (XCom/Prefect)."""
    df = pd.read_csv(caminho_features)
    feature_cols = [c for c in df.columns if c.startswith("feature_")]
    X, y = df[feature_cols], df["fraude"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.3, random_state=42, stratify=y
    )

    modelo = RandomForestClassifier(n_estimators=150, max_depth=6, random_state=42)
    modelo.fit(X_train, y_train)

    os.makedirs(MODELS_DIR, exist_ok=True)
    versao = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    caminho_modelo = os.path.join(MODELS_DIR, f"modelo_fraude_{versao}.pkl")

    with open(caminho_modelo, "wb") as f:
        pickle.dump(modelo, f)

    # Persiste o split de teste para a etapa de avaliação (poderia ser um XCom
    # grande demais para o Airflow, por isso trafegamos apenas o caminho do arquivo)
    caminho_teste = os.path.join(DATA_DIR, "teste.csv")
    X_test.assign(fraude=y_test).to_csv(caminho_teste, index=False)

    print(f"[Treino] Modelo treinado e salvo em {caminho_modelo} (versão {versao})")
    return {"versao": versao, "caminho_modelo": caminho_modelo, "caminho_teste": caminho_teste}


def avaliar_modelo(info_treino: dict) -> dict:
    """Avalia o modelo contra o Quality Gate mínimo de F1-Score."""
    with open(info_treino["caminho_modelo"], "rb") as f:
        modelo = pickle.load(f)

    df_teste = pd.read_csv(info_treino["caminho_teste"])
    feature_cols = [c for c in df_teste.columns if c.startswith("feature_")]
    X_test, y_test = df_teste[feature_cols], df_teste["fraude"]

    preds = modelo.predict(X_test)
    acc = accuracy_score(y_test, preds)
    f1 = f1_score(y_test, preds, average="macro")

    print(f"[Avaliação] versão={info_treino['versao']} accuracy={acc:.4f} f1_macro={f1:.4f}")

    # Ative SIMULAR_FALHA_TRANSITORIA=avaliacao para forçar uma reprovação no Quality Gate
    # e observar o comportamento de retry/alerta do orquestrador.
    if os.environ.get("SIMULAR_FALHA_TRANSITORIA") == "avaliacao":
        f1 = 0.0

    if f1 < F1_QUALITY_GATE:
        raise ValueError(
            f"Quality Gate reprovado: F1-Score {f1:.4f} abaixo do mínimo exigido ({F1_QUALITY_GATE})."
        )

    return {
        "versao": info_treino["versao"],
        "caminho_modelo": info_treino["caminho_modelo"],
        "accuracy": acc,
        "f1_score": f1,
    }


def registrar_modelo(info_avaliacao: dict) -> dict:
    """Simula o registro do modelo aprovado em um Model Registry (ver Aula 19)."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    caminho_metadata = os.path.join(MODELS_DIR, "registry.json")

    registro = {
        "nome": "ModeloDeteccaoFraude",
        "versao": info_avaliacao["versao"],
        "caminho_modelo": info_avaliacao["caminho_modelo"],
        "accuracy": info_avaliacao["accuracy"],
        "f1_score": info_avaliacao["f1_score"],
        "alias": "challenger",
        "registrado_em": datetime.now(timezone.utc).isoformat(),
    }

    historico = []
    if os.path.exists(caminho_metadata):
        with open(caminho_metadata, "r") as f:
            historico = json.load(f)
    historico.append(registro)

    with open(caminho_metadata, "w") as f:
        json.dump(historico, f, indent=2)

    print(
        f"[Registro] Versão {registro['versao']} registrada com alias '@challenger' "
        f"em {caminho_metadata}"
    )
    print("           (Em um cenário real, esta etapa chamaria o Model Registry da Aula 19 via MLflow.)")
    return registro
