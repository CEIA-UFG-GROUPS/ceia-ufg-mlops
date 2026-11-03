# Semana 06 — GCP fundamentos

> **Encontro 7 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

Navegar o Google Cloud sem medo: projetos, IAM, `gcloud` e a decisão entre Cloud Run e Compute Engine — culminando no primeiro deploy manual da API.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Entender a hierarquia de recursos: organização, projeto e recurso
- Conceder e revogar permissões com IAM seguindo o menor privilégio
- Operar o `gcloud` CLI (configurações, projetos, autenticação)
- Escolher entre Cloud Run e Compute Engine para um dado workload
- Fazer o primeiro deploy manual da API no Cloud Run

---

## Pré-requisitos

- Semana 05 concluída (imagem publicada no Artifact Registry)
- `gcloud` CLI instalado e autenticado

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- Hierarquia de recursos e por que tudo vive dentro de um projeto
- IAM: principals, roles e policies; papéis primitivos vs predefinidos
- Service accounts: identidade de máquina, não de pessoa
- Serverless vs IaaS: Cloud Run, Compute Engine e onde a GPU 4090 entra
- Billing, créditos e alertas de orçamento — como não queimar a verba

### 💻 Mão na massa (~60 min)

- Configurar o `gcloud` (`gcloud init`, `gcloud config set project`)
- Explorar o IAM: criar uma service account com o papel mínimo necessário
- Configurar um alerta de orçamento no billing
- Rodar `gcloud run deploy` apontando para a imagem do Artifact Registry
- Testar a URL pública do serviço com `curl` e revisar os logs

### 🎯 Desafio (~15 min)

Primeiro deploy manual da API de sentimento no Cloud Run, acessível por URL pública.

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

- [Google Cloud — visão geral do IAM](https://cloud.google.com/iam/docs/overview)
- [gcloud CLI — referência](https://cloud.google.com/sdk/gcloud/reference)
- [Cloud Run — documentação](https://cloud.google.com/run/docs)
- [Como escolher um serviço de computação no GCP](https://cloud.google.com/hosting-options)

> **TODO (host):** acrescentar os links específicos que você usar na condução.

---

## Notas para o host

- Comece pelo alerta de orçamento: é o item que evita susto no fim do semestre
- Deixe claro o padrão de nomes de projeto e serviço, para facilitar o suporte depois
- Permissão insuficiente é o erro mais comum do dia — tenha a lista de roles necessárias à mão
- Combine quem desliga o quê ao fim do lab

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [ ] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
