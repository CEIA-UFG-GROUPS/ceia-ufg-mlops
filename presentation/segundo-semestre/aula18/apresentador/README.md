# Feature Stores

## README do Apresentador

Este documento organiza a apresentação da aula e serve como **guia conceitual** para
o expositor. A estrutura abaixo é uma sugestão para garantir clareza, progressão
lógica e alinhamento com o grupo.

> 💡 **Fio condutor sugerido**: começar de uma história de terror de MLOps — *"o modelo
> tinha AUC 0.95 no notebook e despencou em produção"* — e revelar duas causas
> clássicas que o feature store ataca: **training-serving skew** e **data leakage por
> join sem tempo**. Mostrar que o feature store é a **interface entre dados e modelos**
> que garante *a mesma feature no treino e na produção*. Fechar construindo isso ao
> vivo com Feast e mostrando o ângulo 2026 (busca vetorial/RAG no mesmo sistema).

---

## 1️⃣ Motivação

### 1.1 A história de terror: skew e leakage
- *"AUC 0.95 offline, péssimo em produção"* — pergunte à turma o que pode ter acontecido.
- **Training-serving skew**: a feature calculada em Spark no treino e reescrita em outra linguagem no serviço online → diferenças sutis (nulos, fuso, arredondamento) → degradação silenciosa.
- **Data leakage**: montar o dataset de treino com um `JOIN` por chave pega valores **do futuro** em relação ao rótulo → métrica inflada.

### 1.2 A feature é a interface entre dados e modelos
- Modelo não come dado bruto; come **features**. Calcular features certo, consistente e no tempo certo é a maior fonte de complexidade de dados em ML.
- **Definição**: feature store = sistema central para **definir, armazenar, servir e governar** features, garantindo consistência treino↔produção.

### 1.3 Por que MLOps se importa
- Reuso: as features mais populares em grandes empresas são usadas por dezenas/centenas de modelos.
- É o ponto onde **dados viram produto reutilizável**; conecta pipeline de dados ao ciclo do modelo.

---

## 2️⃣ Como Funciona

### 2.1 Componentes (dar o mapa mental)
- **Transformação** (batch/streaming/on-demand), **Storage** (offline+online), **Serving**, **Monitoramento**, **Registry**.
- Desenhar no quadro: fonte → transformação → offline/online → serving; registry como catálogo central.

### 2.2 Offline vs Online (conceito central)
- **Offline**: histórico, alto volume (warehouse/lake) → **treino**.
- **Online**: valores mais recentes, baixa latência (Redis/Dynamo) → **inferência**. Propriedades **LATS**.
- Mensagem: são dois storages porque os requisitos são opostos (volume vs latência).

### 2.3 Point-in-time correctness (o "momento aha")
- Mostrar o diagrama rótulo × histórico: pegar a feature **as-of** o timestamp do rótulo, nunca o futuro.
- `JOIN` por chave = leakage; `get_historical_features` = join temporal correto.
- Essa é a ideia que separa "cientista de dados" de "engenheiro de ML".

### 2.4 Uma definição, dois mundos (o que mata o skew)
- A **mesma feature view** alimenta `get_historical_features` (treino) e `get_online_features` (produção).
- É isso — não disciplina manual — que elimina o training-serving skew.

### 2.5 Feast em 5 peças
- **Entity**, **Data Source**, **Feature View**, **Feature Service**, **Registry**.
- Comandos: `feast apply` → `get_historical_features` → `feast materialize-incremental` → `get_online_features`.

### 2.6 Panorama 2026 (para situar)
- Consolidação: **Tecton → Databricks**; Hopsworks, SageMaker, Vertex; **Feast** = padrão OSS.
- **Convergência com vector DB**: feature stores servindo embeddings + busca por similaridade para **RAG/real-time** — liga com Qdrant e com a Aula 13 (agentes/MCP).

---

## 3️⃣ Quickstart & Demos

> 💡 **Material pronto**: a pasta `../monitor/atividade/` traz um lab Feast completo
> (Feast + Docker). O jeito mais seguro ao vivo é rodar o Caminho B (Docker), que
> executa tudo de uma vez em `python:3.10-slim`. Já tenha a imagem buildada antes.

### 3.1 Demo 1 — As definições
- Abrir `feature_repo/definitions.py`: mostrar `Entity`, `FileSource`, as duas `FeatureView` (`customer_stats` e `kb_docs` com `embedding` + `vector_index=True`) e o `FeatureService`.
- `feast apply` → mostrar que criou o registry e as tabelas do online store.

### 3.2 Demo 2 — Treino com point-in-time
- `python src/train.py`: destacar que o `entity_df` são rótulos+timestamp e que o join é as-of.
- (Se der tempo) mostrar a correlação/feature: o valor veio de quando o rótulo aconteceu.

### 3.3 Demo 3 — Materialize + serving online
- `feast materialize-incremental` → offline vira online.
- `python src/serve_online.py`: buscar só pela **chave** `customer_id`, features frescas vêm do online store, modelo prediz. **Mesma definição do treino.**

### 3.4 Demo 4 — Busca vetorial / RAG (ângulo 2026)
- `python src/rag_retrieve.py`: uma consulta em linguagem natural → embedding → `retrieve_online_documents_v2` → documentos relevantes.
- Discutir: o feature store agora é **também** a camada de recuperação de um agente. Onde termina o feature store e começa o vector DB?
- ⚠️ Lembrar: a busca vetorial no sqlite do Feast 0.65 exige **Python 3.10** (por isso a imagem Docker é 3.10-slim).

### 3.5 Para fechar
- Recap: offline/online, point-in-time, **uma definição nos dois mundos**.
- Frase-síntese: *"se a feature é calculada de dois jeitos, o modelo em produção não é o que você avaliou."*
- Amarrar com Pipelines (17), Model Registry (19) e a convergência com vetores (Aula 13 / Qdrant).

---

## 4️⃣ Quando Usar (e Quando NÃO Usar)

### Usar ✅
- Features reutilizadas por vários modelos/times.
- Necessidade de **serving online** consistente com o treino (evitar skew).
- Casos real-time/RAG que combinam features + busca vetorial.

### Não usar / cuidado ❌
- Projeto único, exploratório, sem serving online e sem reuso — pode ser overkill.
- Um feature store gerenciado tem custo operacional; avalie Feast (leve) antes de plataformas pesadas.
- Não substitui versionamento de dados brutos (DVC) nem model registry — **complementa**.

> **Regra prática**: se a **mesma feature** precisa existir no treino **e** na produção,
> e/ou é reutilizada por mais de um modelo, ela merece um feature store.
