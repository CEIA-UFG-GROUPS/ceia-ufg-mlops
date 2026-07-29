# =========================================================
# Dockerfile para Atividade de Pipelines de Treinamento (Aula 17)
# Imagem Airflow Standalone com dependências extras de ML
# =========================================================

FROM apache/airflow:2.9.3-python3.11

COPY requirements.txt /requirements.txt
RUN pip install --no-cache-dir -r /requirements.txt

COPY dags/ /opt/airflow/dags/
COPY src/ /opt/airflow/dags/src/
