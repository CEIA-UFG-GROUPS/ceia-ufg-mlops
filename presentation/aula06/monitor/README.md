# 📘 Aula 06 — Modelos de Embeddings em Produção
## Material de Estudo Prévio (Monitor)

Este material tem como objetivo **preparar o monitor para a aula de Modelos de Embeddings em Produção**, oferecendo uma base conceitual sólida para acompanhar, complementar e aprofundar a discussão conduzida pelo apresentador.

⚠️ **Este conteúdo não é um guia de instruções para o monitor**, mas sim um **material de estudo prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do CEIA/UFG.

Recomenda-se fortemente a leitura dos links e documentações de referência mais abaixo. Essas documentações explicam muito bem fundamentos, boas práticas e desafios reais de embeddings em produção. Se for para começar, leia a documentação do sentence-transformers e do Hugging Face Transformers — são excelentes e muito bem organizadas.

---

## 🎯 Objetivo da Aula

Ao final desta aula, espera-se que os participantes compreendam:

- O que são embeddings e por que eles são fundamentais na IA moderna
- Como gerar, escolher e avaliar modelos de embeddings para diferentes domínios
- Desafios de levar embeddings para produção (drift, latência, custo, versioning)
- Melhores práticas de MLOps aplicadas a embeddings (CI/CD, monitoring, re-embedding)
- Diferenças entre embeddings pré-treinados, fine-tuned e proprietários
- Integração com bancos vetoriais e pipelines de RAG
- Como balancear precisão, velocidade e custo em cenários reais

---

## 🧠 Contexto: Evolução dos Embeddings

### Breve História

**Embeddings Clássicos (2013–2018):**
- Word2Vec, GloVe, fastText → vetores estáticos por palavra
- Limitações: sem contexto, polissemia não resolvida

**Era Contextual (2018–2022):**
- ELMo, BERT, RoBERTa → embeddings contextuais por token
- Sentence-BERT → embeddings de sentenças otimizados para similaridade

**Era Moderna (2022–2026):**
- Modelos leves e eficientes: MiniLM, BGE, E5, GTE
- Multimodal: CLIP, BLIP, SigLIP
- Proprietários: text-embedding-3-large (OpenAI), Cohere Embed, Voyage
- Fine-tuning em domínios específicos e multilingual

**Por que Embeddings Importam Agora?**
- Base de quase toda aplicação de LLM (RAG, agents, recomendação)
- Qualidade do embedding determina qualidade do retrieval → afeta resposta final
- Custo de inferência e latência viraram gargalos em produção

> **"O embedding é o novo feature engineering"** — Princípio fundamental em IA moderna

---

## 📋 Conceitos Fundamentais de Embeddings em Produção

### O que é um Embedding?

**Definição:** Representação vetorial densa de dados (texto, imagem, código, áudio) que captura semântica e permite buscas por similaridade.

**Características principais:**
- Dimensão fixa (384, 768, 1024, 1536…)
- Normalização comum (L2) para usar cosine similarity
- Modelos otimizados para sentence-level ou passage-level

### Tipos de Modelos de Embeddings

#### 1. Modelos Leves e Eficientes (Produção Preferida)

**Objetivo:** Baixa latência e baixo consumo de memória/GPU

**Exemplos:**
- all-MiniLM-L6-v2 (384 dim, ~80 MB)
- BGE-small-en-v1.5 / multilingual
- E5-small / E5-base
- GTE-small / GTE-base

**Vantagens:**
- Rápidos em CPU
- Baratos em escala
- Bom trade-off precisão × velocidade

#### 2. Modelos de Alta Performance

**Exemplos:**
- text-embedding-3-large (OpenAI)
- Cohere Embed v3
- Voyage-2
- bge-large-en-v1.5

**Vantagens:**
- Maior precisão (MTEB leaderboard)
- Melhor em tarefas complexas

**Limitações:**
- Mais caros (API) ou pesados (GPU necessária)

#### 3. Multimodais

**Exemplos:**
- CLIP-ViT-L-14
- SigLIP
- BLIP-2 embeddings

**Casos de uso:**
- Busca texto-imagem
- Recomendação visual + textual

### Desafios em Produção

**Principais problemas:**
- **Drift semântico** — mudança no vocabulário/domínio ao longo do tempo
- **Latência** — inferência em batch vs real-time
- **Custo** — API vs self-hosted em escala
- **Versioning** — incompatibilidade entre versões de modelo
- **Bias e faireness** — embeddings amplificam viés dos dados de treino

**Checklist de produção:**
- Modelo suporta multilingual?
- Latência < 50 ms por query em média?
- Memória GPU/CPU aceitável?
- Existe plano de re-embedding periódico?
- Monitoring de cosine drift ou embedding distance?

