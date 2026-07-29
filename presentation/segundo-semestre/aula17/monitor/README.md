# 📘 Aula 17 — Pipelines de Treinamento (Airflow/Prefect)

## Material de Estudo Prévio

Este material tem como objetivo **preparar para a aula de Pipelines de Treinamento**, oferecendo uma base conceitual sólida para acompanhar, complementar e aprofundar a discussão conduzida pelo apresentador.

⚠️ **Este conteúdo não é um guia de instruções**, mas sim um **material de estudo prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do CEIA/UFG.

---

## 🎯 Objetivo da Aula

Ao final desta aula, espera-se que os participantes compreendam:

- Por que scripts de treinamento rodados manualmente não escalam para times e produção
- O que é um **DAG (Directed Acyclic Graph)** e como ele modela dependências entre etapas de um pipeline de ML
- Os conceitos de **idempotência, retries, backfill e agendamento (scheduling)**
- As diferenças arquiteturais entre **Apache Airflow** (declarativo, baseado em Operators) e **Prefect** (Pythonic, dinâmico)
- Como um pipeline de treinamento se conecta ao **Model Registry** e ao **CI/CD**, fechando o ciclo de **Continuous Training (CT)**
- Boas práticas de observabilidade, alertas e recuperação de falhas em pipelines de produção

---

## 🧠 Contexto: Por que precisamos de orquestração de pipelines?

### O Anti-Pattern do Script Solitário

Em times de Data Science que ainda não amadureceram suas práticas de engenharia, é comum que o treinamento de modelos siga um fluxo artesanal:

```text
1. Cientista de dados abre um notebook local
2. Executa manualmente: carregar dados -> limpar -> treinar -> avaliar
3. Se der certo, salva o modelo em uma pasta
4. Repete o processo "à mão" na próxima vez que for necessário retreinar
```

Esse fluxo funciona em exploração inicial, mas quebra rapidamente à medida que o sistema amadurece:

1. **Sem agendamento confiável**: retreinar "quando alguém lembrar" não é uma estratégia de Continuous Training.
2. **Sem tolerância a falhas**: se a extração de dados falhar no meio do processo (API fora do ar, timeout de rede), não há retry automático — alguém precisa notar e rodar tudo de novo manualmente.
3. **Sem rastreabilidade de execução**: não há histórico de quando cada etapa rodou, quanto tempo levou, ou qual foi o erro exato de uma falha específica.
4. **Sem paralelismo controlado**: etapas independentes (ex.: gerar duas features diferentes) não são executadas em paralelo, desperdiçando tempo.

### Pipeline como DAG: A Ideia Central

Um pipeline de treinamento de ML raramente é uma única etapa — é uma cadeia de tarefas dependentes:

```text
Ingestão de Dados
      │
      ▼
Validação de Schema/Qualidade
      │
      ▼
Feature Engineering
      │
      ▼
Split Treino/Validação/Teste
      │
      ▼
Treinamento do Modelo
      │
      ▼
Avaliação de Métricas
      │
      ▼
Registro no Model Registry (Aula 19)
```

Modelar isso como um **DAG (Directed Acyclic Graph — Grafo Acíclico Dirigido)** permite que o orquestrador saiba exatamente:

- Quais tarefas podem rodar em paralelo (sem dependência entre si).
- Quais tarefas precisam esperar outras terminarem antes de iniciar.
- O que fazer quando uma tarefa específica falha (retry, pular, alertar, abortar o pipeline inteiro).

> **A Definição de Orquestrador de Pipelines:** um sistema que agenda, executa, monitora e recupera automaticamente a execução de um grafo de tarefas dependentes, garantindo que o pipeline rode de forma confiável mesmo diante de falhas parciais de infraestrutura ou dados.

---

## ⚙️ Pilares de um Pipeline de Treinamento Confiável

### 1. Agendamento (Scheduling)

- **Cron-like scheduling**: `@daily`, `@hourly`, ou expressões cron (`0 3 * * *` = todo dia às 3h da manhã).
- **Event-driven scheduling**: o pipeline dispara quando um evento acontece (ex.: novo arquivo chegou no bucket S3, um Webhook do Model Registry ou do CI/CD foi recebido) em vez de um horário fixo.

### 2. Idempotência

- Rodar a mesma tarefa duas vezes, com a mesma entrada, deve produzir o mesmo resultado — sem duplicar dados, sobrescrever incorretamente ou gerar efeitos colaterais inesperados.
- Exemplo prático: uma tarefa que insere linhas em uma tabela deve usar `upsert` (inserir ou atualizar) em vez de `insert` puro, para que reexecuções não dupliquem registros.

### 3. Retries, Backoff e Tolerância a Falhas

