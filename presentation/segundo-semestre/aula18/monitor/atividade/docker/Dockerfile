# =========================================================
# Dockerfile — Feature Store com Feast (Aula 18)
# Python 3.10: exigido pela busca vetorial (sqlite_vec) do Feast 0.65.
# =========================================================

FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY feature_repo/ ./feature_repo/
COPY docker/run_demo.sh ./run_demo.sh
RUN chmod +x run_demo.sh

ENV PYTHONUNBUFFERED=1
# src/ no PYTHONPATH para os `from common import ...` funcionarem de qualquer cwd.
ENV PYTHONPATH=/app/src

EXPOSE 6566 8888

CMD ["./run_demo.sh"]
