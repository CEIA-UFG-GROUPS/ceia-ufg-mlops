# Semana 00 — Onboarding (ao vivo)

> **Encontro 1 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

Encontro de abertura: todo mundo sai com o ambiente pronto para os 11 labs seguintes — contas, acessos, ferramentas e canal de comunicação funcionando.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Criar e configurar a conta GCP com os créditos educacionais ativos
- Ter um ambiente local funcional (WSL2 + Docker) ou saber usar a alternativa do lab
- Acessar por SSH as máquinas com GPU 4090 do laboratório
- Ter Git e GitHub configurados (chave SSH, nome, e-mail, repositório pessoal criado)
- Estar no servidor do Discord, no canal certo e com o nome identificável

---

## Pré-requisitos

- Notebook/desktop próprio com permissão para instalar software
- Conta Google (para o GCP) e conta GitHub
- Nenhum conhecimento prévio de cloud é necessário

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- Como o grupo funciona: labs independentes, rodízio de hosts, entrega por pull request
- O domínio recorrente do semestre: análise de sentimento (NLP) como fio condutor
- Visão geral da infraestrutura: GCP (créditos) + máquinas 4090 do lab, e quando usar cada uma
- Regras de custo: o que pode ficar ligado e o que precisa ser desligado ao fim do lab

### 💻 Mão na massa (~60 min)

- Criar o projeto no GCP e ativar os créditos educacionais
- Instalar WSL2 + Docker Desktop (Windows) ou Docker Engine (Linux/macOS)
- Gerar chave SSH, cadastrar no GitHub e testar com `ssh -T git@github.com`
- Primeiro acesso SSH às máquinas 4090 do lab (`nvidia-smi` para confirmar a GPU)
- Entrar no Discord, se apresentar e escolher a semana que vai hostear

### 🎯 Desafio (~15 min)

Criar o repositório pessoal do projeto do semestre e rodar um hello world (local e na máquina do lab), abrindo o primeiro pull request.

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

- [Google Cloud para educação](https://cloud.google.com/edu)
- [Instalação do WSL2](https://learn.microsoft.com/windows/wsl/install)
- [Docker Desktop](https://docs.docker.com/desktop/)
- [Gerando uma chave SSH para o GitHub](https://docs.github.com/authentication/connecting-to-github-with-ssh)

> **TODO (host):** acrescentar os links específicos que você usar na condução.

---

## Notas para o host

- Esta é a única sessão majoritariamente de setup — proteja o tempo, nada de teoria longa
- Tenha um checklist compartilhado (planilha ou thread no Discord) para marcar quem concluiu cada item
- Separe duas pessoas como plantão de setup, para resolver problemas individuais sem travar a turma
- Peça para quem terminar cedo ajudar quem travou — é o primeiro exercício de peer review

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [ ] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
