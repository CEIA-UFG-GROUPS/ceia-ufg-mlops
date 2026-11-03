# Semana 07 — CD serverless

> **Encontro 8 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

Fechar o ciclo: push na `main` dispara build, publicação e deploy automático no Cloud Run — sem ninguém rodando comando na mão.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Entender entrega contínua e os riscos de automatizar o deploy
- Encadear build, push e deploy em um único workflow do GitHub Actions
- Passar variáveis de ambiente para o serviço no Cloud Run
- Verificar o deploy automaticamente (smoke test pós-deploy)
- Saber como reverter para a revisão anterior

---

## Pré-requisitos

- Semana 06 concluída (deploy manual funcionando)
- CI publicando a imagem no Artifact Registry (Semana 05)

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- Continuous Delivery vs Continuous Deployment
- Revisões do Cloud Run, divisão de tráfego e rollback
- Variáveis de ambiente: o que pode e o que não pode ficar ali (gancho para a Semana 08)
- Gates de deploy: testes, aprovação manual e ambientes
- Idempotência e repetibilidade do pipeline

### 💻 Mão na massa (~60 min)

- Estender o workflow com um job `deploy` dependente do job de build
- Configurar as permissões da service account de deploy
- Injetar variáveis de ambiente no `gcloud run deploy`
- Adicionar um smoke test que chama `/health` após o deploy
- Provocar um deploy ruim e fazer rollback para a revisão anterior

### 🎯 Desafio (~15 min)

Deploy automático no Cloud Run a cada push na `main`, com smoke test e rollback documentado.

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

- [Deploy contínuo no Cloud Run](https://cloud.google.com/run/docs/continuous-deployment-with-cloud-build)
- [google-github-actions/deploy-cloudrun](https://github.com/google-github-actions/deploy-cloudrun)
- [Gerenciando revisões e tráfego no Cloud Run](https://cloud.google.com/run/docs/managing/revisions)
- [GitHub Actions — environments e proteções](https://docs.github.com/actions/deployment/targeting-different-environments)

> **TODO (host):** acrescentar os links específicos que você usar na condução.

---

## Notas para o host

- O erro mais comum é permissão da service account de deploy — tenha a lista pronta
- Mostre o rollback na prática; a turma precisa ver que dá para desfazer
- Deixe explícito que os secrets ainda estão mal resolvidos aqui — isso é assunto da Semana 08
- Se o tempo apertar, corte o smoke test e deixe-o como parte do desafio

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [ ] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
