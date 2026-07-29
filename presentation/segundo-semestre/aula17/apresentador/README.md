# Pipelines de Treinamento (Airflow/Prefect) — Guia do Apresentador

Este documento organiza a apresentação da aula e serve como **guia conceitual** para o expositor.
A estrutura abaixo é uma sugestão para garantir clareza, progressão lógica e alinhamento com o grupo.

> 💡 **Fluxo sugerido**: começar do script `train.py` monolítico rodado manualmente no notebook do cientista de dados, mostrar por que isso não escala nem é confiável ("o script quebrou às 3h da manhã e ninguém percebeu"), e evoluir até um **DAG orquestrado**, versionado, agendado e observável. A aula é sobre **orquestração, confiabilidade e reprodutibilidade de pipelines**, não sobre decorar sintaxe de uma ferramenta específica.

---

## 1️⃣ Motivação

### 1.1 Por que isso importa para MLOps?

- **O anti-pattern do script solitário**: `python train.py` rodado manualmente por uma pessoa, no seu próprio notebook, sem agendamento, sem retry e sem histórico de execuções.
- **O problema de dependências implícitas**: um pipeline de ML não é uma única etapa — é uma cadeia (`extrair dados → validar → preparar features → treinar → avaliar → registrar`). Rodar essas etapas "na mão" e fora de ordem é fonte constante de bugs silenciosos.
- **Falhas parciais são a norma, não a exceção**: a API de dados cai no meio da extração, o job de treino estoura memória, o container é encerrado pelo Kubernetes. Um pipeline de produção precisa **sobreviver** a isso (retry, alertas, idempotência).
- **Continuous Training (CT) exige automação**: para retreinar modelos periodicamente (diário, semanal) sem intervenção manual, é preciso um motor de agendamento e execução confiável — não um cron job cru.

### 1.2 O que o grupo vai sair sabendo fazer

- Modelar um pipeline de ML como um **DAG (Directed Acyclic Graph)**: tarefas, dependências e ordem de execução.
- Diferenciar **orquestração** (Airflow/Prefect/Dagster) de **execução** (o código que efetivamente treina o modelo).
- Entender os conceitos de **idempotência, retries, backfill e agendamento (scheduling)**.
- Comparar Airflow (clássico, baseado em operators) com Prefect (Pythonic, dinâmico) e saber quando cada um faz mais sentido.
- Conectar o pipeline de treinamento ao **Model Registry** (Aula 19) e ao **CI/CD** (Aula 10).

### 1.3 Conexão com aulas anteriores

- **Aula 10 (CI/CD Básicos)**: CI/CD automatiza a entrega de *código*; pipelines de treinamento automatizam a entrega de *modelos*. Um workflow do Airflow/Prefect é frequentemente disparado **a partir de** um pipeline de CI/CD.
- **Aula 19 (Model Registry)**: a última tarefa de um DAG de treinamento tipicamente registra o modelo candidato no Registry, fechando o ciclo de Continuous Training (CT).

---

## 2️⃣ Como Funciona

### 2.1 Pipeline como DAG

- Um pipeline de treinamento é modelado como um **grafo acíclico dirigido**: cada nó é uma tarefa (task), cada aresta é uma dependência.
- Exemplo típico: `ingestão_dados → validação_schema → feature_engineering → split_treino_teste → treino → avaliação → registro_no_model_registry`.
- **Por que acíclico?** Porque uma tarefa não pode depender (direta ou indiretamente) de si mesma — isso garante uma ordem de execução bem definida.

```text
┌──────────┐   ┌───────────┐   ┌──────────────┐   ┌────────┐   ┌───────────┐   ┌───────────┐
│ Ingestão │──►│ Validação │──►│   Feature    │──►│ Treino │──►│ Avaliação │──►│ Registro  │
│  Dados   │   │  Schema   │   │ Engineering  │   │        │   │  Métricas │   │  Modelo   │
└──────────┘   └───────────┘   └──────────────┘   └────────┘   └───────────┘   └───────────┘
```

### 2.2 Airflow — O Padrão Clássico da Indústria

- **Conceitos-chave**: `DAG` (o pipeline), `Operator` (o tipo de tarefa: `PythonOperator`, `BashOperator`, `KubernetesPodOperator`), `Task Instance` (uma execução específica de uma tarefa), `Scheduler` (decide quando rodar).
- **Definição estática**: o DAG é declarado em Python, mas sua estrutura (quais tarefas existem e como se conectam) é fixa em tempo de definição — o "código" descreve o grafo, não o executa diretamente.
- **Ecossistema maduro**: UI rica para visualizar execuções, retries automáticos configuráveis por tarefa, `Sensors` para esperar por eventos externos (ex.: arquivo chegou no S3), suporte a `XCom` para passar pequenos dados entre tarefas.
- **Executor**: `LocalExecutor` (single machine), `CeleryExecutor` (distribuído com fila de mensagens), `KubernetesExecutor` (cada tarefa vira um Pod efêmero — o mais comum em MLOps moderno).

### 2.3 Prefect — A Abordagem Pythonic e Dinâmica

