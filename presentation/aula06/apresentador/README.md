# Modelos de Embeddings em Produção

## README do Apresentador

Este documento organiza a apresentação da aula e serve como **guia conceitual** para o expositor.  
A estrutura abaixo deve ser seguida para garantir clareza, progressão lógica e alinhamento com o grupo.

---

## 1️⃣ Motivação

### 1.1 Por que entender embeddings em produção antes de aplicações avançadas de IA?

- Evolução dos embeddings: de Word2Vec (2013) a modelos modernos como BERT e multimodal (CLIP), impulsionados por LLMs e RAG  
- Necessidade de vetores em alta dimensão para representar dados não estruturados (texto, imagem, áudio)  
- Trade-offs entre embeddings simples (rápidos, leves) e avançados (precisos, mas custosos)  
- Embeddings são a base para RAG, recomendação e busca semântica em produção  
- Base sólida facilita integração em pipelines de IA generativa e evita falhas comuns como drift ou incompatibilidade

### 1.2 A importância de gerenciar embeddings com MLOps

- Por que embeddings precisam de MLOps: versioning, monitoramento de drift, automação de re-embedding  
- Benefícios de pipelines estruturados: redução de latência, custo e erros em escala  
- Evitar "garbage in, garbage out" em produção (ex.: embeddings ruins afetam todo o RAG)  
- Melhor colaboração entre data scientists e ops para deploy contínuo  
- Reprodutibilidade e compliance (ex.: rastrear bias em embeddings)

### 1.3 Impacto prático

- Aplicações reais: RAG em chatbots, recomendação em e-commerce, busca multimodal em apps  
- Casos de uso apropriados: quando usar embeddings pré-treinados vs fine-tuned  
- Quando começar simples (prototipagem com sentence-transformers) e quando escalar (produção com ONNX/Docker)  
- Relação com MLOps: embeddings impactam monitoring, CI/CD e custo de inferência em cloud

---

## 2️⃣ Como Funciona

### 2.1 Conceitos fundamentais de embeddings em produção

- Embeddings: vetores densos que capturam semântica (ex.: dim=768 para BERT)  
- Geração: via modelos como sentence-transformers, Hugging Face ou APIs (OpenAI)  
- Desafios: drift de dados, versioning de modelos, escalabilidade em bilhões de vetores  
- Estratégias: batch vs real-time embedding, quantização para eficiência  
- Integração: com bancos vetoriais (Qdrant, Pinecone) para retrieval

### 2.2 Deploy de modelos de embeddings

- Serialização: salvar com pickle, joblib ou ONNX para portabilidade  
- Containerização: Docker para empacotar modelo + dependências  
- API para inferência: FastAPI/Flask para endpoints de embedding  
- Cloud deploy: AWS SageMaker, GCP Vertex AI ou Kubernetes para escala  
- Monitoring: rastrear latência, drift e performance em produção

### 2.3 Desafios comuns e melhores práticas

- Problemas: mismatch treino/produção, bias amplificado, custo alto em escala  
- Práticas: automação CI/CD para re-treino, A/B testing de modelos, feature stores para embeddings  
- Ferramentas: MLflow para registry, DVC para versioning de dados  
- Estratégias: começar com embeddings leves, monitorar com Prometheus/Grafana  
- Exemplos: Uber usando embeddings para real-time em 130M+ usuários

### 2.4 Escolhendo a abordagem certa

- Critérios: precisão vs latência, custo vs escalabilidade, domínio (texto vs multimodal)  
- Trade-offs: modelos open-source (grátis, customizáveis) vs proprietários (fáceis, mas caros)  
- Começar simples e iterar: protótipo local → deploy em cloud  
- Importância para MLOps: embeddings afetam todo o pipeline, de ingestão a serving

---

## 3️⃣ Quickstart

### 3.1 Prática: Embeddings com Hugging Face + Deploy em FastAPI

**Repositório de referência:** [qdrant/examples](https://github.com/qdrant/examples)
Este repositório oficial contém tutoriais e demos para geração de embeddings e integração com bancos vetoriais.

**Tutoriais recomendados (ordem sugerida para aula):**
1. Embeddings Basics - Geração simples com sentence-transformers  
   https://github.com/qdrant/examples/tree/master/qdrant_101_text_data  
2. RAG com Embeddings - Integração em pipeline  
   https://qdrant.tech/documentation/tutorials-search-engineering/ 
3. Deploy de Modelo - Exemplo com API  
   https://huggingface.co/docs/transformers/en/index 
4. Monitoring Embeddings - Básico com MLflow  
   https://mlflow.org/docs/latest/ml/tutorials-and-examples/

### 3.2 Objetivos da Prática

**Fase 1: Executar e Entender**
- Instalar dependências e gerar embeddings locais  
- Executar notebooks em ordem (básico → RAG)  
- Entender: geração de vetores, similaridade, integração com banco  

**Fase 2: Experimentar e Modificar**
- Alterar modelos (ex.: all-MiniLM-L6-v2 para multilingual)  
- Adicionar quantização ou fine-tuning simples  
- Testar batch vs real-time, medir latência  
- Comparar precisão: cosine similarity em datasets de teste  
- Aplicar MLOps: versionar com MLflow

**Fase 3: Deploy Simples (API)**
- Serializar modelo com ONNX  
- Criar API REST com FastAPI  
- Endpoint: receber input (texto/imagem) → gerar embedding → retornar vetor  
- Testar localmente e deploy em cloud (ex.: Heroku ou AWS)  
- Considerações para produção: auth, scaling, logging

### 3.3 Estrutura da Prática

**Setup inicial:**
- Instalar: `pip install sentence-transformers fastapi uvicorn mlflow docker`  
- Hugging Face setup: baixar modelo via `SentenceTransformer('all-MiniLM-L6-v2')`  
- Verificar: gerar embedding de teste e medir similaridade  
- Quickstart oficial: https://huggingface.co/docs/transformers/en/quicktour

**Desenvolvimento:**
- Seguir tutoriais sequencialmente  
- Para cada notebook: executar, entender código, modificar (ex.: trocar modelo), experimentar  
- Documentar mudanças e resultados (ex.: latência antes/depois de quantização)

**Deploy:**
- Escolher um modelo (ex.: leve para produção)  
- Criar script de inferência  
- Implementar API REST básica  
- Testar com exemplos reais  
- Discussão sobre melhorias: CI/CD, monitoring de drift

### 3.4 Conexão com MLOps

Esta prática demonstra:
- **Data Preparation**: geração e versionamento de embeddings  
- **Modeling**: escolha e fine-tuning de modelos de embedding  
- **Evaluation**: medir qualidade (similarity, drift)  
- **Deployment**: servir embeddings via API escalável  
- **Iteração**: A/B testing e re-treino automático  
- **Preparação**: base para RAG avançado e monitoring em produção