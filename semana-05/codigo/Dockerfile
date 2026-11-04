# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# Dockerfile da API de sentimento — multi-stage.
#
# Estágio 1 (builder): instala as dependências dentro de um virtualenv.
# Estágio 2 (runtime): copia só o virtualenv pronto + o código da aplicação.
# Resultado: a imagem final não carrega pip cache, wheels nem lixo de build.
#
# Herdado da Semana 04 sem mudanças: é exatamente este Dockerfile que o
# workflow de CI builda e publica no Artifact Registry.
#
# Build local (a partir de semana-05/codigo/):
#   docker build -t sentimento-api:semana-05 .
# ---------------------------------------------------------------------------

# ----------------------------- estágio builder -----------------------------
FROM python:3.12-slim AS builder

WORKDIR /app

# Só o requirements primeiro: enquanto ele não mudar, o Docker reaproveita
# esta layer e pula a instalação inteira. Copiar o código antes disso é o
# erro clássico que invalida o cache a cada edição de .py.
COPY app/requirements.txt ./requirements.txt

RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
    && /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# ----------------------------- estágio runtime -----------------------------
FROM python:3.12-slim AS runtime

# PATH aponta para o venv: `python` e `uvicorn` já saem resolvidos.
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    LIMIAR_NEUTRO=0.60

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY app/ ./app/

# Rodar como root dentro do container é desnecessário — e evitável de graça.
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Healthcheck sem instalar curl: o Python do venv já está aqui.
HEALTHCHECK --interval=10s --timeout=3s --start-period=20s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
