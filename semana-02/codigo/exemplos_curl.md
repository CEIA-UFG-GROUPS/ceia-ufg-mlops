# Exemplos de `curl` — Semana 02

Todos os comandos assumem o servidor rodando em `http://127.0.0.1:8000`:

```bash
cd semana-02/codigo
python servidor.py
```

> **Windows / PowerShell:** `curl` é apelido de `Invoke-WebRequest` e **não**
> aceita `-X`, `-d` nem `-i`. Use **`curl.exe`** (vem com o Windows 10+) no lugar
> de `curl`, ou o `Invoke-RestMethod` indicado no final de cada bloco.
> No Git Bash e no WSL, `curl` já é o curl de verdade.

Flags úteis:

| Flag | O que faz |
| --- | --- |
| `-i` | mostra os **headers de resposta** junto do corpo |
| `-v` | mostra a conversa inteira: `>` = o que foi enviado, `<` = o que voltou |
| `-X` | escolhe o **método** HTTP |
| `-H` | acrescenta um **header** de requisição |
| `-d` | manda um **corpo** (e muda o método para POST automaticamente) |
| `-o /dev/null -w "%{http_code}\n"` | imprime só o **status code** |

---

## 1. `GET /` — 200 OK

```bash
curl -i http://127.0.0.1:8000/
```

```http
HTTP/1.1 200 OK
Server: servidor-sentimento/1.0.0
Date: Wed, 04 Nov 2026 17:10:26 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 223

{"servico": "servidor-sentimento", "versao": "1.0.0", "modelo": "tfidf+logreg", "rotas": {...}}
```

## 2. `GET /health` — 200 OK

```bash
curl -i http://127.0.0.1:8000/health
```

```json
{"status": "ok", "modelo_carregado": true, "versao": "1.0.0"}
```

É a rota que o Docker (Semana 04) e o Cloud Run (Semana 07) vão chamar para
decidir se o serviço recebe tráfego.

## 3. `POST /prever` — 200 OK (caso positivo)

```bash
curl -i -X POST http://127.0.0.1:8000/prever \
  -H "Content-Type: application/json" \
  -d '{"texto": "adorei o atendimento, chegou antes do prazo"}'
```

```json
{"texto": "adorei o atendimento, chegou antes do prazo", "sentimento": "positivo", "score": 0.7274, "modelo": "tfidf+logreg"}
```

## 4. `POST /prever` — 200 OK (caso negativo)

```bash
curl -X POST http://127.0.0.1:8000/prever \
  -H "Content-Type: application/json" \
  -d '{"texto": "pessimo, veio quebrado e atrasado"}'
```

```json
{"texto": "pessimo, veio quebrado e atrasado", "sentimento": "negativo", "score": 0.7708, "modelo": "tfidf+logreg"}
```

## 5. `POST /prever` — 200 OK (caso neutro)

Quando a confiança fica abaixo de `0.60`, o rótulo vira `neutro` em vez de
cravar um palpite:

```bash
curl -X POST http://127.0.0.1:8000/prever \
  -H "Content-Type: application/json" \
  -d '{"texto": "o pedido chegou"}'
```

```json
{"texto": "o pedido chegou", "sentimento": "neutro", "score": 0.5534, "modelo": "tfidf+logreg"}
```

---

## 6. Rota que não existe — 404 Not Found

```bash
curl -i http://127.0.0.1:8000/predict
```

```http
HTTP/1.1 404 Not Found
```
```json
{"erro": "rota não encontrada", "caminho": "/predict", "rotas_disponiveis": ["/", "/health", "/prever"]}
```

**404** = o servidor respondeu (ele está vivo!), mas não há nada nesse caminho.
Repare que `/predict` é o nome que a rota vai ter na Semana 03 — aqui ela se
chama `/prever`.

## 7. Método errado na rota certa — 405 Method Not Allowed

```bash
curl -i http://127.0.0.1:8000/prever
```

```http
HTTP/1.1 405 Method Not Allowed
Allow: POST
```
```json
{"erro": "método não permitido nesta rota", "metodo": "GET", "permitidos": ["POST"]}
```

**405** ≠ 404: a rota existe, o verbo é que não serve. A RFC obriga o servidor a
mandar o header `Allow` dizendo o que ele aceitaria.

## 8. Corpo que não é JSON válido — 400 Bad Request

```bash
curl -i -X POST http://127.0.0.1:8000/prever \
  -H "Content-Type: application/json" \
  -d '{"texto": '
```

