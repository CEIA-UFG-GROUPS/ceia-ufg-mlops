# 🚀 Aula 10 — CI/CD Básicos em MLOps

## 📝 Visão Geral
Nesta etapa do grupo de estudos, deixamos de realizar processos manuais para adotar a automação. O objetivo é garantir que cada alteração no código do nosso sistema de Machine Learning seja testada, empacotada e esteja pronta para o deploy de forma consistente e segura.

A automação é o divisor de águas entre um projeto acadêmico isolado e um produto de IA escalável. Saímos do cenário onde o código "funciona na minha máquina" para um ambiente onde o código prova seu valor a cada *commit*.

---

## 🎯 Objetivos de Aprendizagem
* Compreender os pilares do **CI (Integração Contínua)** e **CD (Entrega Contínua)** aplicados a projetos de software que envolvem ML.
* Utilizar o conhecimento prévio de **Docker** e **Nuvem** para automatizar o ciclo de vida do código.
* Implementar um pipeline básico que execute testes unitários e realize o "build" de uma imagem.
* Diferenciar a automação de software tradicional da automação específica para fluxos de Machine Learning.

---

## 🧠 Fundamentação Teórica

### 1. O que é CI/CD no contexto de MLOps?
Nesta fase, focamos na **automação do software**:

* **CI (Continuous Integration):** Automação de testes a cada "push". Impede que erros de lógica cheguem ao ambiente compartilhado.
* **CD (Continuous Delivery):** Garante que o artefato (API ou script) esteja sempre pronto para implantação.

#### 🔎 Detalhando a Integração Contínua (CI)
O CI é o coração da cultura DevOps adaptada ao MLOps. O objetivo primordial é o **feedback rápido**. Se você introduziu um bug em uma função de pré-processamento, você deve saber disso em minutos, não semanas depois.

**Os estágios fundamentais de um CI robusto incluem:**
1.  **Linting e Estilo:** Verificação estática (ex: `flake8`, `black`). Garante que o código seja legível por qualquer membro do grupo, seguindo padrões como o PEP8.
2.  **Testes de Unidade (Unit Testing):** Validação de funções isoladas. Em ML, isso é vital para testar scripts que tratam valores nulos, normalização de strings ou conversões de tipos.
3.  **Security Scanning:** Busca por vulnerabilidades em bibliotecas de terceiros ou chaves de API expostas acidentalmente no código.
4.  **Verificação de Dependências:** Garante que o seu `requirements.txt` está consistente e que a instalação não quebrará em uma máquina nova.



#### 🔎 Detalhando a Entrega Contínua (CD)
Se o CI garante a qualidade do código, o CD garante a **confiabilidade da entrega**. Em MLOps, o CD transforma seu código testado em um "Artefato de Produção" — quase sempre uma imagem Docker.

**Diferença entre Delivery e Deployment:**
* **Continuous Delivery:** O processo gera a imagem e a coloca em um "Registry" (como Docker Hub ou AWS ECR). Ela está **pronta** para ir ao ar, mas a implantação final depende de uma aprovação humana.
* **Continuous Deployment:** O processo é 100% automático. Se o código passar em todos os testes, ele é enviado diretamente para o servidor de produção sem intervenção manual.

---

### 2. Por que usar CI/CD agora?
* **Reprodutibilidade:** O ambiente é o mesmo para todos via Docker. Evitamos o erro clássico de versões diferentes de bibliotecas alterando os resultados.
* **Segurança:** Testes automáticos validam funções de limpeza e pré-processamento de dados antes do modelo ser treinado ou servido.

#### 🛡️ O Princípio do "Shift Left"
Em MLOps, falamos muito em "trazer o teste para a esquerda". Isso significa identificar problemas o mais cedo possível. Ao automatizar o CI/CD, garantimos que falhas de infraestrutura (Docker que não builda) sejam resolvidas antes de gastarmos recursos caros de Nuvem com treinamento ou inferência.

#### 📦 Imutabilidade e Rastreabilidade
Ao usar CD, trabalhamos com **Infraestrutura Imutável**. Uma vez que a imagem Docker é gerada e testada, ela não é alterada. Se precisarmos de uma mudança, geramos uma nova imagem. Isso cria uma trilha de auditoria: sabemos exatamente qual versão do código gerou qual versão da API de predição.

---

### 3. CI/CD de Software vs. MLOps
Embora nesta aula foquemos no básico, é importante entender que MLOps adiciona camadas extras ao pipeline tradicional:

| Componente | Software Tradicional | MLOps (Aulas Futuras) |
| :--- | :--- | :--- |
| **Gatilho (Trigger)** | Alteração no Código | Alteração no Código, nos Dados ou Drift |
| **Teste** | Unitário, Integração | Unitário + Validação de Dados + Modelo |
| **Artefato** | Binário ou Jar | Imagem Docker com Modelo Serializado |
| **Métrica** | Cobertura de Código | Acurácia, F1-Score, Latência |

Em pipelines de ML, podemos definir thresholds de qualidade via código. Por exemplo, o CI pode falhar se a métrica de validação não atingir um patamar mínimo:

$$Accuracy > 0.85$$

---

### 4. Anatomia do Pipeline (GitHub Actions) Passo a Passo

Para que a automação ocorra, o GitHub Actions utiliza um arquivo de configuração no formato **YAML**. Vamos decompor o exemplo da atividade.

[Image of GitHub Actions workflow structure with Events, Jobs, and Steps]

#### 4.1. Gatilhos (Events)
```yaml
on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
```
* **`push`**: O pipeline roda ao enviar código para a `main`.
* **`pull_request`**: O pipeline roda ao solicitar a integração de código na `main`, garantindo que o novo código não "quebre" o sistema (CI).

