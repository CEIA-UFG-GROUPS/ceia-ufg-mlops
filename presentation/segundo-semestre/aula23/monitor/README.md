# 📘 Aula 23 — Monitoramento e Drift (Evidently AI)

## Material de Estudo Prévio

Este material tem como objetivo **preparar para a aula de Monitoramento e Drift em MLOps**, oferecendo uma base conceitual e prática sólida para acompanhar, complementar e aprofundar a discussão conduzida pelo apresentador.

⚠️ **Este conteúdo não é um guia de instruções**, mas sim um **material de estudo prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do CEIA/UFG.

---

## 🎯 Objetivo da Aula

Ao final desta aula, espera-se que os participantes compreendam:

- A diferença fundamental entre **observabilidade de infraestrutura tradicional (APM)** e **observabilidade de modelos de Machine Learning (ML Observability)**.
- O conceito de **falha silenciosa (*silent failure*)** e por que respostas `HTTP 200 OK` com baixa latência não garantem que um modelo esteja tomando decisões corretas.
- As 3 dimensões de degradação em MLOps: **Covariate Shift ($P(X)$)**, **Concept Shift ($P(Y|X)$)** e **Prior Probability / Label Shift ($P(Y)$)**.
- Os principais métodos de detecção estatística (**KS-Test**, **PSI**, **Wasserstein/EMD**, **Jensen-Shannon**, **Chi-Square**) e como interpretar seus resultados no Evidently AI.
- A arquitetura e funcionamento interno da biblioteca **Evidently AI**: abstrações de *Reports*, *Test Suites*, *Presets* e *Collectors*.
- O monitoramento de **LLMs e GenAI**: detecção de *drift* em embeddings (espaço latente), métricas de RAG (*Faithfulness*, *Context Precision*, *Answer Relevance*) e avaliação via *LLM-as-a-Judge*.
- A integração da observabilidade com o ciclo MLOps: **Continuous Training (CT)** acionado por alertas de *drift* integrados ao **Model Registry** e à **Feature Store**.

---

## 🧠 Contexto: O que é e por que precisamos de Observabilidade em ML?

### O Anti-Pattern: O Mito do *Deploy & Forget* e o APM Tradicional

Na engenharia de software tradicional, o comportamento de um sistema é puramente determinístico e governado pelas regras lógicas do código. Ferramentas de *Application Performance Monitoring* (APM) como Prometheus, Grafana, Datadog ou Dynatrace foram projetadas para monitorar a infraestrutura:

```text
┌─────────────────────────────────────────────────────────────────┐
│              OBSERVABILIDADE TRADICIONAL DE TI (APM)            │
├─────────────────────────────────────────────────────────────────┤
│ • CPU / GPU Usage (%)       • Latência p95 / p99 (ms)           │
│ • Consumo de Memória (RAM)  • Taxa de Erros HTTP (4xx / 5xx)    │
│ • Vazão (Requests / sec)    • Uptime / Availability (SLA/SLO)   │
└─────────────────────────────────────────────────────────────────┘
```

Em Machine Learning, o desempenho do sistema depende criticamente dos **dados do mundo real**, que mudam ao longo do tempo. O modelo degrada naturalmente mesmo sem nenhuma alteração no código. Esse fenômeno é a **Degradação de Modelo (*Model Decay*)**.

### As 3 Fases de Falha: Software Bug vs Data Drift vs Concept Drift

| Tipo de Falha | O que acontece? | Como o APM tradicional reage? | Como a observabilidade de ML reage? |
|---|---|---|---|
| **Software Bug / Infra** | Exceção não tratada, estouro de memória (OOM), servidor inoperante. | 🚨 **Alerta Máximo**: Dispara alarmes de HTTP 500, pod caindo, uso de CPU em 100%. | Captura a falha na camada de serviço REST/gRPC. |
| **Data Drift (Covariate Shift)** | Os dados de entrada dos usuários mudaram de perfil (ex.: novo público, nova região). | 🟢 **Verde (Falso OK)**: O container responde HTTP 200 OK em 12ms. | 🚨 **Alerta de Drift**: Detecta alteração na distribuição estatística de entrada $P(X)$. |
| **Concept Drift** | A relação entre a entrada e o mundo real mudou (ex.: crise financeira, pandemia). | 🟢 **Verde (Falso OK)**: O sistema opera com perfeita estabilidade de infraestrutura. | 🚨 **Alerta de Performance**: Detecta queda na acurácia/F1 quando o *ground truth* chega. |

