# Define uma imagem base para iniciar o build
FROM python:3.12.4 

# Define uma pasta interna na imagem na qual vamos trabalhar a partir dessa linha
WORKDIR /app

# Copia o arquivo requirements.txt para dentro da pasta /app (onde estamos trabalhando) 
COPY requirements.txt . 

# Instala dependências do sistema
RUN pip install --no-cache-dir -r requirements.txt 

# Copia todo o restante dos arquivos da aplicação para a pasta /app
COPY . . 

# Define comando que será executado quando o container for iniciado
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 