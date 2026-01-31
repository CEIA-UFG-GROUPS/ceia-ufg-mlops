FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Comando apenas ilustrativo para o exercício
CMD ["python", "-c", "print('Ambiente de MLOps pronto!')"]