### Melhores Práticas MLOps para Embeddings

**1. Versionamento**
- Usar MLflow / DVC para registrar modelo + dataset
- Taggear versões (ex.: v1.5-bge-small-2025-03)

**2. Ingestão e Re-embedding**
- Pipeline Airflow / Prefect / Dagster
- Re-embed quando drift detectado ou novo modelo disponível

**3. Monitoring**
- Prometheus + Grafana: latência, throughput, drift (ex.: average cosine distance)
- Evidently AI ou Alibi Detect para drift detection

**4. Serving**
- FastAPI / Triton Inference Server
- ONNX Runtime para acelerar inferência
- Batch inference para grandes volumes

**5. Escalabilidade**
- Kubernetes + Horizontal Pod Autoscaling
- Cache de embeddings frequentes (Redis)

**Importância:**
> **"Um embedding ruim derruba todo o RAG"** — Verdade comum em produção

---

## 🤖 Modelos Recomendados para Produção (2026)

### Top 5 para Texto (MTEB Leaderboard + Prática Real)

1. **bge-m3** — multilingual, multi-função (dense + sparse + colbert)
2. **bge-large-en-v1.5** — melhor custo-benefício inglês
3. **E5-mistral-7b-instruct** — alta performance (precisa GPU)
4. **text-embedding-3-large** — OpenAI (fácil, mas pago)
5. **all-MiniLM-L12-v2** — baseline rápido e confiável

### Quando Usar Cada Um?

**Use modelos leves quando:**
- Latência crítica (< 30 ms)
- Orçamento limitado
- CPU-only ou edge

**Use modelos pesados quando:**
- Recall/precisão máxima é prioridade
- Tem GPU/TPU disponível
- Domínio muito específico

**Use APIs quando:**
- Zero-ops desejado
- Prototipagem rápida
- Escalabilidade automática aceita custo

---

## ⚖️ Comparação: Modelos de Embeddings em Produção

| Modelo                        | Dimensão | Tamanho   | Latência CPU (aprox.) | MTEB Score (2025/26) | Multilingual | Recomendado para          |
|-------------------------------|----------|-----------|-------------------------|------------------------|--------------|----------------------------|
| all-MiniLM-L6-v2             | 384      | ~80 MB    | ~5–10 ms               | ~57–60                | Sim          | Prototipagem / baseline    |
| bge-small-en-v1.5            | 384      | ~130 MB   | ~8–15 ms               | ~62–64                | Limitado     | Produção custo-benefício   |
| bge-large-en-v1.5            | 1024     | ~1.3 GB   | ~20–40 ms              | ~64–66                | Limitado     | Alta precisão inglês       |
| bge-m3                       | 1024     | ~1.3 GB   | ~30–60 ms              | ~66–68                | Excelente    | Multilingual + híbrido     |
| text-embedding-3-large       | 3072     | API       | ~50–150 ms (rede)      | ~64–65                | Sim          | Zero-ops enterprise        |
| E5-mistral-7b-instruct       | 4096     | ~14 GB    | GPU necessária         | ~68+                  | Sim          | Estado da arte (com GPU)   |

### Princípio: Começar Simples

> **"Start with MiniLM, scale to BGE/E5 when needed"**

1. Comece com modelo leve (MiniLM / bge-small)
2. Estabeleça baseline de recall/latência
3. Monitore métricas em produção
4. Suba para modelos maiores se necessário
5. Considere fine-tuning apenas se ganho > 5–8%

---

## 🛠️ Frameworks e Ferramentas

### sentence-transformers

**O que é:**
- Biblioteca mais usada para embeddings de sentenças
- Modelos otimizados do Hugging Face

**Exemplo básico:**
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode([
    "Este é um texto de exemplo.",
    "Outro texto similar."
])
print(embeddings.shape)  # (2, 384)
```

### Hugging Face Transformers

**O que é:**
- Acesso direto a milhares de modelos de embeddings e transformers
- Permite carregar qualquer modelo do Hub com poucas linhas

**Vantagens:**
- Ecossistema enorme (mais de 500k modelos)
- Suporte a fine-tuning, quantização e exportação ONNX
- Integração nativa com sentence-transformers

**Exemplo básico:**
```python
from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("intfloat/e5-small-v2")
model = AutoModel.from_pretrained("intfloat/e5-small-v2")

text = "query: Texto de exemplo para embedding"
inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
with torch.no_grad():
    embeddings = model(**inputs).last_hidden_state.mean(dim=1)
```

### FastAPI para Serving

**O que é:**
- Framework leve e rápido para criar APIs de inferência
- Ideal para expor embeddings como serviço REST

**Vantagens:**
- Async nativo para alta concorrência
- Documentação automática (Swagger)
- Fácil deploy em containers ou cloud

**Exemplo básico:**
```python
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel

