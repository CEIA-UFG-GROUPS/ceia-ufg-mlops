# 📘 Aula 08 — Serverless com Containers e Funções & Microsserviços e Aplicações com Agentes
## Material de Estudo Prévio (Monitor)

Este material tem como objetivo **preparar o monitor para a aula sobre Serverless e Microsserviços aplicados a sistemas de agentes de IA**, oferecendo base conceitual sólida para acompanhar, complementar e aprofundar a discussão conduzida pelo apresentador.

⚠️ **Este conteúdo não é um guia de instruções para o monitor**, mas sim um **material de estudo prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do CEIA/UFG.

Recomenda-se fortemente a leitura dos links de referência ao final do documento, especialmente a documentação do **Google Cloud Run** e do framework **Agno**.

---

## 🎯 Objetivo da Aula

Ao final desta aula, espera-se que os participantes compreendam:

- O que é serverless e por que ele importa em sistemas de IA
- A diferença entre microsserviços e arquiteturas de pipeline
- Por que microsserviços e serverless se complementam naturalmente
- Como aplicações agênticas se beneficiam de microsserviços como *tools*
- Melhores práticas de gerenciamento de secrets em microsserviços
- Exemplos concretos de arquiteturas de agentes usando microsserviços no GCP
- Quando **usar** e quando **não usar** essa abordagem

---

## ☁️ Conceito de Serverless

### O que é Serverless?

**Serverless** não significa "sem servidores" — significa que **você não gerencia servidores**. A infraestrutura é completamente abstraída pelo provedor de nuvem.

**Características fundamentais:**
- **Escala automática**: de zero a milhares de instâncias conforme a demanda
- **Pay-per-use**: você paga pelo tempo de execução real, não por instâncias ociosas
- **Stateless por natureza**: cada invocação é independente
- **Zero gerenciamento de infraestrutura**: sem patching, sem configuração de SO
- **Alta disponibilidade**: gerenciada pelo provedor

### Dois modelos principais de Serverless

| Modelo | O que é | Exemplos | Quando usar |
|--------|---------|---------|-------------|
| **FaaS** (Function as a Service) | Funções individuais, sem estado, com tempo de vida curto | Cloud Functions, AWS Lambda, Azure Functions | Triggers pontuais, transformações, webhooks |
| **CaaS** (Container as a Service) | Containers completos com auto-scaling até zero | Cloud Run, AWS Fargate, Azure Container Apps | APIs REST, microsserviços, workloads com dependências complexas |

### Cold Start — o principal trade-off

**Cold start** é o tempo que leva para uma instância serverless ser inicializada quando não há instâncias ativas.

```
Requisição → Nenhuma instância ativa → [Cold Start] → Inicializa container → Processa → Responde
                                         ↑
                                     Pode levar de 200ms a 3s
```

**Fatores que aumentam o cold start:**
- Imagens Docker grandes
- Imports pesados no Python (ex.: `torch`, `tensorflow`)
- Muitas dependências

**Como mitigar:**
- Manter imagens leves (multi-stage builds)
- Usar `min-instances` no Cloud Run para manter pelo menos 1 instância quente
- Lazy loading de modelos pesados

> **Ponto de atenção para agentes:** Se um microsserviço-tool for chamado por um agente com latência crítica, cold starts podem ser problemáticos. Configurar `min-instances: 1` resolve na maioria dos casos.

---

## 🧩 Conceito de Microsserviço

### O que é um Microsserviço?

Um **microsserviço** é uma unidade de software pequena, independente e com **responsabilidade única**, que se comunica com outros serviços via APIs bem definidas.

**Princípios fundamentais:**
- **Single Responsibility**: faz uma coisa e faz bem
- **Independentemente deployável**: pode ser atualizado sem afetar outros serviços
- **Descentralizado**: cada serviço pode ter sua própria linguagem, banco de dados e runtime
- **Comunicação via rede**: REST, gRPC, eventos (Pub/Sub)
- **Falha isolada**: um serviço caindo não derruba o sistema inteiro

