"""
Script 1: DAG de exemplo no Airflow — o mesmo pipeline de treinamento implementado
como Flow do Prefect em src/prefect_flow.py, usando a TaskFlow API do Airflow 2.x.

Ingestão -> Validação -> Feature Engineering -> Treino -> Avaliação -> Registro.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow.decorators import dag, task

from src.pipeline_logic import (
    avaliar_modelo,
    feature_engineering,
    ingerir_dados,
    registrar_modelo,
    treinar_modelo,
    validar_dados,
)

DEFAULT_ARGS = {
    "owner": "grupo-mlops-ceia-ufg",
    "retries": 2,
    "retry_delay": timedelta(seconds=10),
}


@dag(
    dag_id="pipeline_treinamento_deteccao_fraude",
    description="Pipeline de treinamento orquestrado (Aula 17 - Airflow)",
    schedule="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["aula17", "treinamento", "airflow"],
)
def pipeline_treinamento_fraude():

    @task
    def t_ingerir():
        return ingerir_dados()

    @task
    def t_validar(caminho_dataset: str):
        return validar_dados(caminho_dataset)

    @task
    def t_features(caminho_dataset: str):
        return feature_engineering(caminho_dataset)

    @task
    def t_treinar(caminho_features: str):
        return treinar_modelo(caminho_features)

    @task
    def t_avaliar(info_treino: dict):
        return avaliar_modelo(info_treino)

    @task
    def t_registrar(info_avaliacao: dict):
        return registrar_modelo(info_avaliacao)

    caminho_dataset = t_ingerir()
    caminho_validado = t_validar(caminho_dataset)
    caminho_features = t_features(caminho_validado)
    info_treino = t_treinar(caminho_features)
    info_avaliacao = t_avaliar(info_treino)
    t_registrar(info_avaliacao)


pipeline_treinamento_fraude()
