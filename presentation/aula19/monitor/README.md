# 📘 Aula 19 — Model Registry (MLOps)

## Material de Estudo Prévio

Este material tem como objetivo **preparar para a aula de Model Registry em MLOps**, oferecendo uma base conceitual sólida para acompanhar, complementar e aprofundar a discussão conduzida pelo apresentador.

⚠️ **Este conteúdo não é um guia de instruções**, mas sim um **material de estudo prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do CEIA/UFG.

---

## 🎯 Objetivo da Aula

Ao final desta aula, espera-se que os participantes compreendam:

- O que é um **Model Registry** e por que buckets de armazenamento (S3/GCS) ou sistemas de controle de versão de código (Git) são insuficientes para gerenciar artefatos de IA
- As **5 dimensões da linhagem de ML (ML Lineage)**: código, dados, hiperparâmetros, ambiente e métricas
- O ciclo de vida de um modelo de Machine Learning: de experimento a candidato, staging ($\text{Challenger}$), produção ($\text{Champion}$) e arquivado
- As diferenças arquiteturais entre **Stages legados** e **Aliases/Tags modernos** (`@champion`, `@challenger`)
- As principais ferramentas do ecossistema: **MLflow Model Registry**, **Weights & Biases (W&B Models)**, **DVC + Studio**, **SageMaker/Vertex AI/Azure ML** e **Databricks Unity Catalog**
- A evolução do Model Registry na era dos **LLMs e GenAI**: versionamento de adaptadores LoRA/PEFT, prompt templates, quantizações (GGUF, AWQ, FP8) e métricas de *LLM-as-a-Judge*
- Como o Model Registry conecta o pipeline de **Treinamento Contínuo (CT)** ao **Deployment Contínuo (CD)** via Webhooks e Quality Gates automatizados

---

## 🧠 Contexto: O que é e por que precisamos de um Model Registry?

### O Anti-Pattern Clássico: O Caos dos Binários Soltos

Nos primeiros estágios de maturidade em Ciência de Dados, o gerenciamento de modelos costuma ocorrer de forma artesanal. Os modelos treinados são serializados em arquivos binários (`.pkl`, `.joblib`, `.pth`, `.h5`, `.onnx`) e salvos em pastas locais ou buckets em nuvem com nomes arbitrários:

```text
s3://meu-bucket-de-modelos/
├── modelo_fraude_v1.pkl
├── modelo_fraude_v2_ajustado.pkl
├── modelo_fraude_v2_FINAL.pkl
├── modelo_fraude_v2_FINAL_mesmo.pkl
└── modelo_fraude_novo_teste.pkl
```

Essa abordagem ingênua gera sérios problemas à medida que o sistema ganha complexidade:

1. **Amnésia de Metadados**: O arquivo binário guarda os pesos numéricos do modelo, mas perde totalmente o contexto. Não se sabe qual acurácia ele teve, qual conjunto de validação foi usado ou quem autorizou a versão.
2. **Impossibilidade de Reprodutibilidade**: Se o cientista de dados que treinou o modelo sair da empresa, torna-se quase impossível recriar exatamente o mesmo binário, pois não há vínculo formal com o commit do Git nem com o hash dos dados de treino.
3. **Acoplamento Frágil na Inferência**: O microsserviço de produção faz a requisição diretamente para um caminho fixo (`s3://.../modelo_fraude_v2_FINAL.pkl`). Se o arquivo for acidentalmente alterado ou sobrescrito, a inferência em produção pode ser interrompida.
4. **Vulnerabilidade de Segurança e Compliance**: Sem controle de acesso (RBAC) granular e histórico de auditoria (quem promoveu o modelo e quando), a empresa fica exposta a violações regulatórias e falhas de governança.

### Binários vs Código vs Dados vs Model Registry

É fundamental distinguir o papel de cada repositório na arquitetura moderna de MLOps:

