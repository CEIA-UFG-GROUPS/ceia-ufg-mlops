# 🧪 Atividade Prática — Aula 20: CI/CD for Machine Learning (CD4ML)

Prática guiada que percorre o **trabalho real de CI/CD para ML**: gerar dados sintéticos de fraude, validar schema, treinar um candidato, **bloquear regressão** com quality gate, publicar um *model-diff* (o padrão que o CML popularizou) e registrar o modelo com aliases no estilo da Aula 19.

Há **duas camadas** (ambas obrigatórias no desenho pedagógico):

| Camada | Onde roda | Objetivo |
|---|---|---|
| **1 — GitHub Actions** | Repo próprio do aluno (free tier, CPU) | PR que degrada o modelo → check vermelho + comentário; correção → verde; merge → registro |
| **2 — Local / Docker** | `scripts/run_ci_local.sh` ou Compose | Mesma sequência de gates, mesmos exit codes — funciona offline |

---

## ⚠️ Caveat crítico: este workflow NÃO roda a partir do monorepo

O arquivo `.github/workflows/ml-ci.yml` vive em:

`presentation/segundo-semestre/aula20/monitor/atividade/.github/workflows/`

O GitHub Actions **só descobre workflows em `.github/workflows/` na raiz do repositório**. Enquanto o lab estiver aninhado neste monorepo do grupo, **nenhum PR aqui vai disparar o `ml-ci.yml`**.

Para a Camada 1, copie o conteúdo de `atividade/` para a **raiz** de um repositório seu:

```bash
# Exemplo: criar um repo novo e copiar o lab para a raiz
mkdir -p ~/lab-aula20-cicd && cd ~/lab-aula20-cicd
git init -b main
cp -a /caminho/para/ceia-ufg-mlops/presentation/segundo-semestre/aula20/monitor/atividade/. .
# Garanta que .github/workflows/ml-ci.yml está na RAIZ do repo novo
ls .github/workflows/ml-ci.yml
git add .
git commit -m "feat: lab aula 20 CD4ML"
# Crie o repo no GitHub e faça push; depois abra um PR
```

Sem esse passo, use a Camada 2 — o aprendizado dos gates é idêntico.

---

## 🎯 O que você vai construir

```text
 ┌────────────────────────────────────────────────────────────────────────────┐
 │                     FLUXO CD4ML DO LAB (mesma ordem no Actions)            │
 ├────────────────────────────────────────────────────────────────────────────┤
 │ 1. generate_data   → data/train.csv + data/test.csv (sintético, sem net)   │
 │ 2. validate_data   → schema + nulos + faixas (exit ≠ 0 se quebrar)         │
 │ 3. train_model     → models/candidate.joblib + reports/metrics.json        │
 │ 4. evaluate_gate   → compara com baselines/baseline_metrics.json           │
 │ 5. pr_comment      → reports/pr_comment.md (model-diff markdown)           │
 │ 6. security_scan   → SHA-256 (+ model-signing opcional, degrada ok)        │
 │ 7. register_model  → registry/models.json (@challenger / @champion)        │
 └────────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Estrutura de Diretórios

```text
atividade/
├── README.md
├── requirements.txt
├── .gitignore
├── baselines/
│   └── baseline_metrics.json          # contrato versionado do gate
├── .github/workflows/
│   └── ml-ci.yml                      # workflow real (use na RAIZ do seu repo)
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml             # serviço ci-lab
├── scripts/
│   └── run_ci_local.sh                # Camada 2
└── src/
    ├── utils.py
    ├── 01_generate_data.py
    ├── 02_validate_data.py
    ├── 03_train_model.py
    ├── 04_evaluate_gate.py
    ├── 05_write_pr_comment.py
    ├── 06_security_scan.py
    └── 07_register_model.py