---

## ⚙️ Conceitos Fundamentais de Drift

### Fatoração de Probabilidade e Tipos de Desvio

Considere $X$ como os atributos de entrada (*features*) e $Y$ como a variável alvo (*target*). A relação entre dados e predições é dividida em três formas de desvio (*shift*):

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                          TAXONOMIA FORMAL DO DRIFT                          │
├─────────────────────────────────────────────────────────────────────────────┤
│ 1. Covariate Shift (Data Drift):  Distribuição de entrada P(X) muda.        │
│    (Ex.: perfil do público muda, mas as regras de negócio permanecem)       │
├─────────────────────────────────────────────────────────────────────────────┤
│ 2. Concept Shift (Concept Drift): Relação P(Y|X) entre entrada e alvo muda. │
│    (Ex.: mesmo perfil de cliente passa a ter comportamento de compra oposto)│
├─────────────────────────────────────────────────────────────────────────────┤
│ 3. Label Shift (Prior Shift):     Distribuição do alvo P(Y) muda.           │
│    (Ex.: aumento global na proporção de fraudes na indústria)               │
├─────────────────────────────────────────────────────────────────────────────┤
│ 4. Upstream Data Quality:         Erros de pipeline e eng. de dados.        │
│    (Ex.: campos nulos, mudança de tipos, falhas em APIs de terceiros)       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### Entendendo os Testes Estatísticos de Forma Prática

Para identificar se a distribuição dos dados recentes de produção (*Current*) divergiu do conjunto de referência (*Reference/Treino*), o Evidently AI aplica testes estatísticos automáticos. Abaixo está a explicação prática de cada um:

```text
                  ┌────────────────────────────────────────────────────────┐
                  │              SELEÇÃO DE TESTES ESTATÍSTICOS            │
                  └───────────────────────────┬────────────────────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼                                                   ▼
         [ Variáveis Contínuas ]                             [ Variáveis Categóricas ]
        ┌───────────┴───────────┐                           ┌───────────┴───────────┐
        ▼                       ▼                           ▼                       ▼
 Amostras Pequenas       Amostras Grandes            Poucas Categorias       Muitas Categorias
  (< 10.000 obs)          (≥ 10.000 obs)               (< 20 níveis)           (≥ 20 níveis)
┌───────────────┐       ┌───────────────┐           ┌───────────────┐       ┌───────────────┐
│ Kolmogorov-   │       │ Wasserstein / │           │ Teste Qui-    │       │ Divergência   │
│ Smirnov (KS)  │       │ EMD ou PSI    │           │ Quadrado (χ²) │       │ Jensen-Shannon│
└───────────────┘       └───────────────┘           └───────────────┘       └───────────────┘
```

#### 1. Teste Kolmogorov-Smirnov (KS-Test)
- **O que mede**: A maior distância vertical entre as curvas de distribuição acumulada dos dois conjuntos de dados.
- **Quando usar**: Variáveis numéricas contínuas com amostras pequenas ou médias (< 10.000 observações).
- **Como interpretar no Evidently AI**: Retorna um valor $p\text{-value}$. Se $p\text{-value} < 0.05$, a hipótese de que as distribuições são iguais é rejeitada $\rightarrow$ **Drift Detectado**.

#### 2. Population Stability Index (PSI)
- **O que mede**: O deslocamento percentual de observações entre faixas (*bins*) de valores. É a métrica padrão da indústria bancária e financeira.
- **Quando usar**: Variáveis numéricas ou pontuações de crédito em grandes volumes de dados.
- **Regra Prática de Interpretação**:
  - $PSI < 0.10$: Sem alteração significativa (**Normal**).
  - $0.10 \le PSI < 0.25$: Alteração moderada (**Atenção / Alerta Amarelo**).
  - $PSI \ge 0.25$: Alteração severa (**Drift Crítico / Re-treinamento Necessário**).

