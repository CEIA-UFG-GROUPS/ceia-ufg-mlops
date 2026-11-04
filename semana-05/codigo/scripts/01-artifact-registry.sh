#!/usr/bin/env bash
# =============================================================================
# 01 — Criar o repositório no Artifact Registry e publicar a imagem na mão.
#
# Rode UMA VEZ, antes de ativar o CI. Serve para separar os problemas:
# se o push manual funciona, o que sobra de erro no Actions é autenticação.
#
# Uso (a partir de semana-05/codigo/):
#   bash scripts/01-artifact-registry.sh
# =============================================================================
set -euo pipefail

# --- Ajuste estas variáveis ---------------------------------------------------
PROJECT_ID="SEU-PROJECT-ID"      # gcloud projects list
REGION="us-central1"
REPOSITORY="mlops-estudos"
IMAGE_NAME="api-sentimento"
# ------------------------------------------------------------------------------

REGISTRY_HOST="${REGION}-docker.pkg.dev"
IMAGE="${REGISTRY_HOST}/${PROJECT_ID}/${REPOSITORY}/${IMAGE_NAME}"

echo "==> Projeto ativo: ${PROJECT_ID}"
gcloud config set project "${PROJECT_ID}"

echo "==> Habilitando a API do Artifact Registry (idempotente)"
gcloud services enable artifactregistry.googleapis.com

echo "==> Criando o repositório Docker '${REPOSITORY}' em ${REGION}"
# Se já existir, o gcloud devolve ALREADY_EXISTS — por isso o `|| true`.
gcloud artifacts repositories create "${REPOSITORY}" \
    --repository-format=docker \
    --location="${REGION}" \
    --description="Imagens do grupo de estudos MLOps" || true

echo "==> Repositórios existentes:"
gcloud artifacts repositories list --location="${REGION}"

echo "==> Autorizando o Docker local a falar com ${REGISTRY_HOST}"
gcloud auth configure-docker "${REGISTRY_HOST}" --quiet

# A tag do SHA é a que importa: liga a imagem ao commit que a gerou.
SHA="$(git rev-parse HEAD)"

echo "==> Build: ${IMAGE}:${SHA}"
docker build -t "${IMAGE}:${SHA}" -t "${IMAGE}:latest" .

echo "==> Push"
docker push "${IMAGE}:${SHA}"
docker push "${IMAGE}:latest"

echo "==> Imagens no repositório:"
gcloud artifacts docker images list "${REGISTRY_HOST}/${PROJECT_ID}/${REPOSITORY}"

echo
echo "Pronto. Imagem publicada: ${IMAGE}:${SHA}"
