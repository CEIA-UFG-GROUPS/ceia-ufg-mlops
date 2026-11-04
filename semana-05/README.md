# Semana 05 — CI + Artifact Registry

> **Encontro 6 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

Automatizar a qualidade: GitHub Actions rodando testes e lint a cada push, e a imagem versionada indo parar no Artifact Registry do GCP.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Entender o que é integração contínua e por que ela antecede o deploy
- Escrever um workflow de GitHub Actions com jobs, steps e cache
- Rodar `pytest` e lint automaticamente em cada pull request
- Buildar e publicar a imagem Docker no Artifact Registry
- Versionar imagens com tags úteis (SHA do commit, `latest`, semver)

---

## Pré-requisitos

- Semana 04 concluída (imagem Docker da API de sentimento funcionando)
- Projeto GCP ativo, com billing/créditos habilitados
- `gcloud` instalado e autenticado (`gcloud auth login`)
- Docker rodando localmente (`docker run hello-world`)
- Python 3.12 e um repositório pessoal no GitHub

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- CI/CD: o que é cada letra e onde o CI termina
- Anatomia de um workflow: trigger, job, runner, step e action
- Secrets e autenticação: por que não se commita chave (e o que é Workload Identity Federation)
- Registries: Docker Hub vs Artifact Registry, público vs privado
- Estratégia de tags: rastreabilidade entre commit e imagem em produção

### 💻 Mão na massa (~60 min)

- Escrever os testes `pytest` do `/predict` e configurar o `ruff`
- Criar `.github/workflows/ci.yml` com os jobs de teste e lint
- Fazer o CI falhar de propósito e corrigir até ficar verde
- Criar o repositório no Artifact Registry via `gcloud`
- Autenticar o Actions no GCP e publicar a imagem com a tag do SHA
- Proteger a branch `main` exigindo CI verde para o merge

### 🎯 Desafio (~15 min)

Pipeline de CI verde em todo pull request e imagem publicada automaticamente no Artifact Registry a cada merge na `main`.

Enunciado completo em [`desafio.md`](./desafio.md).

---

## Passo a passo

O ponto de partida é a API da Semana 04: `app/`, `Dockerfile` e `.dockerignore` na raiz do seu repositório pessoal. Quem não tiver esse estado pronto copia de [`codigo/`](./codigo/) — é exatamente o mesmo código.

A aplicação **não muda** hoje. Tudo o que vamos escrever fica em volta dela: `tests/`, `pyproject.toml`, `requirements-dev.txt` e `.github/workflows/ci.yml`.

Os comandos estão em **PowerShell**, rodados da raiz do repositório. As diferenças para Linux/macOS estão anotadas.

> **Windows / PowerShell:** `curl` é apelido de `Invoke-WebRequest` e **não** aceita `-X`/`-d`. Use `curl.exe`.

---

### Bloco A — Testes e lint rodando na sua máquina (passos 1 a 5, ~15 min)

Nada vai para o CI antes de funcionar localmente. CI é a sua máquina, só que na nuvem e sem desculpa.

**1. Preparar o ambiente**

Crie `requirements-dev.txt` na raiz — é o que o CI vai instalar:

```
-r app/requirements.txt

httpx==0.28.1
pytest==8.3.4
ruff==0.8.4
```

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
```

*Esperado:* `Successfully installed ... fastapi ... pytest ... ruff ...`. O prompt passa a começar com `(.venv)`.

**2. Confirmar que a API sobe**

```powershell
uvicorn app.main:app --port 8000
```

Em outro terminal:

```powershell
curl.exe http://localhost:8000/health
```

*Esperado:* `{"status":"ok","modelo_carregado":true,"versao":"1.0.0"}`.
Derrube o servidor com `Ctrl+C` antes de seguir.

**3. Escrever o primeiro teste do `/predict`**

Crie `tests/test_predict.py`:

```python
from fastapi.testclient import TestClient

from app.main import app


def test_predict_classifica_positivo():
    with TestClient(app) as client:
        resposta = client.post(
            "/predict", json={"texto": "adorei o atendimento, chegou antes do prazo"}
        )

    assert resposta.status_code == 200
    assert resposta.json()["sentimento"] == "positivo"