- Falhas transitórias (timeout de rede, API externa temporariamente fora do ar, container reiniciado pelo Kubernetes) são a **norma**, não a exceção, em ambientes distribuídos.
- Um orquestrador de produção reexecuta automaticamente a tarefa falha um número configurável de vezes, com espera crescente entre tentativas (*exponential backoff*), antes de escalar para um alerta humano.

### 4. Backfill e Reprocessamento Histórico

- Capacidade de rodar o pipeline retroativamente para um intervalo de datas passadas — essencial quando um bug é corrigido e é preciso reprocessar os últimos N dias de dados/modelos.

### 5. Observabilidade de Execução

- Histórico completo de execuções (Gantt chart de tarefas, tempo de duração, logs por tarefa).
- Alertas automáticos (Slack, e-mail, PagerDuty) quando uma tarefa crítica falha após esgotar os retries.

---

## 🛠️ Ecossistema de Ferramentas

### 1. Apache Airflow (Padrão da Indústria)

- **Componentes centrais**: `DAG` (definição do pipeline em Python), `Operator` (tipo de tarefa — `PythonOperator`, `BashOperator`, `KubernetesPodOperator`), `Scheduler` (decide quando disparar cada execução), `Webserver` (UI de monitoramento).
- **Modelo de definição estático**: o grafo de tarefas é definido de forma declarativa; o código Python descreve a estrutura do DAG, mas a "forma" do grafo não muda durante a execução.
- **Executors**: `LocalExecutor` (execução em uma única máquina), `CeleryExecutor` (execução distribuída via fila de mensagens), `KubernetesExecutor` (cada tarefa roda em um Pod efêmero — comum em ambientes cloud-native de MLOps).
- **Recursos avançados**: `Sensors` (esperam por uma condição externa, como a chegada de um arquivo), `XCom` (troca de pequenos dados entre tarefas), `Task Groups` (organização visual de tarefas relacionadas na UI).

### 2. Prefect (Abordagem Pythonic e Dinâmica)

- **Filosofia diferente**: pipelines são escritos como funções Python comuns, decoradas com `@flow` (o pipeline) e `@task` (cada etapa). O grafo de dependências é inferido dinamicamente a partir da execução do código, em vez de ser declarado estaticamente.
- **Vantagens práticas**: menos boilerplate para casos simples, mais fácil de testar localmente (uma `@flow` é só uma função Python que pode ser chamada diretamente em um teste unitário), suporte nativo a lógica condicional e loops dentro do fluxo.
- **Prefect Cloud/Server**: interface de observabilidade e agendamento, com o conceito de `Work Pools` e `Workers` para execução distribuída.

### 3. Outras Ferramentas do Ecossistema

- **Dagster**: foco forte em *assets* (o dado/modelo produzido) em vez de apenas tarefas, com ênfase em contratos de dados e testabilidade.
- **Kubeflow Pipelines**: orquestração nativa para Kubernetes, com foco específico em workflows de Machine Learning (treino, tuning de hiperparâmetros, serving).
- **Metaflow (Netflix)**: abstração de alto nível voltada para cientistas de dados, com forte integração a notebooks e versionamento automático de execuções.

### Matriz Comparativa

| Característica | Apache Airflow | Prefect | Kubeflow Pipelines |
|---|---|---|---|
| **Modelo de definição** | DAG estático declarativo | Flow dinâmico (Python puro) | DAG estático (YAML/SDK) |
| **Curva de aprendizado** | Mais íngreme | Mais suave para quem já sabe Python | Exige familiaridade com Kubernetes |
| **Foco principal** | Orquestração geral de dados | Produtização rápida de código Python | Pipelines de ML nativos em Kubernetes |
| **Maturidade** | Muito madura, padrão de mercado | Crescendo rapidamente | Madura em ambientes Kubernetes |

---

## 🌐 Conexão com o Ciclo de Continuous Training (CT)

```text
 ┌─────────────────┐   (1. Webhook/agendamento dispara o DAG)   ┌─────────────────┐
 │   CI/CD Pipeline │────────────────────────────────────────────►│  Orquestrador   │
 │   (Aula 10)      │                                             │ (Airflow/Prefect)│
 └─────────────────┘                                              └────────┬────────┘
                                                                            │ (2. Executa o DAG)
                                                                            ▼
                                                              ┌───────────────────────────┐
                                                              │ Ingestão → Validação →     │
                                                              │ Features → Treino → Avaliação│
                                                              └─────────────┬─────────────┘
                                                                            │ (3. Registra o modelo)
                                                                            ▼
                                                                  ┌─────────────────┐
                                                                  │ Model Registry  │
                                                                  │   (Aula 19)     │
                                                                  └─────────────────┘
```

1. **Gatilho**: um push no Git, uma chegada de novos dados, ou um agendamento periódico dispara o DAG.
2. **Execução orquestrada**: o Airflow/Prefect executa as tarefas na ordem correta, com retries e monitoramento.
3. **Registro do candidato**: a última tarefa registra o modelo treinado no Model Registry, com estado de candidato.
4. **Quality Gates**: um pipeline de CI/CD (Aula 10) valida o candidato antes de promovê-lo a `@champion`.

