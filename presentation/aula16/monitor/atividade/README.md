# 🧪 Atividade Prática — Aula 16: Data Version Control (DVC)

Prática guiada que percorre o ciclo completo do DVC: **versionar dados → viajar no tempo → remote (push/pull) → pipeline reprodutível → métricas e experimentos**.

Ela pode ser executada de **duas formas equivalentes** — escolha a sua:

| Caminho | Para quem | Requisitos | Remote usado |
|---|---|---|---|
| **A. Notebook (Colab)** | Quer executar célula a célula, sem instalar nada | Conta Google (não precisa de GPU) | Diretório local (simulado) |
| **B. Código-fonte + Docker** | Quer o fluxo de equipe de verdade | Docker | **MinIO — um S3 self-hosted com console web** |

O **pipeline é o mesmo** nos dois caminhos: o notebook replica, célula a célula, o código documentado em `src/`.

---

## 🎯 O que você vai fazer

1. **Versionar dados** — `dvc add`, entender o ponteiro `.dvc` e o cache content-addressable
2. **Viajar no tempo** — `git checkout <tag>` + `dvc checkout` restaurando dado + código de qualquer versão
3. **Remote** — `dvc push` / `dvc pull`: o "GitHub dos dados" (no Docker, com MinIO/S3 de verdade)
4. **Pipeline reprodutível** — `dvc.yaml` (prepare → train → evaluate), `dvc repro` com memoização por hash, `dvc.lock`
5. **Comparar execuções** — `dvc metrics diff`, `dvc params diff` e experimentos com `dvc exp run/show`

O pipeline treina um RandomForest sobre um dataset sintético de classificação — leve de propósito: o assunto aqui é o **versionamento**, não o modelo.

---

## 📂 Estrutura

```text
atividade/
├── README.md                       # este arquivo
├── requirements.txt                # dvc[s3] + sklearn + pandas
├── params.yaml                     # hiperparâmetros (o "painel de controle")
├── dvc.yaml                        # o pipeline declarado como DAG
├── notebooks/
│   └── aula16_pratica_colab.ipynb  # Caminho A: notebook auto-contido
├── src/                            # Caminho B: código-fonte documentado
│   ├── get_data.py                 # gera o dado FONTE (versionado com dvc add)
│   ├── prepare.py                  # estágio: split treino/teste
│   ├── train.py                    # estágio: treina e serializa o modelo
│   └── evaluate.py                 # estágio: métricas (metrics) + plots
└── docker/
    ├── Dockerfile                  # workspace com git + dvc[s3] + starter files
    └── docker-compose.yml          # workspace + MinIO (S3) + criação do bucket
```

> ⚠️ **Não rode `git init`/`dvc init` diretamente nesta pasta** — ela vive dentro do repositório git do curso, e repositórios aninhados causam confusão. O notebook cria um workspace separado automaticamente; no Docker, o lab acontece num volume isolado (`/workspace`).

---

## 🅰️ Caminho A — Notebook no Colab