### Microsserviço vs Monolito

```
MONOLITO
┌──────────────────────────────────┐
│  Auth + Busca + Recomendação     │
│  + Notificação + Pagamento       │
│  (tudo em um único deploy)       │
└──────────────────────────────────┘
         ↓ qualquer mudança
    deploy de tudo de novo

MICROSSERVIÇOS
┌───────┐  ┌────────┐  ┌─────────────┐
│ Auth  │  │ Busca  │  │ Recomendação│
└───────┘  └────────┘  └─────────────┘
     ↕           ↕            ↕
┌───────────┐  ┌───────┐  ┌──────────┐
│Notificação│  │Pagto  │  │  (...)   │
└───────────┘  └───────┘  └──────────┘
         ↓ cada um deploya independente
```

---

## 🔀 Arquitetura de Microsserviços vs Arquitetura de Pipeline

Esta é uma distinção conceitual **muito importante** e frequentemente confundida.

### Arquitetura de Pipeline

Um **pipeline** é uma **sequência ordenada e acoplada de etapas**, onde cada etapa passa o resultado para a próxima.

```
Dados Brutos → [Etapa 1] → [Etapa 2] → [Etapa 3] → Resultado Final
                  ↑            ↑            ↑
             Dependente    Dependente    Dependente
             do anterior   do anterior   do anterior
```

**Características:**
- Fluxo unidirecional e determinístico
- Etapas acopladas por dependência de dados
- Falha em qualquer etapa interrompe o fluxo
- Difícil de escalar etapas individuais
- Comum em ETL, treinamento de modelos, processamento em batch

**Exemplos práticos:** Kubeflow Pipelines, Apache Airflow DAGs, MLflow Pipelines

### Arquitetura de Microsserviços

Microsserviços são **serviços independentes que se comunicam via APIs**, sem ordem obrigatória.

```
         ┌──────────────────────────────┐
         │         API Gateway          │
         └──────┬──────────┬────────────┘
                │          │
         ┌──────▼──┐  ┌────▼────┐
         │ Serviço │  │Serviço  │
         │    A    │  │    B    │
         └──────┬──┘  └────┬────┘
                │          │
         ┌──────▼──────────▼──────┐
         │       Serviço C        │
         └────────────────────────┘
```

**Características:**
- Serviços chamáveis independentemente
- Escalonamento individual por demanda
- Cada serviço tem seu ciclo de vida próprio
- Comunicação sob demanda, não obrigatoriamente sequencial

### Comparação direta

| Critério | Pipeline | Microsserviços |
|----------|---------|---------------|
| **Fluxo** | Sequencial e acoplado | Sob demanda, desacoplado |
| **Escalonamento** | Todo o pipeline junto | Serviço a serviço |
| **Falha** | Interrompe o pipeline | Isolada ao serviço |
| **Flexibilidade** | Baixa (ordem fixa) | Alta (qualquer combinação) |
| **Ideal para** | ETL, treinamento, batch | APIs, tools de agentes, sistemas reativos |
| **Latência** | Tolerante | Precisa ser baixa |

> **Insight para MLOps:** Treinamento de modelos → pipeline. Servir o modelo como ferramenta para um agente → microsserviço.

---

## 🤝 Por que Microsserviços e Serverless se Complementam

Serverless é o **modelo de deploy ideal para microsserviços** pelos seguintes motivos:

1. **Escala por serviço**: cada microsserviço escala independentemente de acordo com sua própria demanda — exatamente o que serverless oferece
2. **Custo proporcional ao uso**: um serviço que é chamado raramente (ex.: tool de análise de PDF) não gera custo quando inativo
3. **Zero overhead operacional**: sem gerenciar clusters, sem configurar load balancers por serviço
4. **Deploy independente nativo**: cada Cloud Run service é um deploy isolado
5. **Isolamento de falhas físico**: cada serviço roda em containers separados

**Analogia prática:**
> Se microsserviços são os tijolos de uma construção, serverless é o terreno que já tem toda a infraestrutura (água, luz, rede) instalada. Você só coloca os tijolos.

