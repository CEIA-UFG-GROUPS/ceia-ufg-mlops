# =========================================================
# Dockerfile para Atividade de Model Registry (MLOps)
# Imagem multi-uso para MLflow Registry e Serviço FastAPI
# =========================================================

FROM python:3.10-slim

WORKDIR /app

# Instalar dependências de sistema necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código fonte e estrutura
COPY src/ ./src/

# Variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1
ENV MLFLOW_TRACKING_URI=http://mlflow-server:5000

# Porta exposta padrão
EXPOSE 8000 5000

CMD ["uvicorn", "src.service:app", "--host", "0.0.0.0", "--port", "8000"]
