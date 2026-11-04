#!/usr/bin/env bash
# Verificador de ambiente da Semana 00 (Linux / WSL / macOS).
#
# Checa, item a item, se o ambiente do grupo de estudos esta pronto: git,
# GitHub por SSH, python, docker, WSL, gcloud e (opcionalmente) o acesso a
# maquina 4090 do laboratorio. Nada e instalado ou alterado: o script so le.
#
# Uso:
#   ./verificar-ambiente.sh
#   ./verificar-ambiente.sh --host-lab aluno@gpu01.lab.ufg.br
#   ./verificar-ambiente.sh --pular-rede
#
# Codigo de saida: 0 se tudo passou, 1 se algum item obrigatorio falhou.

set -uo pipefail

HOST_LAB="${LAB_SSH_HOST:-}"
PULAR_REDE=0

while [ $# -gt 0 ]; do
  case "$1" in
    --host-lab)
      HOST_LAB="${2:-}"
      if [ -z "$HOST_LAB" ]; then
        echo "erro: --host-lab exige um valor (ex.: aluno@gpu01.lab.ufg.br)" >&2
        exit 2
      fi
      shift 2
      ;;
    --pular-rede)
      PULAR_REDE=1
      shift
      ;;
    -h|--help)
      sed -n '2,15p' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "erro: opcao desconhecida '$1' (use --help)" >&2
      exit 2
      ;;
  esac
done

OK="✅"
FALHA="❌"
AVISO="⚠️"

FALHAS=0
AVISOS=0

secao()    { printf '\n-- %s\n' "$1"; }
ok()       { printf '%s %s' "$OK" "$1"; [ $# -gt 1 ] && printf '  %s' "$2"; printf '\n'; }
falha()    { FALHAS=$((FALHAS + 1)); printf '%s %s\n' "$FALHA" "$1"; [ $# -gt 1 ] && [ -n "$2" ] && printf '     -> %s\n' "$2"; return 0; }
aviso()    { AVISOS=$((AVISOS + 1)); printf '%s %s\n' "$AVISO" "$1"; [ $# -gt 1 ] && [ -n "$2" ] && printf '     -> %s\n' "$2"; return 0; }

tem() { command -v "$1" >/dev/null 2>&1; }

# primeira_linha <texto>
primeira_linha() { printf '%s\n' "$1" | head -n 1; }

# checa_ferramenta <rotulo> <comando> <dica> [args de versao...]
checa_ferramenta() {
  local rotulo="$1" cmd="$2" dica="$3"
  shift 3
  if ! tem "$cmd"; then
    falha "$rotulo - '$cmd' nao encontrado no PATH" "$dica"
    return
  fi
  local saida
  if saida="$("$cmd" "$@" 2>&1)" && [ -n "$saida" ]; then
    ok "$rotulo" "$(primeira_linha "$saida")"
  else
    falha "$rotulo - instalado, mas nao respondeu" "$dica"
  fi
}

echo "============================================="
echo " Verificador de ambiente - Semana 00 (CEIA)  "
echo "============================================="
printf 'Maquina: %s | Usuario: %s | %s\n' "$(uname -n)" "${USER:-${USERNAME:-?}}" "$(date '+%d/%m/%Y %H:%M')"

# ------------------------------------------------------------------- Git ----
secao "Git e GitHub"

checa_ferramenta "git" "git" "Instale com: sudo apt update && sudo apt install -y git" --version

if tem git; then
  nome="$(git config --global user.name 2>/dev/null || true)"
  email="$(git config --global user.email 2>/dev/null || true)"
  [ -n "$nome" ]  && ok "git config user.name" "$nome"   || falha "git config user.name nao definido"  'git config --global user.name "Seu Nome"'
  [ -n "$email" ] && ok "git config user.email" "$email" || falha "git config user.email nao definido" 'git config --global user.email "voce@exemplo.com"'
fi

chaves="$(ls -1 "$HOME"/.ssh/*.pub 2>/dev/null | xargs -r -n1 basename | tr '\n' ' ' || true)"
if [ -n "$chaves" ]; then
  ok "Chave SSH encontrada" "$chaves"
else
  falha "Nenhuma chave SSH publica em ~/.ssh" 'ssh-keygen -t ed25519 -C "voce@exemplo.com"'
fi

if [ "$PULAR_REDE" -eq 1 ]; then
  aviso "SSH para o GitHub - pulado (--pular-rede)" ""
elif ! tem ssh; then
  falha "ssh nao encontrado no PATH" "sudo apt install -y openssh-client"
else
  saida_gh="$(ssh -T -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 git@github.com 2>&1 || true)"
  # O GitHub sempre encerra com exit code 1; o que vale e a mensagem.
  case "$saida_gh" in
    *"successfully authenticated"*)
      ok "SSH para o GitHub" "$(primeira_linha "$saida_gh")" ;;
    *"Permission denied"*)
      falha "SSH para o GitHub - Permission denied" "A chave publica ainda nao foi adicionada em https://github.com/settings/keys" ;;
    *)
      falha "SSH para o GitHub falhou" "$(primeira_linha "$saida_gh")" ;;
  esac
fi

# ---------------------------------------------------------------- Python ----
secao "Python"

# Pegamos o primeiro que REALMENTE responde: no Windows (Git Bash / PATH do
# Store) existe um "python3.exe" que e so um atalho para a loja e nao executa nada.
PY=""
for candidato in python3 python; do
  if tem "$candidato" && "$candidato" --version >/dev/null 2>&1; then
    PY="$candidato"
    break
  fi
done

if [ -n "$PY" ]; then
  checa_ferramenta "python" "$PY" "" --version
  if "$PY" -m pip --version >/dev/null 2>&1; then
    ok "pip" "$("$PY" -m pip --version 2>&1 | head -n 1)"
  else
    falha "pip nao disponivel" "sudo apt install -y python3-pip  (ou: $PY -m ensurepip --upgrade)"
  fi
  if "$PY" -m venv --help >/dev/null 2>&1; then
    ok "modulo venv" "disponivel"
  else
    falha "modulo venv indisponivel" "sudo apt install -y python3-venv"
  fi
else
  falha "python nao encontrado no PATH" "sudo apt update && sudo apt install -y python3 python3-pip python3-venv"
fi

# ---------------------------------------------------------------- Docker ----
secao "Docker"

if ! tem docker; then
  falha "docker nao encontrado no PATH" "Windows: instale o Docker Desktop e ative a integracao com esta distro WSL (Settings > Resources > WSL Integration). Linux: https://docs.docker.com/engine/install/"
else
  checa_ferramenta "docker (cliente)" "docker" "" --version

  if server="$(docker info --format '{{.ServerVersion}}' 2>/dev/null)" && [ -n "$server" ]; then
    ok "docker daemon respondendo" "server $server"
  else
    falha "docker daemon nao respondeu" "Suba o Docker Desktop (ou: sudo systemctl start docker). Se der 'permission denied', rode: sudo usermod -aG docker \$USER e reabra o terminal."
  fi

  if compose="$(docker compose version 2>/dev/null)" && [ -n "$compose" ]; then
    ok "docker compose" "$(primeira_linha "$compose")"
  else
    aviso "docker compose nao disponivel" "Atualize o Docker (Compose V2 ja vem embutido)."
  fi
fi

# ------------------------------------------------------------------- WSL ----
secao "WSL2"

if grep -qiE "microsoft|wsl" /proc/version 2>/dev/null; then
  ok "Rodando dentro do WSL" "$(uname -sr)"
  if [ -d /mnt/c ]; then
    ok "Disco do Windows montado" "/mnt/c acessivel"
  else
    aviso "/mnt/c nao encontrado" "Interop com o Windows desativado; normalmente nao atrapalha o lab."
  fi
else
  aviso "Nao e WSL" "Checagem pulada - voce esta em Linux/macOS nativo, que serve igual."
fi

# ---------------------------------------------------- Google Cloud (opt) ----
secao "Google Cloud (opcional nesta semana)"

if ! tem gcloud; then
  aviso "gcloud nao encontrado (opcional)" "So e obrigatorio a partir da Semana 06: https://cloud.google.com/sdk/docs/install"
else
  ok "gcloud" "$(gcloud --version 2>/dev/null | head -n 1)"

  conta="$(gcloud config get-value account 2>/dev/null | head -n 1)"
  case "$conta" in
    ""|*unset*|*"(unset)"*) aviso "gcloud sem conta ativa" "gcloud auth login" ;;
    *)                      ok "gcloud autenticado" "$conta" ;;
  esac

  projeto="$(gcloud config get-value project 2>/dev/null | head -n 1)"
  case "$projeto" in
    ""|*unset*|*"(unset)"*) aviso "Nenhum projeto GCP configurado" "gcloud config set project <SEU_PROJETO>" ;;
    *)                      ok "Projeto GCP configurado" "$projeto" ;;
  esac
