# 📘 Aula 18 — Feature Stores

## Material de Estudo Prévio (Monitor)

Este material tem como objetivo **preparar para a aula de Feature Stores**, oferecendo
uma base conceitual sólida para acompanhar, complementar e aprofundar a discussão
conduzida pelo apresentador.

⚠️ **Este conteúdo não é um guia de instruções**, mas sim um **material de estudo
prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do CEIA/UFG.

---

## 🎯 Objetivo da Aula

Ao final desta aula, espera-se que os participantes compreendam:

- **Que problema o feature store resolve**: por que servir features em treino e em produção "cada um do seu jeito" causa bugs silenciosos e retrabalho
- O conceito de **training-serving skew** e por que ele é uma das falhas mais caras (e difíceis de depurar) em ML
- A distinção entre **offline store** (histórico, alto volume) e **online store** (baixa latência)
- **Point-in-time correctness** (o join "com viagem no tempo") e por que ele evita **data leakage**
- Os **componentes** de um feature store: transformação, storage, serving, monitoramento e **feature registry**
- **Reuso e governança** de features como ativos versionados e compartilhados
- Como construir tudo isso na prática com o **Feast** (entity, data source, feature view, feature service)
- O **panorama de 2026**: consolidação do mercado e a **convergência feature store + vector database** para casos real-time/RAG
- A ponte com o **Design Pattern 26 "Feature Store"** (Machine Learning Design Patterns) e o Cap. 10 de *Designing ML Systems*

---

## 🧠 Contexto: Por que Feature Stores existem?

### A feature é a interface entre dados e modelos

