# Model Registry (MLOps)

Este documento organiza a apresentação da aula e serve como **guia conceitual** para o expositor.
A estrutura abaixo é uma sugestão a ser seguida para garantir clareza, progressão lógica e alinhamento com o grupo.

> 💡 **Fluxo sugerido**: começar com o caos do armazenamento ingênuo de artefatos de IA (`model_v2_final_FINAL.pkl` jogado em um bucket S3 ou pasta compartilhada), mostrar por que a falta de governança e rastreabilidade quebra sistemas em produção ("qual código e quais dados geraram esta predição errada no cliente X?"), e evoluir gradualmente até um ecossistema governado com **Model Registry**, integrado a pipelines de CI/CD/CT e LLMOps. A aula é sobre **governança, rastreabilidade, ciclo de vida e automação**, não apenas sobre escolher uma ferramenta.

---

## 1️⃣ Motivação

### 1.1 O caos dos artefatos "soltos": Por que S3/GCS/Git não são um Model Registry?

- **O anti-pattern clássico**: salvar o arquivo de modelo (`.pkl`, `.onnx`, `.pt`, `.safetensors`) em uma pasta do Google Drive ou em um bucket S3 com nomes como `modelo_fraude_v3_final.pkl`.
- **Por que Git não resolve**: Git foi desenhado para código-fonte. Commitar binários de múltiplos gigabytes estoura o repositório e inviabiliza o fluxo de desenvolvimento.
- **Por que S3/GCS puro não resolve**: Buckets armazenam *blobs* (bytes), mas não entendem o que é um modelo. Falta metadado estruturado: quais métricas de treino ele alcançou? Qual commit gerou este binário? Qual conjunto de dados foi usado? Quem aprovou a ida para produção?
- **O dilema em produção**: O serviço de inferência faz download de `s3://meu-bucket/model.pkl`. Se alguém sobrescrever esse arquivo por engano, a produção quebra ou passa a servir um modelo sem validação.

### 1.2 A pergunta fundamental de MLOps: Rastreabilidade e Reprodutibilidade

- **As 5 dimensões da linhagem de ML (ML Lineage)**:
  1. **Código**: Commit exato do Git (SHA) que executou o treinamento.
  2. **Dados**: Versão ou hash do conjunto de dados de treino e validação (via DVC, Feature Store ou Data Lakehouse).
  3. **Hiperparâmetros & Configurações**: Taxa de aprendizado, arquitetura, seed aleatória, tolerâncias.
  4. **Ambiente de Execução**: `requirements.txt`, `environment.yml` ou hash da Imagem Docker.
  5. **Métricas de Validação**: Acurácia, F1-Score, ROC-AUC, Latência p95, viés/fairness.
- **A pergunta sem resposta no caos**: "O modelo em produção apresentou comportamento discriminatório no cliente Y hoje às 14h. Qual foi o código, dado e ambiente exatos que geraram esse modelo há 3 meses?"

### 1.3 Impacto prático e de negócio

- **Regulamentação e Compliance**: EU AI Act, LGPD, resoluções do BACEN e FDA exigem auditabilidade ponta a ponta dos modelos que tomam decisões automatizadas.
- **Prevenção de regressão de qualidade**: Garantir que nenhum modelo vá para produção sem passar por *Quality Gates* automatizados.
- **Rollback Instantâneo**: Se a versão atual apresentar anomalias em produção, o sistema precisa fazer rollback para a versão estável anterior em segundos, apenas alterando uma referência (alias/tag), sem ter que reconstruir artefatos.

---

## 2️⃣ Como Funciona

### 2.1 Anatomia de um Model Registry

O Model Registry é um repositório centralizado de modelos de ML que gerencia todo o ciclo de vida do artefato. Ele é composto por 3 camadas fundamentais:

```text
┌─────────────────────────────────────────────────────────────────┐
│                      MODEL REGISTRY ENGINE                      │
├─────────────────────────────────────────────────────────────────┤
│ 1. Metadata Store (SQL / DB Key-Value)                          │
│    - Versões, Tags, Aliases, Status de Aprovação, Linhagem      │
├─────────────────────────────────────────────────────────────────┤
│ 2. Artifact Store (S3 / GCS / Azure Blob / MinIO)               │
│    - Pesos do modelo (.pt, .safetensors, .onnx, .bento)         │
├─────────────────────────────────────────────────────────────────┤
│ 3. API & Client Layer (REST / gRPC / Python SDK / Webhooks)     │
│    - CLI, Integrações CI/CD, Triggers para Serving              │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Ciclo de Vida, Estados e Aliases

- **Transição de Estados (Lifecycle Stages)**:
  - `Experimental` / `None`: Modelo registrado ao final de um experimento de treino.
  - `Staging` ($\text{Challenger}$): Modelo sob validação automatizada ou teste A/B / Shadow Deployment.
  - `Production` ($\text{Champion}$): O modelo ativo servindo tráfego real.
  - `Archived`: Modelos legados substituídos, mantidos apenas para histórico e auditoria.
- **A evolução: De Stages fixos para Aliases e Tags (MLflow 2.x+)**:
  - *Stages fixos* (`Staging`/`Production`) são rígidos e sofrem com problemas de concorrência.
  - *Aliases flexíveis* (`@champion`, `@challenger`, `@baseline`, `@llm-v1-prod`): Referências mutáveis que apontam para versões imutáveis do modelo.
  - O código de inferência consome: `models:/FraudeModel@champion` em vez de caminhos hardcoded!

### 2.3 Matriz de Comparação do Ecossistema

| Ferramenta | Tipo | Ponto Forte | Melhor Uso |
|---|---|---|---|
| **MLflow Model Registry** | Open Source / Padrão da Indústria | Abstração de *Flavors* (PyTorch, Sklearn, ONNX, vLLM), suporte a Aliases e Webhooks | Padrão aberto, multi-nuvem, integração direta com Python/Databricks |
| **Weights & Biases (W&B Models)** | SaaS / Híbrido | DX excepcional, visualização gráfica de linhagem de artefatos (Artifact Graphs) | Times focados em pesquisa profunda e LLMs com interface visual rica |
| **DVC + Studio / Dagshub** | Git-centric (Open Source) | Rastreabilidade baseada em Git, sem dependência de servidor de metadados complexo | Times com cultura GitOps forte |
| **AWS SageMaker Model Registry** | Cloud Native (AWS) | Integração nativa com IAM, Pipelines do SageMaker e deployments ECS/EKS | Infraestrutura 100% AWS com exigência de compliance corporativo |
| **Databricks Unity Catalog** | Data & AI Governance | Governança unificada de Dados (Tabelas/Delta) e IA (Modelos/LLMs) com lineage SQL | Ambientes corporativos Lakehouse em grande escala |

### 2.4 Model Registry na Era dos LLMs e GenAI

Servir e gerenciar LLMs trouxe novos desafios para o Model Registry:

- **Pesos Gigantes vs Adaptadores Ligeiros**: Não se registra um modelo de 70B (140GB) a cada experimento. Registra-se o **LoRA/PEFT Adapter** (dezenas de MB) vinculado à versão imutável do **Base Model**.
- **Prompts como Artefatos**: O Prompt Template e o System Prompt influenciam o comportamento tanto quanto os pesos. O Model Registry moderno versiona a combinação **Prompt + Pesos + Hiperparâmetros de Geração (Temperature, Top-P)**.
- **Quantizações e Formatos de Serving**: Versionamento de múltiplos alvos de inferência para o mesmo modelo (ex.: modelo FP16 para GPU de datacenter vs versão GGUF INT4 para CPU/Edge).
- **Métricas de Avaliação GenAI**: Registro de avaliações via **LLM-as-a-Judge**, ROUGE/BERTScore, e benchmarks de alucinação e segurança (Guardrails).

---

## 3️⃣ Quickstart & Demos

> 💡 **Instruções para ao vivo**: As demos a seguir podem ser executadas utilizando o MLflow instalado localmente via Python (`pip install mlflow`).

### 3.1 Demo 1 — MLflow: Do experimento ao registro com Alias `@champion`

Mostrar o fluxo simples em Python de logar um modelo e registrá-lo no Model Registry local com a tag/alias `@champion`:

```python
import mlflow
import mlflow.sklearn
from sklearn.ensemble import RandomForestClassifier

