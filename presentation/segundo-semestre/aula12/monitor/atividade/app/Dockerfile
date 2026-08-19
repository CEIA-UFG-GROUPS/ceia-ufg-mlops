# Imagem enxuta de propósito: a demo precisa de build rápido e `minikube image
# load` rápido. Em produção, pinne também o digest da base.
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

# A versão da APLICAÇÃO é assada na imagem — muda com rebuild e rolling update.
# A versão do MODELO vem do ConfigMap — muda sem rebuild. São eixos diferentes,
# e a demo mostra os dois separadamente (Ato 6 vs Ato 7).
ARG VER=v1
ENV APP_VERSION=$VER

# Usuário não-root: o mínimo de higiene que qualquer revisão de segurança pede.
RUN useradd --create-home --uid 10001 apponly
USER 10001

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
