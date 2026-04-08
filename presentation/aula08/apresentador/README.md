# Serverless, Microsserviços & Aplicações com Agentes

## README do Apresentador

Este documento organiza a apresentação da aula e serve como **guia conceitual** para o expositor.
A estrutura abaixo deve ser seguida para garantir clareza, progressão lógica e alinhamento com o grupo.

---

## 1️⃣ Motivação

### 1.1 Por que isso importa para MLOps com Agentes?

- Agentes de IA tomam decisões e executam ações via **tools** — como essas tools são deployadas define a qualidade do sistema
- Sistemas agenticos em produção precisam de **escala, observabilidade e deploy independente por tool**
- Serverless resolve o problema operacional; microsserviços resolvem o problema arquitetural
- A combinação dos dois é o padrão emergente para aplicações de IA em produção

### 1.2 O que o grupo vai sair sabendo fazer

- Entender quando uma arquitetura de microsserviços faz sentido (vs monolito ou pipeline)
- Configurar tools em um agente Agno apontando para endpoints de microsserviços no Cloud Run
- Gerenciar secrets com segurança usando GCP Secret Manager
- Tomar decisões conscientes sobre quando usar (e não usar) essa abordagem

### 1.3 Conexão com aulas anteriores

- **Aula anterior (Docker e Deploy):** nesta aula cada microsserviço é um container Docker deployado como Cloud Run service
- Os containers que o grupo aprendeu a criar viram **serviços independentes e escaláveis**
- O banco vetorial (Qdrant) visto anteriormente pode ser exposto como um microsserviço de busca

---

## 2️⃣ Como Funciona

### 2.1 Serverless — conceito e modelos

- **Serverless ≠ sem servidores** — significa que você não os gerencia
- Escala automática (incluindo para zero), pay-per-use, stateless por natureza
- **FaaS (Function as a Service):** Cloud Functions, AWS Lambda — funções curtas e pontuais
- **CaaS (Container as a Service):** Cloud Run, AWS Fargate — containers completos com auto-scaling
- **Trade-off principal:** cold start — mitigado com `min-instances` no Cloud Run

### 2.2 Microsserviços — conceito e princípios

- Unidade pequena, independente, com **responsabilidade única**
- Deployável, escalável e falha de forma **isolada**
- Comunicação via APIs (REST, gRPC) — não por chamada de função interna
- Cada serviço pode ter sua própria linguagem, banco e runtime

### 2.3 Microsserviços vs Pipeline — a distinção mais importante da aula

| | **Pipeline** | **Microsserviços** |
|---|---|---|
| **Fluxo** | Sequencial e acoplado | Sob demanda, desacoplado |
| **Escalonamento** | Todo o pipeline junto | Serviço a serviço |
| **Falha** | Interrompe tudo | Isolada ao serviço |
| **Ideal para** | ETL, treinamento de modelos | APIs, tools de agentes |

> **Ponto importante:** Treinamento de modelos → pipeline. Servir o modelo como tool de agente → microsserviço.

### 2.4 Por que Serverless e Microsserviços se complementam

- Cada microsserviço escala **independentemente** — exatamente o que serverless oferece
- Zero overhead operacional: sem gerenciar clusters ou load balancers
- Deploy independente nativo: cada Cloud Run service é isolado
- Custo proporcional ao uso real de cada serviço

### 2.5 Agentes e Microsserviços — a combinação que fecha o ciclo

- Cada **tool do agente** pode ser um microsserviço independente
- **Observabilidade individual:** logs, métricas e traces por tool no Cloud Run
- **Escala independente:** tool de busca escala diferente de tool de geração de PDF
- **Reutilização:** o mesmo microsserviço serve múltiplos agentes
- **Isolamento de falhas:** se uma tool falha, o agente pode degradar graciosamente
- **Flexibilidade tecnológica:** cada microsserviço usa a stack ideal para sua função

### 2.6 Gerenciamento de Secrets — a parte que gera mais bugs silenciosos

**O que NUNCA fazer:**
- Hardcoded no código
- Commitado no `.env` no repositório
- Logado acidentalmente

**O modelo correto:**
```
Código/Imagem Docker → zero secrets
GCP Secret Manager  → secrets versionados e auditados
Cloud Run Service   → injeta como variável de ambiente em runtime
Container rodando   → lê de os.environ
```

**Configuração no deploy:**
```bash
gcloud run deploy meu-microsservico \
  --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest" \
  --service-account=sa-meu-servico@projeto.iam.gserviceaccount.com
```

**Princípio do menor privilégio:** cada microsserviço acessa **apenas** os secrets que precisa.

---

## 3️⃣ Quickstart

### 3.1 Prática: Agente Agno com tools via Cloud Run

