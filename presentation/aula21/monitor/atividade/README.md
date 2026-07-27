# 🧪 Atividade Prática — Aula 21: Servindo Modelos Pesados

Prática guiada que percorre a progressão da aula na prática: **medir → acelerar → servir**, do batching manual até o continuous batching de LLMs.

Ela pode ser executada de **duas formas equivalentes** — escolha a sua:

| Caminho | Para quem | Requisitos |
|---|---|---|
| **A. Notebook (Colab)** | Quer executar célula a célula, sem instalar nada | Conta Google; GPU T4 gratuita (opcional, só para a Parte 5) |
| **B. Código-fonte + Docker** | Quer ver como isso vira um deploy de verdade | Docker (+ GPU NVIDIA e NVIDIA Container Toolkit apenas para o vLLM) |

O **código é o mesmo** nos dois caminhos: o notebook replica, célula a célula, o que está documentado em `src/`.

---

## 🎯 O que você vai fazer

1. **Baseline** — medir latência de inferência do jeito certo (warmup, p50/p95/p99)
2. **Batching** — levantar a curva latência × throughput e entender o trade-off central do serving
3. **Aceleração** — exportar o modelo para ONNX e quantizá-lo para INT8 (~4x menor)
4. **Serving** — subir um serviço BentoML com **adaptive batching** e comprová-lo com um teste de carga
5. **LLMs (GPU)** — servir um LLM pequeno com **vLLM** e medir o efeito do **continuous batching** (e, no Docker, TTFT/TPOT via streaming)

O modelo usado é o DistilBERT de análise de sentimento (~67M parâmetros): pequeno o bastante para rodar em qualquer lugar, grande o bastante para os efeitos aparecerem. A mecânica é idêntica para um YOLO, um Whisper ou um modelo de embeddings.

---

## 📂 Estrutura

```text
atividade/
├── README.md                      # este arquivo
├── requirements.txt               # ambiente completo (dev local)
├── requirements-export.txt        # deps só da exportação (build stage do Docker)
├── requirements-serve.txt         # deps só do runtime de serving (sem PyTorch!)
├── notebooks/
│   └── aula21_pratica_colab.ipynb # Caminho A: notebook auto-contido
├── src/                           # Caminho B: código-fonte documentado
│   ├── benchmark.py               # utilitários de medição (percentis, warmup)
│   ├── export_onnx.py             # exportação ONNX + quantização INT8
│   ├── service.py                 # serviço BentoML com adaptive batching
│   ├── load_test.py               # teste de carga do serviço (RPS, p50/p95/p99)
│   └── load_test_llm.py           # teste de carga do vLLM (TTFT, TPOT, tokens/s)
└── docker/
    ├── Dockerfile                 # build multi-stage (exporter → runtime enxuto)
    └── docker-compose.yml         # sentiment-api (CPU) + vllm (profile gpu)
```

---

## 🅰️ Caminho A — Notebook no Colab