#### 3. Distância de Wasserstein (Earth Mover's Distance - EMD)
- **O que mede**: O "trabalho mínimo" necessário para transformar uma distribuição de probabilidade na outra.
- **Quando usar**: Amostras contínuas muito grandes (onde o $p\text{-value}$ do teste KS tende a acusar falso positivo muito facilmente devido ao alto volume).
- **Como interpretar no Evidently AI**: Fornece uma distância na mesma escala da variável (ex.: se a variável é renda em reais, um EMD de R$ 500 indica desvio médio dessa magnitude).

#### 4. Divergência de Jensen-Shannon (JS Divergence)
- **O que mede**: A diferença de informação entre duas distribuições. É uma versão simétrica e limitada entre 0 e 1 da Divergência KL.
- **Quando usar**: Variáveis categóricas com muitas categorias (alta cardinalidade) ou probabilidade de classes.
- **Como interpretar no Evidently AI**: Valores próximos de 0 indicam distribuições idênticas; valores acima do limiar (ex.: $> 0.1$) indicam *drift*.

#### 5. Teste Qui-Quadrado ($\chi^2$)
- **O que mede**: A diferença entre as frequências observadas na produção e as frequências esperadas com base no treino.
- **Quando usar**: Variáveis categóricas com poucas categorias (ex.: estado civil, tipo de dispositivo).
- **Como interpretar no Evidently AI**: Retorna um $p\text{-value}$. Se $p\text{-value} < 0.05$ $\rightarrow$ **Drift Categórico Detectado**.

---

## 🛠️ Arquitetura e Funcionamento do Evidently AI

O **Evidently AI** organiza o monitoramento em abstrações simples e declarativas:

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          EVIDENTLY AI ARCHITECTURE                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 1. ColumnMapping: Mapeia a semântica (target, prediction, numerical, text)      │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 2. Metrics & Presets: Métricas individuais (ex.: DataDriftPreset, QualityPreset)│
├─────────────────────────────────────────────────────────────────────────────────┤
│ 3. Execution Objects:                                                           │
│    ├── Report -> Análise Exploratória Visual em Dashboard HTML / JSON           │
│    └── TestSuite -> Regras determinísticas (Pass/Fail) para automação CI/CD     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 4. Collectors & Exporters: Exportador Prometheus para Grafana e Evidently Cloud │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Monitoramento de LLMs e GenAI

O monitoramento de aplicações com Grandes Modelos de Linguagem (LLMs) e RAG exige olhar para dados textuais não-estruturados:

### 1. Embedded Space Drift (Drift no Espaço Latente)
Textos são convertidos em vetores densos (embeddings). O Evidently AI avalia se o domínio das perguntas mudou medindo a **Distância Coseno dos Centroides** ou aplicandos testes de *Maximum Mean Discrepancy* (MMD) no vetor latente.

### 2. Métricas de RAG (RAG Triad)
- **Context Precision**: Os documentos recuperados do banco vetorial são relevantes para a pergunta?
- **Faithfulness (Fidelidade / Anti-Alucinação)**: A resposta gerada é fundamentada exclusivamente no contexto recuperado?
- **Answer Relevance**: A resposta atende diretamente à necessidade do usuário?

### 3. Text Descriptors
Extração de atributos numéricos a partir do texto para monitoramento univariado: tamanho da resposta, pontuação de sentimento, toxicidade e taxa de palavras fora do vocabulário (OOV).

---

## 🌐 Conexão do Monitoramento com o Ciclo MLOps (CI/CD/CT)

O monitoramento atua como o **gatilho de retroalimentação** no ciclo de vida automatizado:

```text
 ┌─────────────────┐       (1. Logs de Inferência)       ┌─────────────────┐
 │ Serving API     │────────────────────────────────────►│ Storage / Logs  │
 │ (FastAPI/vLLM)  │                                     │ (S3 / Parquet)  │
 └─────────────────┘                                     └────────┬────────┘
          ▲                                                       │
          │ (6. Deploy do Novo Champion)                          │ (2. Leitura de Janela)
          │                                                       ▼
 ┌────────┴────────┐       (5. Promoção @champion)       ┌─────────────────┐
 │  MODEL REGISTRY │◄────────────────────────────────────│  EVIDENTLY AI   │
 │ (MLflow/Unity)  │                                     │ MONITOR WORKER  │
 └─────────────────┘                                     └────────┬────────┘
          ▲                                                       │
          │ (4. Registra Modelo Retreinado)                       │ (3. Alerta de Drift)
 ┌────────┴────────┐                                              ▼
 │ Continuous      │◄────────────────────────────────────┌─────────────────┐
 │ Training (CT)   │          (Dispara Pipeline)         │ Orchestrator /  │
 └─────────────────┘                                     │ Airflow / K8s   │
                                                         └─────────────────┘
```