### Quando usar GCP Cloud Run para microsserviços

**Cloud Run** é a escolha natural no GCP para microsserviços porque:
- Sobe qualquer container Docker como endpoint HTTP/gRPC
- Escala para zero (sem custo quando inativo)
- Permite `min-instances` para serviços com latência crítica
- Integração nativa com Secret Manager, IAM, Pub/Sub
- Suporta autenticação via service account sem código adicional
- Deploy em segundos via `gcloud run deploy`

---

## 🤖 Como Aplicações Agênticas se Beneficiam de Microsserviços

### O modelo de tools em agentes

Agentes de IA tomam decisões e executam ações através de **tools** — funções que podem ser chamadas pelo LLM com parâmetros específicos. Ao modelar cada tool como um microsserviço independente, você obtém benefícios que vão muito além do código:

```
┌─────────────────────────────────────────────────────┐
│                   AGENTE (Agno)                     │
│                                                     │
│  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │  Tool A    │  │  Tool B    │  │   Tool C     │  │
│  │(HTTP call) │  │(HTTP call) │  │ (local func) │  │
│  └─────┬──────┘  └─────┬──────┘  └──────────────┘  │
└────────│───────────────│─────────────────────────────┘
         │               │
         ▼               ▼
┌────────────────┐  ┌────────────────┐
│ Microsserviço  │  │ Microsserviço  │
│   Cloud Run    │  │   Cloud Run    │
│  (busca docs)  │  │ (exec. código) │
└────────────────┘  └────────────────┘
```

### Benefícios concretos

**1. Observabilidade individual por tool**
- Cada microsserviço tem seus próprios logs, métricas e traces no Cloud Run
- Você consegue responder: "essa tool está sendo chamada com que frequência? Com que latência? Com que taxa de erro?"
- No modelo monolítico isso fica enterrado em logs genéricos do agente

**2. Escalonamento independente**
- Uma tool de "busca semântica" pode receber 1000 chamadas/minuto enquanto a tool de "geração de relatório PDF" recebe 5
- Cada uma escala conforme sua própria demanda sem desperdiçar recursos

**3. Deploy e atualização sem downtime do agente**
- Atualizar a lógica de uma tool não exige redeploy da aplicação do agente
- Versioning de tools independente: pode ter `v1` e `v2` rodando em paralelo com traffic splitting

**4. Reutilização entre agentes**
- O mesmo microsserviço de "busca semântica" pode ser usado pelo agente de suporte, pelo agente de pesquisa e pelo agente de onboarding
- Uma atualização beneficia todos automaticamente

**5. Isolamento de falhas**
- Se a tool de "análise de sentimento" falhar, o agente pode degradar graciosamente (responder sem essa informação) em vez de crashar
- Mais fácil de implementar circuit breakers e retries

**6. Flexibilidade tecnológica**
- Tool de OCR em Go, tool de análise numérica em Python com numpy, tool de ML inference com TensorFlow Serving
- O agente não precisa carregar todas as dependências — apenas faz HTTP calls

### Exemplo em Agno — configurando tools via endpoint

```python
import httpx
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools import tool

@tool(description="Busca documentos relevantes na base de conhecimento")
def buscar_documentos(query: str, top_k: int = 5) -> dict:
    """Chama o microsserviço de busca semântica no Cloud Run."""
    response = httpx.post(
        "https://busca-semantica-xxxxx-uc.a.run.app/search",
        json={"query": query, "top_k": top_k},
        headers={"Authorization": f"Bearer {get_id_token()}"},
        timeout=10.0,
    )
    response.raise_for_status()
    return response.json()

@tool(description="Executa código Python e retorna o resultado")
def executar_codigo(codigo: str) -> dict:
    """Chama o microsserviço de execução segura de código."""
    response = httpx.post(
        "https://code-executor-xxxxx-uc.a.run.app/execute",
        json={"code": codigo},
        headers={"Authorization": f"Bearer {get_id_token()}"},
        timeout=30.0,
    )
    response.raise_for_status()
    return response.json()

agente = Agent(
    model=Gemini(id="gemini-2.0-flash"),
    tools=[buscar_documentos, executar_codigo],
    instructions="Você é um assistente de análise de dados...",
)
```

