# Monitoramento e Drift (Evidently AI)

Este documento organiza a apresentação da aula e serve como **guia conceitual** para o expositor.
A estrutura abaixo é uma sugestão a ser seguida para garantir clareza, progressão lógica e alinhamento com o grupo.

> 💡 **Fluxo sugerido**: começar desconstruindo o mito do "deploy and forget" em Inteligência Artificial, demonstrando a diferença fundamental entre uma falha de software tradicional (crash, HTTP 500, estouro de memória) e a **falha silenciosa (*silent failure*)** de um modelo de Machine Learning (onde o código responde HTTP 200 OK em 10ms, mas prevê respostas completamente erradas devido a alterações no mundo real). Evoluir a discussão explicando as dimensões formais do *Drift* (*Covariate Shift*, *Concept Shift*, *Prior Probability Shift* e *Upstream Data Quality*), introduzir os testes estatísticos de detecção ($\text{KS-Test}$, $\text{PSI}$, $\text{Wasserstein/EMD}$, $\chi^2$), e demonstrar a aplicação prática com a ferramenta **Evidently AI**, conectando o monitoramento de dados tabulares e LLMs à observabilidade em malha fechada (*Continuous Training* - CT).

---

## 1️⃣ Motivação

### 1.1 O mito do "deploy and forget": Por que APM tradicional não detecta degradação de IA?

- **O falso sentimento de segurança**: Ferramentas tradicionais de Application Performance Monitoring (APM), como Datadog, Dynatrace, New Relic ou Prometheus/Grafana voltados à infraestrutura, monitoram métricas de TI: uso de CPU/GPU, consumo de RAM, latência de rede p95/p99 e taxa de erros HTTP (4xx/5xx).
- **Por que a infraestrutura verde esconde um modelo falhando**: Um microsserviço de inferência pode estar operando com 99,99% de *uptime*, respondendo em 15 milissegundos com código `200 OK`, enquanto suas predições financeiras ou diagnósticos médicos tornam-se inفسidadis por completo.
- **Diferença fundamental entre Erro de Engenharia e Erro de Modelo**:
  - *Software Bug*: O código lança uma exceção, quebra a pilha de execução ou encerra o processo.
  - *Model Decay*: O modelo calcula saídas matematicamente válidas a partir de entradas válidas, mas a premissa estatística sobre a qual o modelo foi treinado deixou de existir.

### 1.2 A falha silenciosa (*Silent Failure*) e as dimensões da degradação

- **Degradação de Desempenho (*Concept Drift*)**: A relação estatística entre os atributos de entrada ($X$) e a variável alvo ($Y$) se altera ao longo do tempo. O modelo perde precisão sem que as variáveis de entrada tenham necessariamente mudado sua faixa de valores.
- **Mudança na Distribuição de Entrada (*Data Drift / Covariate Shift*)**: A distribuição dos dados de produção $P(X)$ diverge da distribuição dos dados de treinamento $P_{ref}(X)$.
- **Anomalias de Pipeline (*Upstream Data Quality*)**: Mudanças de esquema no banco de dados, falhas de scraping, alteração de unidade de medida (ex.: Celsius para Fahrenheit), bugs no código do aplicativo mobile ou valores *null* introduzidos por atualizações de software upstream.

### 1.3 Impacto de negócio, governança e compliance

- **Prejuízo Financeiro e Operacional**: Modelos de concessão de crédito, precificação dinâmica ou detecção de fraude degradados podem gerar perdas milionárias em poucos dias de operação desajustada.
- **Risco Regulatório e Auditoria**: Regulamentações como o **EU AI Act**, LGPD e diretrizes do Banco Central (BACEN) exigem monitoramento contínuo da qualidade dos dados e viés de modelos que tomam decisões automatizadas com impacto social.
- **Atraso no *Ground Truth* (Rótulos)**: Em muitos cenários reais (ex.: inadimplência bancária em 90 dias, churn de clientes em 6 meses, diagnóstico de saúde), o rótulo real ($Y$) demora meses para ser conhecido. O monitoramento de **Data Drift em $X$** torna-se o único sistema de alarme antecipado (*early warning system*) viável antes que a métrica de desempenho real possa ser calculada.

