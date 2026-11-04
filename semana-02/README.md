# Semana 02 — Como a web funciona I (Redes)

> **Encontro 3 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

O que acontece entre digitar uma URL e receber uma resposta — e por que isso importa para quem vai colocar um modelo no ar.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Explicar o caminho de uma requisição: DNS, TCP, TLS e HTTP
- Ler e interpretar métodos, headers, corpo e status codes em uma troca HTTP real
- Entender portas, `localhost`, `0.0.0.0` e por que o servidor "parece não responder"
- Escrever um servidor HTTP do zero com a biblioteca padrão, roteando caminho e método na mão
- Escolher o status code certo para cada situação (200, 400, 404, 405, 415, 422, 500)
- Servir o modelo de sentimento por HTTP **sem nenhum framework**

---

## Pré-requisitos

- Semana 01 concluída (terminal e Git confortáveis)
- Python 3.10+ instalado no ambiente local (`python --version`)
- `curl` funcionando: Git Bash, WSL ou `curl.exe` no PowerShell
- `scikit-learn` instalado (`pip install -r semana-02/codigo/requirements.txt`) — **antes** do encontro, para não gastar o lab esperando o `pip`
- Repositório do grupo clonado

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- Modelo cliente-servidor e o ciclo request/response
- DNS: do nome ao IP, cache e por que a mudança demora a propagar
- TCP, portas e sockets — o mínimo necessário
- HTTP vs HTTPS: o que o TLS protege e o que ele não protege
- Anatomia de uma requisição: método, path, headers, body e status

### 💻 Mão na massa (~60 min)

- Inspecionar requisições reais com `curl -v`, `dig`/`nslookup` e `ss`/`netstat`
- Escrever um servidor HTTP mínimo com `http.server`, respondendo `GET /` e `GET /health`
- Acrescentar `POST /prever`: ler o corpo JSON, chamar o modelo e devolver JSON
- Tratar erros de verdade: 404, 405, 400 e 422, cada um no seu lugar
- Fechar o ciclo testando tudo com `curl` e lendo os headers de resposta

### 🎯 Desafio (~15 min)

Subir o **seu** servidor HTTP cru servindo o modelo de sentimento, com `/health`,
um endpoint de predição e pelo menos três status codes tratados corretamente.

Enunciado completo em [`desafio.md`](./desafio.md).

---

## Passo a passo

Todos os comandos rodam a partir de `semana-02/codigo/`.

> **Windows / PowerShell:** `curl` é apelido de `Invoke-WebRequest` e **não**
> aceita `-X`, `-d` nem `-i`. Use **`curl.exe`** no lugar de `curl`, ou o
> `Invoke-RestMethod` indicado no [`codigo/exemplos_curl.md`](./codigo/exemplos_curl.md).
> No Git Bash e no WSL, `curl` já é o curl de verdade.

### Bloco 1 — HTTP de verdade, por fora (~20 min)

O objetivo deste bloco é **ver** o protocolo antes de escrevê-lo. Nada de código
ainda.

1. **Do nome ao número: DNS.** Antes de qualquer HTTP, o cliente precisa
   descobrir o IP por trás do nome.

   ```bash
   dig +short developer.mozilla.org        # Linux/macOS/WSL
   nslookup developer.mozilla.org          # Windows (ou se não tiver dig)
   ```

   *Esperado:* um ou mais endereços IP. Repita o comando: na segunda vez a
   resposta vem **instantânea**, porque veio do cache. Rode `dig` completo e
   olhe o campo `TTL` — é o tempo, em segundos, que aquela resposta pode ficar
   em cache. É por isso que trocar um registro DNS "demora a propagar": você não
   espera o DNS, você espera os TTLs expirarem pelo mundo.

   ```bash
   dig developer.mozilla.org | grep -A 2 "ANSWER SECTION"
   ```