```

E `pyproject.toml` na raiz, para o pytest achar o pacote `app`:

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
addopts = "-q"
```

```powershell
pytest -v
```

*Esperado:* `1 passed`.

> **O `with` não é opcional.** É ele que dispara o `lifespan` do FastAPI e, com isso, o treino do modelo no startup. Sem o `with`, `estado["modelo"]` fica `None` e o `/predict` estoura com `AttributeError: 'NoneType' object has no attribute 'predict_proba'`. Esse erro vai aparecer para alguém — vale antecipar.
>
> `ModuleNotFoundError: No module named 'app'` quer dizer que falta o `pythonpath = ["."]`.

**4. Cobrir os quatro blocos de caso**

Um teste só não protege nada. Mova o `TestClient` para uma fixture em `tests/conftest.py` (veja [`codigo/tests/conftest.py`](./codigo/tests/conftest.py)) e cubra:

| Bloco | O que verificar |
| --- | --- |
| **Status codes** | `200` no caminho feliz; `422` sem o campo `texto`, com texto vazio, com texto acima de 1000 caracteres e com tipo errado; `405` no `GET /predict` |
| **Formato da resposta** | as chaves são exatamente `texto`, `sentimento`, `score` e `modelo`; os tipos batem; `0.0 <= score <= 1.0`; `modelo == "tfidf+logreg"` |
| **Comportamento** | 4 frases positivas e 4 negativas via `@pytest.mark.parametrize`; o caso `neutro` (texto sem opinião fica abaixo do limiar de 0.60); determinismo (mesma entrada → mesma saída) |
| **Endpoints de apoio** | `/health` com `modelo_carregado: true`, `/` e `/openapi.json` |

O arquivo completo está em [`codigo/tests/test_predict.py`](./codigo/tests/test_predict.py).

```powershell
pytest -v
```

*Esperado:* `26 passed` se você copiou o arquivo de referência inteiro. Com os seus próprios testes o número muda — o que importa é tudo verde.

> Repare no que **não** está testado: a acurácia do modelo. Isso é assunto das semanas de avaliação. O que o CI protege aqui é o **contrato**: status codes, formato e os casos óbvios. Teste de CI tem que ser rápido e determinístico, senão o time aprende a ignorá-lo.

**5. Configurar o `ruff`**

O `ruff` faz o trabalho de `flake8` + `isort` + `black` num binário só, em milissegundos. Acrescente ao `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py312"
line-length = 100

[tool.ruff.lint]
# E/W = pycodestyle, F = pyflakes, I = isort,
# UP = pyupgrade, B = bugbear, SIM = simplify.
select = ["E", "W", "F", "I", "UP", "B", "SIM"]

[tool.ruff.format]
quote-style = "double"
```

```powershell
ruff check .
ruff format --check .
```

*Esperado:* `All checks passed!` e `5 files already formatted`.
Se o `format --check` reclamar, rode `ruff format .` — ele corrige, e você commita a correção.

> ### ✅ Checkpoint 1 (~15 min)
> `pytest` verde e `ruff check .` limpo na sua máquina.
> **Todo mundo chegou até aqui?** Quem travou no venv, no `ModuleNotFoundError` ou no `with TestClient` levanta a mão agora — daqui pra frente só fica mais difícil de diagnosticar.

---

### Bloco B — O CI rodando no GitHub (passos 6 a 10, ~18 min)

**6. Criar o workflow**

```powershell
mkdir -Force .github\workflows
```

Crie `.github/workflows/ci.yml`. O arquivo completo e comentado está em [`codigo/github-actions/ci.yml`](./codigo/github-actions/ci.yml) — por enquanto, copie só até o fim do job `test`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

env:
  PYTHON_VERSION: "3.12"

jobs:
  lint:
    name: Lint (ruff)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
          cache-dependency-path: |
            app/requirements.txt
            requirements-dev.txt
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: ruff format --check .

  test:
    name: Testes (pytest)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: pip
          cache-dependency-path: |
            app/requirements.txt
            requirements-dev.txt
      - run: pip install -r requirements-dev.txt
      - run: pytest -v