app = FastAPI()
model = SentenceTransformer("all-MiniLM-L6-v2")

class TextInput(BaseModel):
    text: str

@app.post("/embed")
def embed_text(input: TextInput):
    embedding = model.encode(input.text).tolist()
    return {"embedding": embedding}
```

### Outras Ferramentas

**MLflow** — registry e experiment tracking  
**ONNX Runtime** — inferência acelerada (CPU/GPU)  
**Evidently AI** — drift detection em embeddings  
**LangChain / LlamaIndex** — integração direta em pipelines RAG  
**Triton Inference Server** — serving multi-modelo em GPU com alta performance  
**FastEmbed** — alternativa ultraleve ao sentence-transformers (Qdrant)  
**Docker** — containerização para consistência entre dev e prod

---

## 💡 Boas Práticas

### Versionamento e Reprodutibilidade
- Sempre fixe versão do modelo no Hugging Face Hub (ex.: `BAAI/bge-m3:v1`)
- Use `requirements.txt`, `poetry.lock` ou `pipenv` para dependências
- Registre experimentos, datasets e métricas no MLflow
- Documente prefixos usados (ex.: "query: " vs "passage: ")

### Monitoring em Produção
- Latência média, p50, p95 e p99 por endpoint
- Cosine drift médio entre batches novos e referência
- Volume de queries por modelo / versão
- Taxa de cache hit (se usar Redis ou similar)
- Métricas de qualidade: recall@K em queries de validação

### Evitar Problemas Comuns
- Não esqueça prefixos instruídos em modelos E5/BGE/GTE
- Sempre normalizar vetores (L2) antes de salvar no vetor DB
- Testar multilingual mesmo em aplicações "só português"
- Planejar estratégia de re-embedding ao trocar de modelo
- Evitar modelos muito grandes sem GPU/TPU dedicada
- Monitorar uso de memória e evitar OOM em batch grande

### Conexão com MLOps
- Embeddings são assets versionáveis como qualquer outro modelo
- Mudança de embedding exige re-indexação no vetor DB → impacto downstream
- CI/CD deve incluir testes automáticos de qualidade de embedding (recall, drift)
- Custo de inferência de embeddings deve ser monitorado junto com o LLM
- Use feature stores (Feast, Tecton) para embeddings reutilizáveis em múltiplos modelos

---

## 💬 Pontos para Reflexão Pré-Aula

Como monitor, reflita sobre:

1. **Por que a escolha do embedding importa mais do que o LLM em muitos casos de RAG?**
   - Qual o impacto real na qualidade final da resposta e na experiência do usuário?

2. **Como detectar e tratar drift em embeddings em produção?**
   - Quais métricas usar (cosine drift, embedding distance, KL-divergence)?
   - Quando disparar re-embedding automático?

3. **Quando vale a pena fine-tunar um embedding vs usar um modelo maior?**
   - Qual o custo vs benefício típico em termos de tempo, dados e ganho de performance?

4. **Qual o trade-off real entre latência, custo e precisão em produção?**
   - Como convencer stakeholders a aceitar um modelo "menos preciso" mas 5–10x mais rápido e barato?

5. **Como versionar embeddings sem quebrar aplicações downstream?**
   - Estratégias para migração suave (shadow mode, dual indexing, gradual rollout)?

6. **Multilingual e multimodal: quando investir nisso?**
   - Impacto em custo, complexidade e latência?
   - Quando um app "nacional" precisa de multilingual?

Esses pontos são fundamentais para enriquecer a discussão durante o encontro e conectar teoria com desafios reais de produção.

---

## 📚 Referências

### Documentação e Recursos Online

1. **sentence-transformers Documentation**  
   https://www.sbert.net/

2. **Hugging Face MTEB Leaderboard**  
   https://huggingface.co/spaces/mteb/leaderboard

3. **Hugging Face Transformers – Deployment**  
   https://huggingface.co/docs/transformers/en/deployment

4. **BGE Family (BAAI General Embedding)**  
   https://huggingface.co/BAAI/bge-m3

5. **E5 Family Documentation**  
   https://huggingface.co/intfloat/e5-mistral-7b-instruct

### Exemplos Práticos e Repositórios

6. **Qdrant + Embeddings Examples**  
   https://github.com/qdrant/examples

7. **LangChain RAG com Embeddings Custom**  
    https://python.langchain.com/docs/modules/data_connection/retrievers/

8. **FastEmbed – Embeddings Leves**  
    https://github.com/qdrant/fastembed

9. **MTEB – Massive Text Embedding Benchmark**  
    https://github.com/embeddings-benchmark/mteb