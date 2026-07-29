# =============================================================================
# Build MULTI-STAGE — uma lição de serving em si:
#
#   Estágio 1 (exporter): precisa do PyTorch (~2 GB) para converter o modelo
#     para ONNX e quantizar para INT8. Nada disso é necessário em produção.
#
#   Estágio 2 (runtime): imagem final enxuta, só com ONNX Runtime + BentoML.
#     Copia apenas o artefato do modelo do estágio anterior. Imagem menor =
#     pull mais rápido = COLD START menor ao escalar réplicas.
#
# Build (a partir da pasta atividade/):
#   docker build -f docker/Dockerfile -t aula21-sentiment .
# =============================================================================

# ---------- Estágio 1: exportação e quantização do modelo -------------------
FROM python:3.11-slim AS exporter

WORKDIR /app

COPY requirements-export.txt .
# Wheels de CPU do PyTorch: suficientes para exportar e muito menores
# que as wheels padrão com CUDA.
RUN pip install --no-cache-dir -r requirements-export.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu

COPY src/ src/

# Baixa o modelo do HF Hub, exporta para ONNX e quantiza para INT8.
# O download acontece em BUILD time: a imagem final é auto-contida e
# o container sobe sem depender de rede/HF Hub (reprodutibilidade).
RUN python -m src.export_onnx --output-dir /app/models

# ---------- Estágio 2: runtime de serving (sem PyTorch) ---------------------
FROM python:3.11-slim

WORKDIR /app

COPY requirements-serve.txt .
RUN pip install --no-cache-dir -r requirements-serve.txt

COPY src/ src/
COPY --from=exporter /app/models /app/models

ENV MODEL_DIR=/app/models/onnx-int8

EXPOSE 3000

CMD ["bentoml", "serve", "src.service:SentimentService", "--host", "0.0.0.0", "--port", "3000"]