| Recurso | Repositório Adequado | O que gerencia | O que NÃO faz |
|---|---|---|---|
| **Código-Fonte** | **Git** (GitHub, GitLab) | Código de pré-processamento, arquitetura, testes e scripts de treino | Não armazena arquivos binários grandes nem métricas de execução dinâmicas |
| **Conjunto de Dados** | **Data Lake / Lakehouse / Feature Store / DVC** | Tabelas Delta/Parquet, features versionadas, dados brutos e transformados | Não gerencia pesos treinados nem APIs de promoção de serviços |
| **Artefatos Genéricos** | **Object Storage** (S3, GCS, Blob) | Arquivos brutos sem semântica de IA (*blobs* de bytes) | Não possui interface de ciclo de vida de ML, nem aliasing ou métricas |
| **Modelos de ML** | **Model Registry** | Binários + Metadados + Linhagem + Governança + Ciclo de Vida + Aliases | Não substitui o Data Lake nem o repositório Git, mas atua como a **ponte unificadora** entre eles |

> **A Definição de Model Registry:** Um repositório centralizado e governado, dotado de um catálogo de modelos, armazenamento de artefatos e banco de metadados, projetado para rastrear a linhagem completa, controlar versões imutáveis, gerenciar transições de estado e integrar o modelo treinado com os serviços de implantação e monitoramento.

---

## ⚙️ Pilares de um Model Registry Moderno

```text
                 ┌────────────────────────────────────────────────────────┐
                 │                   LINHAGEM COMPLETA                    │
                 │  (Git Commit + Data Hash + Hyperparams + Environment)  │
                 └───────────────────────────┬────────────────────────────┘
                                             │
                                             ▼
 ┌──────────────────────┐        ┌──────────────────────┐        ┌──────────────────────┐
 │    TRACKING ENGINE   │───────►│    MODEL REGISTRY    │───────►│    SERVING ENGINE    │
 │ (MLflow/W&B/Neptune) │        │ (Versões / Aliases)  │        │(FastAPI/Bento/vLLM)  │
 └──────────────────────┘        └──────────────────────┘        └──────────────────────┘
                                             │
                                             ▼
                 ┌────────────────────────────────────────────────────────┐
                 │                 GOVERNANÇA & INTEGRITY                 │
                 │     (RBAC + Quality Gates + Webhooks + Signatures)     │
                 └────────────────────────────────────────────────────────┘
```

### 1. Rastreabilidade & Linhagem em 5 Dimensões (ML Lineage Graph)

Um Model Registry de alta maturidade vincula o artefato final a 5 dimensões essenciais:

1. **Código-Fonte (Git SHA)**: O commit exato da aplicação de ML que executou o treinamento (`git commit: a1b2c3d4`).
2. **Versão dos Dados (Data Hash / Feature Store Version)**: O ponteiro exato da tabela Delta ou snapshot do DVC (`data_version: v3.2.0` ou `hash: 9f8e7d6c`).
3. **Hiperparâmetros e Configuração**: O arquivo de configuração completo usado na execução (`learning_rate: 0.001`, `max_depth: 6`, `seed: 42`).
4. **Especificação do Ambiente (Environment Specs)**: A lista de dependências exata (`requirements.txt`, `environment.yml` ou `docker_image_digest`).
5. **Métricas de Desempenho e Validação**: Relatório detalhado das métricas obtidas no conjunto de validação e teste (`accuracy: 0.94`, `p95_latency: 12ms`, `fairness_score: 0.98`).

### 2. Versionamento Semântico e Imutabilidade

- **Versões Imutáveis**: Uma vez que uma versão de modelo é registrada (ex.: `ModeloFraude` v1), seus binários e metadados tornam-se **somente leitura**. Nenhuma alteração de código ou re-treino pode sobrescrever a v1. Novas iterações obrigatoriamente geram a v2.
- **Flavors / Abstrações de Formato**: Registries modernos como o MLflow salvam o modelo em múltiplos "sabores" (*flavors*). Por exemplo, um modelo PyTorch pode ser registrado com o flavor nativo (`pytorch`), o flavor genérico Python (`pyfunc`) e o flavor otimizado (`onnx`), permitindo que diferentes clientes o consumam sem reescrever o código de carregamento.

### 3. Ciclo de Vida: Stages Legados vs. Aliases Modernos

Historicamente, o MLflow e outros registradores utilizavam **Stages fixos** para indicar o estado de um modelo:
`None` $\rightarrow$ `Staging` $\rightarrow$ `Production` $\rightarrow$ `Archived`.

Contudo, a prática de engenharia evoluiu para **Aliases e Tags flexíveis**:

