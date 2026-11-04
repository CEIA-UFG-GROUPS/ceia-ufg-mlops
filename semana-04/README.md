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
- Imagem base baixada antes do encontro: `docker pull python:3.12-slim`

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
- Subir a API + uma mini-UI Streamlit com `docker compose up`
- Fazer os dois serviços conversarem pela network do Compose

### 🎯 Desafio (~15 min)

Containerizar a API e orquestrá-la com um segundo serviço via Docker Compose.

Enunciado completo em [`desafio.md`](./desafio.md).

---

## Passo a passo

Todos os comandos rodam a partir de `semana-04/codigo/`.

> **Windows / PowerShell:** `curl` é apelido de `Invoke-WebRequest` e **não** aceita
> `-X`/`-d`. Use `curl.exe` no lugar de `curl`, ou a versão `Invoke-RestMethod`
> indicada no [`codigo/README.md`](./codigo/README.md).

### Bloco 1 — do código local ao primeiro container (~20 min)

1. **Confirmar que o Docker responde.**

   ```bash
   docker run --rm hello-world
   docker version
   ```

   *Esperado:* a mensagem "Hello from Docker!". Se falhar aqui, o Docker Desktop
   não está rodando — resolva antes de seguir.

2. **Abrir o código e entender o que vamos empacotar.**

   ```bash
   cd semana-04/codigo
   ls app
   ```

   *Esperado:* `main.py`, `modelo.py`, `requirements.txt`. Leia `modelo.py` em voz
   alta: o modelo é um TF-IDF + Regressão Logística treinado no startup, a partir
   de ~60 frases embutidas no próprio arquivo. Sem download, sem GPU, sem artefato.

3. **Rodar a API sem Docker, para ter uma base de comparação.**

   ```bash
   python -m venv .venv
   source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
   pip install -r app/requirements.txt
   uvicorn app.main:app --port 8000
   ```

   *Esperado:* nos logs, `modelo 'tfidf+logreg' treinado em ~30 ms` e
   `Uvicorn running on http://127.0.0.1:8000`. Abra <http://localhost:8000/docs>,
   teste o `/predict` por lá e encerre com `Ctrl+C`.