---

## 2️⃣ Como Funciona

### 2.1 Anatomia do Monitoramento de ML: Reference Data vs Current Data

O monitoramento estatístico de dados baseia-se na comparação entre dois conjuntos de dados:

```text
┌─────────────────────────────────────────────────────────────────┐
│                      EVIDENTLY MONITORING ENGINE                │
├─────────────────────────────────────────────────────────────────┤
│ 1. Reference Dataset (Baseline - Treino / Validação Aprovada)   │
│    - Distribuição P_ref(X), Histórico de Features, Métricas     │
├─────────────────────────────────────────────────────────────────┤
│ 2. Current Dataset (Produção - Inferências da Janela Recente)   │
│    - Distribuição P_curr(X), Produção real das últimas N horas  │
├─────────────────────────────────────────────────────────────────┤
│ 3. Statistical Testing Engine (KS, PSI, Wasserstein, Chi-Sq)    │
│    - Cálculo de p-values, Scores de Drift e Alertas Automatizados│
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Taxonomia Formal do Drift

Seja $X$ o vetor de atributos (*features*) e $Y$ a variável alvo (*target*). A distribuição conjunta de probabilidade é dada por $P(X, Y) = P(X) \cdot P(Y|X) = P(Y) \cdot P(X|Y)$.

1. **Covariate Shift (Data Drift)**:
   $$\Delta P(X) \neq 0 \quad \text{enquanto} \quad P(Y|X) \text{ permanece constante}$$
   *Exemplo*: Uma fintech expande sua operação para uma nova região geográfica. O perfil dos clientes ($X$) muda, mas o critério básico de inadimplência dado o perfil ($P(Y|X)$) continua o mesmo.

2. **Concept Shift (Concept Drift)**:
   $$\Delta P(Y|X) \neq 0 \quad \text{enquanto} \quad P(X) \text{ pode ou não mudar}$$
   *Exemplo*: Durante uma crise econômica repentina ou pandemia, clientes com a mesma renda e histórico ($X$) passam a ter comportamentos de pagamento ($Y$) totalmente diferentes.

3. **Prior Probability Shift (Label Shift)**:
   $$\Delta P(Y) \neq 0 \quad \text{enquanto} \quad P(X|Y) \text{ permanece constante}$$
   *Exemplo*: Mudança na proporção global de transações fraudulentas devido a uma fraude em massa coordenada na indústria.

4. **Upstream Data Quality**:
   Alterações estruturais na coleta ou pré-processamento (tipos de dados corrompidos, desvio de formato de data, perda de cardinalidade).

### 2.3 Matriz de Comparação de Ferramentas de Observabilidade de ML

| Ferramenta | Tipo | Ponto Forte | Melhor Uso |
|---|---|---|---|
| **Evidently AI** | Open Source / Cloud | Abstração completa de *Reports*, *Test Suites*, suporte a Tabular, Texto e LLMs, exportador Prometheus nativo | Monitoramento flexível em Python, dashboards estáticos HTML, integração com Kubernetes, Grafana e CI/CD |
| **Deepchecks** | Open Source / Cloud | Foco em suítes formais de testes (*Validation Suites*) para pré-treino, pós-treino e produção | Validação automatizada de dados em pipelines de CI/CD e testes unitários de ML |
| **Great Expectations** | Open Source / Cloud | Validação rigorosa de esquemas, expectativas e qualidade de dados de entrada | Governança de pipelines de ETL/ELT e Data Engineering |
| **Arize AI / WhyLabs** | Enterprise SaaS | Observabilidade de produção em escala enterprise, busca em vetores e rastreamento de LLMs | Empresas corporativas buscando plataforma SaaS totalmente gerenciada sem infraestrutura própria |
| **AWS SageMaker Model Monitor** | Cloud Native (AWS) | Integração nativa com endpoints SageMaker e triggers via CloudWatch e EventBridge | Infraestrutura 100% AWS que consome dados de inferência do S3 |

### 2.4 Monitoramento e Drift na Era dos LLMs e GenAI

O monitoramento de Aplicações com LLM e RAG (Retrieval-Augmented Generation) exige novas abordagens estatísticas e semânticas:

- **Data Drift em Embeddings (Latent Space Drift)**: Modelos de linguagem convertem texto não-estruturado em vetores de alta dimensão. O drift de dados é avaliado medindo a distância entre distribuições no espaço latente utilizando **Maximum Mean Discrepancy (MMD)**, **Cosine Distance Drift** ou redução de dimensionalidade (PCA/UMAP) seguida de testes univariados.
- **Métricas de RAG (Retrieval & Generation)**:
  - *Context Precision & Recall*: Qualidade dos documentos recuperados da Vector Database.
  - *Faithfulness (Fidelidade)*: Se a resposta gerada é estritamente fundamentada no contexto recuperado (detecção de alucinação).
  - *Answer Relevance*: Se a resposta gerada atende diretamente à intenção do usuário.
- **Drift de Prompts e Respostas**: Monitoramento de tamanho de resposta, toxicidade, sentimento, *refusal rate* (taxa de recusa) e custo de tokens.
- **LLM-as-a-Judge**: Utilização de modelos auxiliares (ex.: GPT-4o, Claude 3.5 Sonnet ou modelos locais menores) para classificar programmaticamente a qualidade e segurança da saída gerada.

---

## 3️⃣ Quickstart & Demos (Evidently AI)

> 💡 **Instruções para ao vivo**: As demos a seguir utilizam o pacote `evidently` (`pip install evidently pandas scikit-learn`).

### 3.1 Demo 1 — Evidently AI: Gerando Data Drift Report e Test Suites em Python

Mostrar a criação simples de um relatório visual em HTML e de uma suíte de testes automatizada para comparar dados de referência com dados correntes:

```python
import pandas as pd
import numpy as np
from sklearn.datasets import fetch_california_housing