- **Por que Stages caíram em desuso?** Stages fixos permitiam apenas um modelo em `Production` por vez dentro do registrador. Isso dificultava arquiteturas modernas com múltiplos targets de deploy (ex.: servir o modelo em GPU na nuvem e em INT4 no Edge ao mesmo tempo, ou rodar Canary Deployments).
- **Aliases mutáveis (`@champion`, `@challenger`, `@canary`, `@baseline`)**: Um alias é uma etiqueta dinâmica que aponta para uma versão imutável. 
  - A API de inferência consulta: `models:/ModeloFraude@champion`.
  - Quando a v2 é aprovada, o alias `@champion` é movido da v1 para a v2 instantaneamente. O serviço de produção passa a carregar a v2 sem nenhuma alteração na linha de código ou configuração do cliente.

### 4. Governança, RBAC e Assinaturas Criptográficas

- **Controle de Acesso Baseado em Papéis (RBAC)**: Cientistas de dados podem registrar novas versões de modelos (criação de rascunhos), mas **apenas** engenheiros de MLOps ou pipelines automatizados de CI/CD possuem permissão para atribuir o alias `@champion`.
- **Assinatura e Checksum (SHA-256)**: Para ambientes altamente regulados (finanças, saúde, defesa), o Model Registry gera um hash SHA-256 ou assinatura digital no momento do registro. O servidor de inferência valida esse checksum antes de carregar o modelo na memória da GPU/CPU, impedindo ataques de tampering (modificação maliciosa de pesos).

---

## 🛠️ Ecossistema de Ferramentas & Arquiteturas

### 1. MLflow Model Registry (Open Source Benchmark)

O **MLflow** é a ferramenta open source mais adotada no ecossistema global de MLOps.

- **Componentes**:
  - `Tracking`: Registra experimentos, parâmetros e métricas.
  - `Model Registry`: Interface gráfica e API para gerenciar modelos registrados, versões, aliases, tags e anotações em Markdown.
  - `MLmodel File`: Arquivo YAML que descreve os *flavors*, dependências e assinaturas de entrada/saída (Input/Output Signature).
- **Recursos Avançados**: Suporte nativo a Webhooks (notificar Slack/Teams ou disparar um pipeline do GitHub Actions quando um alias for alterado) e suporte ao MLflow Server descentralizado com backend em PostgreSQL/MySQL e artefatos no S3/GCS.

### 2. Weights & Biases (W&B Models & Artifacts)

O **W&B** se destaca pela experiência do desenvolvedor (DX) e por seu poderoso sistema de rastreamento visual.

- **Grafos de Artefatos (Artifact Lineage Graphs)**: O W&B visualiza graficamente a árvore de dependência completa: `Dataset Artifact` $\rightarrow$ `Training Run` $\rightarrow$ `Model Artifact` $\rightarrow$ `Evaluation Run` $\rightarrow$ `Registry Collection`.
- **Foco em Pesquisa e LLMs**: Excelente para acompanhar métricas de perda em tempo real, comparar hiperparâmetros com gráficos de coordenadas paralelas e auditar artefatos pesados.

### 3. DVC (Data Version Control) + DVC Studio / Dagshub

Uma abordagem centrada no ecossistema **Git (GitOps)**.

- **Como funciona**: O DVC não exige um servidor de metadados SQL dedicado. Ele cria pequenos arquivos ponteiros `.dvc` que são commitados diretamente no repositório Git. O binário do modelo vai para o S3/GCS via comando `dvc push`.
- **DVC Studio / Dagshub**: Adiciona uma interface web para visualizar o registro de modelos, comparar experimentos e promover modelos através de *Pull Requests* ou chamadas de API integradas ao Git.

### 4. Cloud Native Registries (AWS, Azure, GCP)

- **AWS SageMaker Model Registry**: Integrado ao AWS IAM, AWS EventBridge e SageMaker Pipelines. Permite aprovação formal de modelos via console ou SDK e dispara atualizações de endpoints SageMaker automaticamente.
- **Azure Machine Learning Model Registry**: Integrado ao Azure DevOps, RBAC do Azure Active Directory e ML-flow tracking API.
- **GCP Vertex AI Model Registry**: Integrado aos pipelines do Vertex AI, BigQuery ML e AutoMl, oferecendo visão unificada de avaliação e implantação no Google Cloud.

### 5. Databricks Unity Catalog

A solução corporativa da Databricks que unifica governança de dados e IA sob uma mesma camada de catálogo.