4. **Escrever o Dockerfile — versão 1, single-stage.** Crie `Dockerfile.v1` e
   desative temporariamente o `.dockerignore` do repositório, para enxergar como
   fica um build ingênuo:

   ```bash
   mv .dockerignore dockerignore.off
   ```

   ```dockerfile
   # Dockerfile.v1 — de propósito cheio de defeitos
   FROM python:3.12-slim
   WORKDIR /app
   COPY . .
   RUN pip install --no-cache-dir -r app/requirements.txt
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

   Repare no `--host 0.0.0.0`: com `127.0.0.1`, a API só escuta *dentro* do
   container e nenhuma publicação de porta funciona. É o erro número um do dia.

5. **Buildar e cronometrar.**

   ```bash
   docker build -f Dockerfile.v1 -t sentimento-api:v1 .
   docker images sentimento-api
   ```

   *Esperado:* build de 1–3 min (depende da rede). Anote **dois** números: o
   `transferring context: ... MB` da primeira linha do build e o `SIZE` da imagem.
   Se você rodou o passo 3, o `.venv/` inteiro foi junto — o contexto passa dos
   300 MB e a imagem fica bem acima de meio giga. Vamos reduzir os dois no bloco 2.

> ✅ **checkpoint 1 — todo mundo chegou até aqui?**
> Todos com `docker images` listando `sentimento-api:v1`.

### Bloco 2 — rodar, testar e enxugar a imagem (~20 min)

6. **Subir o container e publicar a porta.**

   ```bash
   docker run --rm -d -p 8000:8000 --name sentimento sentimento-api:v1
   docker ps
   docker logs sentimento
   ```

   *Esperado:* o container em `Up ...`, e nos logs a mesma linha de treino do
   passo 3. O `-p 8000:8000` lê-se "porta 8000 do host → porta 8000 do container".

7. **Testar o `/predict` de fora do container.**

   ```bash
   curl http://localhost:8000/health
   curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{"texto": "adorei o atendimento, chegou antes do prazo"}'
   ```

   *Esperado:*

   ```json
   {"texto":"adorei o atendimento, chegou antes do prazo","sentimento":"positivo","score":0.7274,"modelo":"tfidf+logreg"}
   ```

   (o `score` pode variar nos últimos decimais conforme a versão do scikit-learn;
   o que importa é o `sentimento`)

   Mande também `{"texto": "pessimo, veio quebrado e atrasado"}` (deve vir
   `negativo`) e `{"texto": ""}` (deve vir **422** — a validação da Semana 03
   continua valendo dentro do container).

8. **Espiar por dentro do container.**

   ```bash
   docker exec -it sentimento sh -c "ls -a /app && ls /app/app"
   docker exec -it sentimento sh -c "whoami"
   docker stop sentimento
   ```

   *Esperado:* o conteúdo copiado pelo `COPY . .` — inclusive `.venv/`,
   `__pycache__/`, `README.md` e a pasta `ui/`, que não têm nada a ver com rodar
   a API. E `whoami` respondendo `root`. Ambos são problemas; vamos corrigir agora.

9. **Quebrar e reaproveitar o cache de layer.** Edite uma linha qualquer de
   `app/main.py` (uma mensagem de log serve) e rebuilde:

   ```bash
   docker build -f Dockerfile.v1 -t sentimento-api:v1 .
   ```

   *Esperado:* o `pip install` roda **de novo**, porque o `COPY . .` veio antes
   dele e invalidou todas as layers seguintes. Essa é a dor que o Dockerfile
   definitivo resolve copiando `requirements.txt` primeiro.

10. **Trocar para o Dockerfile multi-stage do repositório.** Restaure o
    `.dockerignore`, leia os dois arquivos e compare com a v1:

    ```bash
    mv dockerignore.off .dockerignore
    ```

    No [`Dockerfile`](./codigo/Dockerfile): `requirements.txt` copiado **antes** do
    código, dependências instaladas em um venv no estágio `builder`, estágio
    `runtime` recebendo só o venv pronto, usuário não-root e `HEALTHCHECK`. No
    [`.dockerignore`](./codigo/.dockerignore): `.venv/`, `.git/`, `__pycache__/` e
    `ui/` fora do contexto.

    ```bash
    docker build -t sentimento-api:semana-04 .
    docker images sentimento-api
    ```

    *Esperado:* `transferring context` cai para poucos KB e a imagem fica
    **visivelmente menor** que a `v1` (sem cache de pip, sem `.venv`, sem `.git`).
    Rebuilde depois de editar um `.py` e confirme o `CACHED` no passo do
    `pip install` — o build inteiro agora leva segundos.

> ✅ **checkpoint 2 — todo mundo chegou até aqui?**
> `docker images` mostrando as duas tags lado a lado e a diferença de tamanho.
> Quem ficou para trás pode seguir só com `sentimento-api:semana-04`.

### Bloco 3 — dois serviços com Compose (~20 min)

11. **Ler o [`docker-compose.yml`](./codigo/docker-compose.yml)** antes de rodar:
    dois serviços (`api` e `ui`), a UI apontando para `http://api:8000` e um
    `depends_on` com `condition: service_healthy`.

    ```bash
    docker compose config --quiet && echo "compose ok"
    ```

    *Esperado:* `compose ok` (o comando valida o arquivo sem subir nada).

12. **Subir o ambiente completo.**

    ```bash
    docker compose up --build
    ```

    *Esperado:* a API sobe primeiro; a UI só inicia depois que o healthcheck da
    API passa. Em outro terminal:

    ```bash
    docker compose ps
    ```

    A coluna STATUS do serviço `api` deve mostrar `(healthy)`.

