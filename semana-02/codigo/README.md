# Código — Semana 02 (Como a web funciona I: Redes)

Servidor HTTP que serve o modelo de análise de sentimento **sem framework
nenhum**: só `http.server`, da biblioteca padrão do Python.

```
codigo/
├── servidor.py         # o servidor: roteamento, parse do corpo e status codes na mão
├── modelo.py           # TF-IDF + Regressão Logística + mini-dataset PT-BR
├── exemplos_curl.md    # um curl para cada rota e cada erro
├── requirements.txt    # só o scikit-learn (o servidor não precisa de nada)
└── README.md           # este arquivo
```

O modelo é treinado **em memória, no startup**, a partir de ~60 frases embutidas
em `modelo.py`. Não baixa nada, não precisa de GPU e leva milissegundos. É o
mesmo classificador que acompanha o grupo até o fim do semestre.

---

## Subir o servidor

A partir desta pasta (`semana-02/codigo/`):

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

python servidor.py
```

Saída esperada:

```
2026-11-04 14:10:26,541 | INFO | modelo 'tfidf+logreg' treinado em 16 ms (acurácia no treino: 1.00)
2026-11-04 14:10:26,619 | INFO | servindo em http://127.0.0.1:8000 (Ctrl+C para parar)
```

Opções:

```bash
python servidor.py --porta 8080     # outra porta
python servidor.py --host 0.0.0.0   # aceita conexões de outras máquinas da rede
```

> `127.0.0.1` só aceita conexões da **própria máquina**. Para o colega do lado
> alcançar o seu servidor, é `--host 0.0.0.0` — e é exatamente o mesmo motivo
> pelo qual, na Semana 04, o container precisa de `--host 0.0.0.0` para que o
> `-p 8000:8000` funcione.

Para testar o modelo sem servidor nenhum:

```bash
python modelo.py
```

```
('positivo', 0.7274)     adorei o atendimento, chegou antes do prazo
('negativo', 0.7708)     pessimo, veio quebrado e atrasado
('neutro', 0.5534)       o pedido chegou
```

---

## Testar

```bash
curl -i http://127.0.0.1:8000/health

curl -X POST http://127.0.0.1:8000/prever \
  -H "Content-Type: application/json" \
  -d '{"texto": "adorei o atendimento, chegou antes do prazo"}'
```

```json
{"texto": "adorei o atendimento, chegou antes do prazo", "sentimento": "positivo", "score": 0.7274, "modelo": "tfidf+logreg"}
```

> **Windows / PowerShell:** `curl` é apelido de `Invoke-WebRequest` e não aceita
> `-X`/`-d`/`-i`. Use `curl.exe` (vem com o Windows 10+) ou:
>
> ```powershell
> Invoke-RestMethod -Uri http://127.0.0.1:8000/prever -Method Post `
>   -ContentType "application/json" `
>   -Body '{"texto": "adorei o atendimento, chegou antes do prazo"}'
> ```

A bateria completa — incluindo todos os casos de erro — está em
[`exemplos_curl.md`](./exemplos_curl.md).

---

## Contrato do servidor

| Método | Rota | Entrada | Status | Saída |
| --- | --- | --- | --- | --- |
| `GET` | `/` | — | `200` | metadados e lista de rotas |
| `GET` | `/health` | — | `200` | `{"status","modelo_carregado","versao"}` |
| `POST` | `/prever` | `{"texto": "..."}` (1–1000 chars) | `200` | `{"texto","sentimento","score","modelo"}` |

`sentimento` ∈ `positivo` \| `negativo` \| `neutro`. O rótulo vira `neutro`
quando a confiança fica abaixo de `LIMIAR_NEUTRO_PADRAO` (`0.60`).

### Erros

| Status | Quando | Exemplo de corpo |
| --- | --- | --- |
| `400 Bad Request` | corpo não é JSON válido, está vazio ou o `Content-Length` é inválido | `{"erro": "corpo não é um JSON válido", ...}` |
| `404 Not Found` | caminho não existe | `{"erro": "rota não encontrada", ...}` |
| `405 Method Not Allowed` | caminho existe, método não (manda `Allow`) | `{"erro": "método não permitido nesta rota", ...}` |
| `413 Content Too Large` | corpo acima de 64 KB | `{"erro": "corpo grande demais", ...}` |
| `415 Unsupported Media Type` | `Content-Type` não é `application/json` | `{"erro": "Content-Type não suportado", ...}` |
| `422 Unprocessable Content` | JSON válido, contrato violado | `{"erro": "não pode ser vazio", "campo": "texto"}` |
| `500 Internal Server Error` | exceção não tratada (bug nosso) | `{"erro": "erro interno no servidor"}` |

---

## O que o `servidor.py` faz na mão

Tudo o que o FastAPI esconde na Semana 03:

| No `servidor.py` | Na Semana 03 (FastAPI) |
| --- | --- |
| dicionário `ROTAS` + `_tratar()` | `@app.get("/")`, `@app.post("/predict")` |
| `_ler_corpo_bruto()` lendo `Content-Length` | injeção do `body` no parâmetro da função |
| `json.loads` / `json.dumps` explícitos | serialização automática |
| `_validar_texto()` com `if` atrás de `if` | modelo Pydantic com `Field(min_length=1)` |
| `self.send_response(404)` escrito por você | `HTTPException(status_code=404)` |
| `Content-Length` calculado à mão | — (o framework calcula) |
| nenhuma documentação | `/docs` gerado sozinho |

Não é "o jeito certo de servir modelo em produção" — é o jeito de **entender** o
que a produção faz. A versão de verdade começa na Semana 03.
