# Logging, Monitoramento e Observabilidade em MLOps

## README do Apresentador

Este documento organiza a apresentação da aula e serve como **guia conceitual** para o expositor.
A estrutura abaixo deve ser seguida para garantir clareza, progressão lógica e alinhamento com o grupo.

---

## 1️⃣ Motivação

### 1.1 Por que monitorar sistemas de ML?

- Modelos podem degradar silenciosamente sem gerar erros explícitos
- Dados em produção podem divergir dos dados de treinamento (data drift)
- Performance do modelo pode degradar ao longo do tempo (model drift)
- Impacto direto no negócio quando modelos falham

### 1.2 Diferenças entre software tradicional e ML

- Software tradicional: erros são explícitos (exceções, timeouts)
- ML: erros podem ser silenciosos (predições incorretas que não quebram o sistema)
- Necessidade de monitorar métricas de negócio, não apenas técnicas

### 1.3 Impacto prático

- Riscos de não monitorar modelos em produção
- Custos de downtime e degradação de qualidade
- Necessidade de observabilidade para debugging e otimização

---

## 2️⃣ Como Funciona

### 2.1 Conceitos fundamentais

- Logging: o que são logs, tipos (text, structured), níveis (DEBUG, INFO, WARNING, ERROR)
- Monitoramento: white-box (métricas internas) vs black-box (testes sintéticos)
- Observabilidade: os três pilares (logs, métricas, traces)
- Alerting: quando e como alertar, evitar alert fatigue, SLOs

### 2.2 O que monitorar em sistemas de ML

- Métricas de modelo (accuracy, precision, recall, F1)
- Métricas de negócio (conversão, receita)
- Métricas de infraestrutura (latência, throughput, utilização)
- Data drift e model drift (NÃO É PARA SE APROFUNDAR NESSES DRIFTS)
- Prediction latency, request rate, error rate
- Para LLMs: tamanho do prompt/resposta, custo por requisição, taxa de truncamento, uso de contexto (tokens em cache)

### 2.3 Desafios específicos de ML

- Como medir qualidade de predições em produção
- Detecção de drift sem labels verdadeiras
- Monitoramento de modelos em batch vs real-time
- Para LLMs: avaliar qualidade de respostas (alucinações, toxicidade, segurança), dificuldade de obter ground truth e uso de métricas proxy (ex: avaliação automática, feedback do usuário)

---

## 3️⃣ Quickstart

### 3.1 Estrutura de logging

- Structured logging (JSON)
- Contexto e rastreabilidade (request ID, user ID)
- Log aggregation
- Pode fazer um exemplo de codigo usando uma biblioteca simples de logging do python. Pode ser a ferramenta padrão `logging`, recomendo olhar o `loguru`

### 3.2 Ferramentas e exemplos

- Monitoramento geral: Prometheus, Grafana, CloudWatch, Datadog
- Específicas para ML: Evidently AI, Fiddler, Arize
- Visualização: dashboards e métricas
- LLMOps: ferramentas focadas em LLMs (Weights & Biases, LangSmith, OpenAI dashboards, observabilidade de pipelines de prompts)

### 3.3 Exemplo mínimo (conceitual ou prático)

- Instrumentação básica de um modelo de ML
- Coleta de métricas essenciais (latência, taxa de erro, distribuição de features)
- Para LLM: monitorar latência e custo por chamada, tamanho médio de prompt/response, e taxa de respostas consideradas ruins via feedback do usuário
- Dashboard simples para visualização
- Alerta básico baseado em threshold

### 3.4 Boas práticas

- Definir SLOs e SLIs
- Evitar alert fatigue
- Documentar runbooks
- Implementar troubleshooting sistemático
- Em LLMOps: definir políticas claras para uso de LLM (limites de custo, tempo de resposta, critérios de qualidade mínima) e sempre registrar contexto das chamadas (prompt, versão do modelo, parâmetros)