**Objetivo:** Subir dois microsserviços simples no Cloud Run e configurar um agente Agno para usá-los como tools.

**Repositórios e referências de apoio:**
- [Agno — Custom Tools](https://docs.agno.com/tools/custom-tools) — criando tools personalizadas no Agno
- [Google Cloud Run Quickstart](https://cloud.google.com/run/docs/quickstarts/build-and-deploy/deploy-python-service) — deploy de serviço Python no Cloud Run
- [Cloud Run — Configuring Secrets](https://cloud.google.com/run/docs/configuring/secrets) — injeção de secrets

### 3.2 Arquitetura da prática

```
┌──────────────────────────────────────────┐
│         Agente Agno (local ou Cloud Run) │
│  tools:                                  │
│    - buscar_documentos → Cloud Run       │
│    - analisar_sentimento → Cloud Run     │
│    - buscar_na_web (tool nativa Agno)    │
└──────────────┬───────────────────────────┘
               │
       ┌───────┴────────┐
       ▼                ▼
┌─────────────┐  ┌──────────────┐
│ Cloud Run   │  │  Cloud Run   │
│  busca-svc  │  │ sentimento-  │
│             │  │     svc      │
│ POST /search│  │ POST /analyze│
└─────────────┘  └──────────────┘
```

### 3.3 Objetivos da Prática

**Fase 1: Executar e Entender**
- Explorar a estrutura de um microsserviço simples com FastAPI
- Fazer deploy de um serviço no Cloud Run via `gcloud run deploy`
- Testar o endpoint com `curl` ou httpx
- Entender o fluxo de autenticação via service account

**Fase 2: Experimentar e Modificar**
- Conectar o serviço como tool em um agente Agno
- Verificar logs separados por serviço no Cloud Logging
- Simular uma falha em um serviço e observar o comportamento do agente
- Adicionar um secret via Secret Manager e injetar no serviço

**Fase 3: Reflexão Arquitetural**
- Quando faria sentido extrair mais tools para microsserviços?
- Como versionar uma tool sem quebrar o agente?
- Quais métricas você monitoraria por microsserviço em produção?
- Como estruturaria o CI/CD para múltiplos microsserviços?

### 3.4 Exemplo de microsserviço mínimo (FastAPI para Cloud Run)

```python
# main.py — microsserviço de análise de sentimento
from fastapi import FastAPI
from pydantic import BaseModel
import os

app = FastAPI()

class AnalisarRequest(BaseModel):
    texto: str

@app.post("/analyze")
def analisar_sentimento(req: AnalisarRequest) -> dict:
    # lógica real aqui
    return {"sentimento": "positivo", "confianca": 0.92}

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

```dockerfile
# Dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```bash
# Deploy no Cloud Run
gcloud run deploy sentimento-svc \
  --source . \
  --region us-central1 \
  --allow-unauthenticated  # para fins de estudo; em produção use IAM
```

### 3.5 Configurando a tool no agente Agno

```python
import httpx
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools import tool

SENTIMENTO_SVC_URL = "https://sentimento-svc-xxxxx-uc.a.run.app"

@tool(description="Analisa o sentimento de um texto (positivo, negativo, neutro)")
def analisar_sentimento(texto: str) -> dict:
    response = httpx.post(
        f"{SENTIMENTO_SVC_URL}/analyze",
        json={"texto": texto},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()

agente = Agent(
    model=Gemini(id="gemini-2.0-flash"),
    tools=[analisar_sentimento],
    instructions="Você analisa feedbacks de clientes e identifica tendências.",
)

agente.print_response("Analise este feedback: 'O produto chegou rápido mas veio danificado'")
```

### 3.6 Conexão com MLOps

Esta prática demonstra:
- **Deployment:** deploy independente de cada componente do sistema de IA
- **Observabilidade:** logs e métricas isolados por serviço no Cloud Logging
- **Escalabilidade:** cada tool escala de acordo com sua própria demanda
- **Segurança:** secrets gerenciados centralizadamente, nunca no código
- **Manutenibilidade:** atualizar uma tool sem redeploy do agente

---

## 4️⃣ Quando Usar (e Quando NÃO Usar)

### Usar ✅
- Tools com dependências pesadas (ML models, GPU) que tornariam o container do agente enorme
- Tools reutilizadas por múltiplos agentes ou equipes
- Produção com requisitos de SLA e escala independente
- Times diferentes responsáveis por cada tool

### Não usar ❌
- Prototipagem / POC — use tools locais, extraia depois se necessário
- Tools simples sem reuso (over-engineering)
- Latência crítica < 50ms (microsserviços adicionam overhead de rede)
- Time pequeno sem maturidade operacional para gerenciar múltiplos deploys

> **Regra prática:** Comece com tools locais no agente. Extraia para microsserviço quando a complexidade justificar.