from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.test_suite import TestSuite
from evidently.tests import TestNumberOfColumns, TestShareOfDriftedColumns

# 1. Carregar dados de exemplo e dividir em Reference (Baseline) e Current (Produção)
data = fetch_california_housing(as_frame=True).frame
reference_data = data.sample(n=5000, random_state=42)
current_data = data.drop(reference_data.index).sample(n=5000, random_state=101)

# Simular Data Drift artificialmente na feature 'MedInc' (Renda Médian)
current_data['MedInc'] = current_data['MedInc'] * 1.45

# 2. Criar e executar um Report visual
drift_report = Report(metrics=[
    DataDriftPreset(),
    DataQualityPreset()
])
drift_report.run(reference_data=reference_data, current_data=current_data)
drift_report.save_html("data_drift_report.html")

# 3. Criar uma Test Suite automatizada para integração CI/CD
data_drift_suite = TestSuite(tests=[
    TestNumberOfColumns(),
    TestShareOfDriftedColumns(lt=0.3) # Alerta se mais de 30% das features tiverem drift
])
data_drift_suite.run(reference_data=reference_data, current_data=current_data)

if not data_drift_suite.as_dict()["summary"]["all_passed"]:
    print("⚠️ ALERTA DE MLOPS: Drift excessivo detectado no conjunto de dados!")
else:
    print("✅ Dados dentro dos parâmetros estatísticos aceitáveis.")