- **Diferença filosófica**: em vez de declarar o grafo de forma estática, o Prefect permite escrever pipelines como **funções Python normais** decoradas com `@flow` e `@task`. O grafo é inferido dinamicamente a partir da execução do código.
- **Vantagens práticas**: menos boilerplate, mais fácil de testar localmente (é só uma função Python), suporte nativo a lógica condicional e loops dentro do fluxo sem *hacks*.
- **Prefect Cloud/Server**: interface de observabilidade e agendamento, similar em espírito à UI do Airflow, mas com um modelo de execução mais leve (`Work Pools` e `Workers`).

### 2.4 Airflow vs. Prefect — Matriz de Comparação

| Critério | Airflow | Prefect |
|---|---|---|
| **Modelo de definição** | DAG estático, declarativo | Flow dinâmico, imperativo (código Python puro) |
| **Curva de aprendizado** | Mais íngreme (Operators, Executors, conceitos próprios) | Mais suave para quem já sabe Python |
| **Maturidade / Comunidade** | Extremamente madura, padrão de facto em muitas empresas | Mais recente, crescendo rápido, forte em times Python-first |
| **Observabilidade nativa** | UI robusta, logs por tarefa, Gantt chart de execução | UI moderna, ótimo para debugging local antes de produção |
| **Melhor uso** | Pipelines de dados complexos e heterogêneos em larga escala (Data Engineering) | Times de Data Science que querem produtizar notebooks/scripts rapidamente |

### 2.5 Conceitos Essenciais de Confiabilidade

- **Idempotência**: rodar a mesma tarefa duas vezes com a mesma entrada deve produzir o mesmo resultado, sem efeitos colaterais duplicados (ex.: não duplicar linhas em uma tabela).
- **Retries e Backoff**: uma tarefa que falha por instabilidade transitória (rede, timeout) deve ser reexecutada automaticamente, com espera crescente entre tentativas.
- **Backfill**: capacidade de rodar o pipeline retroativamente para datas passadas (ex.: reprocessar os últimos 30 dias após corrigir um bug).
- **Alertas**: notificação automática (Slack, e-mail, PagerDuty) quando uma tarefa crítica falha após esgotar os retries.

---

## 3️⃣ Quickstart & Demos

> 💡 **Instruções para ao vivo**: as demos podem ser executadas com `pip install apache-airflow` (modo standalone) ou `pip install prefect` — ambos funcionam localmente sem infraestrutura de nuvem.

### 3.1 Demo 1 — Um DAG mínimo no Airflow

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def extrair_dados():
    print("Extraindo dados de treino...")

def treinar_modelo():
    print("Treinando modelo...")

def registrar_modelo():
    print("Registrando modelo no Model Registry...")

with DAG(
    dag_id="pipeline_treinamento_fraude",
    start_date=datetime(2026, 1, 1),
    schedule="@daily",
    catchup=False,
) as dag:
    t1 = PythonOperator(task_id="extrair_dados", python_callable=extrair_dados)
    t2 = PythonOperator(task_id="treinar_modelo", python_callable=treinar_modelo)
    t3 = PythonOperator(task_id="registrar_modelo", python_callable=registrar_modelo)

    t1 >> t2 >> t3  # define a ordem de execução (dependências)
```

### 3.2 Demo 2 — O mesmo pipeline no Prefect

```python
from prefect import flow, task

@task(retries=3, retry_delay_seconds=10)
def extrair_dados():
    print("Extraindo dados de treino...")

@task
def treinar_modelo():
    print("Treinando modelo...")

@task
def registrar_modelo():
    print("Registrando modelo no Model Registry...")

@flow(name="pipeline-treinamento-fraude")
def pipeline_treinamento():
    extrair_dados()
    treinar_modelo()
    registrar_modelo()

if __name__ == "__main__":
    pipeline_treinamento()
```

### 3.3 Demo 3 — Discussão ao vivo: onde este pipeline se conecta?

- Mostrar como a última tarefa (`registrar_modelo`) chamaria `mlflow.sklearn.log_model(...)` (Aula 19).
- Mostrar como um Webhook do GitHub (push na branch `main`) poderia disparar este DAG via API do Airflow/Prefect (conexão com Aula 10 — CI/CD).

---

## 4️⃣ Quando Usar (e Quando NÃO Usar)

### Usar ✅
- Pipelines com múltiplas etapas dependentes que precisam rodar de forma agendada e confiável.
- Continuous Training: retreinar modelos periodicamente sem intervenção manual.
- Quando falhas parciais precisam de retry automático e alertas.

### Não usar ❌
- Prototipagem exploratória em notebook, ainda sem etapas bem definidas.
- Um único script simples que roda uma vez e não será reagendado.
- Quando a equipe não tem ainda infraestrutura para manter o orquestrador rodando (considerar alternativas gerenciadas, como Astronomer para Airflow ou Prefect Cloud).

> **Regra prática:** se o pipeline precisa rodar **mais de uma vez**, com **dependências entre etapas** e **tolerância a falhas**, ele precisa de um orquestrador — não de um cron job.
