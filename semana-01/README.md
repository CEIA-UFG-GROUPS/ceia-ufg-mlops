# Semana 01 — Linux + Bash + Git

> **Encontro 2 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

A base de tudo que vem depois: viver no terminal, automatizar com bash e trabalhar em equipe com o fluxo de branch, commit e pull request.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Navegar e manipular arquivos no terminal com confiança
- Entender permissões (`chmod`, `chown`) e quando elas quebram um deploy
- Conectar-se a máquinas remotas por SSH e mover arquivos (`scp`, `rsync`)
- Escrever um script bash com variáveis, argumentos, condicionais e tratamento de erro
- Executar o fluxo completo de Git: branch, commit, push, pull request e review

---

## Pré-requisitos

- Semana 00 concluída (ambiente, SSH e GitHub funcionando)
- Acesso ao terminal (WSL, Linux ou macOS)

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- Filosofia Unix: programas pequenos, pipes e texto como interface
- Árvore de diretórios, caminhos absolutos vs relativos, variáveis de ambiente e `PATH`
- Permissões e usuários: por que `Permission denied` aparece tanto
- SSH: chaves pública/privada, `authorized_keys` e `~/.ssh/config`
- Modelo mental do Git: working tree, staging area, commits e branches

### 💻 Mão na massa (~60 min)

- Tour pelo terminal: `ls`, `cd`, `find`, `grep`, pipes e redirecionamentos
- Baixar um dataset público de análise de sentimento e inspecioná-lo com `head`, `wc` e `cut`
- Escrever um script bash que baixa, descompacta e normaliza o dataset
- Tornar o script executável, adicionar `set -euo pipefail` e testar falhas propositais
- Criar branch, commitar o script, abrir pull request e revisar o PR de um colega

### 🎯 Desafio (~15 min)

Escrever um script bash que prepara o dataset de sentimento (download, limpeza básica e split treino/teste) e entregá-lo via pull request.

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

- [The Missing Semester of Your CS Education — MIT](https://missing.csail.mit.edu/)
- [ShellCheck — linter para scripts bash](https://www.shellcheck.net/)
- [Pro Git (livro, PT-BR)](https://git-scm.com/book/pt-br/v2)
- [explainshell — explica qualquer comando](https://explainshell.com/)

> **TODO (host):** acrescentar os links específicos que você usar na condução.

---

## Notas para o host

- Escolha um único dataset de sentimento e padronize-o para o semestre inteiro (ex.: IMDb, B2W Reviews, tweets em PT-BR)
- Deixe o dataset espelhado em um bucket ou na máquina do lab — não dependa de link externo na hora do lab
- Reserve 10 minutos finais só para o fluxo de pull request; é aí que as dúvidas aparecem
- Quem já domina bash pode fazer par com quem está começando

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [ ] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
