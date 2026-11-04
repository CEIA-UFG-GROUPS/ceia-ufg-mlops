# Desafio — Semana 05: CI verde + imagem no Artifact Registry

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Garantir que **nenhum código entre na `main` sem passar nos testes**, e que **cada merge gere uma imagem rastreável até o commit** que a originou.

No fim, a pergunta "qual código está rodando nesta imagem?" tem que ter resposta em dois comandos.

---

## O que entregar

No **seu repositório pessoal** do projeto (o mesmo da Semana 04):

**1. Testes (`tests/`)**

- No mínimo **10 testes** cobrindo os quatro blocos vistos no lab:
  - status codes (`200`, `422` nas validações, `405` no método errado);
  - formato da resposta (chaves exatas `texto`, `sentimento`, `score`, `modelo` e seus tipos);
  - comportamento (pelo menos 2 frases positivas e 2 negativas, via `@pytest.mark.parametrize`);
  - `/health` respondendo com `modelo_carregado: true`.
- Pelo menos um teste **seu**, que não esteja em [`codigo/tests/test_predict.py`](./codigo/tests/test_predict.py). Escreva no PR o que ele protege.
- `pytest` tem que passar com o repositório recém-clonado, sem passo manual nenhum.

**2. Lint (`pyproject.toml`)**

- `ruff` configurado com, no mínimo, `select = ["E", "W", "F", "I"]`.
- `ruff check .` e `ruff format --check .` limpos.

**3. Workflow (`.github/workflows/ci.yml`)**

- Jobs **separados** de lint e de teste, disparados em `push` na `main` e em `pull_request`.
- Job de build e push com `needs: [lint, test]` e `if` que o restringe a push na `main`.
- Autenticação no GCP **sem chave JSON commitada** — WIF é o esperado; chave em Secret é aceita com a justificativa escrita no PR.
- A imagem publicada com **duas tags**: `${{ github.sha }}` e `latest`.

**4. Branch `main` protegida**

- Pull request obrigatório antes do merge.
- Status checks de lint e teste obrigatórios para liberar o merge.
- Push direto na `main` bloqueado.

**5. README do seu repositório**

- Badge do CI no topo:
  ```markdown
  ![CI](https://github.com/<SEU-USUARIO>/<SEU-REPO>/actions/workflows/ci.yml/badge.svg)
  ```
- O endereço completo da imagem no Artifact Registry.
- Como rodar os testes localmente, em dois comandos.

---

## Critérios de aceite

Cada item precisa de **evidência verificável** (link, print ou saída de terminal colada no PR).

### CI

- [ ] O CI roda automaticamente ao abrir um pull request — *link para a aba Checks do PR*
- [ ] Lint e teste são jobs separados e rodam em paralelo — *print da aba Actions mostrando os dois*
- [ ] O pipeline **falha** quando um teste quebra — *link para uma execução vermelha, com o log do `pytest` visível*
- [ ] O pipeline volta ao verde depois da correção — *link para a execução verde seguinte*
- [ ] O badge do CI aparece verde no README

### Imagem

- [ ] A imagem está no Artifact Registry — *saída de `gcloud artifacts docker images list ... --include-tags`*
- [ ] A tag é **o SHA do commit de merge** — *a mesma saída acima, lado a lado com `git log -1 --format=%H` na `main`*
- [ ] A imagem foi publicada **pelo CI**, não pela sua máquina — *link para a execução do job `build-and-push` na `main`*
- [ ] O job de push **não roda** em pull request — *print do PR mostrando `build-and-push` como `Skipped`*

### Segurança

- [ ] Nenhuma credencial commitada — *saída de `git log -p | Select-String -Pattern "private_key"` sem resultados*
- [ ] Se usou chave JSON em vez de WIF, a escolha está justificada no PR e a revogação está agendada
- [ ] A service account tem **apenas** `roles/artifactregistry.writer` — *saída de `gcloud projects get-iam-policy`*

### Branch protegida

- [ ] Push direto na `main` é recusado — *cole a saída `! [remote rejected] main -> main (protected branch hook declined)`*
- [ ] Um PR com teste quebrando **não** pode ser mergeado — *print do botão de merge bloqueado*

---

## Nível 2 (opcional)

Para quem terminou e quer ir além — escolha um:

- **Cobertura:** adicione `pytest-cov` ao CI e falhe o build abaixo de 80% (`--cov=app --cov-fail-under=80`).
- **Matriz:** rode os testes em Python 3.11 **e** 3.12 com `strategy.matrix`, e explique no PR o que isso pegaria.
- **Tag semântica:** publique também uma tag `v<major>.<minor>.<patch>` quando o push for de uma git tag (`on: push: tags: ['v*']`).
- **Cache do Docker:** use `docker/build-push-action` com `cache-from`/`cache-to` e compare o tempo do build antes e depois.
- **Limpeza:** crie uma *cleanup policy* no Artifact Registry que mantenha só as 10 imagens mais recentes, e explique o trade-off.

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-05/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 05 — <resumo em poucas palavras>`;
   - descrição do que foi feito, como rodar e o que ficou pendente;
   - evidências de cada critério de aceite (prints, saída de terminal, links do serviço).
5. **Não feche o PR.** Ele é a entrega: é nele que o CI aparece rodando e é nele que o peer review acontece. Faça o merge só depois da revisão.
6. Poste o link do pull request no canal da semana no **Discord**.

> O PR desta semana é especial: ele é, ao mesmo tempo, a entrega e a demonstração de que o mecanismo funciona. Um PR sem checks verdes visíveis não conta como entregue.

---

## Peer review

- Revise o pull request de **pelo menos 1 colega** antes do próximo encontro.
- Comente de forma específica: aponte o trecho, explique o porquê e sugira uma alternativa.
- Procure especificamente por:
  - **Credencial vazada** — `.json` de service account, token, chave em texto no YAML ou no log do Actions;
  - **CI de fachada** — job com `continue-on-error: true`, `|| true` no fim do comando, `pytest` sem testes de verdade, lint com tudo ignorado;
  - **Rastreabilidade** — a tag da imagem bate com algum commit real? Ou só tem `latest`?
  - **`if` do job de push** — ele publicaria imagem a partir de um pull request de fork? (Isso é um buraco de segurança clássico.)
  - **Reprodutibilidade** — clonando o repositório e seguindo o README, você consegue rodar os testes?
- Aprove apenas se você conseguiria rodar o projeto seguindo o README.
- Receber review também faz parte da entrega: responda aos comentários antes do encontro seguinte.
