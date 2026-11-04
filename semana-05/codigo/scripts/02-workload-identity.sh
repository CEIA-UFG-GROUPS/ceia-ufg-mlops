#!/usr/bin/env bash
# =============================================================================
# 02 — Workload Identity Federation: deixar o GitHub Actions publicar no
#      Artifact Registry SEM chave JSON de service account.
#
# A ideia: o Actions emite um token OIDC dizendo "sou o workflow X do repo Y".
# O GCP confia nesse emissor, confere o repositório e devolve uma credencial
# temporária (minutos). Não existe segredo de longa duração para vazar.
#
# Rode UMA VEZ por projeto. Precisa de permissão de admin no projeto GCP.
#
# Uso (a partir de semana-05/codigo/):
#   bash scripts/02-workload-identity.sh
# =============================================================================
set -euo pipefail

# --- Ajuste estas variáveis ---------------------------------------------------
PROJECT_ID="SEU-PROJECT-ID"
GITHUB_REPO="SEU-USUARIO/SEU-REPO"   # exatamente como aparece na URL do GitHub
POOL="github-pool"
PROVIDER="github-provider"
SA_NAME="github-actions"
# ------------------------------------------------------------------------------

SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud config set project "${PROJECT_ID}"
PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"

echo "==> Habilitando as APIs necessárias"
gcloud services enable \
    iamcredentials.googleapis.com \
    sts.googleapis.com \
    artifactregistry.googleapis.com

echo "==> Criando a service account que o Actions vai personificar"
gcloud iam service-accounts create "${SA_NAME}" \
    --display-name="GitHub Actions (CI)" || true

echo "==> Dando a ela permissão de escrita no Artifact Registry (e só isso)"
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/artifactregistry.writer"

echo "==> Criando o Workload Identity Pool"
gcloud iam workload-identity-pools create "${POOL}" \
    --location="global" \
    --display-name="GitHub Actions" || true

echo "==> Criando o provider OIDC do GitHub"
# `attribute-condition` é o que impede QUALQUER repositório do GitHub de
# assumir esta service account. Sem essa linha, o pool fica aberto demais.
gcloud iam workload-identity-pools providers create-oidc "${PROVIDER}" \
    --location="global" \
    --workload-identity-pool="${POOL}" \
    --display-name="GitHub OIDC" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
    --attribute-condition="assertion.repository == '${GITHUB_REPO}'" || true

echo "==> Autorizando SOMENTE o repositório ${GITHUB_REPO} a personificar a SA"
gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
    --role="roles/iam.workloadIdentityUser" \
    --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL}/attribute.repository/${GITHUB_REPO}"

PROVIDER_PATH="projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL}/providers/${PROVIDER}"

cat <<EOF

=============================================================================
Cadastre estes valores no GitHub, em:
  Settings > Secrets and variables > Actions > aba "Variables"

  GCP_PROJECT_ID       ${PROJECT_ID}
  GCP_WIF_PROVIDER     ${PROVIDER_PATH}
  GCP_SERVICE_ACCOUNT  ${SA_EMAIL}

São variáveis, não secrets: nenhum desses valores é sigiloso. O que protege
o acesso é a attribute-condition acima, amarrada ao repositório.
=============================================================================
EOF