# 1. Configurar MLflow Tracking e Registry local
mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("detec_fraude")

with mlflow.start_run() as run:
    model = RandomForestClassifier(n_estimators=100)
    model.fit([[0, 1], [1, 0]], [0, 1])
    
    # Log das métricas e hiperparâmetros
    mlflow.log_param("n_estimators", 100)
    mlflow.log_metric("f1_score", 0.95)
    
    # 2. Log e Registro simultâneo do Modelo no Registry
    model_info = mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path="model",
        registered_model_name="ModeloFraude"
    )

# 3. Atribuir o Alias '@champion' à versão criada
client = mlflow.MlflowClient()
client.set_registered_model_alias(
    name="ModeloFraude", 
    alias="champion", 
    version=model_info.registered_model_version
)

print(f"Modelo versão {model_info.registered_model_version} registrado como @champion!")
```

### 3.2 Demo 2 — Promoção de modelo programática e triggers via Webhook

- Explicar como a transição do alias `@champion` da versão 1 para a versão 2 envia um Webhook HTTP para o pipeline de CD.
- O pipeline de CD captura o evento e dispara o redeploy sem intervenção humana manual.

```python
# Transfere o alias @champion da versão antiga para a nova versão validada (Versão 2)
client.set_registered_model_alias("ModeloFraude", "champion", version="2")
client.set_registered_model_alias("ModeloFraude", "challenger", version="1")
```

### 3.3 Demo 3 — Serving dinâmico consumindo o `@champion`

Mostrar como a API de inferência (FastAPI/BentoML) carrega a versão ativa apontada pelo alias, eliminando arquivos locais ou caminhos fixos:

```python
import mlflow.pyfunc
from fastapi import FastAPI

app = FastAPI()

# Carrega a versão atual associada ao alias @champion direto do Registry
MODEL_URI = "models:/ModeloFraude@champion"
model = mlflow.pyfunc.load_model(MODEL_URI)

@app.post("/predict")
def predict(features: list[float]):
    prediction = model.predict([features])
    return {"prediction": prediction.tolist(), "model_uri": MODEL_URI}
```

---

## 4️⃣ Boas Práticas para Fechar a Aula

1. **Imutabilidade de Versões**: Uma vez registrada uma versão de modelo (ex.: v1.0.0), os seus artefatos e metadados **nunca** devem ser alterados ou sobrescritos. O progresso é sempre feito registrando novas versões.
2. **Separe Tracking de Registro**: MLflow Tracking serve para explorar centenas de experimentos de rascunho. O Model Registry deve conter **apenas** modelos candidatos e aprovados.
3. **Automatize os Quality Gates**: Promoção para `@staging` ou `@champion` deve ser feita por pipelines de CI/CD após passar em testes unitários de código, testes de estresse de latência e checagem de viés.
4. **Governança e RBAC**: Restrinja a permissão de alterar o alias `@champion` apenas para papéis autorizados (Lead Data Scientist / MLOps Engineer / Pipeline CI/CD).
5. **Decouple Serving do Registry em Produção**: Para alta disponibilidade em produção crítica, o servidor de inferência pode baixar o artefato apontado pelo `@champion` durante o startup ou build de container, evitando dependência síncrona com o servidor do Registry no momento da predição.