```

Três coisas para notar:

- `lint` e `test` são jobs **independentes** → rodam em paralelo, em máquinas separadas. Steps dentro de um job são sequenciais.
- `PYTHON_VERSION: "3.12"` é a mesma versão do `FROM python:3.12-slim` do Dockerfile. Testar numa versão e publicar em outra é pedir para o bug aparecer só em produção.
- `cache: pip` reaproveita os pacotes entre execuções. A primeira roda leva ~1 min; a segunda, metade disso.

**7. Abrir o pull request**

```powershell
git checkout -b semana-05/ci
git add .
git commit -m "feat: adiciona testes do /predict e pipeline de CI"
git push -u origin semana-05/ci
```

Abra o PR pela interface do GitHub (ou `gh pr create --fill`).

*Esperado:* na aba **Checks** do PR aparecem `Lint (ruff)` e `Testes (pytest)`, amarelos e depois verdes.

**8. Quebrar o CI de propósito**

Esta é a parte que ensina. Um CI que você nunca viu falhar não é um CI, é decoração.

Em `app/modelo.py`, mexa no limiar — uma mudança plausível, do tipo que alguém faz "para reduzir falso positivo":

```python
LIMIAR_NEUTRO_PADRAO = 0.95   # era 0.60
```

```powershell
git commit -am "chore: aumenta o limiar de neutro para 0.95"
git push
```

*Esperado:* o job `Testes (pytest)` fica **vermelho**, e o PR mostra "Some checks were not successful". Abra o log do step `pytest -v` e leia até achar:

```
FAILED tests/test_predict.py::test_predict_classifica_positivo[adorei o atendimento, chegou antes do prazo]
AssertionError: assert 'neutro' == 'positivo'
```

Discuta com o grupo: essa mudança **não quebrou o código** — ele roda perfeitamente. Ela quebrou o **comportamento acordado**. Sem teste, isso chega em produção e vira ticket de suporte duas semanas depois.

**9. Quebrar o lint também**

Adicione um import não usado no topo de `app/main.py`:

```python
import json   # ninguém usa
```

```powershell
git commit -am "chore: import nao utilizado"
git push
```

*Esperado:* `Lint (ruff)` vermelho, com o log apontando a linha exata:

```
app/main.py:14:8: F401 [*] `json` imported but unused
  = help: Remove unused import: `json`
```

E `Testes (pytest)` continua... **vermelho também**, por causa do passo 8 — mas são falhas independentes, em jobs separados. É exatamente por isso que separamos: um relatório diz "o estilo está errado", o outro diz "o comportamento está errado".

**10. Corrigir e ver verde**

Desfaça as duas quebras. Rode local **antes** de empurrar:

```powershell
pytest -q
ruff check .
```

```powershell
git commit -am "fix: restaura o limiar e remove o import nao usado"
git push
```

*Esperado:* os dois checks verdes no PR. **Não faça o merge ainda** — o PR continua aberto para o Bloco D.

> ### ✅ Checkpoint 2 (~33 min)
> CI rodando no PR, com pelo menos uma falha vista, lida no log e corrigida.
> **Todo mundo chegou até aqui?** Problemas comuns: workflow fora de `.github/workflows/`, indentação do YAML, `requirements-dev.txt` ou `pyproject.toml` não commitados.

---

### Bloco C — Artifact Registry na mão (passos 11 a 14, ~15 min)

Antes de automatizar, faça manualmente. Se o push manual funciona, qualquer erro que sobrar no Actions é de **autenticação** — e não de Docker, rede ou nome de imagem. Isso economiza meia hora de chute.

**11. Apontar o `gcloud` para o seu projeto**

```powershell
gcloud auth login
gcloud projects list
gcloud config set project SEU-PROJECT-ID
gcloud services enable artifactregistry.googleapis.com
```

*Esperado:* `Updated property [core/project].` e `Operation ... finished successfully.`

**12. Criar o repositório**

```powershell
gcloud artifacts repositories create mlops-estudos `
    --repository-format=docker `
    --location=us-central1 `
    --description="Imagens do grupo de estudos MLOps"

gcloud artifacts repositories list --location=us-central1
```

*Esperado:* a tabela lista `mlops-estudos | DOCKER | us-central1`.
`ALREADY_EXISTS` significa que já estava criado — siga em frente.

Um "repositório" no Artifact Registry é um **namespace de imagens**, não uma imagem. O endereço final se lê assim:

```
us-central1-docker.pkg.dev / SEU-PROJECT-ID / mlops-estudos / api-sentimento : <tag>
└──── host da região ────┘   └─ projeto ──┘   └ repositório ┘  └── imagem ──┘
```

**13. Autorizar o Docker e publicar**

```powershell
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet

$Image = "us-central1-docker.pkg.dev/SEU-PROJECT-ID/mlops-estudos/api-sentimento"
$Sha = (git rev-parse HEAD).Trim()

docker build -t "${Image}:$Sha" -t "${Image}:latest" .
docker push "${Image}:$Sha"
docker push "${Image}:latest"
```

*Esperado:* uma linha `<tag>: digest: sha256:... size: ...` no fim de cada `push`.

> `denied: Permission "artifactregistry.repositories.uploadArtifacts" denied` = o `configure-docker` não rodou, ou a sua conta não tem a role `roles/artifactregistry.writer` no projeto.

O script [`codigo/scripts/01-artifact-registry.ps1`](./codigo/scripts/01-artifact-registry.ps1) faz os passos 11 a 13 de uma vez (há a versão `.sh` também).

**14. Conferir o que foi publicado**

```powershell
gcloud artifacts docker images list `
    us-central1-docker.pkg.dev/SEU-PROJECT-ID/mlops-estudos --include-tags
```

*Esperado:* uma linha com `IMAGE`, `DIGEST` e `TAGS: <sha-do-commit>, latest`.

Compare a tag com `git rev-parse HEAD`: é **o mesmo SHA**. É isso que torna a imagem rastreável — de um container rodando em produção você volta ao commit, ao PR e à discussão que o originou. `latest` não te dá nada disso: amanhã ele aponta para outra coisa, e você nunca vai saber qual versão estava no ar na hora do incidente.

> ### ✅ Checkpoint 3 (~48 min)
> Imagem publicada no Artifact Registry, com a tag do SHA, feita na mão.
> **Todo mundo chegou até aqui?** Quem está sem projeto GCP faz dupla com um colega — os passos 15 a 17 dependem disso.

---

### Bloco D — O CI publicando sozinho + branch protegida (passos 15 a 18, ~12 min)

**15. Autenticar o Actions no GCP (Workload Identity Federation)**

Existem dois caminhos:

| Caminho | Como funciona | Risco |
| --- | --- | --- |
| **WIF** (preferível) | O Actions emite um token OIDC ("sou o workflow do repositório X"); o GCP confere e devolve uma credencial válida por minutos | Nenhum segredo de longa duração; o acesso fica amarrado ao repositório |
| Chave JSON de service account | Um arquivo com chave privada guardado em *Secrets* | É um segredo permanente: se vazar (log, fork, print na tela), vale até alguém lembrar de revogar |

Rode o script de referência, que cria a service account, o pool, o provider OIDC e amarra tudo ao **seu** repositório:

```powershell
# edite ProjectId e GitHubRepo no topo do arquivo antes de rodar
.\semana-05\codigo\scripts\02-workload-identity.ps1
```

Ele imprime três valores no fim. Cadastre-os em **Settings → Secrets and variables → Actions → aba Variables** do seu repositório:

| Nome | Exemplo |
| --- | --- |
| `GCP_PROJECT_ID` | `meu-projeto-mlops` |
| `GCP_WIF_PROVIDER` | `projects/123456789/locations/global/workloadIdentityPools/github-pool/providers/github-provider` |
| `GCP_SERVICE_ACCOUNT` | `github-actions@meu-projeto-mlops.iam.gserviceaccount.com` |

> São **Variables**, não **Secrets**: nenhum dos três é sigiloso. O que protege o acesso é a `attribute-condition` do provider, que só aceita token vindo do seu repositório. Sem essa condição, qualquer repositório do GitHub poderia assumir a sua service account.
>
> **Plano B** (se o WIF não sair no tempo do encontro): `gcloud iam service-accounts keys create chave.json --iam-account=...`, cole o conteúdo num Secret `GCP_SA_KEY` e troque o bloco `with:` do step de autenticação por `credentials_json: ${{ secrets.GCP_SA_KEY }}`. Confirme que `chave.json` está no `.gitignore` e, depois do encontro, **revogue a chave** com `gcloud iam service-accounts keys delete`.

**16. Acrescentar o job de build e push**

Copie o job `build-and-push` de [`codigo/github-actions/ci.yml`](./codigo/github-actions/ci.yml) para o fim do seu `ci.yml`. Os quatro pontos que importam:

```yaml
  build-and-push:
    needs: [lint, test]                  # só roda se lint e test passaram
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    permissions:
      contents: read
      id-token: write                    # exigido pelo WIF: emite o token OIDC