2. **O caminho até lá.** O IP sozinho não garante que dá para chegar:

   ```bash
   ping -c 3 developer.mozilla.org         # Windows: ping -n 3 developer.mozilla.org
   ```

   *Esperado:* ou respostas com tempo em ms, ou timeout (muita CDN bloqueia
   ICMP — timeout aqui **não** significa que o site está fora). Conclusão
   didática: `ping` testa a camada de rede, `curl` testa a aplicação. São
   perguntas diferentes.

3. **A conversa inteira, byte a byte.** Agora o HTTP:

   ```bash
   curl -v https://developer.mozilla.org/pt-BR/docs/Web/HTTP -o /dev/null
   ```

   *Esperado:* leia a saída em voz alta com o grupo e identifique as camadas
   empilhadas, na ordem em que aparecem:

   - `Trying 2600:...:443` → **TCP**, conectando ao IP na **porta 443**
   - `ALPN`, `TLS handshake`, `SSL connection using TLSv1.3` → **TLS**, antes de
     qualquer byte de HTTP
   - linhas com `>` → o que o **seu cliente enviou** (request): a request line
     `GET /pt-BR/... HTTP/2`, e os headers `Host:`, `User-Agent:`, `Accept:`
   - linhas com `<` → o que o **servidor respondeu**: a status line
     `HTTP/2 200`, e os headers `content-type`, `content-length`, `server`,
     `cache-control`

   Três perguntas para o grupo, respondidas direto da saída:
   - *Por que o header `Host` existe, se o IP já identificou a máquina?*
     (porque um mesmo IP serve milhares de sites — o `Host` escolhe qual)
   - *O TLS protege o quê?* (o conteúdo e os headers; **não** esconde o IP de
     destino nem, em geral, o nome do host)
   - *Qual foi o status code?*

4. **Só os headers, só o status.** Duas formas mais secas de perguntar a mesma coisa:

   ```bash
   curl -I https://developer.mozilla.org          # HEAD: só os headers
   curl -s -o /dev/null -w "%{http_code}\n" https://developer.mozilla.org
   ```

   *Esperado:* `200`. Agora provoque o servidor de propósito e colecione status
   codes reais:

   ```bash
   curl -s -o /dev/null -w "%{http_code}\n" https://developer.mozilla.org/rota-que-nao-existe
   curl -s -o /dev/null -w "%{http_code}\n" http://developer.mozilla.org
   ```

   *Esperado:* `404` na primeira (a rota não existe) e `301` ou `302` na segunda
   (o `http://` redireciona para `https://` — veja o header `location` com
   `curl -I`). Introduza aqui a regra de bolso que vale o dia inteiro:

   | Família | Quem é o dono do problema |
   | --- | --- |
   | `2xx` | deu certo |
   | `3xx` | continua em outro lugar (redirect) |
   | `4xx` | **o cliente errou** |
   | `5xx` | **o servidor errou** |

5. **Quem está escutando na sua máquina.** Portas são do sistema operacional,
   não do Python:

   ```bash
   ss -tlnp            # Linux/WSL
   netstat -ano        # Windows (PowerShell/cmd)
   ```

   *Esperado:* uma lista de `endereço:porta` em estado `LISTEN`. Procure se
   alguém já ocupa a `8000` — se ocupar, use outra porta no bloco 2.

> ✅ **checkpoint 1 — todo mundo chegou até aqui?**
> Cada pessoa consegue apontar, na saída do `curl -v`, onde termina o TLS, onde
> começa o request HTTP e qual foi o status code.

### Bloco 2 — o servidor mínimo (~20 min)

Agora invertemos os papéis: até aqui todo mundo foi **cliente**. Vamos ser o
**servidor**.

6. **O servidor que já vem pronto.** O Python tem um servidor HTTP embutido:

   ```bash
   cd semana-02/codigo
   python -m http.server 8000
   ```

   Em outro terminal:

   ```bash
   curl -i http://127.0.0.1:8000/
   curl -s -o /dev/null -w "%{http_code}\n" http://127.0.0.1:8000/nao-existe
   ```

   *Esperado:* `200` com uma listagem HTML da pasta, e `404` no caminho
   inexistente. Repare que o terminal do servidor imprime uma linha por
   requisição — é um **access log**. Encerre com `Ctrl+C`.

   Esse servidor só sabe servir arquivos. O que vamos escrever agora substitui a
   parte que decide *o que responder*.

