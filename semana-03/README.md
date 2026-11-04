# Semana 03 — Como a web funciona II (APIs)

> **Encontro 4 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

Do servidor cru para uma API de verdade: REST, JSON, status codes e validação, construindo com FastAPI o serviço que vai nos acompanhar até o Demo Day.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Projetar uma API REST com recursos, métodos e status codes coerentes
- Serializar e validar entrada/saída com JSON e Pydantic (e explicar de onde vem o 422)
- Construir uma API com FastAPI e documentá-la automaticamente (OpenAPI/Swagger)
- Carregar o modelo uma única vez no startup, com `lifespan`, em vez de a cada requisição
- Entender o papel do TLS e quando o certificado é responsabilidade da plataforma

---

## Pré-requisitos

- Semana 02 concluída (HTTP, portas e status codes claros)
- Python 3.10+ e ambiente virtual configurado (`python --version`)
- Um cliente HTTP à mão: `curl` (ou `curl.exe` no Windows) e, opcionalmente, a extensão
  [REST Client](https://marketplace.visualstudio.com/items?itemName=humao.rest-client) no VS Code
- Porta `8000` livre na máquina

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- REST na prática: recursos, verbos e idempotência
- Status codes que importam: 200, 201, 400, 404, 405, 422 e 500
- JSON como contrato: schema, validação e versionamento da API
- TLS/HTTPS: terminação no load balancer e certificados gerenciados
- Por que FastAPI: tipagem, validação automática e documentação de graça

### 💻 Mão na massa (~60 min)

- Criar o projeto FastAPI e subir com `uvicorn`
- Definir os schemas de request/response com Pydantic
- Implementar `/health` e `/predict` chamando o modelo de sentimento
- Explorar a documentação automática em `/docs` e testar por lá
- Forçar erros de validação e observar o 422 do FastAPI

### 🎯 Desafio (~15 min)

Implementar um endpoint `/predict` que recebe um texto e devolve o sentimento com score, respeitando o contrato JSON e os status codes.

Enunciado completo em [`desafio.md`](./desafio.md).

---

## Passo a passo

Todos os comandos rodam a partir de `semana-03/codigo/`. A versão final de cada
arquivo está em [`codigo/`](./codigo/) — mas **escreva junto**, não copie: o
objetivo do lab é ver a API crescer, de um `{"ok": true}` até o contrato que
vamos congelar hoje.

> **Windows / PowerShell:** `curl` é apelido de `Invoke-WebRequest` e **não** aceita
> `-X`/`-d`. Use `curl.exe` no lugar de `curl`, ou a versão `Invoke-RestMethod`
> indicada no [`codigo/README.md`](./codigo/README.md).

### Bloco 1 — hello FastAPI e a documentação de graça (~15 min)

1. **Preparar a pasta e o ambiente.**

   ```bash
   mkdir -p semana-03/codigo/app
   cd semana-03/codigo
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
   ```

   Crie `app/requirements.txt` com as versões **fixadas** — é assim que todo mundo
   roda o mesmo código, e é esse arquivo que a Semana 04 vai copiar para dentro da
   imagem:

   ```
   fastapi==0.115.6
   uvicorn==0.34.0
   scikit-learn==1.6.1
   ```

   ```bash
   pip install -r app/requirements.txt
   ```

   *Esperado:* o prompt prefixado com `(.venv)` e o `pip` instalando também as
   dependências transitivas (`pydantic`, `starlette`, `numpy`, `scipy`).

2. **O menor FastAPI possível.** Crie um `app/__init__.py` vazio (ele transforma
   a pasta em um pacote Python) e `app/main.py` com:

   ```python
   from fastapi import FastAPI

   app = FastAPI(title="API de Sentimento — Semana 03")


   @app.get("/")
   def raiz():
       return {"servico": "api-sentimento", "status": "no ar"}
   ```

   São oito linhas e já é uma API HTTP completa. Compare mentalmente com a Semana
   02, onde a status line e os headers saíram na mão.

3. **Subir o servidor.**

   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

   Leia o comando: `app.main` é o **módulo** (`app/main.py`), `:app` é o **objeto**
   `FastAPI` dentro dele. O `--reload` reinicia o servidor a cada alteração de
   arquivo — ótimo no lab, proibido em produção.

   *Esperado:*

   ```
   INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
   INFO:     Application startup complete.
   ```

   Em **outro terminal** (o primeiro fica ocupado com o servidor):

   ```bash
   curl -i http://localhost:8000/
   ```

   *Esperado:* `HTTP/1.1 200 OK`, `content-type: application/json` e o corpo
   `{"servico":"api-sentimento","status":"no ar"}`. Ninguém escreveu o header nem
   serializou o dicionário: o framework fez os dois.

4. **Abrir a documentação que você não escreveu.** No navegador:

   - <http://localhost:8000/docs> — Swagger UI, interativa
   - <http://localhost:8000/redoc> — a mesma coisa, outro layout
   - <http://localhost:8000/openapi.json> — o contrato da API em JSON

   *Esperado:* a rota `GET /` listada, com o botão **Try it out** funcionando. Esse
   JSON do `/openapi.json` é o documento [OpenAPI](https://swagger.io/specification/):
   é dele que nascem o Swagger, os clientes gerados automaticamente e, mais para a
   frente, os testes de contrato.

5. **Provar o `--reload`.** Sem derrubar o servidor, mude o valor de `"status"`
   para `"ok"`, salve e rode `curl http://localhost:8000/` de novo.

   *Esperado:* no terminal do servidor, `Reloading...` seguido de
   `Application startup complete.`, e o `curl` já devolvendo o valor novo.

> ✅ **checkpoint 1 — todo mundo chegou até aqui?**
> Todo mundo com o `/docs` aberto no navegador e o `GET /` respondendo 200.

### Bloco 2 — o contrato: Pydantic, `/predict` e o 422 (~25 min)

6. **Trazer o modelo para dentro do projeto.** Copie
   [`codigo/app/modelo.py`](./codigo/app/modelo.py) para o seu `app/`. Ele não é o
   assunto da semana: são ~60 frases em PT-BR, um TF-IDF + Regressão Logística e
   três funções. Leia a assinatura que vamos usar:

   ```python
   classificar(modelo, texto, limiar_neutro) -> tuple[str, float]
   ```

   Teste fora da API, para separar "o modelo funciona" de "a API funciona":

   ```bash
   python -c "from app.modelo import treinar_modelo, classificar; m = treinar_modelo(); print(classificar(m, 'adorei o atendimento, chegou antes do prazo'))"
   ```

   *Esperado:* `('positivo', 0.7274)`. O segundo valor é a confiança da classe
   vencedora; abaixo de `0.60` o rótulo vira `neutro`. (Os últimos decimais podem
   variar conforme a versão do scikit-learn.)

7. **Modelar a entrada e a saída com Pydantic.** Em `app/main.py`:

   ```python
   from pydantic import BaseModel, Field


   class PedidoPredicao(BaseModel):
       texto: str = Field(
           ...,
           min_length=1,
           max_length=1000,
           description="Texto a ser classificado.",
           examples=["adorei o atendimento, chegou antes do prazo"],
       )


   class RespostaPredicao(BaseModel):
       texto: str
       sentimento: str = Field(description="positivo, negativo ou neutro")
       score: float = Field(ge=0.0, le=1.0, description="Confiança da classe vencedora")
       modelo: str
   ```

   Três coisas acontecem de uma vez, e vale dizer em voz alta: isso é **validação**
   (`min_length`, `ge`/`le`), é **documentação** (`description`, `examples` aparecem
   no `/docs`) e é **tipagem** (o editor autocompleta `pedido.texto`).

   > O nome da classe vira o nome do schema no `/openapi.json`. Por isso
   > `PedidoPredicao` e não `TextoEntrada`: o nome descreve o papel do objeto no
   > contrato, não o tipo do campo que ele carrega.

8. **Implementar o `POST /predict`.** Versão ingênua de propósito — ela treina o
   modelo dentro da rota:

   ```python
   from app.modelo import NOME_MODELO, classificar, treinar_modelo


   @app.post("/predict", response_model=RespostaPredicao)
   def predict(pedido: PedidoPredicao) -> RespostaPredicao:
       modelo = treinar_modelo()                      # ⚠️ consertamos isso no bloco 3
       sentimento, score = classificar(modelo, pedido.texto)
       return RespostaPredicao(
           texto=pedido.texto,
           sentimento=sentimento,
           score=score,
           modelo=NOME_MODELO,
       )
   ```

   Repare no que **não** está escrito: não há `json.loads`, não há `if "texto" not in body`,
   não há `return 400`. A anotação `pedido: PedidoPredicao` é o que diz ao FastAPI
   para ler o corpo, validar e converter. O `response_model` faz o caminho de volta.

9. **Testar o caminho feliz.**

   ```bash
   curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"texto": "adorei o atendimento, chegou antes do prazo"}'

   curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"texto": "pessimo, veio quebrado e atrasado"}'
   ```

   *Esperado:*

   ```json
   {"texto":"adorei o atendimento, chegou antes do prazo","sentimento":"positivo","score":0.7274,"modelo":"tfidf+logreg"}
   {"texto":"pessimo, veio quebrado e atrasado","sentimento":"negativo","score":0.7708,"modelo":"tfidf+logreg"}
   ```

   Agora faça a mesma coisa **pelo `/docs`**: recarregue a página, abra o
   `POST /predict`, clique em *Try it out*, edite o JSON de exemplo e envie. O
   Swagger mostra o `curl` equivalente, a URL, o status e o corpo da resposta.

   Teste também `{"texto": "o pedido chegou"}`: sai `neutro` com score `0.5534`,
   porque a confiança ficou abaixo do limiar. Admitir incerteza é uma decisão de
   produto, e ela mora no contrato.

10. **Quebrar de propósito e ler os status codes.** Rode cada um com `-i` para ver
    a status line:

    ```bash
    curl -i -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"texto": ""}'
    curl -i -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"frase": "campo errado"}'
    curl -i -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"texto": 42}'
    curl -i -X GET  http://localhost:8000/predict
    curl -i http://localhost:8000/predicao
    ```

    *Esperado:*

    | Requisição | Status | Mensagem do FastAPI |
    | --- | --- | --- |
    | `{"texto": ""}` | **422** | `String should have at least 1 character` |
    | `{"frase": ...}` | **422** | `Field required` |
    | `{"texto": 42}` | **422** | `Input should be a valid string` |
    | `GET /predict` | **405** | `Method Not Allowed` — a rota existe, o verbo não |
    | `GET /predicao` | **404** | `Not Found` — a rota não existe |

    O corpo do 422 vem estruturado, com `loc` apontando o campo culpado:

    ```json
    {"detail":[{"type":"string_too_short","loc":["body","texto"],"msg":"String should have at least 1 character","input":"","ctx":{"min_length":1}}]}
    ```

    Discuta em 2 minutos: **422 vs 400**. O JSON chegou e foi entendido (não é 400
    "não entendi a sintaxe"), mas o conteúdo não satisfaz o schema — *Unprocessable
    Content*. É a convenção do FastAPI e é o status que o `desafio.md` vai cobrar.

> ✅ **checkpoint 2 — todo mundo chegou até aqui?**
> Todo mundo com um `200` e um `422` do `/predict` colados no chat da turma.

### Bloco 3 — startup, `/health` e a vida em produção (~20 min)

11. **Medir a dor do passo 8.** Cada requisição está retreinando o modelo:

    ```bash
    time curl -s -X POST http://localhost:8000/predict \
      -H "Content-Type: application/json" \
      -d '{"texto": "entrega rápida e tudo certo"}' > /dev/null
    ```

    *Esperado:* algo na casa de dezenas de milissegundos só de treino, **em toda
    chamada**. Com um modelo de verdade (centenas de MB vindos do disco) isso seria
    segundos. O trabalho tem que acontecer uma vez, no startup.

12. **Carregar o modelo uma única vez com `lifespan`.** No topo de `app/main.py`:

    ```python
    import logging
    import os
    import time
    from contextlib import asynccontextmanager

    from app.modelo import LIMIAR_NEUTRO_PADRAO, NOME_MODELO, acuracia_treino, classificar, treinar_modelo

    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    logger = logging.getLogger("api-sentimento")

    VERSAO = "1.0.0"
    LIMIAR_NEUTRO = float(os.getenv("LIMIAR_NEUTRO", LIMIAR_NEUTRO_PADRAO))

    estado: dict[str, object] = {"modelo": None}


    @asynccontextmanager
    async def lifespan(_: FastAPI):
        inicio = time.perf_counter()
        modelo = treinar_modelo()
        estado["modelo"] = modelo
        logger.info(
            "modelo '%s' treinado em %.0f ms (acurácia no treino: %.2f, limiar neutro: %.2f)",
            NOME_MODELO, (time.perf_counter() - inicio) * 1000, acuracia_treino(modelo), LIMIAR_NEUTRO,
        )
        yield
        estado["modelo"] = None
        logger.info("encerrando a API")


    app = FastAPI(title="API de Sentimento — Semana 03", version=VERSAO, lifespan=lifespan)
    ```

    Tudo **antes** do `yield` roda no startup; tudo depois, no shutdown. Troque o
    `treinar_modelo()` de dentro do `/predict` por `modelo = estado["modelo"]` e
    passe o limiar: `classificar(modelo, pedido.texto, LIMIAR_NEUTRO)`.

    Repare também no `os.getenv("LIMIAR_NEUTRO", ...)`: o que varia por ambiente sai
    do código e vira variável de ambiente. É o primeiro ensaio da Semana 08.

13. **Adicionar o `GET /health`.**

    ```python
    class RespostaSaude(BaseModel):
        status: str
        modelo_carregado: bool
        versao: str


    @app.get("/health", response_model=RespostaSaude)
    def health() -> RespostaSaude:
        return RespostaSaude(
            status="ok",
            modelo_carregado=estado["modelo"] is not None,
            versao=VERSAO,
        )
    ```

    Esta rota parece boba hoje e é lida por **máquinas** daqui para a frente: o
    `HEALTHCHECK` do container (Semana 04), o `depends_on: service_healthy` do
    Compose (Semana 04) e o probe do Cloud Run (Semana 07). Por isso ela responde
    `modelo_carregado` — "o processo está de pé" e "o serviço está pronto" são
    perguntas diferentes.

14. **Reiniciar e comparar.** Derrube o servidor (`Ctrl+C`) e suba de novo.

    ```bash
    uvicorn app.main:app --reload --port 8000
    ```

    *Esperado:* nos logs, **uma** linha de treino, no startup:

    ```
    2026-11-04 14:08:54 | INFO | modelo 'tfidf+logreg' treinado em 29 ms (acurácia no treino: 1.00, limiar neutro: 0.60)
    INFO:     Application startup complete.
    ```

    E depois:

    ```bash
    curl http://localhost:8000/health
    # {"status":"ok","modelo_carregado":true,"versao":"1.0.0"}

    time curl -s -X POST http://localhost:8000/predict \
      -H "Content-Type: application/json" \
      -d '{"texto": "entrega rápida e tudo certo"}' > /dev/null
    ```

    *Esperado:* o `/predict` agora responde em poucos milissegundos, e **nenhuma**
    linha nova de treino aparece — só o `predict | sentimento=... score=...`.

    Por fim, enriqueça o `GET /` para apontar o caminho das pedras (veja a versão
    final em [`codigo/app/main.py`](./codigo/app/main.py)).

15. **Congelar o contrato.** Abra <http://localhost:8000/openapi.json> e procure:

    - `paths`: deve conter exatamente `/`, `/health` e `/predict`
    - `components.schemas`: `PedidoPredicao`, `RespostaPredicao`, `RespostaSaude`
      e — sem você ter escrito uma linha — `HTTPValidationError` e `ValidationError`
    - dentro de `POST /predict`, as respostas `200` **e** `422` já documentadas

    Este é o contrato da semana, e ele vale até o Demo Day:

    | Método | Rota | Entrada | Saída |
    | --- | --- | --- | --- |
    | `GET` | `/` | — | metadados do serviço |
    | `GET` | `/health` | — | `{"status","modelo_carregado","versao"}` |
    | `POST` | `/predict` | `{"texto": "..."}` (1 a 1000 chars) | `{"texto","sentimento","score","modelo"}` |

    Anote-o no README do **seu** repositório. A Semana 04 containeriza exatamente
    esta API, a Semana 07 a publica no Cloud Run e a Semana 10 usa este contrato
    como roteiro do load test. Mudou aqui, quebrou lá.

16. **Nota sobre HTTPS/TLS — e por que a nossa API fala HTTP.** Tudo que rodamos
    hoje foi `http://localhost:8000`, sem criptografia. Em produção isso seria
    inaceitável: sem TLS, qualquer um no caminho lê e altera o JSON.

    O ponto é **onde** o TLS acontece. O padrão da indústria é *TLS termination* na
    borda — o certificado vive no load balancer, no proxy reverso ou na plataforma,
    que descriptografa a requisição e a repassa em HTTP puro para a aplicação, na
    rede interna:

    ```
    navegador --HTTPS(443)--> Cloud Run / load balancer --HTTP(8000)--> uvicorn
             \____________ certificado vive aqui ____________/
    ```

    Na Semana 07, quando publicarmos esta mesma API no **Cloud Run**, o serviço já
    nasce com um domínio `https://...run.app` e certificado gerenciado e renovado
    automaticamente pelo Google. Nós **não** vamos configurar certificado nenhum.
    O que fica de combinado:

    - Não é papel da aplicação lidar com certificado; é da plataforma. Resista à
      tentação de `uvicorn --ssl-keyfile` em produção.
    - A aplicação continua escutando HTTP na porta que a plataforma mandar
      (`PORT`), e `--host 0.0.0.0` passa a importar (Semana 04).
    - Se a app precisar saber o esquema original do cliente, ele chega no header
      `X-Forwarded-Proto` — quem termina o TLS é quem preenche.
    - Certificado expirado é incidente de produção clássico. Gerenciado > manual.

17. **Fechar o ciclo.** Derrube o servidor, confira o que foi criado e versione:

    ```bash
    ls app/            # __init__.py  main.py  modelo.py  requirements.txt
    git status
    ```

    O `.venv/` **não** entra no commit (confira o `.gitignore`). A entrega da semana
    está em [`desafio.md`](./desafio.md).

> ✅ **checkpoint 3 — todo mundo chegou até aqui?**
> Todo mundo com `/health` em 200, `/predict` em 200 e 422, e o `/docs` refletindo
> o contrato congelado.

---

## Código

O código de apoio desta semana vive em [`codigo/`](./codigo/) — veja
[`codigo/README.md`](./codigo/README.md) para rodar em três comandos.

| Arquivo | O que é |
| --- | --- |
| [`codigo/app/main.py`](./codigo/app/main.py) | API FastAPI: `/`, `/health` e `POST /predict`, com `lifespan` |
| [`codigo/app/modelo.py`](./codigo/app/modelo.py) | TF-IDF + Regressão Logística e o mini-dataset PT-BR |
| [`codigo/app/requirements.txt`](./codigo/app/requirements.txt) | Dependências da API, com versões fixadas |
| [`codigo/exemplos_requests.http`](./codigo/exemplos_requests.http) | Requisições prontas (sucesso, 422, 404, 405) para o REST Client |
| [`codigo/README.md`](./codigo/README.md) | Como subir a API, exemplos de `curl` e o contrato |

> É **o mesmo `app/`** que a Semana 04 empacota em uma imagem Docker: lá o código
> não muda, só ganha `Dockerfile` e `docker-compose.yml`.

---

## Recursos e links

- [FastAPI — Tutorial oficial](https://fastapi.tiangolo.com/tutorial/)
- [FastAPI — Lifespan events](https://fastapi.tiangolo.com/advanced/events/)
- [Pydantic — documentação](https://docs.pydantic.dev/)
- [MDN — Glossário: REST](https://developer.mozilla.org/en-US/docs/Glossary/REST)
- [MDN — Status codes HTTP](https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Status)
- [RFC 9110 §15.5.21 — 422 Unprocessable Content](https://www.rfc-editor.org/rfc/rfc9110#name-422-unprocessable-content)
- [JSON — introdução oficial (em português)](https://www.json.org/json-pt.html)
- [OpenAPI Specification (Swagger)](https://swagger.io/specification/)
- [Cloudflare Learning — O que é HTTPS?](https://www.cloudflare.com/learning/ssl/what-is-https/)
- [Cloud Run — certificados TLS gerenciados](https://cloud.google.com/run/docs/mapping-custom-domains)
- [REST API Tutorial](https://restfulapi.net/)

---

## Notas para o host

- Material de referência do grupo anterior: `presentation/primeiro-semestre/aula03` na branch `main` (pode ser reaproveitado)
- Congele o contrato do `/predict` aqui: ele será reusado das Semanas 04 a 11
- Peça para a turma anotar o contrato no README — vai virar referência do load test da Semana 10
- Mostre o `/docs` cedo (passo 4); costuma ser o momento mais marcante da sessão
- O passo 11 → 14 (treinar na rota vs no `lifespan`) é o momento didático mais importante do dia; não pule a medição, é ela que convence
- Deixe claro que o `--reload` é de desenvolvimento, não de produção — isso volta na Semana 04
- Se alguém travar na instalação do `scikit-learn`, deixe seguir só com o `/health` e o `/predict` devolvendo um stub; o assunto da semana é a API, não o modelo
- O debate 422 vs 400 rende; dê o tempo, mas corte em 2 minutos

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [x] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