1. Abra `notebooks/aula21_pratica_colab.ipynb` no [Google Colab](https://colab.research.google.com/) (upload do arquivo ou abrindo direto do GitHub).
2. (Opcional, necessário só para a Parte 5) Ative a GPU: `Ambiente de execução > Alterar tipo de ambiente de execução > T4 GPU`.
3. Execute as células em ordem. O notebook detecta automaticamente se há GPU e adapta o que roda.

**Notas para o Colab:**

- Sem GPU, as Partes 1–4 funcionam normalmente (a comparação CPU × GPU e a Parte 5 são puladas).
- A instalação do vLLM (Parte 5) demora alguns minutos e pode pedir reinício do runtime — por isso ela é a última parte. Se o runtime reiniciar, re-execute só a célula de instalação e continue.
- O notebook também roda localmente (Jupyter/VS Code) com `pip install -r requirements.txt`.

---

## 🅱️ Caminho B — Código-fonte + Docker

### B.1 — Serviço de sentimento (funciona em qualquer máquina, só CPU)

```bash
cd atividade/docker
docker compose up --build sentiment-api
```

O build usa **multi-stage** (leia os comentários do `Dockerfile` — ele é parte do conteúdo!):

- **Estágio 1 (exporter)**: instala PyTorch, baixa o modelo e roda `src/export_onnx.py` (ONNX + INT8) em *build time* — a imagem final é auto-contida.
- **Estágio 2 (runtime)**: só ONNX Runtime + BentoML, **sem PyTorch**. Imagem menor → pull mais rápido → **cold start menor**.

Com o serviço no ar, rode o experimento de adaptive batching (em outro terminal, na pasta `atividade/`, com `pip install httpx numpy`):

```bash
# baseline: 1 requisição por vez (nenhuma chance de formar batch)
python -m src.load_test --requests 200 --concurrency 1

# 32 clientes simultâneos: o servidor funde requisições em batches de até 32
python -m src.load_test --requests 200 --concurrency 32
```

**O que observar**: o RPS deve subir várias vezes com concorrência 32, enquanto o p50 individual sobe pouco — é o trade-off do batching em ação. Experimente variar `max_latency_ms` em `src/service.py` (5, 20, 100) e refazer o teste.

### B.2 — vLLM (exige GPU NVIDIA + NVIDIA Container Toolkit)

```bash
cd atividade/docker
docker compose --profile gpu up vllm
```

Isso sobe o **Qwen2.5-0.5B-Instruct** com API OpenAI-compatible na porta 8000 (o primeiro start baixa ~1 GB de pesos — repare no tempo: esse é o *cold start* de que a aula fala). Depois:

```bash
pip install openai numpy

# 1 requisição por vez
python -m src.load_test_llm --requests 8 --concurrency 1

# 8 simultâneas: continuous batching processa todas juntas
python -m src.load_test_llm --requests 8 --concurrency 8
```

**O que observar**: com concorrência 8, o tempo total despenca e o throughput agregado (tokens/s) se multiplica, enquanto o **TPOT** individual piora pouco. O **TTFT** pode subir um pouco (fila + prefill compartilhando a GPU) — conecte isso com a discussão de *disaggregated serving* do material do monitor.

### B.3 — Rodando sem Docker (dev local)

```bash
cd atividade
pip install -r requirements.txt
python -m src.export_onnx --output-dir models
bentoml serve src.service:SentimentService --port 3000
```

---

## 💬 Perguntas para discutir no encontro

1. Qual `max_latency_ms` você escolheria para um SLO de **p95 < 100 ms**? E para **p95 < 30 ms**? O que se perde em cada caso?
2. A versão INT8 é ~4x menor e mais rápida — como você **provaria** que a qualidade não degradou antes de promovê-la a produção?
3. Por que o ganho do batching é muito maior na GPU do que na CPU?
4. Por que o *dynamic batching* clássico (Parte 4) não é suficiente para LLMs, e o que o *continuous batching* (Parte 5) faz de diferente?
5. A imagem Docker final não tem PyTorch. Que impacto isso tem em **cold start** e **autoscaling**? E se o modelo tivesse 20 GB em vez de 65 MB?
6. Este lab roda em uma máquina. O que muda quando o modelo **não cabe em uma GPU**? (tensor/pipeline parallelism, *disaggregated serving* — material do monitor)

---

## ⚠️ Solução de problemas

| Sintoma | Causa provável / solução |
|---|---|
| `bentoml serve` falha com "Modelo não encontrado" | Rode antes `python -m src.export_onnx --output-dir models` (no Docker isso acontece no build) |
| Notebook: servidor BentoML não fica pronto | Re-execute a célula removendo `stdout/stderr=DEVNULL` para ver o log de erro |
| vLLM: erro de bfloat16 na T4 | Já tratado: usamos `--dtype half`; mantenha essa flag em GPUs pré-Ampere |
| vLLM: out of memory | Reduza `--max-model-len` e/ou `--gpu-memory-utilization` |
| Colab reinicia após instalar vLLM | Comportamento conhecido; re-execute a célula de instalação e continue da Parte 5 |
| `docker compose --profile gpu` não vê a GPU | Instale o [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) e teste com `docker run --rm --gpus all nvidia/cuda:12.4.1-base-ubuntu22.04 nvidia-smi` |

---

📖 **Material teórico**: veja o [README do monitor](../README.md) — em especial as seções de batching, quantização e a árvore de decisão de frameworks.
