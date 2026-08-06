FROM python:3.10-slim

WORKDIR /app

# Instalar dependências de sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivo de dependências e instalar
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código-fonte da aplicação
COPY . /app

EXPOSE 8000 8080

CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