#### 4.2. O Ambiente (Jobs)
```yaml
jobs:
  qualidade-e-build:
    runs-on: ubuntu-latest
```
* **`runs-on: ubuntu-latest`**: Define o **Runner** (máquina virtual Linux) onde os comandos serão executados.

#### 4.3. Os Passos (Steps)
**A. Checkout do Código**
```yaml
      - name: Checkout do Código
        uses: actions/checkout@v3
```
* **Função**: "Clona" seu repositório para dentro da máquina virtual.

**B. Preparar Python**
```yaml
      - name: Configurar Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
```
* **Função**: Instala a versão específica do Python para garantir **reprodutibilidade**.

**C. Instalação de Ferramentas**
```yaml
      - name: Instalar Dependências
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
```
* **Função**: Instala as bibliotecas necessárias listadas no seu `requirements.txt`.

**D. Validação de Qualidade (CI)**
```yaml
      - name: Executar Testes Unitários
        run: pytest tests/
```
* **Função**: Executa testes automatizados. Se falhar, o pipeline para imediatamente.

**E. Empacotamento (CD)**
```yaml
      - name: Build da Imagem Docker
        run: |
          docker build -t ml-app-ufg:latest .
```
* **Função**: Cria a imagem Docker, garantindo que o software testado está pronto para ser enviado para a nuvem.

---

## 🛠️ Atividade Prática

**Desafio: "O Pipeline Inquebrável"**
1.  **Crie um novo repositório no GitHub:** Dentro do repositório, cole todo o conteúdo da pasta atividade (mantenha a estrutura).
2.  **Mãos à obra:** Siga as instruções do arquivo README.md dentro da pasta atividade.

---

## 📖 Leituras Recomendadas

### 📚 Livros e Artigos Base

* **"Engenharia de Confiabilidade do Google (SRE)"**: Fundamental para entender como a automação reduz o trabalho braçal. https://sre.google/sre-book/table-of-contents/

* **Documentação Oficial do GitHub Actions**: Guia prático sobre a sintaxe YAML e o uso de segredos de ambiente. https://docs.github.com/pt/actions

* **Stack Overflow (Tag: GitHub Actions / Docker):** O melhor lugar para resolver erros específicos de configuração e permissões no Windows. https://stackoverflow.com/questions/tagged/github-actions

---

## 🔎 Glossário Técnico: Termos Essenciais de CI/CD e MLOps

Este glossário serve como guia de referência rápida para nivelar o conhecimento técnico do grupo, padronizando os termos utilizados no mercado de engenharia de machine learning.

### 🚀 Automação e Fluxo de Trabalho
* **Artifact (Artefato):** O produto final gerado por um pipeline (ex: uma imagem Docker ou um arquivo de modelo `.pkl`). É o arquivo pronto para ser utilizado no deploy.
* **CD (Continuous Delivery / Entrega Contínua):** A prática de automatizar a criação e o teste de artefatos, garantindo que o código esteja sempre em um estado pronto para ser implantado.
* **CI (Continuous Integration / Integração Contínua):** Prática de integrar alterações de código frequentemente em um repositório compartilhado, validando cada mudança com builds e testes automatizados.
* **Job (Trabalho):** Uma unidade de execução dentro de um workflow que agrupa um conjunto de passos executados em um mesmo Runner.
* **Pipeline:** A sequência lógica e automatizada de etapas (linting, testes, build, deploy) que o código percorre.
* **Runner:** O servidor ou máquina virtual (provido pelo GitHub ou autohospedado) que executa fisicamente os comandos do pipeline.
* **Step (Passo):** Uma tarefa individual dentro de um Job (ex: rodar um script Python ou clonar um repositório).
* **Workflow:** O arquivo de configuração (YAML) que define todo o processo de automação e seus gatilhos.

### 🧪 Qualidade e Monitoramento
* **Drift (Desvio):** Fenômeno onde a performance do modelo cai ao longo do tempo devido a mudanças nos dados de entrada ou no comportamento do mundo real. É um dos principais gatilhos para CI/CD em MLOps avançado.
* **Linting:** Processo de análise estática do código para encontrar erros de sintaxe, problemas de estilo ou construções perigosas sem precisar executar o código.
* **Regression (Regressão):** Um erro ou bug que aparece em uma funcionalidade que anteriormente funcionava bem, geralmente após uma nova alteração no código.
* **Threshold (Limiar):** Um valor limite definido para determinar o sucesso ou falha de uma etapa. Em MLOps, é comum usar thresholds de métricas (ex: o build falha se $Accuracy < 0.80$).
* **Unit Test (Teste Unitário):** Teste automatizado que valida a menor parte funcional de um software (uma função ou método) de forma isolada.

### 🏗️ Infraestrutura e Configuração
* **Docker:** Tecnologia de conteinerização que empacota o software e suas dependências, garantindo que o código rode da mesma forma em qualquer ambiente.
* **Environment Variables (Variáveis de Ambiente):** Variáveis externas ao código usadas para configurar comportamentos (ex: definir se o ambiente é "produção" ou "desenvolvimento").
* **Secrets:** Variáveis de ambiente sensíveis (como senhas e chaves de API) que são armazenadas de forma criptografada pelo GitHub e nunca devem ser escritas diretamente no código.
* **Shift Left (Mover para a Esquerda):** Conceito de mover as validações e testes para o início do processo de desenvolvimento, identificando erros o mais cedo possível.
* **YAML:** Linguagem de serialização de dados (utilizada no GitHub Actions) focada em ser legível por humanos para configurações de sistemas.