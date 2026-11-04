# Código — Semana 04 (Docker)

API de análise de sentimento da Semana 03, agora pronta para rodar em container,
junto de uma mini-UI que conversa com ela pela network do Compose.

```
codigo/
├── app/                   # a API FastAPI
│   ├── main.py            # rotas /, /health e /predict
│   ├── modelo.py          # TF-IDF + Regressão Logística + mini-dataset PT-BR
│   └── requirements.txt
├── ui/                    # segundo serviço: mini-UI Streamlit
│   ├── app_ui.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
├── Dockerfile             # imagem da API (multi-stage)
├── .dockerignore
└── docker-compose.yml     # api + ui
```

O modelo é treinado **em memória, no startup**, a partir de ~60 frases embutidas
em `app/modelo.py`. Não baixa nada, não precisa de GPU e leva milissegundos.

---

## Rodar sem Docker (opcional, para comparar)

A partir desta pasta (`semana-04/codigo/`):

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r app/requirements.txt
uvicorn app.main:app --reload --port 8000
```

Documentação interativa: <http://localhost:8000/docs>

---

## Rodar só a API em container

```bash
docker build -t sentimento-api:semana-04 .
docker run --rm -p 8000:8000 --name sentimento-api sentimento-api:semana-04
```

Testar o `/predict`:

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"texto": "adorei o atendimento, chegou antes do prazo"}'
```

Resposta esperada:

```json
{
  "texto": "adorei o atendimento, chegou antes do prazo",
  "sentimento": "positivo",
  "score": 0.7274,
  "modelo": "tfidf+logreg"
}
```

> **Windows / PowerShell:** `curl` é apelido de `Invoke-WebRequest` e não aceita
> `-X`/`-d`. Use `curl.exe` (vem com o Windows 10+) ou:
>
> ```powershell
> Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post `
>   -ContentType "application/json" `
>   -Body '{"texto": "adorei o atendimento, chegou antes do prazo"}'
> ```

---

## Subir os dois serviços com Compose

```bash
docker compose up --build
```

| Serviço | URL | O que é |
| --- | --- | --- |
| `api` | <http://localhost:8000/docs> | FastAPI + modelo de sentimento |
| `ui` | <http://localhost:8501> | Streamlit que chama `http://api:8000` |

A UI só sobe depois que o `healthcheck` da API passa (`depends_on: service_healthy`).
Acompanhe com:

```bash
docker compose ps          # coluna STATUS mostra (healthy)
docker compose logs -f api
docker compose down        # derruba tudo
```

---

## Contrato da API

| Método | Rota | Entrada | Saída |
| --- | --- | --- | --- |
| `GET` | `/` | — | metadados do serviço |
| `GET` | `/health` | — | `{"status","modelo_carregado","versao"}` |
| `POST` | `/predict` | `{"texto": "..."}` (1 a 1000 chars) | `{"texto","sentimento","score","modelo"}` |

`sentimento` ∈ `positivo` \| `negativo` \| `neutro`. O rótulo vira `neutro` quando
a confiança fica abaixo de `LIMIAR_NEUTRO` (padrão `0.60`, configurável por
variável de ambiente). Texto vazio ou campo faltando devolve **422**, cortesia do
Pydantic.
