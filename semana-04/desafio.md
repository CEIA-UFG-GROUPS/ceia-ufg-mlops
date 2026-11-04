# Desafio — Semana 04: API containerizada + segundo serviço via Compose

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Rodar **a sua** API de sentimento inteiramente em container, junto de um segundo
serviço, de forma que qualquer colega consiga subir tudo com um comando só e sem
instalar nada além do Docker.

O ponto não é copiar o `codigo/` do lab: é containerizar a API que **você** escreveu
na Semana 03. Se a sua ainda não estiver pronta, parta da do lab e adapte.

---

## O que entregar

Dentro do seu repositório, em uma pasta `semana-04/` (ou equivalente):

| Arquivo | Requisito |
| --- | --- |
| `Dockerfile` | Da API. **Multi-stage**, base `-slim` ou `-alpine`, rodando como usuário não-root |
| `.dockerignore` | Excluindo no mínimo `.git/`, `.venv/`, `__pycache__/` e artefatos locais |
| `docker-compose.yml` | Dois serviços: a API e mais um (UI, cliente, cache, banco ou worker) |
| `README.md` | Como subir em um comando, com um exemplo de `curl` para o `/predict` |

O segundo serviço é livre, desde que **converse com a API ou seja usado por ela**.
Ideias: mini-UI Streamlit, um cliente que dispara requisições em loop, Redis como
cache de predições, Postgres gravando um log de predições.

---

## Critérios de aceite

Marque cada item depois de verificar com o comando indicado.

**Funciona**

- [ ] `docker compose up --build` sobe o ambiente completo, do zero, sem passo manual
- [ ] A API responde `200` em `GET /health` a partir do host
- [ ] `POST /predict` com `{"texto": "..."}` devolve `200` e um JSON com `sentimento` e `score`
- [ ] `POST /predict` com `{"texto": ""}` devolve `422` (a validação da Semana 03 continua valendo)
- [ ] `docker compose down` derruba tudo sem deixar container órfão (`docker ps -a` limpo)

**Imagem enxuta**

- [ ] O `Dockerfile` da API é multi-stage (tem mais de um `FROM`)
- [ ] `docker images` mostra a imagem da API **abaixo de 600 MB**
- [ ] O build **não** copia `.venv/`, `.git/` nem `__pycache__` para dentro da imagem
      (prove com `docker run --rm <imagem> ls -a /app`)
- [ ] Editar um arquivo `.py` e rebuildar **não** refaz o `pip install` (aparece `CACHED`)
- [ ] `docker run --rm <imagem> whoami` **não** responde `root`

**Compose de verdade**

- [ ] Os dois serviços se comunicam pelo **nome do serviço**, não por `localhost` nem IP fixo
      (prove com `docker compose exec <servico2> python -c "import socket; print(socket.gethostbyname('api'))"`)
- [ ] A API tem `healthcheck` e `docker compose ps` mostra `(healthy)`
- [ ] O segundo serviço espera a API ficar saudável (`depends_on` com `condition: service_healthy`)
- [ ] Nenhum segredo hardcoded: o que varia vem de `environment` ou `.env` (e o `.env` está no `.gitignore`)

**Bônus (não obrigatório)**

- [ ] Imagem da API abaixo de **300 MB**
- [ ] Publicar a imagem em um registry (Docker Hub ou GHCR) e documentar o `docker pull`
- [ ] Um volume nomeado persistindo algo entre `down` e `up`

---

## Evidências para o PR

Cole na descrição do pull request:

1. A saída de `docker images <sua-imagem>` (mostrando a tag e o tamanho)
2. A saída de `docker compose ps` com o `(healthy)` visível
3. O `curl` do `/predict` com a resposta JSON
4. Um print da UI/segundo serviço funcionando (se for visual)

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-04/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 04 — <resumo em poucas palavras>`;
   - descrição do que foi feito, como rodar e o que ficou pendente;
   - evidências (prints, saída de terminal, links do serviço).
5. Poste o link do pull request no canal da semana no **Discord**.

---

## Peer review

- Revise o pull request de **pelo menos 1 colega** antes do próximo encontro.
- Comente de forma específica: aponte o trecho, explique o porquê e sugira uma alternativa.
- Procure por: critérios de aceite atendidos, clareza do README, segredos vazados e reprodutibilidade.
- Nesta semana, o teste decisivo é literal: **clone o PR do colega e rode `docker compose up --build`**.
  Se não subir seguindo só o README dele, isso é o review.
- Aprove apenas se você conseguiria rodar o projeto seguindo o README.
- Receber review também faz parte da entrega: responda aos comentários antes do encontro seguinte.
