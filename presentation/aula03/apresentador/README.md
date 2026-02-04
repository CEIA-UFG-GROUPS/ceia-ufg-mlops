# Git, GitHub, GitFlow e Estruturação de Repositórios em MLOps

## README do Apresentador

Este documento organiza a apresentação da aula e serve como **guia conceitual** para o expositor.
A estrutura abaixo deve ser seguida para garantir clareza, progressão lógica e alinhamento com o grupo.

---

## 1️⃣ Motivação

### 1.1 Por que versionar em ML?

- Resultados dependem de **código + dados + parâmetros + modelo**
- Erros podem ser **silenciosos** e difíceis de rastrear
- Reprodutibilidade é requisito para ciência e para produto

### 1.2 Diferenças entre software tradicional e ML

- Software tradicional: foco no código e releases claras
- ML: múltiplos artefatos e ciclos de experimento
- Necessidade de rastrear versões de dados e ambiente

### 1.3 Impacto prático

- Evita perda de experimentos e retrabalho
- Facilita colaboração e revisão
- Dá base para CI/CD e deploy seguro

---

## 2️⃣ Como Funciona

### 2.1 Conceitos fundamentais

- Git: controle de versão distribuído
- Commit, branch, merge e tag
- Repositório remoto como **fonte da verdade**

### 2.2 GitHub e colaboração

- Pull Requests e revisão de código
- Issues para tarefas e discussão
- Ações de CI para testes e validação

### 2.3 Estratégias de branching

- GitFlow: `main`, `develop`, feature, release, hotfix
- Trunk-based/GitHub Flow: branches curtas e integração frequente
- Critérios de escolha: tamanho do time, frequência de deploy, maturidade de CI

### 2.4 Organização de repositórios em ML

- Estrutura de pastas semântica (`src`, `data`, `models`, `notebooks`)
- Convenções de nomes e documentação
- O que **não** versionar (dados sensíveis, arquivos gigantes, temporários)

---

## 3️⃣ Quickstart

### 3.1 Fluxo Git mínimo

- `clone -> branch -> commit -> PR -> merge`
- Mensagens de commit claras
- Atualizar com `pull` antes de trabalhar

### 3.2 Estrutura mínima de repo (conceitual)

- `README.md`, `src/`, `data/`, `models/`, `notebooks/`, `tests/`
- `.gitignore` alinhado ao projeto

### 3.3 Versionamento de dados e modelos

- Git não é ideal para arquivos grandes
- Alternativas: **Git LFS**, **DVC**, **MLflow**
- Referenciar datasets externos e documentar versão usada

### 3.4 Boas práticas

- Padronizar branches e PRs
- Revisar também **organização** do repositório
- Registrar versão de dados e ambiente