- **Governança Unificada**: Permite aplicar políticas de controle de acesso (SQL GRANT/REVOKE) tanto para tabelas Delta quanto para modelos de Machine Learning e LLMs.
- **Lineage Automático**: Rastreia nativamente qual tabela Delta alimentou o treino do modelo registrado no Unity Catalog, criando uma matriz de linhagem de ponta a ponta.

### Matriz Comparativa do Ecossistema

| Característica | MLflow Registry | W&B Models | DVC + Studio | AWS SageMaker Registry | Unity Catalog |
|---|---|---|---|---|---|
| **Modelo de Implantação** | Open Source / Self-Hosted / Managed | SaaS / Hybrid Cloud | Open Source + SaaS | Cloud Managed (AWS) | Cloud Managed (Databricks) |
| **Governança & RBAC** | Média (Alta no Managed) | Alta | Baseada em Git | Muito Alta (IAM) | Muito Alta (SQL Governance) |
| **Interface Visual** | Clara e Funcional | Excepcional / Rica | Integrada ao Git / Studio | Console AWS Standard | Console Databricks Unified |
| **Suporte a Webhooks** | Sim (Nativo) | Sim (Nativo) | Sim (via Git Webhooks) | Sim (via EventBridge) | Sim (via Event Grid/Webhooks) |
| **Abstração de Flavors** | Excelente (`pyfunc`, `onnx`) | Média (Artefato genérico) | Manual | Específica AWS | Excelente (MLflow nativo) |

---

## 🤖 Model Registry na Era dos LLMs e GenAI

O surgimento dos Grandes Modelos de Linguagem (LLMs) e da Inteligência Artificial Generativa redefiniu os requisitos de um Model Registry:

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          GENAI MODEL REGISTRY PACKAGE                       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Base Model Ref    : "meta-llama/Llama-3.1-8B-Instruct" (Immutable SHA)   │
│ 2. PEFT / LoRA Weights: adapter_model.safetensors (50 MB)                   │
│ 3. Prompt Specification: system_prompt.jinja2 + parameters.json (Temp, TopP)│
│ 4. Serving Artifacts  : GGUF-Q4_K_M (CPU) / AWQ-INT4 (GPU) / FP8            │
│ 5. Eval Metadata      : LLM-as-a-Judge Score + Toxicity & Hallucination Eval│
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1. Pesos Gigantes vs. Adaptadores Leves (PEFT/LoRA)

- **O Desafio**: Um modelo base como o Llama-3-70B ocupa ~140 GB em precisão FP16. Registrar um novo arquivo binário de 140 GB a cada experimento de ajuste fino (fine-tuning) é inviável financeira e operacionalmente.
- **A Solução no Registry**: O Model Registry armazena o **LoRA Adapter** (que possui apenas alguns dezenas de megabytes) e grava em seus metadados a referência imutável ao **Base Model** (URI ou repositório Hugging Face com commit SHA fixo).

### 2. Prompt Engineering como Parte do Artefato

Em aplicações de GenAI, alterar o *System Prompt* altera o comportamento do sistema de forma tão drástica quanto modificar os pesos do modelo. 

- O Model Registry moderno versiona o **pacote completo de inferência**: `LoRA Adapter` + `Prompt Template` + `Hiperparâmetros de Geração (Temperature, Top-P, Presence Penalty)` + `Versão da Engine de Serving (vLLM/SGLang)`.

### 3. Múltiplos Formatos de Quantização

Um único modelo fine-tuned pode ser destinado a diferentes ambientes de execução:

- Versão `FP8` / `BF16` para clusters NVIDIA H100.
- Versão `AWQ` / `GPTQ` (INT4) para economizar VRAM em GPUs L4/A10G.
- Versão `GGUF` (INT4/INT8) para execução local em CPU.
- O Model Registry organiza esses múltiplos binários sob a mesma versão conceitual do modelo, marcando cada arquivo com tags de hardware correspondentes.

### 4. Avaliações Automatizadas de GenAI (*LLM-as-a-Judge*)

Em modelos tradicionais de regressão/classificação, registram-se métricas como RMSE ou F1-Score. Para LLMs, o registrador armazena metadados de avaliações complexas:

- Pontuação de **LLM-as-a-Judge** (ex.: nota de 1 a 5 atribuída pelo GPT-4o para coerência e fidelidade ao contexto).
- Métricas de **RAG** (Fidelidade da Resposta, Relevância do Contexto via Ragas/TruLens).
- Benchmarks automatizados de alucinação, toxicidade e vazamento de dados de treinamento (Guardrails).