---

## 🔐 Gerenciamento de Secrets em Microsserviços

Esta seção cobre um dos maiores causadores de bugs silenciosos, falhas de deploy e vulnerabilidades de segurança em sistemas de microsserviços.

### Anti-patterns (o que NUNCA fazer)

```python
# ❌ NUNCA: hardcoded no código
API_KEY = "sk-abc123..."

# ❌ NUNCA: commitado no repositório
# arquivo .env no git

# ❌ NUNCA: passado como argumento na CLI em scripts de CI/CD
# deploy.sh --api-key sk-abc123...

# ❌ NUNCA: logado acidentalmente
print(f"Conectando com key: {os.environ['API_KEY']}")  # expõe em logs
```

### O modelo correto: injeção em runtime

Secrets **nunca devem existir no código ou na imagem Docker**. Eles devem ser injetados em tempo de execução pelo provedor de infraestrutura.

```
[Código/Imagem Docker]  →  ZERO secrets
[GCP Secret Manager]    →  secrets versionados e auditados
[Cloud Run Service]     →  recebe secrets via env vars ou volume na inicialização
[Container em execução] →  acessa via os.environ ou arquivo
```

### GCP Secret Manager — implementação prática

**1. Criando e gerenciando secrets via CLI**

```bash
# Criar um secret
gcloud secrets create OPENAI_API_KEY --replication-policy="automatic"

# Adicionar uma versão (o valor real)
echo -n "sk-sua-chave-aqui" | gcloud secrets versions add OPENAI_API_KEY --data-file=-

# Listar versões
gcloud secrets versions list OPENAI_API_KEY

# Desativar versão antiga após rotação
gcloud secrets versions disable 1 --secret=OPENAI_API_KEY
```

**2. Configurando Cloud Run para injetar o secret como variável de ambiente**

```bash
gcloud run deploy meu-microsservico \
  --image gcr.io/meu-projeto/meu-microsservico:latest \
  --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest" \
  --service-account=meu-sa@meu-projeto.iam.gserviceaccount.com \
  --region=us-central1
```

O `--set-secrets` mapeia `VARIAVEL_ENV=NOME_SECRET:versao`. O Cloud Run injeta automaticamente como variável de ambiente no container.

**3. Permissão correta via IAM (princípio do menor privilégio)**

```bash
# Criar service account para o microsserviço
gcloud iam service-accounts create sa-busca-semantica \
  --display-name="SA Microsserviço Busca Semântica"

# Dar permissão APENAS para acessar os secrets que esse serviço precisa
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
  --member="serviceAccount:sa-busca-semantica@meu-projeto.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

> **Princípio do menor privilégio:** cada microsserviço deve ter acesso **apenas** aos secrets que realmente precisa. Se o serviço de busca não precisa da chave de pagamento, ele não deve ter acesso a ela.

**4. Acessando secrets via Python SDK (fallback ou desenvolvimento local)**

```python
from google.cloud import secretmanager
import os

def get_secret(secret_id: str, project_id: str = None) -> str:
    """Obtém secret do Secret Manager. Em dev local, usa variável de ambiente."""
    if os.environ.get("ENV") == "local":
        return os.environ[secret_id]  # usa .env local (nunca commitar!)
    
    project = project_id or os.environ["GOOGLE_CLOUD_PROJECT"]
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")
```

**5. Uso no microsserviço**

```python
import os
from fastapi import FastAPI

app = FastAPI()

# Em Cloud Run: injetado automaticamente via --set-secrets
# Em dev local: definido no .env (que está no .gitignore)
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
```

### Rotação de secrets

```
1. Criar nova versão do secret no Secret Manager
2. Atualizar o Cloud Run service para usar a nova versão (ou :latest automático)
3. Cloud Run faz rolling deploy sem downtime
4. Desativar a versão antiga
5. Revogar tokens antigos na fonte (OpenAI, banco de dados, etc.)
```

### Secrets em desenvolvimento local

```bash
# .env.example — commitado no repositório (sem valores reais)
OPENAI_API_KEY=your-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/db
QDRANT_API_KEY=your-qdrant-key

