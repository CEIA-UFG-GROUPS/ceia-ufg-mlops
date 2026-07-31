# =========================================================
# Dockerfile — Servidor MCP de MLOps (Aula 13)
# Imagem única reaproveitada pelos serviços mcp-server e agent
# =========================================================

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

# Treina o modelo em tempo de build -> a imagem já sai com os artefatos prontos.
RUN python src/train_model.py

ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=streamable-http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

EXPOSE 8000

CMD ["python", "src/mcp_server.py"]
