# Código — Semana 03 (APIs com FastAPI)

A API de análise de sentimento do grupo, na sua primeira versão: FastAPI +
Pydantic + Uvicorn, sem Docker (isso é a Semana 04).

```
codigo/
├── app/
│   ├── __init__.py
│   ├── main.py             # rotas /, /health e POST /predict
│   ├── modelo.py           # TF-IDF + Regressão Logística + mini-dataset PT-BR
│   └── requirements.txt    # dependências com versão fixada
└── exemplos_requests.http  # requisições prontas (VS Code REST Client)
```

O modelo é treinado **em memória, no startup**, a partir de ~60 frases embutidas
em `app/modelo.py`. Não baixa nada, não precisa de GPU e leva milissegundos.

---

## Rodar

A partir desta pasta (`semana-03/codigo/`):

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r app/requirements.txt
uvicorn app.main:app --reload --port 8000
```

Nos logs você deve ver:

```
modelo 'tfidf+logreg' treinado em 31 ms (acurácia no treino: 1.00, limiar neutro: 0.60)
Uvicorn running on http://127.0.0.1:8000
```

| URL | O que é |
| --- | --- |
| <http://localhost:8000/docs> | Swagger UI — dá para testar a API pelo navegador |
| <http://localhost:8000/redoc> | A mesma documentação, em outro layout |
| <http://localhost:8000/openapi.json> | O contrato da API em JSON (OpenAPI) |

O `--reload` reinicia o servidor a cada alteração de arquivo. É ótimo para o
lab e **não** deve ir para produção.

---

## Exemplos de `curl`

```bash
# metadados do serviço
curl http://localhost:8000/

# health check
curl http://localhost:8000/health
# {"status":"ok","modelo_carregado":true,"versao":"1.0.0"}

# predição — caso positivo
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"texto": "adorei o atendimento, chegou antes do prazo"}'

# predição — caso negativo
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"texto": "pessimo, veio quebrado e atrasado"}'

# erro de validação — devolve 422
curl -i -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"texto": ""}'
```

Resposta esperada do caso positivo:

```json
{
  "texto": "adorei o atendimento, chegou antes do prazo",
  "sentimento": "positivo",
  "score": 0.7274,
  "modelo": "tfidf+logreg"
}
```

(o `score` pode variar nos últimos decimais conforme a versão do scikit-learn;
o que importa é o `sentimento`)

> **Windows / PowerShell:** `curl` é apelido de `Invoke-WebRequest` e não aceita
> `-X`/`-d`. Use `curl.exe` (vem com o Windows 10+) ou:
>
> ```powershell
> Invoke-RestMethod -Uri http://localhost:8000/predict -Method Post `
>   -ContentType "application/json" `
>   -Body '{"texto": "adorei o atendimento, chegou antes do prazo"}'
> ```

Para quem usa VS Code, o arquivo [`exemplos_requests.http`](./exemplos_requests.http)
traz as mesmas chamadas (e os casos de erro) prontas para disparar com a
extensão REST Client.

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

**Este contrato está congelado**: a Semana 04 empacota exatamente esta API em um
container, a Semana 07 a publica no Cloud Run e a Semana 10 a usa no load test.
Mudou o contrato aqui, quebrou lá na frente.

---

## Variáveis de ambiente

| Variável | Padrão | O que faz |
| --- | --- | --- |
| `LIMIAR_NEUTRO` | `0.60` | Abaixo desta confiança, o sentimento vira `neutro` |

```bash
LIMIAR_NEUTRO=0.9 uvicorn app.main:app --port 8000   # quase tudo vira "neutro"
```