# .env — NUNCA commitado (está no .gitignore)
OPENAI_API_KEY=sk-real-key-here
DATABASE_URL=postgresql://user:real-pass@localhost:5432/db
```

```python
# Carregando .env apenas em desenvolvimento
from dotenv import load_dotenv
import os

if os.environ.get("ENV", "local") == "local":
    load_dotenv()  # só carrega em dev — em produção as vars já estão injetadas
```

---

## 🏗️ Exemplos de Arquiteturas de Agentes com Microsserviços

### Arquitetura 1 — Separação clara: Agente + Tools como Microsserviços

```
┌────────────────────────────────────────────────────────────┐
│              Cloud Run: agente-mlops-app                   │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                  Agno Agent                          │  │
│  │  model: Gemini 2.0 Flash                            │  │
│  │  tools:                                              │  │
│  │    - buscar_documentos  → HTTP → Cloud Run          │  │
│  │    - executar_analise   → HTTP → Cloud Run          │  │
│  │    - gerar_relatorio    → HTTP → Cloud Run          │  │
│  │    - buscar_na_web      → (tool local nativa)       │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌──────────────────┐  ┌─────────────────┐
│   Cloud Run     │  │    Cloud Run     │  │   Cloud Run     │
│ busca-semantica │  │ code-executor    │  │ relatorio-svc   │
│                 │  │                  │  │                 │
│ FastAPI + Qdrant│  │ FastAPI + sandbox│  │ FastAPI + WeasyP│
│ POST /search    │  │ POST /execute    │  │ POST /generate  │
└─────────────────┘  └──────────────────┘  └─────────────────┘
         │
         ▼
┌─────────────────┐
│     Qdrant      │
│  (banco vetorial│
│   da aula 07)  │
└─────────────────┘
```

**Pontos-chave desta arquitetura:**
- O container do agente **não carrega** as dependências pesadas dos microsserviços
- Cada microsserviço é deployado e versionado **independentemente**
- A aplicação do agente pode ser atualizada sem tocar nas tools
- Cada microsserviço tem seus próprios logs e métricas no Cloud Run

### Arquitetura 2 — Agente com tools mistas (locais + microsserviços)

Nem toda tool precisa ser um microsserviço. A regra prática:

| Tipo de Tool | Onde implementar | Motivo |
|-------------|-----------------|--------|
| Busca semântica | Microsserviço | Dependência pesada (Qdrant client), reutilizável |
| Execução de código | Microsserviço | Isolamento de segurança obrigatório |
| Geração de imagem | Microsserviço | GPU/recurso especializado |
| Formatação de texto | Tool local | Leve, sem dependências externas |
| Busca na web | Tool local (Agno built-in) | Já disponível no framework |
| Cálculo simples | Tool local | Lógica trivial, sem estado |

### Arquitetura 3 — Multi-agent com microsserviços compartilhados

```
┌─────────────────┐      ┌─────────────────┐
│  Agente Suporte │      │ Agente Pesquisa  │
│   (Cloud Run)   │      │   (Cloud Run)    │
└────────┬────────┘      └────────┬────────┘
         │                        │
         └──────────┬─────────────┘
                    │ Ambos usam o mesmo microsserviço
                    ▼
         ┌─────────────────────┐
         │   busca-semantica   │
         │     Cloud Run       │
         └─────────────────────┘