```

```yaml
      - run: |
          docker build \
            --tag "$IMAGEM:${{ github.sha }}" \
            --tag "$IMAGEM:latest" \
            .
```

O `if` é o que separa CI de CD: pull request **testa**, merge na `main` **publica**. E o workflow ainda roda um smoke test — sobe o container e bate no `/health` — antes do push: imagem que não responde não chega ao registry.

```powershell
git commit -am "ci: publica a imagem no Artifact Registry no merge"
git push
```

*Esperado:* no PR, `build-and-push` aparece como **Skipped**. É o comportamento correto — o `if` barra pull request. Só `lint` e `test` precisam estar verdes para liberar o merge.

**17. Fazer o merge e ver a imagem aparecer**

Faça o merge do PR na `main` pela interface do GitHub.

*Esperado:* na aba **Actions**, uma nova execução na `main`, agora com os três jobs. O `build-and-push` leva ~2 min. No fim, o **Summary** da execução mostra o endereço completo da imagem publicada.

```powershell
git checkout main
git pull
gcloud artifacts docker images list `
    us-central1-docker.pkg.dev/SEU-PROJECT-ID/mlops-estudos --include-tags
```

*Esperado:* uma imagem nova, com a tag igual ao SHA do **commit de merge**. Confira com `git log -1 --format=%H`.

**18. Proteger a `main`**

De nada adianta o CI se dá para contorná-lo. Em **Settings → Rules → Rulesets → New branch ruleset** (ou *Settings → Branches → Add rule*, nas interfaces mais antigas):

- Target: `main`
- ✅ **Require a pull request before merging**
- ✅ **Require status checks to pass before merging** → adicione `Lint (ruff)` e `Testes (pytest)`
  - os checks só aparecem na lista depois de terem rodado pelo menos uma vez
  - **não** adicione `Build e push...`: ele é `Skipped` em PR e travaria o merge para sempre
- ✅ **Require branches to be up to date before merging**
- ✅ **Block force pushes**

Teste que a regra pegou:

```powershell
git checkout main
"teste" | Add-Content README.md
git commit -am "test: tentativa de push direto na main"
git push
```

*Esperado:* o push é **recusado**:

```
! [remote rejected] main -> main (protected branch hook declined)
```

Desfaça com `git reset --hard origin/main`.

> ### ✅ Checkpoint final (~60 min)
> CI verde obrigatório no PR, imagem publicada automaticamente no merge com a tag do SHA, e `main` protegida contra push direto.
> **Todo mundo chegou até aqui?** Quem ficou para trás: o estado final está todo em [`codigo/`](./codigo/) — dá para seguir sozinho depois do encontro, e o [`desafio.md`](./desafio.md) cobra exatamente isso.

---

## Código

O código de apoio desta semana vive em [`codigo/`](./codigo/), com instruções de execução em [`codigo/README.md`](./codigo/README.md).

