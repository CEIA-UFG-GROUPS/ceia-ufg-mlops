# Semana 05 — CI + Artifact Registry

> **Encontro 6 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

Automatizar a qualidade: GitHub Actions rodando testes e lint a cada push, e a imagem versionada indo parar no Artifact Registry do GCP.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Entender o que é integração contínua e por que ela antecede o deploy
- Escrever um workflow de GitHub Actions com jobs, steps e cache
- Rodar `pytest` e lint automaticamente em cada pull request
- Buildar e publicar a imagem Docker no Artifact Registry
- Versionar imagens com tags úteis (SHA do commit, `latest`, semver)

---

## Pré-requisitos

- Semana 04 concluída (imagem Docker funcionando)
- Projeto GCP ativo, com billing/créditos habilitados

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- CI/CD: o que é cada letra e onde o CI termina
- Anatomia de um workflow: trigger, job, runner, step e action
- Secrets e autenticação: por que não se commita chave (e o que é Workload Identity Federation)
- Registries: Docker Hub vs Artifact Registry, público vs privado
- Estratégia de tags: rastreabilidade entre commit e imagem em produção

### 💻 Mão na massa (~60 min)

- Criar `.github/workflows/ci.yml` rodando `pytest` e `ruff`
- Fazer o CI falhar de propósito e corrigir até ficar verde
- Criar o repositório no Artifact Registry via `gcloud`
- Autenticar o Actions no GCP e publicar a imagem com a tag do SHA
- Proteger a branch `main` exigindo CI verde para o merge

### 🎯 Desafio (~15 min)

Pipeline de CI verde em todo pull request e imagem publicada automaticamente no Artifact Registry a cada merge na `main`.

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

- [GitHub Actions — documentação](https://docs.github.com/actions)
- [Artifact Registry — documentação](https://cloud.google.com/artifact-registry/docs)
- [Autenticação do GitHub Actions no Google Cloud](https://github.com/google-github-actions/auth)
- [Ruff — linter Python](https://docs.astral.sh/ruff/)

> **TODO (host):** acrescentar os links específicos que você usar na condução.

---

## Notas para o host

- Material de referência do grupo anterior: `presentation/primeiro-semestre/aula10` na branch `main` (pode ser reaproveitado)
- Prefira Workload Identity Federation a chave JSON de service account; se faltar tempo, use a chave e explique o risco
- Minutos de Actions são limitados em repositório privado — oriente a turma a usar repositório público
- Tenha um workflow de exemplo pronto para colar, caso alguém trave no YAML

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [ ] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
