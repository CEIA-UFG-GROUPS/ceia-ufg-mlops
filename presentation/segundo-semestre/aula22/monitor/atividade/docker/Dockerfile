# =========================================================
# Dockerfile para Atividade de Estratégias de Deploy (Aula 22)
# Imagem única reaproveitada pelos serviços champion, canary e gateway
# =========================================================

FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "src.model_service:app", "--host", "0.0.0.0", "--port", "8000"]
