# Bancos Vetoriais (Qdrant)

## README do Apresentador

Este documento organiza a apresentação da aula e serve como **guia conceitual** para o expositor.  
A estrutura abaixo deve ser seguida para garantir clareza, progressão lógica e alinhamento com o grupo.

---

## 1️⃣ Motivação

### 1.1 Por que entender Bancos Vetoriais antes de aplicações avançadas de IA?

- Evolução dos sistemas de busca: de keyword-based para semantic search  
- Necessidade de similaridade semântica em embeddings (texto, imagem, áudio)  
- Trade-offs entre bancos tradicionais (SQL/NoSQL) e vetoriais  
- Bancos vetoriais são fundamentais para RAG, recomendação, busca multimodal  
- Base sólida facilita compreensão de LLMs, agents e pipelines de IA generativa

### 1.2 A importância de escolher o banco certo

- Por que Qdrant se destaca: performance (Rust + HNSW), filtering poderoso, open-source + cloud grátis  
- Benefícios de começar com um banco simples e escalável  
- Redução de latência e custo em produção  
- Melhor integração com ecossistema Python (LangChain, LlamaIndex, sentence-transformers)  
- Reprodutibilidade e facilidade de deploy local/cloud

### 1.3 Impacto prático

- Aplicações reais: semantic search, RAG, recomendação personalizada, detecção de anomalias  
- Casos de uso apropriados: quando usar Qdrant vs Pinecone, Milvus, Weaviate, pgvector  
- Quando começar simples (prototipagem) e quando escalar para produção  
- Relação com MLOps: vetores impactam retrieval, avaliação e monitoramento de LLMs

---

## 2️⃣ Como Funciona

### 2.1 Conceitos fundamentais de Bancos Vetoriais

- Embeddings: vetores de alta dimensão representando significado  
- Métricas de similaridade: Cosine, Euclidean, Dot Product  
- Índices aproximados (ANN): HNSW (usado pelo Qdrant), IVF, PQ  
- Componentes chave: Collection, Point, Vector, Payload (metadados filtráveis)  
- Busca híbrida: dense + sparse vectors (BM25 + vetores)

### 2.2 Qdrant: Visão geral

- Open-source vector database escrito em Rust  
- Alta performance e escalabilidade massiva  
- Suporte nativo a filtering avançado (payloads JSON)  
- Modos: local (Docker), in-memory (Python client), cloud grátis  
- Integrações: LangChain, LlamaIndex, FastEmbed, Hugging Face

### 2.3 Outros bancos vetoriais populares (contexto)

- Pinecone: managed, zero-ops, enterprise  
- Milvus / Zilliz: escala extrema (bilhões de vetores)  
- Weaviate: busca híbrida + multimodal  
- Chroma: prototipagem rápida em Python  
- pgvector: extensão PostgreSQL (baixo custo)  
- Redis: latência ultra-baixa  

### 2.4 Escolhendo a abordagem certa

- Critérios: escala, latência, custo, filtering, facilidade de uso  
- Trade-offs: managed vs open-source, performance vs simplicidade  
- Começar com Qdrant (fácil + poderoso) e migrar se necessário  
- Importância para MLOps: retrieval afeta qualidade do RAG e custo de inferência

---

## 3️⃣ Quickstart

### 3.1 Prática: Semantic Search com Qdrant + sentence-transformers

**Repositório de referência principal:** [qdrant/examples](https://github.com/qdrant/examples)  
Este repositório oficial contém tutoriais, demos e guias práticos para Qdrant.

**Tutoriais recomendados (ordem sugerida para aula):**
1. Qdrant 101 - Getting Started (introdução ao semantic search)  
   https://github.com/qdrant/examples/tree/master/qdrant_101_getting_started  
2. Qdrant 101 - Text Data (NLP + vetores)  
   https://github.com/qdrant/examples/tree/master/qdrant_101_text_data  
3. 5-Minute RAG com DeepSeek / FastEmbed  
   https://qdrant.tech/documentation/tutorials-build-essentials/rag-deepseek  
4. Busca semântica com sentence-transformers  
   https://qdrant.tech/documentation/tutorials-search-engineering/neural-search/

### 3.2 Objetivos da Prática

**Fase 1: Executar e Entender**
- Rodar Qdrant local via Docker ou usar Qdrant Cloud (grátis)  
- Instalar: `pip install qdrant-client sentence-transformers fastembed`  
- Executar notebooks em ordem (getting started → text data → RAG simples)  
- Entender: criação de collection, upsert de pontos, query com similaridade

**Fase 2: Experimentar e Modificar**
- Alterar hiperparâmetros: distância (COSINE/DOT), tamanho do HNSW (m, ef_construct)  
- Adicionar payloads e filtros (ex.: filtrar por autor ou data)  
- Testar diferentes modelos de embedding (all-MiniLM-L6-v2, multilingual)  
- Comparar resultados: recall, latência, relevância  
- Aplicar conceitos: documentar experimentos (criação, inserção, avaliação)

**Fase 3: Deploy Simples (API)**
- Salvar collection ou exportar dados  
- Criar API REST básica (FastAPI ou Flask)  
- Endpoint: receber texto → embed → buscar top-k → retornar resultados + scores  
- Testar localmente com exemplos reais  
- Considerações para produção: autenticação, rate limiting, monitoramento

### 3.3 Estrutura da Prática

**Setup inicial:**
- Docker local: `docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant`  
- Ou Qdrant Cloud: https://cloud.qdrant.io/ (crie cluster grátis)  
- Verificar dashboard: http://localhost:6333/dashboard  
- Executar quickstart oficial: https://qdrant.tech/documentation/quickstart/

**Desenvolvimento:**
- Seguir tutoriais sequencialmente  
- Para cada notebook: executar, entender código, modificar, experimentar  
- Documentar mudanças e resultados (ex.: scores antes/depois de filtros)

**Deploy:**
- Escolher um modelo treinado/simples  
- Criar script de inferência  
- Implementar API REST básica  
- Testar com exemplos reais  
- Discussão sobre melhorias: escalabilidade, versionamento, observabilidade

### 3.4 Conexão com MLOps

Esta prática demonstra:
- **Data Preparation**: geração e armazenamento de embeddings  
- **Modeling**: uso de índices ANN e configurações de coleção  
- **Evaluation**: medir recall, precision, latência em buscas  
- **Deployment**: disponibilizar retrieval via API  
- **Iteração**: experimentar embeddings, métricas, filtros  
- **Preparação**: base para aulas futuras sobre RAG avançado, hybrid search, monitoramento de vetores