```

---

## ✅ Quando Usar (e Quando NÃO Usar) Serverless + Microsserviços em Agentes

### Quando USAR ✅

| Cenário | Por quê faz sentido |
|---------|-------------------|
| Tools com dependências pesadas (GPU, ML models) | Isola o recurso caro no microsserviço dedicado |
| Tools reutilizadas por múltiplos agentes | Uma mudança beneficia todos sem redeploy |
| Tools com tráfego muito diferente entre si | Cada uma escala independentemente |
| Times diferentes responsáveis por cada tool | Deploy independente, sem coordenação |
| Tools que precisam de linguagens diferentes | Cada microsserviço usa a stack ideal |
| Requisitos de observabilidade detalhada por tool | Logs e métricas isolados por serviço |
| Ambientes de produção com SLA | Escala e HA gerenciados pelo Cloud Run |

### Quando NÃO USAR ❌

| Cenário | Alternativa melhor |
|---------|-------------------|
| Prototipagem rápida / POC | Tools locais no agente, tudo em um container |
| Tools com latência crítica < 50ms | Microsserviços adicionam overhead de rede (~10-50ms) |
| Budget muito limitado | Overhead de múltiplos deploys pode superar o benefício |
| Time pequeno (1-2 pessoas) | Complexidade operacional não compensa |
| Tools simples sem reuso | Criar um microsserviço para uma função de 5 linhas é over-engineering |
| Lógica com estado compartilhado complexo | Microsserviços stateless são difíceis com estado compartilhado |
| Sem necessidade de escala individual | Monolito bem estruturado é mais simples |

> **Regra prática:** Comece com tools locais no agente. Extraia para microsserviço quando: (1) a tool tem dependências que tornam o container do agente pesado demais, (2) outra equipe ou agente precisa usar a mesma tool, ou (3) a tool tem requisitos de escala muito diferentes do agente.

---

## 📐 Comparação de Abordagens de Deploy

| | **Tudo em um container** | **Microsserviços serverless** |
|---|---|---|
| **Complexidade** | Baixa | Alta |
| **Custo inicial** | Baixo | Médio (múltiplos serviços) |
| **Custo em escala** | Sobe junto | Proporcional ao uso |
| **Observabilidade** | Logs misturados | Isolada por serviço |
| **Deploy** | Simples (1 container) | Múltiplos deploys |
| **Latência** | Mínima (chamada local) | Overhead de rede |
| **Manutenção** | Acoplada | Independente |
| **Recomendado para** | POC, times pequenos | Produção, múltiplos agentes |

---

## 🔗 Referências

### Serverless e Cloud Run
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs) — referência principal para deploy serverless no GCP
- [Cloud Run — Configuring Secrets](https://cloud.google.com/run/docs/configuring/secrets) — injeção de secrets em variáveis de ambiente
- [Google Cloud Secret Manager](https://cloud.google.com/secret-manager/docs) — gerenciamento centralizado de secrets
- [Cloud Run — Min instances](https://cloud.google.com/run/docs/configuring/min-instances) — evitar cold starts em produção

### Microsserviços
- [Martin Fowler — Microservices](https://martinfowler.com/articles/microservices.html) — artigo seminal sobre microsserviços
- [Google Cloud — Microservices Architecture](https://cloud.google.com/architecture/microservices-architecture-introduction) — guia prático de arquitetura
- [The Twelve-Factor App](https://12factor.net/) — boas práticas para serviços cloud-native (especialmente fatores III e IV sobre config/secrets)

### Agno Framework
- [Agno Documentation](https://docs.agno.com) — documentação oficial do framework Agno (ex-PhiData)
- [Agno — Tools](https://docs.agno.com/tools/custom-tools) — como criar custom tools no Agno
- [Agno — Multi-Agent Teams](https://docs.agno.com/multi-agent) — arquiteturas multi-agente

### Secrets e Segurança
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html) — melhores práticas de segurança
- [Google Cloud IAM — Least Privilege](https://cloud.google.com/iam/docs/using-iam-securely#least_privilege) — princípio do menor privilégio no GCP

### Conceitos de Arquitetura
- [AWS — Serverless vs Containers](https://aws.amazon.com/serverless/faqs/) — comparação entre modelos de deploy
- [Google Cloud — When to use Cloud Run vs Cloud Functions](https://cloud.google.com/blog/products/serverless/cloud-run-vs-cloud-functions-for-serverless) — decisão entre FaaS e CaaS