7. **`127.0.0.1` vs `0.0.0.0` — quebrar e consertar.** Com o servidor do passo 6
   ainda rodando, peça para a pessoa ao lado acessar
   `http://<seu-ip-local>:8000` (descubra o IP com `ip addr` / `ipconfig`).

   *Esperado:* **falha**. Agora suba de novo com `--bind 0.0.0.0` e peça de
   novo.

   ```bash
   python -m http.server 8000 --bind 0.0.0.0
   ```

   *Esperado:* funciona. `127.0.0.1` aceita conexão só da própria máquina;
   `0.0.0.0` significa "qualquer interface de rede desta máquina". Guarde essa
   lição: na Semana 04 ela volta exatamente igual, como "o container não
   responde no `-p 8000:8000`".

   > Se o firewall do lab bloquear, não brigue com ele: demonstre a diferença
   > com `curl http://127.0.0.1:8000` (funciona) vs `curl http://<seu-ip>:8000`
   > (falha) na **sua própria** máquina.

8. **O primeiro servidor escrito por você.** Crie `meu_servidor.py` em
   `semana-02/codigo/` e escreva — digitando, não copiando:

   ```python
   import json
   from http.server import BaseHTTPRequestHandler, HTTPServer


   class Manipulador(BaseHTTPRequestHandler):
       def _json(self, status, corpo, headers_extra=None):
           """Monta a resposta HTTP inteira: status line, headers, corpo."""
           carga = json.dumps(corpo, ensure_ascii=False).encode("utf-8")
           self.send_response(status)
           self.send_header("Content-Type", "application/json; charset=utf-8")
           self.send_header("Content-Length", str(len(carga)))
           for nome, valor in (headers_extra or {}).items():
               self.send_header(nome, valor)
           self.end_headers()
           self.wfile.write(carga)

       def do_GET(self):
           if self.path == "/":
               self._json(200, {"servico": "meu-servidor", "rotas": ["/", "/health"]})
           elif self.path == "/health":
               self._json(200, {"status": "ok"})
           else:
               self._json(404, {"erro": "rota não encontrada", "caminho": self.path})


   HTTPServer(("127.0.0.1", 8000), Manipulador).serve_forever()
   ```

   Pare e leia o `_json` que você escreveu — são as **quatro partes de uma
   resposta HTTP**, na ordem obrigatória do protocolo:

   1. `send_response(status)` → a status line (`HTTP/1.0 200 OK`) e os headers
      `Server` e `Date`
   2. `send_header(...)` → os seus headers
   3. `end_headers()` → **a linha em branco** que separa headers do corpo
   4. `wfile.write(carga)` → os bytes do corpo

   Inverter qualquer uma dessas quatro quebra o cliente. É isso que o
   `return {...}` de um framework faz por baixo.

9. **Rodar e testar.**

   ```bash
   python meu_servidor.py
   ```

   ```bash
   curl -i http://127.0.0.1:8000/
   curl -i http://127.0.0.1:8000/health
   curl -i http://127.0.0.1:8000/rota-errada
   ```

   *Esperado:* `200`, `200` e `404` — e o JSON que **você** escreveu. O `-i`
   mostra os headers: confira que o `Content-Type` diz `application/json` e que
   o `Content-Length` bate com o tamanho do corpo.

   **404** aqui é o primeiro status code que você escolheu de propósito: o
   servidor está vivo e respondeu, mas não existe nada naquele caminho.

10. **Experimento rápido: mentir no `Content-Type`.** Troque
    `application/json` por `text/html` no código, reinicie e abra
    <http://127.0.0.1:8000/> no **navegador**.

    *Esperado:* o navegador tenta renderizar o JSON como página. O header não
    muda o conteúdo — ele é a **promessa** sobre o conteúdo, e o cliente confia
    nela. Desfaça a mudança antes de seguir.

