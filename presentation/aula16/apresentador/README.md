# Data Version Control (DVC)

## README do Apresentador

Este documento organiza a apresentação da aula e serve como **guia conceitual** para o expositor.
A estrutura abaixo deve ser seguida para garantir clareza, progressão lógica e alinhamento com o grupo.

> 💡 **Fio condutor sugerido**: partir de uma história de irreprodutibilidade ("qual dataset treinou o modelo que está em produção?") e mostrar que o DVC é só o modelo mental do Git — commits, checkout, push/pull — estendido para dados. Quanto mais a aula reaproveitar o que a turma já sabe de Git, melhor.

---

## 1️⃣ Motivação

### 1.1 Reprodutibilidade em ML é código + dados + parâmetros + ambiente

- Git resolve código; Docker resolve ambiente; e os dados?
- Perguntas que ficam sem resposta sem versionamento de dados:
  - "Com qual dado exatamente esse modelo foi treinado?"
  - "O modelo piorou pelo código ou pelos dados?"
  - "Como reproduzo o resultado de 6 meses atrás?"
- Auditoria/regulação (crédito, saúde): linhagem de dados é requisito, não luxo

### 1.2 Por que não commitar dados no Git?

- Git faz diff de texto; binário grande = histórico incha para sempre
- Clone baixa TODO o histórico (cada versão antiga do dataset)
- Limites práticos: GitHub bloqueia arquivos > 100 MB
- Dados sensíveis não podem ir para o host do código (compliance)
- Git LFS: resolve metade (ponteiros), mas exige servidor/quotas e não sabe nada de ML

### 1.3 Impacto prático

- Datasets duplicados em pastas/e-mails ("dataset_final_v2_AGORA_VAI.csv")
- Retrabalho: re-executar pipeline inteiro sem necessidade
- Rollback de modelo sem rollback do dado que o gerou

---

## 2️⃣ Como Funciona

### 2.1 A arquitetura do DVC (conceito central da aula)

- Divisão de responsabilidades: **metadados no Git, dados no cache/remote**
- `dvc add` → hash MD5 → cache content-addressable → arquivo-ponteiro `.dvc` (mostrar um `.dvc` aberto: são ~5 linhas de YAML!)
- Cache indexado por conteúdo = deduplicação de graça + checkout instantâneo (mesma ideia dos objetos do Git)
- Links (reflink/hardlink/symlink): workspace não duplica espaço
- **Viagem no tempo**: `git checkout <tag>` + `dvc checkout` (par de comandos que resume a aula)

### 2.2 Remotes: o "GitHub dos dados"

- `dvc remote add` / `dvc push` / `dvc pull`
- Backends: S3, GCS, Azure, SSH, MinIO, Google Drive, diretório local
- Fluxo de equipe: `git push + dvc push` ↔ `git pull + dvc pull`
- Dados ficam NO SEU storage — compliance e custo sob controle

### 2.3 Pipelines reprodutíveis

- `dvc.yaml`: stages com `cmd`, `deps`, `params`, `outs`, `metrics` — o pipeline como DAG declarado
- `dvc repro`: compara hashes e re-executa **só o que mudou** ("Makefile ciente de conteúdo")
- `dvc.lock` como certificado de reprodutibilidade (hashes exatos de cada dep/out)
- `dvc dag` para visualizar
- Distinção didática importante: dado **fonte** = `dvc add`; dado **derivado** = `outs` do pipeline

### 2.4 Params, metrics e experimentos

- `params.yaml` + `dvc params diff`; métricas em JSON + `dvc metrics show/diff`
- `dvc plots` (ex.: matriz de confusão) — mencionar, sem demorar
- `dvc exp run --set-param ...` / `dvc exp show` / `dvc exp apply`: variações baratas sem poluir o Git
- Posicionamento vs MLflow: complementares (dados/pipeline vs tracking/registry) — NÃO transformar em guerra de ferramentas

### 2.5 Ecossistema (rápido, para dar mapa mental)

- Git LFS, lakeFS, Delta Lake/Iceberg, Pachyderm, DagsHub — 1 frase cada
- Mensagem: DVC brilha com **arquivos** + fluxo **git-first**; tabelas gigantes em lakehouse pedem outra família de ferramentas

---

## 3️⃣ Quickstart

> 💡 **Material pronto**: a pasta `../monitor/atividade/` contém um laboratório completo (notebook Colab + código-fonte + Docker com remote MinIO). As demos abaixo podem ser conduzidas ao vivo a partir dele — ou simplesmente guie o notebook com a turma.

### 3.1 Demo 1 — Versionando dados (o essencial)

- `git init` + `dvc init` num diretório limpo
- Gerar um CSV, `dvc add data/raw/data.csv` → abrir o `.dvc` e o `.gitignore` gerados
- Commit + tag `v1.0`; alterar o dado, `dvc add` de novo, commit + tag `v2.0`
- **Momento uau**: `git checkout v1.0 && dvc checkout` → o dado volta no tempo
- Mostrar o cache (`.dvc/cache`) para materializar o content-addressable

### 3.2 Demo 2 — Remote e fluxo de equipe

- Local: `dvc remote add -d storage ../dvc-remote && dvc push`
- Com Docker (mais impactante): MinIO via `docker compose` como S3 self-hosted, console web em `localhost:9001` mostrando os objetos chegando após o `dvc push`
- Simular o colega: clonar o repo em outra pasta, `dvc pull` → dados idênticos

### 3.3 Demo 3 — Pipeline com `dvc repro`

- `dvc.yaml` com `prepare → train → evaluate` (código pronto em `atividade/src/`)
- `dvc repro` completo na primeira vez
- Rodar de novo sem mudar nada → tudo "skipped" (memoização)
- Mudar `train.n_estimators` no `params.yaml` → só `train` e `evaluate` re-executam
- `dvc metrics diff` e `dvc params diff` para comparar
- Se der tempo: `dvc exp run --set-param train.max_depth=10` + `dvc exp show`

### 3.4 Boas práticas para fechar

- Commit sempre inclui `.dvc`/`dvc.lock`; tags para versões importantes
- `dvc push` faz parte do "done" — snapshot sem dados no remote está quebrado
- `data/raw` imutável (`dvc add`); derivados são `outs` do pipeline
- Params fora do código; métricas com `cache: false` para diff no Git
- CI rodando `dvc repro` + `dvc metrics diff` (mencionar CML)
- Dados sensíveis: o remote herda os requisitos de acesso do dado original