---

## 📊 Casos de Uso Práticos

### Caso 1: Retreino Diário de Modelo de Recomendação

- **Cenário**: um e-commerce precisa retreinar seu modelo de recomendação todas as noites com os dados de interação do dia.
- **Arquitetura**: Airflow com `KubernetesExecutor`, agendado via `@daily`, cada tarefa rodando em um Pod isolado.
- **Workflow**: ingestão de logs de clique → validação → geração de features → treino → avaliação → registro com alias `@challenger` (Aula 19).

### Caso 2: Pipeline Event-Driven de Detecção de Fraude

- **Cenário**: um novo lote de transações rotuladas chega ao Data Lake a cada hora; o pipeline deve reagir automaticamente, sem agendamento fixo.
- **Arquitetura**: Prefect com `Work Pool` conectado a um `Sensor`/evento do Data Lake.
- **Workflow**: o `flow` é disparado pelo evento de chegada de dados, processa o novo lote e atualiza o modelo incrementalmente.

---

## 🧪 Atividade Prática (Visão Geral)

Para consolidar os conceitos desta aula, a atividade prática guia os alunos na implementação de um pipeline simples:

1. **Modelagem do DAG**: desenhar as etapas de um pipeline de treinamento simples (ingestão, treino, avaliação, registro) como um grafo de dependências.
2. **Implementação em Airflow**: criar um DAG mínimo com `PythonOperator`s executando localmente.
3. **Implementação equivalente em Prefect**: reescrever o mesmo pipeline usando `@flow`/`@task`, comparando a experiência de desenvolvimento.
4. **Simulação de Falha**: introduzir uma falha proposital em uma tarefa e observar o comportamento de retry configurado.

---

## 💬 Pontos para Reflexão Pré-Aula

Ao estudar este material, reflita sobre as seguintes questões para enriquecer a discussão em sala:

1. **Por que um script de treinamento rodado manualmente no notebook não é suficiente para um sistema de ML em produção?**
2. **O que significa idempotência em uma tarefa de pipeline, e por que ela é essencial para permitir retries seguros?**
3. **Qual a diferença fundamental entre o modelo de definição estático do Airflow e o modelo dinâmico do Prefect?**
4. **Como um pipeline de treinamento orquestrado se conecta ao Model Registry (Aula 19) para fechar o ciclo de Continuous Training?**
5. **Em que cenário faria mais sentido usar agendamento por horário (cron) em vez de agendamento orientado a eventos?**
6. **Quais os riscos de não ter retries e alertas configurados em um pipeline que roda em produção todas as noites?**

---

## 📚 Referências

### Documentação Oficial

1. **Apache Airflow Documentation** — [https://airflow.apache.org/docs/](https://airflow.apache.org/docs/)
2. **Prefect Documentation** — [https://docs.prefect.io/](https://docs.prefect.io/)
3. **Kubeflow Pipelines Documentation** — [https://www.kubeflow.org/docs/components/pipelines/](https://www.kubeflow.org/docs/components/pipelines/)

### Artigos e Publicações

4. **Sculley, D. et al. (2015).** *Hidden Technical Debt in Machine Learning Systems*. NeurIPS 2015. — [https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems.pdf](https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems.pdf)
5. **Kreuzberger, D. et al. (2023).** *Machine Learning Operations (MLOps): Overview, Definition, and Architecture*. IEEE Access. — [https://arxiv.org/abs/2205.02302](https://arxiv.org/abs/2205.02302)

### Livros e Guias da Indústria

6. **Huyen, Chip (2022).** *Designing Machine Learning Systems*. O'Reilly Media. (Capítulos sobre pipelines de treinamento e Continuous Training).
7. **Google Cloud MLOps Architecture Guide** — [https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

---

## 🔗 Conexões com Outras Aulas

Este conteúdo conecta-se diretamente com o ecossistema do curso de MLOps:

- **Aula 10 (CI/CD Básicos)**: pipelines de orquestração de treinamento são frequentemente disparados por, ou disparam, pipelines de CI/CD.
- **Aula 11 (Logging, Monitoramento e Observabilidade)**: a execução dos DAGs precisa ser monitorada da mesma forma que serviços de inferência, com logs e alertas.
- **Aula 19 (Model Registry)**: a etapa final de um pipeline de treinamento registra o modelo candidato, fechando o ciclo de Continuous Training.
- **Aula 22 (Estratégias de Deploy)**: uma vez que o modelo é registrado, as estratégias de deploy definem como ele chega até a produção com segurança.

---

🚀 **Estudo prévio concluído? Prepare suas dúvidas sobre DAGs, idempotência, retries e Continuous Training para debatermos durante nosso encontro!**