```http
HTTP/1.1 400 Bad Request
```
```json
{"erro": "corpo não é um JSON válido", "detalhe": "Expecting value: line 1 column 11 (char 10)"}
```

**400** = "não consegui nem entender os bytes que você mandou".

## 9. JSON válido, conteúdo inválido — 422 Unprocessable Content

```bash
# texto vazio
curl -i -X POST http://127.0.0.1:8000/prever \
  -H "Content-Type: application/json" -d '{"texto": ""}'

# campo obrigatório ausente
curl -X POST http://127.0.0.1:8000/prever \
  -H "Content-Type: application/json" -d '{"frase": "oi"}'

# tipo errado
curl -X POST http://127.0.0.1:8000/prever \
  -H "Content-Type: application/json" -d '{"texto": 42}'
```

```http
HTTP/1.1 422 Unprocessable Content
```
```json
{"erro": "não pode ser vazio", "campo": "texto"}
{"erro": "campo obrigatório ausente", "campo": "texto"}
{"erro": "deve ser string, recebido int", "campo": "texto"}
```

**422** = "entendi perfeitamente o JSON, mas o conteúdo não obedece ao contrato".
É exatamente o código que o Pydantic devolve sozinho na Semana 03.

## 10. `Content-Type` errado — 415 Unsupported Media Type

```bash
curl -i -X POST http://127.0.0.1:8000/prever -d '{"texto": "oi"}'
```

```http
HTTP/1.1 415 Unsupported Media Type
```
```json
{"erro": "Content-Type não suportado", "recebido": "application/x-www-form-urlencoded", "esperado": "application/json"}
```

Sem o `-H "Content-Type: application/json"`, o curl anuncia o corpo como
formulário. O corpo até *é* JSON, mas o cliente mentiu sobre o formato — e o
servidor confia no header, não adivinha.

## 11. Corpo vazio — 400 Bad Request

```bash
curl -X POST http://127.0.0.1:8000/prever \
  -H "Content-Type: application/json" -d ''
```

```json
{"erro": "corpo vazio: envie um JSON com o campo 'texto'"}
```

## 12. Corpo grande demais — 413 Content Too Large

```bash
python -c "
import json, urllib.request, urllib.error
dados = json.dumps({'texto': 'a' * 70000}).encode()
req = urllib.request.Request('http://127.0.0.1:8000/prever', data=dados,
                             headers={'Content-Type': 'application/json'}, method='POST')
try:
    urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print(e.code, e.read().decode())
"
```

```
413 {"erro": "corpo grande demais", "limite_bytes": 65536}
```

Sem esse limite, qualquer cliente derruba o servidor anunciando um
`Content-Length` gigante.

---

## Resumo dos status codes do lab

| Código | Família | Significado | Como provocar |
| --- | --- | --- | --- |
| `200 OK` | 2xx sucesso | deu certo | `GET /health` |
| `400 Bad Request` | 4xx culpa do cliente | corpo ilegível | JSON truncado |
| `404 Not Found` | 4xx culpa do cliente | rota inexistente | `GET /predict` |
| `405 Method Not Allowed` | 4xx culpa do cliente | verbo errado | `GET /prever` |
| `413 Content Too Large` | 4xx culpa do cliente | corpo acima do limite | 70 KB de texto |
| `415 Unsupported Media Type` | 4xx culpa do cliente | formato não suportado | `POST` sem `Content-Type` |
| `422 Unprocessable Content` | 4xx culpa do cliente | contrato violado | `{"texto": ""}` |
| `500 Internal Server Error` | 5xx culpa do servidor | bug nosso | exceção não tratada |

Regra de bolso: **4xx = o cliente errou, 5xx = o servidor errou.** Devolver 500
para um corpo malformado é esconder bug do cliente atrás de culpa sua.

---

## Versão PowerShell (sem `curl.exe`)

```powershell
Invoke-RestMethod -Uri http://127.0.0.1:8000/health

Invoke-RestMethod -Uri http://127.0.0.1:8000/prever -Method Post `
  -ContentType "application/json" `
  -Body '{"texto": "adorei o atendimento, chegou antes do prazo"}'
```

Para **ver o status code dos erros** (o `Invoke-RestMethod` lança exceção em 4xx):

```powershell
try {
  Invoke-RestMethod -Uri http://127.0.0.1:8000/predict
} catch {
  $_.Exception.Response.StatusCode.value__   # 404
}
```