---

## 🌐 Conexão do Model Registry com o Ciclo MLOps (CI/CD/CT)

O Model Registry não é uma ilha isolada. Ele atua como o **orquestrador central de estado** na automação de MLOps:

```text
 ┌─────────────────┐
 │   Treinamento   │
 │ Contínuo (CT)   │
 └────────┬────────┘
          │ (1. Treina & Loga Experimento)
          ▼
 ┌─────────────────┐       (2. Auto-Registra Versão Candidata)       ┌─────────────────┐
 │ MLflow Tracking │────────────────────────────────────────────────►│  MODEL REGISTRY │
 └─────────────────┘                                                 └────────┬────────┘
                                                                              │
                                                                              │ (3. Webhook de Novo Registro)
                                                                              ▼
 ┌─────────────────┐       (5. Aprovado: Promove a @champion)       ┌─────────────────┐
 │  Deployment     │◄───────────────────────────────────────────────│ Quality Gates / │
 │ Contínuo (CD)   │                                                │ CI/CD Pipeline  │
 └────────┬────────┘                                                └─────────────────┘
          │ (6. Pull do @champion)
          ▼
 ┌─────────────────┐       (7. Métricas de Inferência + Version ID) ┌─────────────────┐
 │ Serving Engine  │───────────────────────────────────────────────►│ Observabilidade │
 │ (FastAPI/vLLM)  │                                                │ (Grafana/Prom)  │
 └─────────────────┘                                                └─────────────────┘
```

### O Fluxo Automatizado Ponta a Ponta

1. **Continuous Training (CT)**: Um pipeline automatizado (disparado por novos dados ou agendamento) treina um novo modelo e registra o artefato no Model Registry com o estado de candidato.
2. **Quality Gates & Avaliação Automatizada**: O registro dispara um pipeline de CI/CD (via Webhook). O pipeline executa testes automatizados no modelo:
   - *Testes Unitários de Código e Assinatura*.
   - *Testes de Regressão*: O candidato supera o modelo atual (`@champion`) no dataset de validação?
   - *Testes de Estresse de Latência*: O modelo respeita o SLA de inferência (p99 < 50ms)?
   - *Testes de Viés e Alucinação*.
3. **Promoção Automática ou Human-in-the-Loop**: Se o modelo passar em todas as etapas, o pipeline atribui o alias `@champion` à nova versão (ou envia um alerta no Slack para aprovação final de um especialista).
4. **Continuous Deployment (CD)**: A alteração do alias `@champion` dispara o redeploy dos pods de inferência ou faz um *rolling update* no cluster Kubernetes (KServe/BentoML/vLLM).
5. **Observabilidade e Fechamento do Loop**: As métricas de inferência em produção (Prometheus, Grafana, OpenTelemetry) registram cada predição etiquetada com o `model_version_id` extraído do Registry. Se a observabilidade detectar um pico de anomalias (Aula 11), um script de emergência reverte o alias `@champion` para a versão anterior em segundos!

---

## 🧭 Como Escolher? (Árvore de Decisão)

```text
Sua equipe precisa gerenciar artefatos de ML/LLM em produção?
├── NÃO
│   └── S3 / GCS + Git simples atendem protótipos de pesquisa pura.
└── SIM
    ├── Qual é o ecossistema de nuvem dominante?
    │   ├── 100% AWS com exigência estrita de IAM/Compliance?
    │   │   └── AWS SageMaker Model Registry
    │   ├── 100% Databricks Lakehouse?
    │   │   └── Databricks Unity Catalog (MLflow nativo)
    │   └── Multi-nuvem / On-premises / Cloud agnóstico?
    │       ├── Equipe prioriza cultura GitOps / Controle via Git?
    │       │   └── DVC + DVC Studio / Dagshub
    │       ├── Equipe busca a melhor DX visual e gráficos de artefatos?
    │       │   └── Weights & Biases (W&B Models)
    │       └── Busca o padrão open-source da indústria, sem lock-in?
    │           └── MLflow Model Registry (Self-hosted ou Managed)
```

---

## 📊 Casos de Uso Práticos

### Caso 1: Detecção de Fraude em Cartão de Crédito (Fintech)

