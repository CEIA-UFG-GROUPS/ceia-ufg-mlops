# Semana 04 — Docker

> **Encontro 5 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

Empacotar a API para que ela rode igual na sua máquina, na 4090 do lab e na nuvem — imagens, containers, Dockerfile e Compose.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Diferenciar imagem, container, layer e registry
- Escrever um Dockerfile eficiente (cache de layers, multi-stage, imagem enxuta)
- Orquestrar mais de um serviço com Docker Compose
- Entender networks e volumes: como containers se enxergam e persistem dados
- Containerizar a API de sentimento da Semana 03

---

## Pré-requisitos

- Semana 03 concluída (API FastAPI funcionando)
- Docker instalado e funcionando (`docker run hello-world`)

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- O problema que o Docker resolve: o clássico "na minha máquina funciona"
- Imagem vs container; filesystem em layers e cache de build
- Dockerfile: instruções essenciais e a ordem que economiza build
- Networks: como o Compose resolve nomes de serviço
- Volumes vs bind mounts: dados que sobrevivem ao container

### 💻 Mão na massa (~60 min)

- Rodar containers prontos e inspecioná-los com `docker ps`, `docker logs` e `docker exec`
- Escrever o Dockerfile da API de sentimento e buildar a imagem
- Reduzir o tamanho da imagem com multi-stage e `.dockerignore`
- Subir a API + um segundo serviço (ex.: Redis ou Postgres) com `docker compose up`
- Fazer os dois serviços conversarem pela network do Compose

### 🎯 Desafio (~15 min)

Containerizar a API e orquestrá-la com um segundo serviço via Docker Compose.

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

- [Docker — Get Started](https://docs.docker.com/get-started/)
- [Dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Compose — documentação](https://docs.docker.com/compose/)
- [Play with Docker (ambiente online)](https://labs.play-with-docker.com/)

> **TODO (host):** acrescentar os links específicos que você usar na condução.

---

## Notas para o host

- Material de referência do grupo anterior: `presentation/primeiro-semestre/aula04` na branch `main` (pode ser reaproveitado)
- Cuidado com o tamanho da imagem se o modelo for grande — discuta baixar o modelo no build vs em runtime
- Mostre o cache de layer quebrando ao mudar uma linha do `requirements.txt`
- Se a rede do lab for lenta, pré-baixe as imagens base antes do encontro

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [ ] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
