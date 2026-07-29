"""
Script 2: equivalente em Prefect do DAG do Airflow (dags/pipeline_treinamento_fraude.py).

Execute localmente, sem Docker, a partir da pasta `atividade/`:

    python -m src.prefect_flow

Compare a experiência de desenvolvimento com o DAG do Airflow: aqui o "grafo"
é apenas a ordem natural das chamadas de função Python.
"""

from prefect import flow, task

from src.pipeline_logic import (
    avaliar_modelo,
    feature_engineering,
    ingerir_dados,
    registrar_modelo,
    treinar_modelo,
    validar_dados,
)


@task(retries=2, retry_delay_seconds=5, name="ingerir_dados")
def t_ingerir():
    return ingerir_dados()


@task(retries=2, retry_delay_seconds=5, name="validar_dados")
def t_validar(caminho_dataset: str):
    return validar_dados(caminho_dataset)


@task(name="feature_engineering")
def t_features(caminho_dataset: str):
    return feature_engineering(caminho_dataset)


@task(name="treinar_modelo")
def t_treinar(caminho_features: str):
    return treinar_modelo(caminho_features)


@task(name="avaliar_modelo")
def t_avaliar(info_treino: dict):
    return avaliar_modelo(info_treino)


@task(name="registrar_modelo")
def t_registrar(info_avaliacao: dict):
    return registrar_modelo(info_avaliacao)


@flow(name="pipeline-treinamento-deteccao-fraude")
def pipeline_treinamento_fraude():
    caminho_dataset = t_ingerir()
    caminho_validado = t_validar(caminho_dataset)
    caminho_features = t_features(caminho_validado)
    info_treino = t_treinar(caminho_features)
    info_avaliacao = t_avaliar(info_treino)
    t_registrar(info_avaliacao)


if __name__ == "__main__":
    pipeline_treinamento_fraude()