1. Abra `notebooks/aula16_pratica_colab.ipynb` no [Google Colab](https://colab.research.google.com/) (upload do arquivo ou abrindo direto do GitHub).
2. Execute as células em ordem — **não precisa de GPU**.

O notebook cria um repositório git+dvc limpo em `/content/dvc-lab` (ou `~/dvc-lab` fora do Colab) e usa um **diretório local como remote** para ser auto-contido. Também roda localmente (Jupyter/VS Code) com `pip install -r requirements.txt`.

---

## 🅱️ Caminho B — Código-fonte + Docker (com remote S3 real)

### B.1 — Subir a stack

```bash
cd atividade/docker
docker compose up -d --build
```

Isso sobe o **MinIO** (S3 self-hosted), cria o bucket `dvc-storage` e builda o **workspace** com git + dvc. Abra o console do MinIO em **http://localhost:9001** (usuário/senha: `minioadmin` / `minioadmin`) e deixe-o visível — você vai VER os objetos chegando a cada `dvc push`.

### B.2 — Montar o projeto dentro do workspace

```bash
docker compose exec workspace bash
```

Dentro do container:

```bash
# 1. Cria o repositório do lab com os arquivos iniciais
mkdir -p /workspace/lab && cd /workspace/lab
cp -r /opt/starter/* .
git init && dvc init
git add . && git commit -m "chore: inicializa projeto com git + dvc"

# 2. Configura o remote apontando para o MinIO
dvc remote add -d storage s3://dvc-storage
dvc remote modify storage endpointurl http://minio:9000
git add .dvc/config && git commit -m "chore: configura remote S3 (MinIO)"
```

(As credenciais `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` já estão no ambiente do container — veja o `docker-compose.yml`.)

### B.3 — Versionar dados e dar push

```bash
# v1 do dataset (dado FONTE -> dvc add)
python src/get_data.py --samples 2000
dvc add data/raw/data.csv
git add data/raw/data.csv.dvc data/raw/.gitignore
git commit -m "feat: dataset v1 (2000 amostras)" && git tag v1.0
dvc push        # 👀 olhe o bucket dvc-storage no console do MinIO!

# v2 "chegou mais dado"
python src/get_data.py --samples 4000
dvc add data/raw/data.csv
git add data/raw/data.csv.dvc
git commit -m "feat: dataset v2 (4000 amostras)" && git tag v2.0
dvc push

# ⏰ viagem no tempo
wc -l data/raw/data.csv           # 4001 linhas (v2)
git checkout v1.0 && dvc checkout
wc -l data/raw/data.csv           # 2001 linhas (v1)!
git checkout main && dvc checkout
```

### B.4 — Pipeline, métricas e experimentos

```bash
dvc repro                          # roda prepare -> train -> evaluate
git add . && git commit -m "feat: pipeline completo" && dvc push

dvc dag                            # visualiza o DAG
dvc repro                          # de novo: tudo "skipped" (memoização!)

# muda UM parâmetro e veja que prepare é pulado
sed -i 's/n_estimators: 100/n_estimators: 300/' params.yaml
dvc repro
dvc params diff && dvc metrics diff

# experimentos sem poluir o git
git add . && git commit -m "exp: n_estimators=300"
dvc exp run --set-param train.max_depth=10
dvc exp show
```

### B.5 — Simular o colega de equipe (o gran finale)

Ainda dentro do container, clone o repositório do lab em outra pasta — como faria um colega em outra máquina:

```bash
git clone /workspace/lab /workspace/colega && cd /workspace/colega
ls data/raw/                       # os PONTEIROS vieram... mas cadê o dado?
dvc pull                           # 👈 o dado desce do MinIO
wc -l data/raw/data.csv            # dados idênticos aos do "colega A"
dvc repro                          # nada re-executa: reprodução verificada!
```

Esse é o fluxo de equipe completo: `git push + dvc push` de um lado, `git pull/clone + dvc pull` do outro.

### B.6 — Encerrar

```bash
exit
docker compose down          # -v para apagar também MinIO e o volume do lab
```

---

## 💬 Perguntas para discutir no encontro

1. Por que indexar o cache **pelo hash do conteúdo** (e não pelo nome do arquivo) resolve deduplicação e viagem no tempo ao mesmo tempo?
2. O que deve ser `dvc add` e o que deve ser `outs` de um estágio? Qual o problema de colocar `data/raw` como `outs`?
3. No passo B.4, por que o `prepare` foi pulado quando você mudou `n_estimators`? E se mudasse `base.seed`?
4. O `dvc.lock` commitado + `dvc pull` + `dvc repro` sem nada a executar (B.5) *prova* o quê, exatamente?
5. `models/model.pkl` versionado no DVC substitui um model registry (MLflow)? O que cada abordagem oferece?
6. O bucket do MinIO agora contém cópias dos dados. Se o dado fosse sensível, que políticas o remote precisaria herdar?

---

## ⚠️ Solução de problemas

| Sintoma | Causa provável / solução |
|---|---|
| `dvc init` falha com "not a git repository" | O DVC trabalha **sobre** o git: rode `git init` antes |
| `dvc init` reclama de repositório aninhado | Você está dentro do repo do curso — use o workspace do notebook/Docker (veja o aviso acima) |
| `dvc push` falha com erro de conexão (Docker) | O MinIO subiu? `docker compose ps`; o endpoint dentro do container é `http://minio:9000` (não `localhost`) |
| `dvc push` falha com "Forbidden"/credenciais | Confirme `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` no ambiente (o compose já define) |
| Bucket não existe | O job `minio-init` cria o `dvc-storage`; re-rode `docker compose up minio-init` |
| `dvc exp run` falha por workspace sujo | Commite (ou `git stash`) as mudanças pendentes antes de rodar experimentos |
| Console do MinIO não abre | Porta 9001 ocupada? Ajuste o mapeamento no `docker-compose.yml` |

---

📖 **Material teórico**: veja o [README do monitor](../README.md) — em especial as seções de cache content-addressable, pipelines e o quadro comparativo do ecossistema.
