# 🧪 Atividade Prática — Aula 18: Feature Stores com Feast

Nesta prática você constrói um **feature store** com o **Feast** e percorre o ciclo
completo de MLOps de features:

**definir features → `feast apply` → treinar com join point-in-time → materializar
(offline → online) → servir online (baixa latência) → busca vetorial / RAG**

O cenário é antifraude: um modelo consome features de cliente (`customer_stats`), e
uma base de conhecimento de atendimento (`kb_docs`) é servida por **busca vetorial** —
o ângulo 2026 da **convergência feature store + vector DB**.

A ideia central em uma frase: **uma única definição de feature, servida de forma
consistente no treino e na inferência** — é isso que elimina o *training-serving skew*.

| Caminho | Para quem | Requisitos |
|---|---|---|
| **A. Local** | Explorar comando a comando | **Python 3.10** (ver nota) + pip |
| **B. Docker** | Rodar tudo de uma vez, reproduzível | Docker |

> ⚠️ **Python 3.10**: nesta versão do Feast (0.65), a **busca vetorial** no online
> store sqlite só funciona no **Python 3.10** (a extensão `sqlite_vec` só é carregada
> nessa versão). O treino e o serving online funcionam em 3.10-3.12; **o passo de
> RAG (`rag_retrieve.py`) exige 3.10** — ou rode o Caminho B (Docker), cuja imagem já
> é `python:3.10-slim`.

---

## 🎯 O que você vai fazer

1. **Definir** features num feature repo (`entity`, `data source`, `feature view`, `feature service`).
2. **`feast apply`**: registrar as definições e provisionar o online store.
3. **Treinar** (`train.py`) com `get_historical_features` — o **join point-in-time** que evita data leakage.
4. **Materializar** (`feast materialize-incremental`): mover os valores mais recentes do offline para o online store.
5. **Servir online** (`serve_online.py`) com `get_online_features` — as mesmas features, agora com baixa latência.
6. **Busca vetorial / RAG** (`rag_retrieve.py`): o feature store guardando embeddings e servindo similaridade.

---

## 📂 Estrutura

```text
atividade/
├── README.md
├── requirements.txt            # feast==0.65.0 + sqlite-vec + sklearn
├── feature_repo/               # o "repositório de features" do Feast
│   ├── feature_store.yaml       # provider, offline/online store (sqlite, vector on)
│   ├── definitions.py           # entities, sources, feature views, feature service
│   └── data/                    # Parquets-fonte + registry.db + online_store.db (gerados)
├── src/
│   ├── common.py                # config compartilhada (EMBED_DIM, caminhos, embed())
│   ├── generate_data.py         # gera os Parquets-fonte (offline)
│   ├── train.py                 # treino com join point-in-time
│   ├── serve_online.py          # inferência com features do online store
│   └── rag_retrieve.py          # busca vetorial na base de conhecimento (RAG)
└── docker/
    ├── Dockerfile               # python:3.10-slim
    ├── docker-compose.yml
    └── run_demo.sh              # roda o ciclo completo ponta a ponta
```

> Os conceitos centrais do Feast: **Entity** (a chave), **Data Source** (de onde vêm
> os valores), **Feature View** (o contrato de um grupo de features), **Feature
> Service** (o pacote versionado que um modelo consome) e o **Registry** (catálogo
> central — *single source of truth*).

---

## 🅰️ Caminho A — Local

### A.1 — Ambiente (Python 3.10)

```bash
cd atividade
python3.10 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export PYTHONPATH=$PWD/src        # para os `from common import ...`
```

### A.2 — Gerar dados e registrar as features

```bash
python src/generate_data.py               # cria os Parquets em feature_repo/data/
cd feature_repo && feast apply && cd ..    # registra features + cria as tabelas online
```

Abra o `definitions.py` e note as duas feature views: `customer_stats` (features
numéricas) e `kb_docs` (com o campo `embedding` marcado como `vector_index=True`).

### A.3 — Treinar (join point-in-time)

```bash
python src/train.py
```

O `get_historical_features` recebe o `entity_df` (rótulos + timestamp) e, **para cada
linha, junta o valor da feature como ele era naquele instante** — é o *point-in-time
correct join* que impede vazamento de dados do futuro.

### A.4 — Materializar e servir online

```bash
cd feature_repo && feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S") && cd ..
python src/serve_online.py
```

`serve_online.py` busca apenas pela **chave** (`customer_id`) — os valores frescos vêm
do online store. Mesma definição do treino → **sem training-serving skew**.

### A.5 — Busca vetorial / RAG (ângulo 2026)

```bash
python src/rag_retrieve.py     # requer Python 3.10 (sqlite_vec)
```

O feature store guarda embeddings (`kb_docs:embedding`) e serve **similaridade** via
`retrieve_online_documents_v2` — o mecanismo de recuperação de um assistente/agente
de atendimento (RAG), conectando com a Aula 13 (agentes/MCP) e a Aula de Bancos
Vetoriais (Qdrant).

> Os embeddings do lab são **determinísticos e didáticos** (`HashingVectorizer`, sem
> download de modelo). Em produção use um encoder neural (ex.: sentence-transformers)
> — aqui o foco é o **feature store armazenando/servindo vetores**, não o encoder.

---

## 🅱️ Caminho B — Docker (tudo de uma vez)

```bash
cd atividade/docker
docker compose up --build          # roda generate -> apply -> train -> materialize -> serve -> RAG
```

A imagem é `python:3.10-slim` (para a busca vetorial funcionar nativamente) e o
`run_demo.sh` executa o ciclo completo, imprimindo métricas do modelo, as predições
online e os documentos recuperados.

Para explorar interativamente:

```bash
docker compose run --rm feast-lab bash
# dentro do container: feast ui --host 0.0.0.0   (interface web em :8888)
```

---

## 💬 Perguntas para discutir no encontro

1. Por que o **join point-in-time** (`get_historical_features`) é essencial? O que aconteceria com um `JOIN` comum por chave, ignorando o tempo?
2. O que é **training-serving skew** e como uma **única definição** de feature (offline + online) o elimina?
3. Qual a diferença de requisitos entre o **offline store** e o **online store** (latência, volume, formato)?
4. O que ganha um time quando uma feature vira um ativo **reutilizável e versionado** no registry, em vez de código copiado entre projetos?
5. No passo de RAG, o que significa o feature store **também** guardar embeddings? Onde termina o feature store e começa o vector DB?
6. `feature_view` vs `feature_service`: por que versionar o **pacote** de features que um modelo consome?

---

## ⚠️ Solução de problemas

| Sintoma | Causa provável / solução |
|---|---|
| `rag_retrieve.py` falha com `no such module: vec0` | Você não está no **Python 3.10** — use 3.10 ou rode no Docker |
| `ModuleNotFoundError: common` | Faltou `export PYTHONPATH=$PWD/src` (ou rode a partir de `src/`) |
| `feast apply` não acha os Parquets | Rode `python src/generate_data.py` **antes** do apply |
| `get_online_features` retorna `None` | Faltou `feast materialize-incremental` após o apply |
| Docker: `FileNotFoundError .../data` | Não copie `registry.db`/`online_store.db` para a imagem (há um `.dockerignore`); eles têm caminhos absolutos embutidos |
| Métrica do modelo baixa | Esperado — o dado é sintético e o foco é o **feature store**, não o modelo |

---

📖 **Material teórico**: veja o [README do monitor](../README.md) — componentes de um
feature store, online/offline, point-in-time, training-serving skew, o panorama 2026
e a convergência com vector DBs.
