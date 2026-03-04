# Machine Learning (do Clássico às Redes Neurais) e CRISP-DM

## README do Apresentador

Este documento organiza a apresentação da aula e serve como **guia conceitual** para o expositor.
A estrutura abaixo deve ser seguida para garantir clareza, progressão lógica e alinhamento com o grupo.

---

## 1️⃣ Motivação

### 1.1 Por que entender ML clássico antes de deep learning?

- Evolução histórica dos algoritmos de Machine Learning
- Quando usar algoritmos clássicos vs redes neurais
- Trade-offs entre simplicidade e complexidade
- Algoritmos clássicos ainda são amplamente usados em produção
- Base sólida facilita compreensão de deep learning

### 1.2 A importância de metodologias estruturadas

- Por que CRISP-DM é relevante para projetos de ML
- Benefícios de seguir um processo estruturado
- Redução de erros e retrabalho
- Melhor comunicação entre equipes
- Reprodutibilidade e rastreabilidade

### 1.3 Impacto prático

- Aplicações reais de ML clássico e redes neurais
- Casos de uso apropriados para cada abordagem
- Quando começar simples e quando escalar para deep learning
- Relação com MLOps: entender o modelo é essencial para operacionalização

---

## 2️⃣ Como Funciona

### 2.1 CRISP-DM: Metodologia estruturada

- As 6 fases: Business Understanding, Data Understanding, Data Preparation, Modeling, Evaluation, Deployment
- Iteratividade e flexibilidade do processo
- CRISP-DM como base para metodologias modernas de MLOps
- Adaptação para contextos ágeis e produção

### 2.2 Machine Learning Clássico

- Algoritmos supervisionados: Regressão Linear, Árvores de Decisão, SVM, KNN
- Algoritmos não-supervisionados: K-Means, PCA
- Quando usar cada tipo de algoritmo
- Vantagens: interpretabilidade, menor necessidade de dados, treinamento rápido

### 2.3 Redes Neurais

- Conceitos fundamentais: neurônios, camadas, funções de ativação
- Perceptron e MLP (Multi-Layer Perceptron)
- Introdução a deep learning
- Quando redes neurais são apropriadas

### 2.4 Escolhendo a abordagem certa

- Critérios para escolher entre ML clássico e redes neurais
- Trade-offs: interpretabilidade, dados necessários, complexidade, custo computacional
- Começar simples e escalar quando necessário
- Importância para MLOps: escolhas impactam deploy e monitoramento

---

## 3️⃣ Quickstart

### 3.1 Prática: Análise de Sentimento com PyTorch

**Repositório de referência:** [bentrevett/pytorch-sentiment-analysis](https://github.com/bentrevett/pytorch-sentiment-analysis)

Este repositório contém tutoriais completos sobre classificação de sequências usando PyTorch, focando em análise de sentimento de reviews de filmes.

**Tutoriais disponíveis:**
1. Neural Bag of Words - Modelo básico para classificação de sequências
2. Recurrent Neural Networks (RNN/LSTM) - Redes neurais recorrentes
3. Convolutional Neural Networks (CNN) - CNNs para processamento de texto
4. Transformers - Uso de modelos pré-treinados (BERT)

### 3.2 Objetivos da Prática

**Fase 1: Executar e Entender**
- Clonar o repositório e instalar dependências
- Executar os notebooks em ordem (1 a 4)
- Entender a evolução: do modelo simples ao Transformer(ou um pouco antes)
- Compreender cada componente do código (data loading, model architecture, training loop, evaluation)

**Fase 2: Experimentar e Modificar**
- Alterar hiperparâmetros (learning rate, batch size, número de épocas)
- Modificar arquiteturas (adicionar/remover camadas, mudar funções de ativação)
- Testar diferentes otimizadores
- Comparar resultados entre diferentes abordagens
- Aplicar CRISP-DM: documentar cada experimento seguindo as fases

**Fase 3: Deploy Simples (API)**
- Salvar o modelo treinado
- Criar uma API REST simples (Flask ou FastAPI)
- Endpoint para receber texto e retornar sentimento
- Testar a API localmente
- Considerações para produção (versionamento, logging, monitoramento básico)

### 3.3 Estrutura da Prática

**Setup inicial:**
- Instalar dependências: `pip install -r requirements.txt`
- Verificar ambiente (Python 3.9+, PyTorch, torchtext)
- Executar primeiro notebook para validar setup

**Desenvolvimento:**
- Seguir tutoriais sequencialmente
- Para cada notebook: executar, entender, modificar, experimentar
- Documentar mudanças e resultados
- Aplicar conceitos de CRISP-DM em cada etapa

**Deploy:**
- Escolher um modelo treinado (recomendado: começar com o mais simples)
- Criar script de inferência
- Implementar API REST básica
- Testar com exemplos reais
- Discussão sobre melhorias para produção

### 3.4 Conexão com MLOps

Esta prática demonstra:
- **Modeling**: Treinar diferentes arquiteturas de redes neurais
- **Evaluation**: Comparar performance de modelos
- **Deployment**: Colocar modelo em produção via API
- **Iteração**: Experimentar e melhorar modelos
- **Preparação**: Base para aulas futuras sobre pipelines, versionamento e monitoramento

**Próximos passos (aulas futuras):**
- Versionamento de modelos
- Pipelines automatizados de treinamento
- Monitoramento de modelos em produção
- Retreino automatizado