---

## 🧭 Árvore de Decisão & Comparativo

| Característica | Evidently AI | Deepchecks | Great Expectations | Arize AI / WhyLabs |
|---|---|---|---|---|
| **Foco Principal** | Observabilidade de ML, Drift & LLM | Testes unitários & validação de pipeline | Qualidade e governança de ETL | Observabilidade SaaS Enterprise |
| **Interface Visual** | HTML nativo + Dashboard UI | HTML local + Cloud Dashboard | Data Docs em HTML | Cloud Dashboard completo |
| **Suporte a LLMs / RAG** | Excelente (Descriptors, RAG Evals) | Moderado | Limitado (Foco em dados estruturados) | Excelente |
| **Exportador Prometheus** | Sim (`/metrics` nativo) | Não | Não | Via agentes proprietários |
| **Licenciamento** | Open Source (Apache 2.0) | Open Source (AGPL) | Open Source (Apache 2.0) | Proprietário SaaS |

---

## 📊 Casos de Uso Práticos

1. **Fintech (Crédito)**: Deslocamento no perfil financeiro dos clientes ($PSI = 0.32$ no atributo renda) aciona o retreinamento automatizado com dados recentes da Feature Store.
2. **E-Commerce (Black Friday)**: *Concept Drift* repentino por sazonalidade altera os itens recomendados. O monitoramento identifica a variação e comuta o modelo para uma regra de *Trending Items*.
3. **GenAI Jurídico/Saúde**: Queda no score de *Faithfulness* (< 0.85) em respostas do LLM alerta os engenheiros para atualizar a base vetorial com dados normativos recentes.

---

## 🧪 Atividade Prática

Para consolidar os conceitos desta aula, acesse o diretório da atividade prática:
👉 [Atividade Prática em Docker](./atividade/README.md)

Nesta atividade, você irá executar:
1. Geração de datasets de referência e produção com *Data Drift* e *Concept Drift* simulados.
2. Geração de relatórios visuais HTML e suítes de teste automatizadas com Evidently AI.
3. Avaliação de qualidade e *drift* de texto em cenários de LLM.
4. Simulação de um pipeline de monitoramento em tempo real com emissão de alertas.

---

## 💬 Pontos para Reflexão Pré-Aula

1. Por que responder `HTTP 200 OK` em 10ms não garante que o modelo de IA esteja correto em produção?
2. Se o resultado real (*ground truth*) demora meses para chegar (ex.: inadimplência), por que monitorar o *Data Drift* de entrada $P(X)$ é vital?
3. Qual é o risco de manter o mesmo dataset de referência (*baseline*) por anos sem atualização?
4. Qual a diferença prática entre *Covariate Shift* (mudança na entrada) e *Concept Shift* (mudança na regra do mundo real)?
5. Como os alertas do Evidently AI se integram ao Model Registry para promover automaticamente novos modelos?

---

## 📚 Referências

1. **Gama, J. et al. (2014).** *A survey on concept drift adaptation*. ACM Computing Surveys.
2. **Lu, J. et al. (2018).** *Learning under concept drift: A review*. IEEE TKDE.
3. **Rabanser, S. et al. (2019).** *Failing Loudly: An Empirical Study of Methods for Detecting Dataset Shift*. NeurIPS.
4. **Evidently AI Documentation** — [https://docs.evidentlyai.com/](https://docs.evidentlyai.com/)
5. **Huyen, Chip (2025).** *AI Engineering: Building Applications with Foundation Models*. O'Reilly Media.

---

## 🔗 Conexões com Outras Aulas

- **Aula 11 (Logging e Observabilidade)**: Extensão da observabilidade de TI para métricas de ML.
- **Aula 18 (Feature Store)**: Fonte unificada de dados de treino (referência) e produção.
- **Aula 19 (Model Registry)**: Registro e versionamento do modelo re-treinado pós-alerta de drift.
- **Aula 22 (Pipelines CI/CD/CT)**: Gatilho automatizado para pipelines de retreinamento contínuo.