| Caminho | O que é |
| --- | --- |
| [`codigo/app/main.py`](./codigo/app/main.py) | API FastAPI: `/`, `GET /health` e `POST /predict` (vem da Semana 04) |
| [`codigo/app/modelo.py`](./codigo/app/modelo.py) | TF-IDF + Regressão Logística, treinado no startup (vem da Semana 04) |
| [`codigo/app/requirements.txt`](./codigo/app/requirements.txt) | Dependências de runtime — as que entram na imagem |
| [`codigo/Dockerfile`](./codigo/Dockerfile) | Imagem multi-stage, usuário não-root, `HEALTHCHECK` (vem da Semana 04) |
| [`codigo/tests/test_predict.py`](./codigo/tests/test_predict.py) | **Novo:** 26 testes — status codes, formato da resposta, comportamento e endpoints de apoio |
| [`codigo/tests/conftest.py`](./codigo/tests/conftest.py) | **Novo:** fixture do `TestClient` com `lifespan` |
| [`codigo/pyproject.toml`](./codigo/pyproject.toml) | **Novo:** configuração do `pytest` e do `ruff` |
| [`codigo/requirements-dev.txt`](./codigo/requirements-dev.txt) | **Novo:** runtime + `pytest` + `ruff` — o que o CI instala |
| [`codigo/github-actions/ci.yml`](./codigo/github-actions/ci.yml) | **Novo:** workflow de exemplo (lint, test, build e push) |
| [`codigo/scripts/01-artifact-registry.ps1`](./codigo/scripts/01-artifact-registry.ps1) · [`.sh`](./codigo/scripts/01-artifact-registry.sh) | **Novo:** `gcloud` para criar o repositório e publicar na mão |
| [`codigo/scripts/02-workload-identity.ps1`](./codigo/scripts/02-workload-identity.ps1) · [`.sh`](./codigo/scripts/02-workload-identity.sh) | **Novo:** `gcloud` para configurar o WIF do GitHub Actions |

> ⚠️ `codigo/github-actions/ci.yml` está **fora** de `.github/workflows/` de propósito: assim ele não vira um pipeline ativo do repositório do grupo, que sairia tentando publicar imagem no GCP a cada push. Ele só roda depois de ser copiado para `.github/workflows/ci.yml` do **repositório pessoal** de cada participante.

---

## Recursos e links

- [GitHub Actions — documentação](https://docs.github.com/actions)
- [Sintaxe do workflow — referência de `on`, `jobs`, `needs`, `if`, `permissions`](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions)
- [Variáveis e contextos do Actions (`github.sha`, `github.ref`, `vars`, `secrets`)](https://docs.github.com/actions/learn-github-actions/contexts)
- [Artifact Registry — documentação](https://cloud.google.com/artifact-registry/docs)
- [Artifact Registry — push e pull de imagens Docker](https://cloud.google.com/artifact-registry/docs/docker/pushing-and-pulling)
- [`google-github-actions/auth` — autenticar o Actions no Google Cloud](https://github.com/google-github-actions/auth)
- [Workload Identity Federation com pipelines de deploy (guia do GCP)](https://cloud.google.com/iam/docs/workload-identity-federation-with-deployment-pipelines)
- [Security hardening do GitHub Actions (secrets, OIDC, forks)](https://docs.github.com/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
- [Ruff — linter e formatador Python](https://docs.astral.sh/ruff/)
- [FastAPI — testando com `TestClient`](https://fastapi.tiangolo.com/tutorial/testing/)
- [FastAPI — eventos de `lifespan` (por que o `with` importa nos testes)](https://fastapi.tiangolo.com/advanced/events/)
- [GitHub — rulesets e proteção de branch](https://docs.github.com/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets)

---

## Notas para o host

- Material de referência do grupo anterior: `presentation/primeiro-semestre/aula10` na branch `main` (pode ser reaproveitado)
- Prefira Workload Identity Federation a chave JSON de service account; se faltar tempo, use a chave, explique o risco e **combine a revogação** para depois do encontro
- Minutos de Actions são limitados em repositório privado — oriente a turma a usar repositório público
- Tenha um workflow de exemplo pronto para colar, caso alguém trave no YAML: é [`codigo/github-actions/ci.yml`](./codigo/github-actions/ci.yml)
- O passo 8 (quebrar o CI de propósito) é o coração do encontro — não corte se o tempo apertar; prefira cortar o passo 9
- O `with TestClient(app)` do passo 3 derruba gente todo ano. Mostre o erro acontecendo antes de alguém sofrer sozinho
- O Bloco C depende de projeto GCP com billing. Levante na semana anterior quem não tem e organize as duplas antes
- A primeira execução do workflow não tem cache de pip (`scikit-learn` é o download pesado): avise que ~1 min é normal e que a segunda cai pela metade
- Peça que todos rodem `pip install -r requirements-dev.txt` **antes** do encontro — baixar na hora, em rede compartilhada, come 10 min do lab

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [x] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Deixar um projeto GCP de demonstração com o Artifact Registry já criado (plano B)
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
