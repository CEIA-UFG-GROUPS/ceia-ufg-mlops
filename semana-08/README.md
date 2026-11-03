# Semana 08 — Config, secrets e ambientes

> **Encontro 9 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

Separar código de configuração: variáveis de ambiente, Secret Manager, ambientes staging e prod, e health checks que dizem a verdade.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Aplicar a separação entre código, configuração e segredo
- Usar o Secret Manager do GCP e injetar segredos no Cloud Run
- Manter dois ambientes (staging e prod) com a mesma imagem e configs diferentes
- Implementar health checks úteis (liveness vs readiness)
- Evitar vazamento de segredo em log, build e repositório

---

## Pré-requisitos

- Semana 07 concluída (deploy automático funcionando)
- Permissão para criar secrets no projeto GCP

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- The Twelve-Factor App, fator III: config no ambiente
- Config vs secret: o que muda no tratamento
- Secret Manager: versões, rotação e controle de acesso por IAM
- Promoção entre ambientes: mesma imagem, config diferente
- Health checks: o que o `/health` deve (e não deve) verificar

### 💻 Mão na massa (~60 min)

- Extrair toda configuração hardcoded da API para variáveis de ambiente
- Criar um secret no Secret Manager e dar acesso à service account do serviço
- Injetar o secret no Cloud Run e lê-lo na aplicação
- Criar o serviço `staging` apontando para a mesma imagem, com config diferente
- Melhorar o `/health` para checar dependências reais (modelo carregado, cache acessível)

### 🎯 Desafio (~15 min)

Serviço totalmente parametrizado, com pelo menos um secret gerenciado pelo Secret Manager e ambientes staging e prod separados.

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

- [The Twelve-Factor App (PT-BR)](https://12factor.net/pt_br/)
- [Secret Manager — documentação](https://cloud.google.com/secret-manager/docs)
- [Secrets no Cloud Run](https://cloud.google.com/run/docs/configuring/services/secrets)
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

> **TODO (host):** acrescentar os links específicos que você usar na condução.

---

## Notas para o host

- Peça para a turma procurar valores hardcoded no próprio código antes de explicar a teoria
- Mostre um caso real de secret vazado em log — ajuda a fixar a regra
- Combine o padrão de nomes de secret e de serviço (`*-staging`, `*-prod`)
- Lembre de limitar quem tem o papel `secretmanager.secretAccessor`

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [ ] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
