# =============================================================================
# Workspace da prática de DVC.
#
# Um container com git + dvc[s3] + os arquivos iniciais do lab em
# /opt/starter. O laboratório em si acontece em /workspace (um volume),
# onde o participante cria SEU próprio repositório git+dvc — exatamente
# como faria num projeto real.
#
# Por que não rodar o lab direto na pasta da atividade? Porque ela vive
# DENTRO do repositório git do curso, e um `git init`/`dvc init` aninhado
# causaria confusão. O container dá um ambiente limpo e descartável.
#
# Build (a partir da pasta atividade/):
#   docker build -f docker/Dockerfile -t aula16-dvc .
# =============================================================================

FROM python:3.11-slim

# git: obrigatório — o DVC trabalha SOBRE um repositório git.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git tree \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Arquivos iniciais do lab (código do pipeline + params + dvc.yaml).
# O participante os copia para /workspace no início da prática.
COPY src/ /opt/starter/src/
COPY params.yaml dvc.yaml /opt/starter/

# Identidade git para os commits do lab (num projeto real, seria a sua).
RUN git config --global user.name "Estudante MLOps" \
    && git config --global user.email "estudante@ceia.ufg.br" \
    && git config --global init.defaultBranch main

WORKDIR /workspace

CMD ["bash"]