- **Cenário**: Modelo de classificação de alto risco que toma decisões financeiras em milissegundos. Exigência estrita de auditoria pelo Banco Central.
- **Arquitetura de Registry**: MLflow / SageMaker Registry com controle de acesso RBAC e assinaturas criptográficas SHA-256.
- **Workflow**: O pipeline de CT roda semanalmente. Modelos candidatos são testados em ambiente de *Shadow Deployment* (recebem tráfego real em paralelo sem responder ao cliente). Se o modelo candidato demonstrar maior F1-Score sem aumentar a latência p99, o engenheiro de MLOps assina digitalmente a promoção para `@champion`.

### Caso 2: Sistema de Recomendação de E-Commerce (Continuous Training)

- **Cenário**: Retreino diário com milhões de interações de usuários.
- **Arquitetura de Registry**: Databricks Unity Catalog + MLflow com Webhooks automatizados.
- **Workflow**: O treino automatizado gera uma nova versão do modelo todas as noites. Um pipeline de testes A/B atribui o alias `@challenger` à nova versão e direciona 5% do tráfego. Se a taxa de conversão do `@challenger` for superior à do `@champion` por 24 horas consecutivas, o alias `@champion` é atualizado automaticamente via script.

### Caso 3: Fine-Tuning de LLM para Atendimento Jurídico

- **Cenário**: Modelo Llama-3 8B adaptado com LoRA para sintetizar peças processuais jurídicas.
- **Arquitetura de Registry**: W&B Models / MLflow 2.x+.
- **Workflow**: O registrador armazena o arquivo do adaptador LoRA (`.safetensors`, 40MB), o repositório de prompts versionado e o relatório de avaliação gerado pelo *LLM-as-a-Judge*. O servidor vLLM carrega o modelo base uma única vez na GPU e injeta dinamicamente o adaptador LoRA correspondente ao alias `@champion` informado na requisição da API.

### Caso 4: Visão Computacional em Borda (Inspeção Industrial)

- **Cenário**: Modelo YOLO para detecção de defeitos em linhas de montagem de fábricas, rodando em dispositivos NVIDIA Jetson Edge.
- **Arquitetura de Registry**: DVC + MLflow com suporte a múltiplos alvos de compilação.
- **Workflow**: O Model Registry armazena o modelo treinado em PyTorch e seus binários compilados em TensorRT (FP16 e INT8). As câmeras de borda checam a API do Registry periodicamente: quando uma nova versão compilada para o chip Jetson recebe a tag `@edge-approved`, o dispositivo faz o download seguro do binário e atualiza a inferência local.

---

## 🧪 Atividade Prática (Visão Geral)

Para consolidar os conceitos desta aula, a atividade prática (disponível no diretório da aula) guia os alunos na implementação de um fluxo completo de Model Registry:

1. **Configuração do Servidor de Registro**: Inicialização do servidor MLflow local com backend de metadados em SQLite e armazenamento de artefatos em diretório local.
2. **Treinamento & Registro**: Treinamento de duas versões de um modelo de Machine Learning, registrando parâmetros, métricas e a assinatura dos dados.
3. **Gestão de Aliases**: Atribuição inicial do alias `@champion` à versão 1 e promoção posterior para a versão 2 após validação automatizada.
4. **Consumo Dinâmico em API**: Construção de um microsserviço FastAPI que carrega a versão do modelo através do URI dinâmico `models:/MeuModelo@champion`, demonstrando o consumo desacoplado em produção.

---

## 💬 Pontos para Reflexão Pré-Aula

Ao estudar este material, reflita sobre as seguintes questões para enriquecer a discussão em sala:

1. **Por que armazenar um modelo no S3 e salvar o caminho no Git não é suficiente para caracterizar um Model Registry?** Que metadados críticos ficam faltando?
2. **Qual é a vantagem operacional de utilizar Aliases mutáveis (`@champion`) em vez de alterar o código-fonte da aplicação de inferência a cada novo deploy?**
3. **Em um cenário de retreino automático diário (Continuous Training), o que acontece se o novo modelo treinado tiver um desempenho pior que o atual?** Como o Model Registry e os Quality Gates impedem a degradação em produção?
4. **Como o Model Registry lida com a imutabilidade de artefatos?** Por que nunca devemos sobrescrever uma versão registrada?
5. **Na era dos LLMs, por que registrar apenas os pesos de um adaptador LoRA é mais eficiente do que registrar o modelo completo de 70B parâmetros?**
6. **Qual a diferença entre a função do MLflow Tracking e a do MLflow Model Registry?** Por que nem todo experimento logado no Tracking deve ser promovido para o Registry?
7. **Como a observabilidade em produção (Aula 11) se conecta ao Model Registry durante uma crise de degradação de modelo?** Como funciona o procedimento de rollback?
8. **Quais são os trade-offs entre adotar um Model Registry Open Source (MLflow) vs. uma solução totalmente gerenciada pela nuvem (AWS SageMaker / Databricks Unity Catalog)?**

