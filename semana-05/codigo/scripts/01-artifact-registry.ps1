# =============================================================================
# 01 — Criar o repositório no Artifact Registry e publicar a imagem na mão.
#
# Rode UMA VEZ, antes de ativar o CI. Serve para separar os problemas:
# se o push manual funciona, o que sobra de erro no Actions é autenticação.
#
# Uso (PowerShell, a partir de semana-05/codigo/):
#   .\scripts\01-artifact-registry.ps1
# =============================================================================

$ErrorActionPreference = "Stop"

# --- Ajuste estas variáveis ---------------------------------------------------
$ProjectId  = "SEU-PROJECT-ID"      # gcloud projects list
$Region     = "us-central1"
$Repository = "mlops-estudos"
$ImageName  = "api-sentimento"
# ------------------------------------------------------------------------------

$Host_      = "$Region-docker.pkg.dev"
$Image      = "$Host_/$ProjectId/$Repository/$ImageName"

Write-Host "==> Projeto ativo: $ProjectId"
gcloud config set project $ProjectId

Write-Host "==> Habilitando a API do Artifact Registry (idempotente)"
gcloud services enable artifactregistry.googleapis.com

Write-Host "==> Criando o repositório Docker '$Repository' em $Region"
# Se já existir, o gcloud devolve ALREADY_EXISTS — pode ignorar.
gcloud artifacts repositories create $Repository `
    --repository-format=docker `
    --location=$Region `
    --description="Imagens do grupo de estudos MLOps"

Write-Host "==> Repositórios existentes:"
gcloud artifacts repositories list --location=$Region

Write-Host "==> Autorizando o Docker local a falar com $Host_"
gcloud auth configure-docker $Host_ --quiet

# A tag do SHA é a que importa: liga a imagem ao commit que a gerou.
$Sha = (git rev-parse HEAD).Trim()

Write-Host "==> Build: ${Image}:$Sha"
docker build -t "${Image}:$Sha" -t "${Image}:latest" .

Write-Host "==> Push"
docker push "${Image}:$Sha"
docker push "${Image}:latest"

Write-Host "==> Imagens no repositório:"
gcloud artifacts docker images list "$Host_/$ProjectId/$Repository"

Write-Host ""
Write-Host "Pronto. Imagem publicada: ${Image}:$Sha"
