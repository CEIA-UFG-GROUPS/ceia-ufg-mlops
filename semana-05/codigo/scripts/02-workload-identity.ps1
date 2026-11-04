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
# Uso (PowerShell, a partir de semana-05/codigo/):
#   .\scripts\02-workload-identity.ps1
# =============================================================================

# Os `create` são idempotentes na prática: se o recurso existir, o gcloud
# devolve ALREADY_EXISTS. Por isso não usamos "Stop" global aqui.
$ErrorActionPreference = "Continue"

# --- Ajuste estas variáveis ---------------------------------------------------
$ProjectId  = "SEU-PROJECT-ID"
$GitHubRepo = "SEU-USUARIO/SEU-REPO"   # exatamente como aparece na URL do GitHub
$Pool       = "github-pool"
$Provider   = "github-provider"
$SaName     = "github-actions"
# ------------------------------------------------------------------------------

$SaEmail = "$SaName@$ProjectId.iam.gserviceaccount.com"

gcloud config set project $ProjectId
$ProjectNumber = (gcloud projects describe $ProjectId --format='value(projectNumber)').Trim()

Write-Host "==> Habilitando as APIs necessárias"
gcloud services enable iamcredentials.googleapis.com sts.googleapis.com artifactregistry.googleapis.com

Write-Host "==> Criando a service account que o Actions vai personificar"
gcloud iam service-accounts create $SaName --display-name="GitHub Actions (CI)"

Write-Host "==> Dando a ela permissão de escrita no Artifact Registry (e só isso)"
gcloud projects add-iam-policy-binding $ProjectId `
    --member="serviceAccount:$SaEmail" `
    --role="roles/artifactregistry.writer"

Write-Host "==> Criando o Workload Identity Pool"
gcloud iam workload-identity-pools create $Pool `
    --location="global" `
    --display-name="GitHub Actions"

Write-Host "==> Criando o provider OIDC do GitHub"
# `attribute-condition` é o que impede QUALQUER repositório do GitHub de
# assumir esta service account. Sem essa linha, o pool fica aberto demais.
gcloud iam workload-identity-pools providers create-oidc $Provider `
    --location="global" `
    --workload-identity-pool=$Pool `
    --display-name="GitHub OIDC" `
    --issuer-uri="https://token.actions.githubusercontent.com" `
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" `
    --attribute-condition="assertion.repository == '$GitHubRepo'"

Write-Host "==> Autorizando SOMENTE o repositório $GitHubRepo a personificar a SA"
$PrincipalSet = "principalSet://iam.googleapis.com/projects/$ProjectNumber/locations/global/workloadIdentityPools/$Pool/attribute.repository/$GitHubRepo"
gcloud iam service-accounts add-iam-policy-binding $SaEmail `
    --role="roles/iam.workloadIdentityUser" `
    --member=$PrincipalSet

$ProviderPath = "projects/$ProjectNumber/locations/global/workloadIdentityPools/$Pool/providers/$Provider"

Write-Host ""
Write-Host "============================================================================="
Write-Host "Cadastre estes valores no GitHub, em:"
Write-Host "  Settings > Secrets and variables > Actions > aba 'Variables'"
Write-Host ""
Write-Host "  GCP_PROJECT_ID       $ProjectId"
Write-Host "  GCP_WIF_PROVIDER     $ProviderPath"
Write-Host "  GCP_SERVICE_ACCOUNT  $SaEmail"
Write-Host ""
Write-Host "São variáveis, não secrets: nenhum desses valores é sigiloso. O que protege"
Write-Host "o acesso é a attribute-condition acima, amarrada ao repositório."
Write-Host "============================================================================="
