# Desafio — Semana 02: Servidor HTTP cru servindo o modelo

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Expor o modelo de sentimento por HTTP usando **apenas a biblioteca padrão do
Python**, tratando rota, método, corpo e status code na mão.

O ponto não é copiar o `codigo/servidor.py` do lab: é terminar o
`meu_servidor.py` que **você** começou no passo 8 e fazê-lo responder certo em
todos os casos. Na Semana 03 o FastAPI vai fazer isso por você — e aí você vai
saber exatamente o que ele está fazendo.

**Proibido:** FastAPI, Flask, Django, `requests`, `httpx` ou qualquer pacote de
servidor web. Permitido: `http.server`, `socket`, `json`, `urllib` (stdlib) e o
`scikit-learn`, que é do modelo, não do servidor.

---

## O que entregar

Dentro do seu repositório, em uma pasta `semana-02/` (ou equivalente):

| Arquivo | Requisito |
| --- | --- |
| `servidor.py` | O servidor. Só stdlib, roteamento e status codes escritos por você |
| `modelo.py` | O classificador. Pode copiar o do lab, ou usar o seu da Semana 01 |
| `README.md` | Como subir (host, porta, comando) e um `curl` por rota |
| `exemplos_curl.md` (ou `.sh`) | Um comando por caso testado, com a resposta real colada |
| `requirements.txt` | As dependências — que devem caber em uma linha |

### Rotas obrigatórias

| Método | Rota | Resposta de sucesso |
| --- | --- | --- |
| `GET` | `/health` | `200` + JSON indicando que o serviço está de pé |
| `POST` | `/prever` (ou o nome que você escolher) | `200` + JSON com `sentimento` e `score` |

O nome do endpoint de predição é seu; o contrato de entrada
(`{"texto": "..."}`) e de saída (`sentimento` + `score`) é fixo, porque é o
mesmo que vai valer da Semana 03 até o Demo Day.

### Status codes obrigatórios

No mínimo **três**, cada um saindo no caso certo:

- `200` — sucesso
- `404` — rota que não existe
- `400` **ou** `422` — corpo inválido

Entregar os dois (400 para JSON ilegível, 422 para contrato violado) é o que
separa a entrega boa da entrega mínima.

---

## Critérios de aceite

Marque cada item depois de verificar com o comando indicado.

**Sobe e serve**

- [ ] O servidor sobe com **um único comando** (`python servidor.py`), sem passo manual
- [ ] O `README.md` diz o host e a porta, e o comando funciona copiado e colado
- [ ] `curl -i http://127.0.0.1:<porta>/health` devolve `200` com JSON
- [ ] `POST` com `{"texto": "adorei o atendimento, chegou antes do prazo"}` devolve `200` e `sentimento: "positivo"`
- [ ] `POST` com `{"texto": "pessimo, veio quebrado e atrasado"}` devolve `200` e `sentimento: "negativo"`

**Erros no lugar certo**

- [ ] `GET /rota-que-nao-existe` devolve **`404`** (e não 200, nem 500, nem crash)
- [ ] Corpo que não é JSON válido devolve **`400`**
- [ ] `{"texto": ""}` ou `{}` devolve **`422`** (ou `400`, se você optou por um só)
- [ ] Nenhum caso de erro do cliente devolve `5xx` — 4xx é culpa do cliente, 5xx é sua
- [ ] Um erro inesperado **não derruba o servidor**: ele responde `500` e continua de pé
      (prove: provoque um erro, depois chame `/health` de novo)

**HTTP bem feito**

- [ ] Toda resposta tem `Content-Type: application/json` (confira com `curl -i`)
- [ ] O corpo da resposta é JSON válido em **todos** os casos, inclusive nos erros
- [ ] O servidor imprime um log por requisição (método, caminho e status)

**Sem framework**

- [ ] `requirements.txt` não tem FastAPI, Flask, Django nem equivalente
- [ ] `grep -rE "fastapi|flask|django" .` não acha nada no seu código

**Bônus (não obrigatório)**

- [ ] `405 Method Not Allowed` com o header `Allow` na rota certa com o verbo errado
- [ ] `415 Unsupported Media Type` quando o `Content-Type` não é `application/json`
- [ ] Limite de tamanho do corpo devolvendo `413`
- [ ] `--host`/`--porta` configuráveis por argumento ou variável de ambiente
- [ ] O servidor atende duas requisições simultâneas sem enfileirar (`ThreadingHTTPServer`)
- [ ] Um colega conseguiu chamar o seu servidor de outra máquina da rede (`--host 0.0.0.0`)

---

## Evidências para o PR

Cole na descrição do pull request:

1. O log do servidor subindo (a linha que diz host e porta)
2. A saída de `curl -i` do `/health`
3. O `curl` do endpoint de predição nos **dois** casos: positivo e negativo
4. O status code de cada caso de erro que você tratou, em uma tabela:

   | Caso | Comando | Status |
   | --- | --- | --- |
   | rota inexistente | `curl -s -o /dev/null -w "%{http_code}" .../nao-existe` | `404` |
   | JSON malformado | ... | `400` |
   | texto vazio | ... | `422` |

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-02/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 02 — <resumo em poucas palavras>`;
   - descrição do que foi feito, como rodar e o que ficou pendente;
   - evidências (prints, saída de terminal, links do serviço).
5. Poste o link do pull request no canal da semana no **Discord**.

---

## Peer review

- Revise o pull request de **pelo menos 1 colega** antes do próximo encontro.
- Comente de forma específica: aponte o trecho, explique o porquê e sugira uma alternativa.
- Procure por: critérios de aceite atendidos, clareza do README, segredos vazados e reprodutibilidade.
- Nesta semana, o teste decisivo é literal: **clone o PR do colega, suba o servidor
  dele e tente quebrá-lo**. Mande um JSON torto, um método errado, uma rota que não
  existe, um texto de 100 mil caracteres. Se algo devolver `500` (ou derrubar o
  processo) onde deveria devolver `4xx`, isso é o review.
- Aprove apenas se você conseguiria rodar o projeto seguindo o README.
- Receber review também faz parte da entrega: responda aos comentários antes do encontro seguinte.