> ✅ **checkpoint 2 — todo mundo chegou até aqui?**
> Todo mundo com um `meu_servidor.py` respondendo `200` em `/health` e `404` em
> uma rota qualquer.

### Bloco 3 — servir o modelo e tratar erros (~20 min)

11. **Conhecer o modelo antes de servi-lo.**

    ```bash
    python modelo.py
    ```

    *Esperado:*

    ```
    ('positivo', 0.7274)     adorei o atendimento, chegou antes do prazo
    ('negativo', 0.7708)     pessimo, veio quebrado e atrasado
    ('neutro', 0.5534)       o pedido chegou
    ```

    Abra [`codigo/modelo.py`](./codigo/modelo.py): é um TF-IDF + Regressão
    Logística treinado em memória a partir de ~60 frases embutidas no arquivo.
    A interface que nos interessa é uma função só:
    `classificar(texto) -> (sentimento, score)`. Tudo o que falta é **expor essa
    função por HTTP**.

12. **`POST /prever`: ler o corpo da requisição.** Acrescente ao seu
    `meu_servidor.py`:

    ```python
    from modelo import classificar

    LIMITE = 64 * 1024

    class Manipulador(BaseHTTPRequestHandler):
        # ... do_GET como antes ...

        def do_POST(self):
            if self.path != "/prever":
                self._json(404, {"erro": "rota não encontrada"})
                return

            # Em HTTP quem diz o tamanho do corpo é o header Content-Length.
            tamanho = int(self.headers.get("Content-Length") or 0)
            if tamanho > LIMITE:
                self._json(413, {"erro": "corpo grande demais"})
                return
            corpo = self.rfile.read(tamanho)
    ```

    Pare no `self.rfile.read(tamanho)`. O corpo **não** vem pronto: ele é um
    stream de bytes no socket, e só o `Content-Length` diz onde ele acaba. Ler
    byte a mais trava o servidor esperando; ler byte a menos deixa lixo na
    conexão. É isso que o framework faz por você.

13. **Status code certo para cada tipo de erro.** Complete o `do_POST`:

    ```python
            # 400: não dá nem para entender os bytes
            try:
                dados = json.loads(corpo.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                self._json(400, {"erro": "corpo não é um JSON válido", "detalhe": str(exc)})
                return

            # 422: o JSON é válido, mas o conteúdo não serve
            texto = dados.get("texto") if isinstance(dados, dict) else None
            if not isinstance(texto, str) or not texto.strip():
                self._json(422, {"erro": "campo 'texto' ausente ou vazio", "campo": "texto"})
                return

            # 200: deu certo
            sentimento, score = classificar(texto)
            self._json(200, {"texto": texto, "sentimento": sentimento, "score": score})
    ```

    A diferença entre **400** e **422** é o ponto mais importante do dia:

    | Código | Leitura em voz alta |
    | --- | --- |
    | `400 Bad Request` | "não consegui nem entender os bytes que você mandou" |
    | `422 Unprocessable Content` | "entendi perfeitamente o JSON, mas o conteúdo viola o contrato" |

    Mandar 400 para os dois casos funciona, mas joga fora informação que o
    cliente precisa para se corrigir. Mandar **500** para qualquer um dos dois é
    o erro clássico: 5xx é culpa do servidor, e aqui quem errou foi o cliente.

14. **O método também é parte da rota — 405.** Hoje, `GET /prever` cai no
    `do_GET` e devolve `404`. Mas a rota **existe**: o errado é o verbo. Ajuste
    o `do_GET` para distinguir:

     ```python
        def do_GET(self):
            if self.path == "/":
                self._json(200, {"servico": "meu-servidor", "rotas": ["/", "/health", "/prever"]})
            elif self.path == "/health":
                self._json(200, {"status": "ok"})
            elif self.path == "/prever":
                # A rota existe — o errado é o método.
                self._json(
                    405,
                    {"erro": "método não permitido", "metodo": "GET", "permitidos": ["POST"]},
                    headers_extra={"Allow": "POST"},
                )
            else:
                self._json(404, {"erro": "rota não encontrada", "caminho": self.path})
    ```

    **405 Method Not Allowed** exige o header `Allow` listando os métodos
    aceitos — é obrigação do protocolo, não enfeite. Sem ele, o cliente sabe que
    errou mas não sabe o que tentar.

