# Desafio — Semana 03: sua API de sentimento com FastAPI

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Subir **a sua** API de análise de sentimento com FastAPI: `POST /predict` e
`GET /health` funcionando, entrada validada por Pydantic (422 em payload
inválido) e `/docs` refletindo o contrato real.

O ponto não é copiar o `codigo/` do lab: é escrever a API que **você** vai
containerizar na Semana 04, publicar no Cloud Run na Semana 07 e bombardear no
load test da Semana 10. Daqui para a frente, todas as semanas partem dela.

> **O contrato é fixo.** Nomes de campo, rotas e status codes abaixo não são
> sugestão: as semanas seguintes dependem deles. O que fica livre é o modelo,
> a organização dos arquivos e tudo que você quiser acrescentar além do mínimo.

---

## O que entregar

Dentro do seu repositório, em uma pasta `semana-03/` (ou equivalente):

| Arquivo | Requisito |
| --- | --- |
| `app/main.py` | A API FastAPI: `GET /`, `GET /health` e `POST /predict` |
| `app/modelo.py` | O modelo (pode ser o do lab, adaptado — ou o seu) |
| `app/requirements.txt` | Dependências com **versão fixada** (`fastapi==...`, não `fastapi`) |
| `tests/test_api.py` | Testes com `pytest` cobrindo sucesso **e** erro de validação |
| `README.md` | Como subir em um comando, o contrato e um exemplo de `curl` |

### O contrato (igual ao do lab)

| Método | Rota | Entrada | Saída | Status |
| --- | --- | --- | --- | --- |
| `GET` | `/` | — | metadados do serviço | `200` |
| `GET` | `/health` | — | `{"status","modelo_carregado","versao"}` | `200` |
| `POST` | `/predict` | `{"texto": "..."}` | `{"texto","sentimento","score","modelo"}` | `200` / `422` |

- `texto`: string de **1 a 1000** caracteres (`min_length`/`max_length` no Pydantic)
- `sentimento`: `positivo`, `negativo` ou `neutro`
- `score`: float entre `0.0` e `1.0`
- `modelo`: identificador do modelo usado (ex.: `tfidf+logreg`)

---

## Critérios de aceite

Marque cada item depois de verificar com o comando indicado.

**Funciona**

- [ ] A API sobe com **um** comando documentado no README (ex.: `uvicorn app.main:app --port 8000`)
- [ ] `GET /health` devolve `200` e `modelo_carregado: true`
- [ ] `POST /predict` com `{"texto": "adorei o atendimento, chegou antes do prazo"}` devolve `200` e `sentimento: "positivo"`
- [ ] `POST /predict` com um texto claramente negativo devolve `200` e `sentimento: "negativo"`
- [ ] A resposta do `/predict` tem **exatamente** as quatro chaves `texto`, `sentimento`, `score`, `modelo`

**Valida de verdade**

- [ ] `POST /predict` com `{"texto": ""}` devolve `422`
- [ ] `POST /predict` com `{"frase": "..."}` (campo errado) devolve `422`
- [ ] `POST /predict` com `{"texto": 42}` (tipo errado) devolve `422`
- [ ] `GET /predict` devolve `405` e `GET /rota-inexistente` devolve `404`
- [ ] Nenhum desses casos derruba o servidor nem devolve `500`

**Documentada**

- [ ] `/docs` abre e o `Try it out` do `/predict` funciona
- [ ] `/openapi.json` lista exatamente as rotas `/`, `/health` e `/predict`
- [ ] Os schemas têm `description` nos campos e pelo menos um `example` no `/predict`
- [ ] O contrato está escrito no `README.md` do seu repositório (tabela ou bloco JSON)

**Em condições de ir para a Semana 04**

- [ ] O modelo é carregado **uma vez no startup** (`lifespan`), não a cada requisição
- [ ] O que varia por ambiente vem de variável de ambiente, não hardcoded
- [ ] `pip install -r app/requirements.txt` em uma máquina limpa instala tudo que a API precisa
- [ ] `pytest` passa, com no mínimo um teste de sucesso e um de `422`
- [ ] `.venv/` e `__pycache__/` **não** estão versionados

**Bônus (não obrigatório)**

- [ ] Um `POST /predict/batch` recebendo uma lista de textos (pense no contrato antes de codar)
- [ ] Campo `duracao_ms` na resposta, medindo o tempo da predição
- [ ] Tratamento explícito de `503` no `/predict` quando o modelo ainda não carregou
- [ ] Uma métrica simples de uso (contador de predições por sentimento) exposta em `/health` ou `/stats`

---

## Dica para os testes

O `lifespan` só roda se o `TestClient` for usado como context manager — sem o
`with`, o modelo não carrega e o `/predict` quebra:

```python
from fastapi.testclient import TestClient
from app.main import app


def test_predict_positivo():
    with TestClient(app) as client:           # <- o "with" é obrigatório
        r = client.post("/predict", json={"texto": "adorei o atendimento, chegou antes do prazo"})
    assert r.status_code == 200
    assert r.json()["sentimento"] == "positivo"


def test_predict_texto_vazio_422():
    with TestClient(app) as client:
        r = client.post("/predict", json={"texto": ""})
    assert r.status_code == 422
```

`pytest` e `httpx` (usado pelo `TestClient`) são dependências de **teste**:
coloque-as em um `requirements-dev.txt` separado, para não inchar a imagem da
Semana 04.

---

## Evidências para o PR

Cole na descrição do pull request:

1. A saída de `curl -i` do `/predict` com `200` (status line + JSON)
2. A saída de `curl -i` do `/predict` com `{"texto": ""}` mostrando o `422`
3. Um print do `/docs` com o `POST /predict` expandido
4. A saída do `pytest`

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-03/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 03 — <resumo em poucas palavras>`;
   - descrição do que foi feito, como rodar e o que ficou pendente;
   - evidências (prints, saída de terminal, links do serviço).
5. Poste o link do pull request no canal da semana no **Discord**.

---

## Peer review

- Revise o pull request de **pelo menos 1 colega** antes do próximo encontro.
- Comente de forma específica: aponte o trecho, explique o porquê e sugira uma alternativa.
- Procure por: critérios de aceite atendidos, clareza do README, segredos vazados e reprodutibilidade.
- Nesta semana, o teste decisivo: **clone o PR do colega, suba a API seguindo só o README dele
  e mande um `curl` no `/predict`**. Se o contrato não bater com a tabela acima, isso é o review —
  a Semana 04 dele depende disso.
- Aprove apenas se você conseguiria rodar o projeto seguindo o README.
- Receber review também faz parte da entrega: responda aos comentários antes do encontro seguinte.
