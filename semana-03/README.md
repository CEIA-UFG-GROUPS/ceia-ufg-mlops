# Semana 03 — Como a web funciona II (APIs)

> **Encontro 4 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

Do servidor cru para uma API de verdade: REST, JSON, status codes e validação, construindo com FastAPI o serviço que vai nos acompanhar até o Demo Day.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Projetar uma API REST com recursos, métodos e status codes coerentes
- Serializar e validar entrada/saída com JSON e Pydantic
- Construir uma API com FastAPI e documentá-la automaticamente (OpenAPI/Swagger)
- Tratar erros e retornar mensagens úteis ao cliente
- Entender o papel do TLS e quando o certificado é responsabilidade da plataforma

---

## Pré-requisitos

- Semana 02 concluída (HTTP e portas claros)
- Python 3.10+ e ambiente virtual configurado

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- REST na prática: recursos, verbos e idempotência
- Status codes que importam: 200, 201, 400, 404, 422 e 500
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

> **TODO (host):** detalhar aqui o passo a passo do lab, na ordem em que ele será conduzido.
> Sugestão de formato: um passo numerado por ação, com o comando exato e o resultado esperado.
>
> 1. `> TODO` — passo 1
> 2. `> TODO` — passo 2
> 3. `> TODO` — passo 3
>
> Marque os pontos de checkpoint (`checkpoint: todo mundo chegou até aqui?`) a cada 15-20 minutos.

---

## Código

O código de apoio desta semana vive em [`codigo/`](./codigo/).

> **TODO (host):** incluir ali os arquivos de apoio (scripts, configs, exemplos) usados no lab,
> junto de um `README.md` curto dentro de `codigo/` explicando como executá-los.

---

## Recursos e links

- [FastAPI — documentação oficial](https://fastapi.tiangolo.com/)
- [Pydantic — documentação](https://docs.pydantic.dev/)
- [MDN — Status codes HTTP](https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Status)
- [REST API Tutorial](https://restfulapi.net/)

> **TODO (host):** acrescentar os links específicos que você usar na condução.

---

## Notas para o host

- Congele o contrato do `/predict` aqui: ele será reusado das Semanas 04 a 11
- Peça para a turma anotar o contrato no README — vai virar referência do load test da Semana 10
- Mostre o `/docs` cedo; costuma ser o momento mais marcante da sessão
- Deixe o modelo carregado uma vez no startup, e não a cada requisição

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [ ] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