15. **A bateria de testes.** Suba o servidor e rode tudo, lendo o status code de
    cada um:

    ```bash
    curl -i -X POST http://127.0.0.1:8000/prever \
      -H "Content-Type: application/json" \
      -d '{"texto": "adorei o atendimento, chegou antes do prazo"}'       # 200 positivo

    curl -X POST http://127.0.0.1:8000/prever \
      -H "Content-Type: application/json" \
      -d '{"texto": "pessimo, veio quebrado e atrasado"}'                 # 200 negativo

    curl -i http://127.0.0.1:8000/nao-existe                              # 404
    curl -i http://127.0.0.1:8000/prever                                  # 405 + Allow: POST
    curl -i -X POST http://127.0.0.1:8000/prever \
      -H "Content-Type: application/json" -d '{"texto": '                 # 400
    curl -i -X POST http://127.0.0.1:8000/prever \
      -H "Content-Type: application/json" -d '{"texto": ""}'              # 422
    ```

    *Esperado:*

    ```json
    {"texto": "adorei o atendimento, chegou antes do prazo", "sentimento": "positivo", "score": 0.7274, "modelo": "tfidf+logreg"}
    {"texto": "pessimo, veio quebrado e atrasado", "sentimento": "negativo", "score": 0.7708, "modelo": "tfidf+logreg"}
    ```

    (o `score` pode variar nos últimos decimais conforme a versão do
    scikit-learn; o que importa é o `sentimento` e o status code)

16. **O erro que todo mundo comete uma vez.** Repita o POST **sem** o
    `-H "Content-Type: application/json"`:

    ```bash
    curl -i -X POST http://127.0.0.1:8000/prever -d '{"texto": "oi"}'
    ```

    *Esperado no `servidor.py` de referência:* **415 Unsupported Media Type** —
    o curl anunciou o corpo como `application/x-www-form-urlencoded`. O corpo
    até *é* JSON, mas o cliente mentiu sobre o formato, e o servidor confia no
    header em vez de adivinhar. (No seu `meu_servidor.py`, que ainda não checa o
    `Content-Type`, vai passar como 200 — vale comparar os dois.)

17. **Comparar com a referência.** Agora leia
    [`codigo/servidor.py`](./codigo/servidor.py) inteiro, com o seu próprio
    código do lado:

    ```bash
    python servidor.py --porta 8001
    ```

    O que ele tem a mais, e por quê:

    - tabela `ROTAS` explícita (caminho → métodos) em vez de `if/elif` espalhado
    - `urlparse(self.path).path` — `/health?debug=1` é a **mesma rota** que `/health`
    - o corpo é sempre drenado, mesmo em 404 (com keep-alive, bytes não lidos
      viram a "próxima requisição" e tudo desanda)
    - `415` para `Content-Type` errado e `413` para corpo acima de 64 KB
    - `try/except` geral devolvendo `500` e mandando o stack trace para o log —
      nunca para o cliente
    - `ThreadingHTTPServer`: uma thread por conexão (com o `HTTPServer` simples,
      uma requisição lenta trava todas as outras)

    A bateria completa de `curl`, com a saída esperada de cada caso, está em
    [`codigo/exemplos_curl.md`](./codigo/exemplos_curl.md).

> ✅ **checkpoint 3 — todo mundo chegou até aqui?**
> Todo mundo com `POST /prever` devolvendo `200` com o sentimento, e com `404`,
> `405`, `400` e `422` saindo nos casos certos.

18. **Fechar o ciclo.** Encerre os servidores com `Ctrl+C` e apague o
    `__pycache__` gerado:

    ```bash
    rm -rf __pycache__
    ```

    Guarde o seu `meu_servidor.py`: ele é o ponto de partida do desafio. E
    guarde esta frase para a Semana 03: **tudo o que você escreveu hoje à mão, o
    FastAPI faz em três decoradores — mas agora você sabe o que ele está
    fazendo.**