Em ML, o modelo não consome dados brutos — consome **features**: agregações,
transformações e sinais derivados (ex.: "valor médio de transações do cliente nos
últimos 30 dias"). Calcular essas features **de forma correta, consistente e no tempo
certo** é onde a maior parte da complexidade de dados de um sistema de ML mora.

Sem uma camada dedicada, surgem quatro dores recorrentes:

1. **Training-serving skew**: a feature é calculada de um jeito no pipeline de treino
   (ex.: PySpark/pandas em batch) e de **outro** no serviço de inferência (ex.: um
   `SELECT` em tempo real reescrito em Java). Diferenças sutis — tratamento de nulos,
   fuso horário na janela temporal, arredondamento — produzem entradas distorcidas e
   **degradação silenciosa** do modelo em produção. É catastrófico e difícil de
   depurar, porque o modelo "funciona" nos testes offline.
2. **Retrabalho e duplicação**: cada time reescreve as mesmas features. Não há reuso.
3. **Data leakage**: ao montar o dataset de treino, é fácil acidentalmente usar o
   valor de uma feature **do futuro** em relação ao rótulo — inflando a métrica offline
   e quebrando em produção.
4. **Latência online**: servir features frescas para inferência em tempo real
   (milissegundos) exige um armazenamento diferente do usado para treino em batch.

> **A definição**: um **feature store** é um sistema centralizado para **definir,
> armazenar, servir e governar** features de ML — a interface entre os dados e os
> modelos, garantindo **consistência entre treino e produção**.

### Por que isso importa para MLOps

O feature store é o ponto onde **dados viram um produto reutilizável**. Ele conecta o
pipeline de dados ao ciclo de vida do modelo (treino → deploy → monitoramento) e é
frequentemente descrito como o coração da plataforma de MLOps de nível empresarial.
Em grandes empresas, as features mais populares são reutilizadas por **dezenas ou
centenas** de modelos — reuso que só é possível com um catálogo central.

---

## 🏛️ Como Funciona: Componentes de um Feature Store

Um feature store maduro tem cinco componentes (segundo a literatura de referência):

```text
                    ┌──────────────────────────────────────────────┐
   dados brutos ──► │ 1. TRANSFORMAÇÃO (batch / streaming / on-demand)│
                    └───────────────────────┬──────────────────────┘
                                            │  (materialização)
                 ┌──────────────────────────┼──────────────────────────┐
                 ▼                                                       ▼
      ┌───────────────────┐                                  ┌───────────────────┐
      │ 2a. OFFLINE STORE │  histórico, alto volume          │ 2b. ONLINE STORE  │
      │  (warehouse/lake) │  → dados de TREINO               │  (key-value/Redis)│  → INFERÊNCIA
      └─────────┬─────────┘                                  └─────────┬─────────┘
                │ get_historical_features (point-in-time)              │ get_online_features (baixa latência)
                ▼                                                       ▼
      ┌──────────────────────────── 3. SERVING ────────────────────────────┐
      └─────────────────────────────────┬──────────────────────────────────┘
      ┌─────────────────────────────────┴──────────────────────────────────┐
      │ 4. MONITORAMENTO (drift/skew, latência)  •  5. FEATURE REGISTRY      │
      │                                             (catálogo, versões,      │
      │                                              lineage, single SoT)    │
      └─────────────────────────────────────────────────────────────────────┘
```

### 1. Transformação
Orquestra as transformações que produzem os valores das features — em **batch**
(Spark, SQL), em **streaming** (fluxos em tempo real) e **on-demand** (calculadas no
momento da requisição, ex.: distância entre dois pontos recebidos na request).

### 2. Storage: offline vs online
- **Offline store**: meses/anos de histórico, otimizado para leitura em grande volume
  (data warehouses/lakes: BigQuery, Snowflake, S3/Parquet). Alimenta o **treino** e a
  inferência em batch.
- **Online store**: guarda apenas os **valores mais recentes**, com leitura de
  **baixíssima latência** (key-value: Redis, DynamoDB, Cassandra). Alimenta a
  **inferência online**. Deve ter propriedades **LATS**: baixa latência, alta
  disponibilidade, alto throughput e storage escalável.

### 3. Serving
Acesso offline via SDK (para montar datasets de treino) e serving online de **um vetor
de features por vez**, com os valores mais frescos, para o modelo em produção.

### 4. Monitoramento
Qualidade (drift, skew) e operação (latência, throughput, disponibilidade) das
features servidas.

### 5. Feature Registry
O **catálogo central** — *single source of truth* das definições, metadados, versões e
lineage. É o que torna features **descobríveis e reutilizáveis** entre times.

---

## ⏳ Point-in-Time Correctness: O Join com "Viagem no Tempo"

O conceito mais sutil (e mais importante) da aula. Para montar um dataset de treino,
você tem **rótulos com timestamp** (ex.: "cliente X teve fraude em 12/03 às 10h") e
quer juntar as features **como elas eram naquele instante** — nunca valores
posteriores.

```text
Rótulo:   customer=X | ts=12/03 10:00 | is_fraud=1
Features (histórico do cliente X):
   ...  11/03 → chargeback=0.02   ✅ (é o valor "as-of" 12/03 10:00)
        12/03 11:30 → chargeback=0.30  ❌ (FUTURO em relação ao rótulo — leakage!)
```

Um `JOIN` comum por chave pegaria o valor mais recente — que pode ser **do futuro** em
relação ao rótulo, vazando informação e inflando a métrica offline. O feature store
faz um **point-in-time join** (um *temporal/as-of join*): para cada rótulo, pega o
valor **mais recente que não ultrapassa** o timestamp do rótulo. No Feast, isso é o
`get_historical_features`.

> **Regra de ouro**: métrica offline excelente que despenca em produção é, muitas
> vezes, **data leakage** por join sem correção temporal.

---

## 🐍 Na Prática com Feast

O **Feast** é o feature store open source de referência. Suas peças:

- **Entity**: a chave de negócio pela qual as features são buscadas (ex.: `customer`).
- **Data Source**: de onde vêm os valores (Parquet/BigQuery/...), com um `timestamp_field`.
- **Feature View**: o "contrato" de um grupo de features (nome, tipos, TTL, fonte),
  servido tanto offline quanto online.
- **Feature Service**: um **pacote versionado** de features que um modelo consome.
- **Registry**: o catálogo central provisionado por `feast apply`.

```python
from feast import Entity, FeatureView, Field, FileSource, FeatureService
from feast.types import Float32, Int64

customer = Entity(name="customer", join_keys=["customer_id"])

source = FileSource(path="data/customer_stats.parquet", timestamp_field="event_timestamp")

customer_stats = FeatureView(
    name="customer_stats",
    entities=[customer],
    schema=[Field(name="chargeback_rate", dtype=Float32),
            Field(name="num_tx_30d", dtype=Int64)],
    online=True,
    source=source,
)

fraud_model_v1 = FeatureService(name="fraud_model_v1", features=[customer_stats])
```

O fluxo de comandos:

```bash
feast apply                                 # registra definições + cria online store
# treino:
store.get_historical_features(entity_df, features=[...])   # join point-in-time
feast materialize-incremental <now>          # offline -> online
# inferência:
store.get_online_features(features=[...], entity_rows=[{"customer_id": 42}])
```

**A mesma definição** alimenta `get_historical_features` (treino) e
`get_online_features` (produção) — é exatamente isso que elimina o *training-serving skew*.

---

## 🌐 Panorama 2026: Consolidação e Convergência com Vector DBs

- **Mercado consolidando**: o espaço amadureceu e concentrou. A **Tecton** (pioneira do
  conceito, criada por ex-engenheiros do Michelangelo, da Uber) teve sua tecnologia
  **adquirida pela Databricks** — cujo Feature Store é hoje uma das ofertas dominantes,
  ao lado de **Hopsworks**, **SageMaker Feature Store** (AWS) e **Vertex AI Feature
  Store** (GCP). O **Feast** permanece como o padrão **open source**.
- **Feature store + Vector Database**: a tendência mais forte de 2024-2026 é a
  **convergência**. Sistemas de ML em tempo real (recomendação, busca, **RAG** para
  agentes/LLMs) precisam de **busca por similaridade** (ANN) sobre embeddings — e
  feature stores passaram a **armazenar e servir embeddings** como features, integrando
  busca vetorial. O Feast, por exemplo, suporta indexar um campo de embedding e servir
  `retrieve_online_documents` no online store.
- **Ligação com o resto do curso**: isso conecta feature stores diretamente à Aula de
  **Bancos Vetoriais (Qdrant)** e à Aula 13 (**agentes/MCP**) — o feature store vira
  também a camada de recuperação de contexto de um agente.
- **Pipelines FTI**: um modelo mental popular organiza o sistema em três pipelines —
  **Feature**, **Training** e **Inference** — todos lendo/escrevendo no feature store,
  que atua como o ponto de desacoplamento entre eles.

---

## 💡 Boas Práticas

1. **Uma definição, dois mundos**: a mesma feature view alimenta treino e produção — nunca reescreva a lógica no serviço online.
2. **Sempre point-in-time no treino**: monte datasets com `get_historical_features`, nunca com join simples por chave.
3. **Escolha o storage certo**: offline para volume/histórico; online (key-value) para latência.
4. **Trate features como produto**: nomeie, documente, versione e reutilize via o registry.
5. **Versione o pacote do modelo**: use *feature services* para saber exatamente quais features cada modelo consome.
6. **Monitore skew e drift** das features servidas — não só do modelo.
7. **Materialize com disciplina**: o online store só reflete o que foi materializado; automatize.
8. **On-demand com cuidado**: transformações no momento da request também precisam ser idênticas entre treino e serving.

---

## 📊 Casos de Uso Práticos

### Caso 1: Antifraude em tempo real
- **Dor**: o pipeline de treino calcula "chargeback dos últimos 30 dias" em Spark; o serviço online recalcula em outra linguagem → skew silencioso.
- **Com feature store**: uma única definição; treino via point-in-time, produção via online store. Skew eliminado.

### Caso 2: Reuso entre times
- **Dor**: times de churn, fraude e crédito reescrevem as mesmas features de cliente.
- **Com feature store**: as features viram ativos no registry; cada modelo as consome via feature service.

### Caso 3: RAG para um agente de atendimento (2026)
- **Dor**: um agente precisa recuperar políticas/documentos relevantes para responder.
- **Com feature store + vetores**: embeddings dos documentos são features; a busca por similaridade é servida pelo mesmo sistema (ver atividade).

### Caso 4: Recomendação
- **Dor**: gerar candidatos exige similaridade sobre embeddings de itens, com features de usuário frescas.
- **Com feature store**: features online do usuário + busca vetorial de itens, na mesma camada.

---

## 🧪 Atividade Prática

A pasta [`atividade/`](./atividade/) traz um laboratório completo com **Feast** que
percorre o ciclo: **definir features → `feast apply` → treinar com join point-in-time →
materializar → servir online → busca vetorial/RAG**.

- **`feature_repo/`**: o repositório de features (entity, data source, feature views, feature service).
- **`src/train.py`**: treino com `get_historical_features` (point-in-time).
- **`src/serve_online.py`**: inferência com `get_online_features`.
- **`src/rag_retrieve.py`**: o ângulo 2026 — feature store servindo busca vetorial (RAG).
- **`docker/`**: roda o ciclo completo em `python:3.10-slim`.

Instruções completas no [`atividade/README.md`](./atividade/README.md).

---

## 💬 Pontos para Reflexão Pré-Aula

1. **Training-serving skew**: por que ele é tão perigoso se o modelo passa em todos os testes offline?
2. Por que um **join simples por chave** para montar o dataset de treino é uma armadilha? O que o point-in-time resolve?
3. Quais as diferenças de requisitos entre **offline** e **online store**? Poderia ser um só?
4. O que significa tratar uma **feature como produto reutilizável**? Que problemas de time isso resolve?
5. **Feature store vs vector database**: onde um termina e o outro começa em 2026? Faz sentido serem o mesmo sistema?
6. No seu projeto, **quais features** você promoveria primeiro para um feature store — e por quê?
7. Como o feature store se conecta a **pipelines de treinamento** (Aula 17), **model registry** (Aula 19) e **monitoramento de drift**?

---

## 📚 Referências

### Material Indicado no Cronograma do Grupo

1. **Lakshmanan, V., Robinson, S. & Munn, M. (2020).** *Machine Learning Design Patterns*. O'Reilly. — Cap. 6, Design Pattern 26 "Feature Store", pp. 295-310.
2. **Huyen, Chip (2022).** *Designing Machine Learning Systems*. O'Reilly. — Cap. 10, seção "Feature Store", pp. 325-327.

### Documentação e Ferramentas

3. **Feast — Documentação** — [https://docs.feast.dev/](https://docs.feast.dev/)
4. **Feast — Quickstart** — [https://docs.feast.dev/getting-started/quickstart](https://docs.feast.dev/getting-started/quickstart)
5. **Feast — Vector search / RAG** — [https://docs.feast.dev/reference/beta-rag](https://docs.feast.dev/reference/beta-rag)
6. **Tecton — What is a Feature Store?** — [https://www.tecton.ai/blog/what-is-a-feature-store/](https://www.tecton.ai/blog/what-is-a-feature-store/)
7. **Hopsworks — Feature Store (dictionary)** — [https://www.hopsworks.ai/dictionary/feature-store](https://www.hopsworks.ai/dictionary/feature-store)
8. **Databricks Feature Store** — [https://www.databricks.com/product/feature-store](https://www.databricks.com/product/feature-store)

### Artigos e Fundamentos

9. **Sculley, D. et al. (2015).** *Hidden Technical Debt in Machine Learning Systems*. NeurIPS. — a dependência de dados como dívida técnica.
10. **featurestore.org** — comparativo e conteúdo da comunidade — [https://www.featurestore.org/](https://www.featurestore.org/)

---

## 🔗 Conexões com Outras Aulas

- **Aula 16 (DVC)**: versionar dados; o feature store versiona **features derivadas** e as serve.
- **Aula 17 (Pipelines de Treinamento)**: um pipeline tipicamente materializa features no store antes de treinar.
- **Aula 19 (Model Registry)**: features (feature service) + modelo versionado = reprodutibilidade de ponta a ponta.
- **Aula de Bancos Vetoriais (Qdrant)** e **Aula 13 (MCP/Agentes)**: a convergência feature store + vector DB para RAG/real-time.
- **Monitoramento e Drift**: o feature store é onde se mede skew/drift das features servidas.

---

🚀 **Leitura concluída? Venha para a aula pronto para discutir: se a mesma feature é
calculada de dois jeitos no treino e na produção, o seu modelo em produção é o mesmo
que você avaliou — ou outro?**
