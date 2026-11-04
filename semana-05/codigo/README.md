# Código — Semana 05 (CI + Artifact Registry)

A API de análise de sentimento no estado em que ela chega à Semana 05: a mesma da Semana 04, containerizada e funcionando. O que esta semana acrescenta é o que está **em volta** dela — testes, lint e pipeline.

`app/` e `Dockerfile` são cópias fiéis de [`semana-04/codigo/`](../../semana-04/codigo/): nesta semana a aplicação é o objeto de teste, não o que está sendo construído.

Este diretório é **autossuficiente** — dá para pegar só ele e rodar tudo.

---

## Layout

```
codigo/
├── app/                       # ── vem da Semana 04, sem mudança de comportamento
│   ├── __init__.py
│   ├── main.py                #    endpoints /, /health e /predict (FastAPI)
│   ├── modelo.py              #    TF-IDF + Regressão Logística, treinado no startup
│   └── requirements.txt       #    dependências de runtime (vão para a imagem)
├── Dockerfile                 #    multi-stage, usuário não-root, HEALTHCHECK
├── .dockerignore
│
├── tests/                     # ── novo na Semana 05
│   ├── conftest.py            #    fixture do TestClient (com lifespan!)
│   └── test_predict.py        #    26 testes do /predict, /health e /
├── pyproject.toml             #    configuração do pytest e do ruff
├── requirements-dev.txt       #    runtime + pytest + ruff (o que o CI instala)
├── github-actions/
│   └── ci.yml                 #    workflow de EXEMPLO — não roda daqui
└── scripts/
    ├── 01-artifact-registry.{sh,ps1}   # cria o repositório e faz o push manual
    └── 02-workload-identity.{sh,ps1}   # configura o WIF para o GitHub Actions
```

O layout espelha exatamente o que deve existir na **raiz do seu repositório pessoal**. Copie o conteúdo daqui para lá e os caminhos do workflow funcionam sem ajuste.

---

## Rodar os testes localmente

```powershell
cd semana-05\codigo

python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Linux/macOS: source .venv/bin/activate

pip install -r requirements-dev.txt

pytest -v
```

Esperado: **26 passed**, em cerca de 1 segundo.

> `ModuleNotFoundError: No module named 'app'` significa que você rodou de fora de `semana-05/codigo/` — é de lá que o `pythonpath = ["."]` do `pyproject.toml` é resolvido.

### Lint

```powershell
ruff check .            # erros de lint
ruff format --check .   # formatação
```

Esperado: `All checks passed!` e `5 files already formatted`.
`ruff format .` (sem o `--check`) corrige a formatação no lugar.

### Subir a API

```powershell
uvicorn app.main:app --reload --port 8000
```

Documentação interativa em <http://localhost:8000/docs>.

> **Windows / PowerShell:** `curl` é apelido de `Invoke-WebRequest` e **não** aceita `-X`/`-d`. Use `curl.exe`.

```powershell
curl.exe -X POST http://localhost:8000/predict `
  -H "Content-Type: application/json" `
  -d '{\"texto\": \"adorei o atendimento, chegou antes do prazo\"}'
```

```json
{"texto":"adorei o atendimento, chegou antes do prazo","sentimento":"positivo","score":0.7274,"modelo":"tfidf+logreg"}
```

### Build da imagem

```powershell
docker build -t sentimento-api:semana-05 .
docker run --rm -p 8000:8000 sentimento-api:semana-05
```

---

## Ativar o workflow no seu repositório pessoal

`github-actions/ci.yml` **não roda a partir daqui** — e isso é de propósito. O GitHub Actions só executa workflows que estejam em `.github/workflows/` na raiz do repositório. Se este arquivo estivesse lá, o repositório do grupo sairia tentando publicar imagem no GCP a cada push.

Para ativar no **seu** repositório:

```powershell
mkdir -Force .github\workflows
copy semana-05\codigo\github-actions\ci.yml .github\workflows\ci.yml
```

Depois:

1. Ajuste o bloco `env:` no topo do arquivo (`GCP_REGION`, `AR_REPOSITORY`, `IMAGE_NAME`).
2. Rode `scripts/02-workload-identity.*` e cadastre as três *Variables* no GitHub (`GCP_PROJECT_ID`, `GCP_WIF_PROVIDER`, `GCP_SERVICE_ACCOUNT`).
3. Commite, abra um pull request e veja o CI rodar.

O passo a passo detalhado está no [README da semana](../README.md#passo-a-passo).

---

## O que os testes cobrem

| Bloco | Protege contra |
| --- | --- |
| Status codes | `200` no caminho feliz; `422` sem `texto`, vazio, longo demais ou com tipo errado; `405` no `GET /predict` |
| Formato da resposta | chaves exatas (`texto`, `sentimento`, `score`, `modelo`), tipos, `score` entre 0 e 1, `modelo` identificado |
| Comportamento | 4 frases positivas e 4 negativas parametrizadas, o caso `neutro` abaixo do limiar e o determinismo |
| Endpoints de apoio | `/health` com `modelo_carregado: true`, `/` e `/openapi.json` |

A fixture em `conftest.py` usa `with TestClient(app)`. Isso não é detalhe de estilo: é o `with` que dispara o `lifespan` do FastAPI e treina o modelo. Sem ele, `estado["modelo"]` fica `None` e todo `/predict` estoura.

---

## Sobre os scripts `gcloud`

Ambos são **idempotentes** — rodar duas vezes não quebra nada (o `gcloud` devolve `ALREADY_EXISTS` e segue). Edite as variáveis no topo de cada arquivo antes de executar.

| Script | O que faz |
| --- | --- |
| `01-artifact-registry` | Habilita a API, cria o repositório Docker, autoriza o Docker local e faz build + push com a tag do SHA |
| `02-workload-identity` | Cria a service account, o Workload Identity Pool e o provider OIDC do GitHub, amarrados ao **seu** repositório; imprime os três valores a cadastrar no GitHub |

Nenhum dos dois grava credencial em arquivo. Se você acabar optando pela chave JSON (plano B), confirme que o `.json` está no `.gitignore` e **revogue a chave** depois do encontro.