---

## Código

O código de apoio desta semana vive em [`codigo/`](./codigo/) — veja
[`codigo/README.md`](./codigo/README.md) para subir em um comando.

| Arquivo | O que é |
| --- | --- |
| [`codigo/servidor.py`](./codigo/servidor.py) | Servidor HTTP de referência, só com a stdlib: roteamento, parse do corpo e status codes na mão |
| [`codigo/modelo.py`](./codigo/modelo.py) | TF-IDF + Regressão Logística e o mini-dataset PT-BR; expõe `classificar(texto)` |
| [`codigo/exemplos_curl.md`](./codigo/exemplos_curl.md) | Um `curl` por rota e por erro, com a resposta esperada |
| [`codigo/requirements.txt`](./codigo/requirements.txt) | Só o `scikit-learn` — o servidor não precisa de nada |
| [`codigo/README.md`](./codigo/README.md) | Como subir, testar e o contrato completo |

---

## Recursos e links

**Base do encontro (do [`ROADMAP.md`](../ROADMAP.md))**

- [MDN — How the Web works](https://developer.mozilla.org/en-US/docs/Learn/Getting_started_with_the_web/How_the_Web_works)
- [MDN — HTTP (referência e guias)](https://developer.mozilla.org/en-US/docs/Web/HTTP)
- [Cloudflare Learning — O que é DNS?](https://www.cloudflare.com/learning/dns/what-is-dns/)
- [Cloudflare Learning — Modelo OSI](https://www.cloudflare.com/learning/ddos/glossary/open-systems-interconnection-model-osi/)
- [Cloudflare Learning — TCP/IP](https://www.cloudflare.com/learning/ddos/glossary/tcp-ip/)
- [High Performance Browser Networking (livro online, O'Reilly)](https://hpbn.co/)

**Para o lab**

- [MDN — Visão geral do HTTP (PT-BR)](https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Overview)
- [MDN — Lista de status codes HTTP](https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Status)
- [MDN — Métodos HTTP](https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Methods)
- [Python — `http.server`](https://docs.python.org/3/library/http.server.html)
- [curl — manual oficial](https://curl.se/docs/manual.html)
- [How DNS works (quadrinho)](https://howdns.works/)
- [RFC 9110 — HTTP Semantics (a fonte da verdade sobre status codes)](https://www.rfc-editor.org/rfc/rfc9110.html)

---

## Notas para o host

- O fio condutor é **entender antes de abstrair**: quem escreveu o `do_POST` à
  mão hoje entende o `@app.post` da Semana 03 em trinta segundos
- O passo 13 (400 vs 422) é o momento didático mais importante do dia; não pule.
  O segundo é o passo 16 (`Content-Type` errado → 415)
- Evite entrar em FastAPI aqui — é assunto da Semana 03. Se alguém perguntar,
  aponte para a tabela de comparação no fim de [`codigo/README.md`](./codigo/README.md)
- Em Python 3.13 o `422` é impresso como `Unprocessable Content` (nome da RFC
  9110); em versões anteriores aparece como `Unprocessable Entity`. É o mesmo código
- **Porta ocupada:** no Windows, `HTTPServer` usa `SO_REUSEADDR` e dois processos
  conseguem "subir" na mesma porta sem erro — o mais antigo continua respondendo.
  Se o grupo achar que uma mudança no código "não fez efeito", é quase sempre
  isso: mate todos os `python servidor.py` antes de reiniciar
- Tenha um plano B se a rede do lab bloquear portas ou ICMP: o passo 7 (acesso de
  outra máquina) e o passo 2 (`ping`) podem falhar por firewall, não por erro do
  aluno. Dá para demonstrar tudo em `127.0.0.1`
- Peça `pip install -r semana-02/codigo/requirements.txt` com antecedência — o
  download do scikit-learn é a única parte lenta
- Material de referência do grupo anterior: `presentation/primeiro-semestre` na
  branch `main` (pode ser reaproveitado)

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [x] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