```

### 3.2 Demo 2 — Detecção de Concept Drift & Performance com Ground Truth Atrasado

Demonstrar como avaliar métricas de regressão/classificação quando os rótulos reais chegam ao sistema:

```python
from evidently.metric_preset import ClassificationPreset
from sklearn.ensemble import RandomForestClassifier

# Simular treino de modelo de classificação
X_ref = reference_data.drop(columns=['MedHouseVal'])
y_ref = (reference_data['MedHouseVal'] > 2.5).astype(int)

X_curr = current_data.drop(columns=['MedHouseVal'])
y_curr = (current_data['MedHouseVal'] > 2.5).astype(int)

model = RandomForestClassifier(random_state=42).fit(X_ref, y_ref)

reference_data['prediction'] = model.predict(X_ref)
reference_data['target'] = y_ref

current_data['prediction'] = model.predict(X_curr)
current_data['target'] = y_curr # Ground truth simulado que chegou com atraso

# Gerar relatório de performance do modelo
classification_report = Report(metrics=[
    ClassificationPreset()
])
classification_report.run(reference_data=reference_data, current_data=current_data)
classification_report.save_html("model_performance_report.html")
print("Relatório de performance do modelo gerado com sucesso!")
```

### 3.3 Demo 3 — Monitoramento de Text Data & Embeddings em LLMs

Mostrar como o Evidently AI avalia derivação de dados textuais e características semânticas:

```python
from evidently.descriptors import Sentiment, TextLength, OOV
from evidently.metric_preset import TextEvals

# Dados de texto de referência e produção
ref_texts = pd.DataFrame({"response": [
    "O serviço foi excelente e rápido.",
    "Atendimento razoável, sem grandes problemas.",
    "Gostei muito da experiência de compra."
]})

curr_texts = pd.DataFrame({"response": [
    "Péssimo serviço, nunca mais compro nesta loja!",
    "Horrível, suporte não responde há 3 dias.",
    "Sistema completamente instável e com erros."
]})

text_report = Report(metrics=[
    TextEvals(column_name="response", descriptors=[
        Sentiment(),
        TextLength(),
        OOV() # Out of Vocabulary
    ])
])
text_report.run(reference_data=ref_texts, current_data=curr_texts)
text_report.save_html("text_drift_report.html")
print("Relatório de monitoramento de texto gerado!")
```

---

## 4️⃣ Boas Práticas para Fechar a Aula

1. **Definição Inteligente do Dataset de Referência**:
   - Não utilize apenas o dataset de treino completo como referência para sempre. Utilize um **baseline validado em produção** (*rolling window* ou *gold dataset*) para evitar falsos positivos causados por sazonalidade conhecida.
2. **Combinação de Janelas de Inferência (*Sliding Windows*)**:
   - Combine janelas curtas (ex.: últimas 1 a 6 horas) para detectar surtos e anomalias de pipeline com janelas longas (ex.: últimos 7 a 30 dias) para identificar tendências lentas de degradação.
3. **Controle de Falsos Alertas (*Alert Fatigue*)**:
   - Ajuste o nível de significância $\alpha$ (p-value, tipicamente 0.05 ou 0.01) e aplique correções para múltiplos testes estatísticos (**Bonferroni correction**) quando monitorar centenas de atributos simultaneamente.
4. **Fechando o Loop de MLOps (Continuous Training - CT)**:
   - A detecção de drift não deve gerar apenas um e-mail de alerta. Ela deve disparar webhooks para orchestradores (Airflow, Kubeflow, GitHub Actions) que coletam novos dados rotulados, validam os dados na Feature Store, acionam o re-treinamento e registram um novo modelo no **Model Registry**.
5. **Decoupled Architecture (Monitoramento Assíncrono)**:
   - Nunca calcule testes de drift dentro da rota síncrona de inferência da API. O serviço de inferência deve apenas publicar logs de entrada/saída assincronamente (via Kafka, Kinesis ou arquivo Parquet no Object Storage) para que o Worker do Evidently processe os relatórios em segundo plano.