---

## 📚 Referências

### Artigos e Publicações Acadêmicas

1. **Sculley, D. et al. (2015).** *Hidden Technical Debt in Machine Learning Systems*. Advances in Neural Information Processing Systems (NeurIPS 2015). — [https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems.pdf](https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems.pdf)
2. **Zaharia, M. et al. (2018).** *Accelerating the Machine Learning Lifecycle with MLflow*. IEEE Data Engineering Bulletin. — [https://www.databricks.com/blog/2018/06/05/introducing-mlflow-an-open-source-machine-learning-platform.html](https://www.databricks.com/blog/2018/06/05/introducing-mlflow-an-open-source-machine-learning-platform.html)
3. **Polyzotis, N. et al. (2017).** *Data Management Challenges in Production Machine Learning*. SIGMOD 2017.
4. **Kreuzberger, D. et al. (2023).** *Machine Learning Operations (MLOps): Overview, Definition, and Architecture*. IEEE Access. — [https://arxiv.org/abs/2205.02302](https://arxiv.org/abs/2205.02302)

### Documentação Oficial

5. **MLflow Model Registry Documentation** — [https://mlflow.org/docs/latest/model-registry.html](https://mlflow.org/docs/latest/model-registry.html)
6. **Weights & Biases Models & Artifacts Guide** — [https://docs.wandb.ai/guides/models](https://docs.wandb.ai/guides/models)
7. **AWS SageMaker Model Registry Developer Guide** — [https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html](https://docs.aws.amazon.com/sagemaker/latest/dg/model-registry.html)
8. **Databricks Unity Catalog AI Governance & Model Registry** — [https://docs.databricks.com/en/data-governance/unity-catalog/index.html](https://docs.databricks.com/en/data-governance/unity-catalog/index.html)
9. **Google Cloud Vertex AI Model Registry** — [https://cloud.google.com/vertex-ai/docs/model-registry/introduction](https://cloud.google.com/vertex-ai/docs/model-registry/introduction)

### Livros e Guias da Indústria (2024–2026)

10. **Huyen, Chip (2025).** *AI Engineering: Building Applications with Foundation Models*. O'Reilly Media. (Capítulos de Model Governance e Management).
11. **Treveil, M. et al. (Dataiku) (2020).** *Introducing MLOps: How to Scale Machine Learning in the Enterprise*. O'Reilly Media.
12. **Google Cloud MLOps Architecture Guide** — [https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

---

## 🔗 Conexões com Outras Aulas

Este conteúdo conecta-se diretamente com o ecossistema do curso de MLOps:

- **Aula 04 (Containers e Docker)**: O Model Registry registra e expõe as dependências necessárias para construir a imagem Docker do container de inferência.
- **Aula 11 (Logging, Monitoramento e Observabilidade)**: As métricas de inferência coletadas pelo Prometheus/Grafana carregam o identificador da versão do Model Registry, viabilizando detecção de drift e rollback.
- **Aula 12 (Kubernetes)**: Orquestração de clusters de inferência que sobem réplicas atualizadas sempre que o alias `@champion` é promovido no Model Registry.
- **Aula 18 (Feature Store e Data Management)**: O Model Registry faz o vínculo biunívoco entre a versão dos dados na Feature Store e a versão dos pesos treinados.
- **Aula 21 (Servindo Modelos Pesados - Triton/BentoML)**: As engines especializadas em servir modelos pesados consomem diretamente as versões apontadas pelo alias `@champion` mantido pelo Model Registry.

---

🚀 **Estudo prévio concluído? Prepare suas dúvidas sobre governança, aliasing, CI/CD/CT e LLMOps para debatermos durante nosso encontro!**