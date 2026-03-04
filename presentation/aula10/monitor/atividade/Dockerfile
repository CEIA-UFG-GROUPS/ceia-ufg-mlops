FROM python:3.10-slim

WORKDIR /app

# 1. Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copiar código fonte
COPY . .

# 3. Treinar o modelo durante o build (Simulação de pipeline robusto)
# Em um cenário real, o modelo viria de um Model Registry ou Artifact Store.
# Aqui, garantimos que a imagem tenha um modelo pronto para servir.
RUN python src/train.py

# 4. Expor a porta da API
EXPOSE 8000

# 5. Comando de inicialização
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]