```

Diretórios `data/`, `models/`, `reports/`, `registry/` são gerados em runtime (gitignore + `.gitkeep`).

---

## 🛠️ Pré-requisitos

- Python **3.12+** (testado com 3.12) **ou** Docker / Docker Compose
- (Camada 1) Conta GitHub e permissão para criar repositório
- Pacotes: ver `requirements.txt` (pandas, numpy, scikit-learn, joblib, PyYAML)

---

## 🛠️ Passo a Passo

### 1. Ambiente local

```bash
cd presentation/segundo-semestre/aula20/monitor/atividade
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
# Não é obrigatório ativar o venv: o script resolve ./.venv/bin/python sozinho.
# (Opcional) source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
```

> Em Ubuntu/Debian/WSL sem o pacote `python-is-python3`, o comando `python` pode não existir — só `python3`. O `run_ci_local.sh` detecta `.venv`, `python3` ou `PYTHON=…` e falha com mensagem clara se nada for encontrado.
### 2. Caminho feliz (Camada 2)

```bash
bash scripts/run_ci_local.sh
echo $?    # deve imprimir 0
```

**O que observar** (tempos **medidos** neste ambiente em 2026-08-14):

| Etapa | Tempo observado |
|---|---|
| Pipeline local completo (happy path) | **~2,0 s** (medido 1,97–2,08 s) |
| Pipeline com `CI_DEGRADE=1` | **~2,1 s** |
| Treino RandomForest isolado | **~0,2 s** |
| Meta pedagógica no GitHub free tier (CPU) | **≪ 2 min** (instalar deps + pipeline) |

Saídas esperadas:

- `reports/metrics.json` com F1 ≈ **0,71** (baseline do lab)
- `reports/pr_comment.md` com status **APROVADO**
- `reports/security_report.json` com SHA-256

### 3. Registrar como em `main`

```bash
MODE=main bash scripts/run_ci_local.sh
cat registry/models.json
```

Esperado: aliases `@champion` e `@challenger` apontando para `v1` (primeira promoção).

### 4. Docker (alternativa sem Python local)

```bash
cd docker
docker compose run --rm ci-lab
# Quebrar o gate:
CI_DEGRADE=1 docker compose run --rm ci-lab
```

### 5. Camada 1 — PR no GitHub

1. Copie `atividade/` para a **raiz** do seu repo (veja o caveat no topo).
2. Em Settings → Branches, exija o check do workflow `ml-ci` / job de gate antes do merge.
3. Abra um PR que degrade o modelo (próxima seção).
4. Confirme: job vermelho + comentário bot com tabela de Δ métricas.
5. Reverta a degradação; gate verde; merge em `main` → job `register-main`.

Action majors usados no YAML (verificados em **2026-08-14**):

| Action | Major |
|---|---|
| `actions/checkout` | **v7** |
| `actions/setup-python` | **v7** |
| `actions/upload-artifact` | **v7** |
| `actions/download-artifact` | **v8** |
| `actions/github-script` | **v9** |

---

## 💥 Quebre o gate de propósito

### Opção A — variável de ambiente (mais rápida)

```bash
CI_DEGRADE=1 bash scripts/run_ci_local.sh
echo $?    # deve ser != 0
cat reports/pr_comment.md
```

Isso embaralha ~45% dos rótulos no gerador de dados → F1 despenca → gate falha → o markdown de *model-diff* ainda é gerado (como no Actions com `continue-on-error` + fail final).

### Opção B — editar o treino (estilo “PR ruim”)

Em `src/03_train_model.py`, force um modelo fraco, por exemplo `n_estimators=1` e `max_depth=1` (ou exporte `N_ESTIMATORS=1 MAX_DEPTH=1`). Rode o script local ou abra o PR. Depois desfaça e confirme o verde.

### Opção C — corromper o schema

Edite temporariamente `data/train.csv` (após gerar) removendo uma coluna e rode só:

```bash
.venv/bin/python -m src.02_validate_data
# ou, com venv ativado:
python -m src.02_validate_data
```

Deve sair com exit 1.

---

## 🏋️ Desafio hands-on

Escolha **um**:

1. **Apertar o limiar**: defina `GATE_THRESHOLD=0.005` e veja o que acontece com ruído amostral.
2. **Gate de schema extra**: em `02_validate_data.py`, exija taxa de fraude ∈ [0.05, 0.60].
3. **Gate de fairness (ponte Aula 24)**: adicione uma coluna sintética `grupo` e falhe se a diferença de *selection rate* entre grupos passar de 0.10.
4. **Assinatura**: `pip install model-signing==1.1.1` e observe se `06_security_scan.py` reporta assinatura (a API pode variar — o lab já degrada com aviso se falhar).

---

## 🧯 Troubleshooting

| Sintoma | Causa provável | Ação |
|---|---|---|
| Workflow nunca aparece no GitHub | Lab ainda no subdiretório do monorepo | Copiar `atividade/` para a **raiz** do repo |
| `Baseline ausente` | `baselines/baseline_metrics.json` faltando | Restaurar o arquivo versionado do material |
| Gate falha “sem motivo” | Limiar muito apertado / seed alterada | Conferir `GATE_THRESHOLD` e não editar a baseline sem regenerar o contrato |
| `ModuleNotFoundError: src` | `PYTHONPATH` | O script `run_ci_local.sh` já exporta; ou rode da pasta `atividade/` |
| Assinatura não gera | `model-signing` ausente | Esperado — pipeline continua |
| Jobs lentos no Actions | cold start + pip | Cache `pip` já habilitado no `setup-python` |

---

## ⏱️ Tempos esperados (medidos)

Medidos em WSL2 Linux, Python 3.12, venv local, **2026-08-14**:

- Happy path sem venv ativado (`bash scripts/run_ci_local.sh` após `.venv/bin/pip install`): **2,08 s**, exit **0** (usa `./.venv/bin/python`)
- Happy path com venv ativado: **1,97 s**, exit **0**
- Degrade (`CI_DEGRADE=1`): exit **1**, `pr_comment.md` gerado
- `python -m py_compile` / `python3 -m py_compile` em `src/*.py`: OK
- Parse do YAML do workflow: OK
- Script sem venv ativado (usa `./.venv/bin/python`): OK
- Script com venv ativado (`VIRTUAL_ENV`): OK

No GitHub-hosted `ubuntu-latest`, espere dezenas de segundos a ~1–2 minutos (checkout + setup-python + pip), ainda dentro da meta pedagógica de “cerca de 2 minutos”. O workflow usa `python` **depois** de `actions/setup-python@v7`, que garante o binário no PATH do runner.

---

## 🔗 Conceitos cruzados (não retreinados aqui)

- **Aula 10**: sintaxe Actions/Docker/secrets
- **Aula 19**: semântica real de registry MLflow / aliases
- **Aula 22**: como o tráfego muda após o alias
- **Aula 23**: drift como gatilho de CT que *dispara* este tipo de pipeline