13. **Usar a UI e fechar o ciclo.** Abra <http://localhost:8501>, escreva uma
    frase e clique em *Classificar*.

    *Esperado:* o sentimento e o score aparecem na tela — e, nos logs da API
    (`docker compose logs -f api`), uma linha `predict | sentimento=... score=...`.
    A UI não tem modelo nenhum: ela só chamou a API.

14. **Provar que o nome do serviço é o hostname.**

    ```bash
    docker compose exec ui python -c "import socket; print(socket.gethostbyname('api'))"
    docker compose exec ui python -c "import urllib.request; print(urllib.request.urlopen('http://api:8000/health').read())"
    ```

    *Esperado:* um IP privado da network do Compose e o JSON do `/health`. Agora
    tente `http://localhost:8000` de dentro da UI: **falha**, porque `localhost`
    dentro do container `ui` é o próprio `ui`.

15. **Derrubar tudo.**

    ```bash
    docker compose down
    docker ps -a
    ```

    *Esperado:* nenhum container do projeto `sentimento-semana-04` sobrando.

> ✅ **checkpoint 3 — todo mundo chegou até aqui?**
> Todos conseguiram classificar uma frase pela UI em <http://localhost:8501>.

16. **Limpeza.** Apague os artefatos de treino do lab e, se o disco estiver
    apertado, a imagem `v1`:

    ```bash
    rm Dockerfile.v1
    ls .dockerignore            # confirme que ele voltou no passo 10
    docker image rm sentimento-api:v1
    docker system df
    ```

---

## Código

O código de apoio desta semana vive em [`codigo/`](./codigo/) — veja
[`codigo/README.md`](./codigo/README.md) para rodar em um comando.

| Arquivo | O que é |
| --- | --- |
| [`codigo/app/main.py`](./codigo/app/main.py) | API FastAPI: `/`, `/health` e `POST /predict` |
| [`codigo/app/modelo.py`](./codigo/app/modelo.py) | TF-IDF + Regressão Logística e o mini-dataset PT-BR |
| [`codigo/app/requirements.txt`](./codigo/app/requirements.txt) | Dependências da API, com versões fixadas |
| [`codigo/Dockerfile`](./codigo/Dockerfile) | Imagem da API: multi-stage, usuário não-root, healthcheck |
| [`codigo/.dockerignore`](./codigo/.dockerignore) | O que não entra no contexto de build |
| [`codigo/docker-compose.yml`](./codigo/docker-compose.yml) | Orquestra `api` + `ui` na mesma network |
| [`codigo/ui/app_ui.py`](./codigo/ui/app_ui.py) | Mini-UI Streamlit que consome `http://api:8000` |
| [`codigo/ui/Dockerfile`](./codigo/ui/Dockerfile) | Imagem da UI (single-stage, para contrastar) |

---

## Recursos e links

- [Docker — Get Started](https://docs.docker.com/get-started/)
- [Dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Docker Compose — documentação](https://docs.docker.com/compose/)
- [Compose file reference — `healthcheck` e `depends_on`](https://docs.docker.com/reference/compose-file/services/)
- [Docker — networking no Compose](https://docs.docker.com/compose/how-tos/networking/)
- [Play with Docker (ambiente online)](https://labs.play-with-docker.com/)

---

## Notas para o host

- Material de referência do grupo anterior: `presentation/primeiro-semestre/aula04` na branch `main` (pode ser reaproveitado)
- O modelo é treinado no startup de propósito: nada de baixar pesos no build. Use isso para abrir a discussão "baixar modelo no build vs em runtime vs volume montado" — que volta na Semana 06
- O passo 9 (cache quebrando ao editar um `.py`) é o momento didático mais importante do dia; não pule
- Se a rede do lab for lenta, peça `docker pull python:3.12-slim` com antecedência e deixe as imagens pré-buildadas em um pendrive/registry local
- Plano B para quem não tiver Docker: <https://labs.play-with-docker.com/> com o repositório clonado
- A UI Streamlit é a parte mais lenta de buildar (~2 min). Se o tempo apertar, suba só a API com `docker compose up api` e mostre a UI do seu ambiente

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [x] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