fi

# ----------------------------------------------------- Maquina 4090 do lab --
secao "Maquina 4090 do laboratorio"

if [ "$PULAR_REDE" -eq 1 ]; then
  aviso "Acesso ao lab - pulado (--pular-rede)" ""
elif [ -z "$HOST_LAB" ]; then
  aviso "Host do lab nao informado" "Rode: ./verificar-ambiente.sh --host-lab usuario@servidor  (o host sai no Discord)"
elif ! tem ssh; then
  falha "ssh nao encontrado no PATH" "sudo apt install -y openssh-client"
else
  saida_lab="$(ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o ConnectTimeout=10 "$HOST_LAB" \
    'nvidia-smi --query-gpu=name --format=csv,noheader || hostname' 2>&1)"
  if [ $? -eq 0 ] && [ -n "$saida_lab" ]; then
    ok "SSH em $HOST_LAB" "$(primeira_linha "$saida_lab")"
  else
    falha "SSH em $HOST_LAB falhou" "$(primeira_linha "$saida_lab")"
  fi
fi

# ---------------------------------------------------------------- Resumo ----
echo ""
echo "---------------------------------------------"
if [ "$FALHAS" -eq 0 ]; then
  printf '%s Ambiente pronto! (%s aviso(s) nao bloqueante(s))\n' "$OK" "$AVISOS"
  exit 0
else
  printf '%s %s item(ns) faltando e %s aviso(s).\n' "$FALHA" "$FALHAS" "$AVISOS"
  echo "   Resolva os itens marcados com $FALHA e rode de novo. Travou? Poste a saida no Discord."
  exit 1
fi
