# Servindo Modelos Pesados

## README do Apresentador

Este documento organiza a apresentação da aula e serve como **guia conceitual** para o expositor.
A estrutura abaixo deve ser seguida para garantir clareza, progressão lógica e alinhamento com o grupo.

> 💡 **Fio condutor sugerido**: começar com um modelo pesado "clássico" (visão/áudio) servido de forma ingênua, mostrar por que não escala, e evoluir gradualmente até LLMs em clusters. A aula é sobre **trade-offs (latência × throughput × custo)**, não sobre decorar ferramentas.

---

## 1️⃣ Motivação

### 1.1 O que é um "modelo pesado" e por que servi-lo é diferente?

- Não é só LLM: YOLO/SAM (visão), Whisper (áudio), Stable Diffusion, embeddings, recomendação (DLRM)
- O modelo não cabe (ou mal cabe) na GPU; uma requisição por vez desperdiça hardware caro
- GPU de datacenter custa dezenas de dólares/hora — utilização baixa é dinheiro queimado
- "FastAPI + model.predict()" (aulas anteriores) quebra: sem batching, sem gestão de memória, Python como gargalo

### 1.2 As métricas que governam tudo

- **Latência** (p50/p95/p99 — por que a média mente) vs **throughput** — eles competem entre si
- Batching: a alavanca central do trade-off (agrupar aumenta throughput, esperar aumenta latência)
- Para LLMs: **TTFT** (tempo até o primeiro token) e **TPOT** (tempo por token) — mostrar como cada um afeta a experiência do usuário de um chat
- Cold start de modelos gigantes: por que autoscaling aqui é difícil

### 1.3 Impacto prático

- Custo por requisição / por 1M de tokens como métrica de negócio
- Self-hosting vs API gerenciada: quando servir o próprio modelo se paga
- Casos reais: chatbot com RAG, transcrição em escala, visão computacional em tempo real

---

## 2️⃣ Como Funciona

### 2.1 Hardware: a base de tudo

- CPU vs GPU vs aceleradores (TPU, Inferentia) — visão geral rápida
- Catálogo NVIDIA na nuvem: T4 → L4/A10G → L40S → A100 → H100/H200 → B200 (arquiteturas Turing → Blackwell)
- **VRAM é o primeiro filtro**; regra de bolso: memória ≈ parâmetros × bytes por precisão
- Inferência de LLM (decode) é **memory-bound**: largura de banda de memória importa mais que FLOPS
- Precisões: FP32 → FP16/BF16 → FP8 → INT4/FP4 (cada geração de GPU habilita novas)
- Compartilhamento de GPU: MIG, time-slicing (mencionar, sem aprofundar)

### 2.2 Aceleração de inferência

- **Quantização**: PTQ vs QAT; GPTQ/AWQ (GPU), GGUF (CPU/edge); sempre validar a perda de qualidade
- **Compilação de grafos**: ONNX Runtime, TensorRT, torch.compile — o que é kernel fusion (intuição, não detalhes)
- **Batching**: static → dynamic (Triton/BentoML) → continuous (vLLM) — ESTE É UM PONTO CENTRAL DA AULA
- **Caching**: cache de resposta, KV cache, prefix caching
- Destilação e decodificação especulativa (mencionar como técnicas complementares)

### 2.3 Frameworks de serving de propósito geral (modelos não-LLM)

- **Triton Inference Server**: model repository, multi-backend (TensorRT/ONNX/PyTorch), dynamic batching, ensembles, métricas Prometheus
- **BentoML**: Service em Python, Bento como artefato empacotado, adaptive batching, DX Python-first
- Posicionamento honesto: Triton = máxima performance/multi-modelo; BentoML = produtividade/empacotamento; eles podem ser usados **juntos**
- Contexto do ecossistema (rápido): TorchServe está em manutenção (evitar); Ray Serve para composição; KServe como camada de orquestração no k8s

### 2.4 Servindo LLMs: por que engines especializadas?

- Anatomia da requisição: **prefill** (compute-bound, paralelo) vs **decode** (memory-bound, token a token)
- O problema do **KV cache**: pode ocupar mais memória que os pesos
- **vLLM**: PagedAttention (analogia com memória virtual do SO) + continuous batching; API OpenAI-compatible
- **SGLang**: RadixAttention / prefix caching — ideal para agentes e prompts repetidos
- **TensorRT-LLM**: máxima performance em NVIDIA, ao custo de complexidade
- **TGI em modo manutenção desde dez/2025** — novos projetos: vLLM ou SGLang
- Edge/local: llama.cpp, Ollama (mencionar)

### 2.5 Escala: de 1 GPU a clusters (NÃO APROFUNDAR DEMAIS — visão panorâmica)

- Paralelismo: tensor (intra-nó, precisa NVLink), pipeline (entre nós), expert (MoE), réplicas
- **Disaggregated serving**: GPUs separadas para prefill e decode — conectar com 2.4 (perfis opostos)
- **NVIDIA Dynamo**: orquestração distribuída sobre vLLM/SGLang/TRT-LLM, roteamento KV-aware, cache multi-tier
- Fechar com a **árvore de decisão** do material do monitor: qual stack para qual cenário

---

## 3️⃣ Quickstart

> 💡 **Material pronto**: a pasta `../monitor/atividade/` contém um laboratório completo (notebook Colab + código-fonte + Docker) cobrindo baseline de latência, batching, ONNX/INT8, BentoML com adaptive batching e vLLM. As demos abaixo podem ser feitas ao vivo a partir dele — ou você pode simplesmente conduzir o notebook com a turma.

### 3.1 Demo 1 — Triton servindo um modelo clássico (recomendada)

- Subir o Triton via Docker com um model repository contendo um modelo ONNX simples (ex.: ResNet ou o modelo de aulas anteriores exportado para ONNX)
- Mostrar o `config.pbtxt` e ativar `dynamic_batching`
- Fazer requisições e mostrar as métricas Prometheus em `/metrics` (conexão com a Aula 11)

```bash
docker run --rm -p 8000:8000 -p 8001:8001 -p 8002:8002 \
  -v ./model_repository:/models \
  nvcr.io/nvidia/tritonserver:25.06-py3 \
  tritonserver --model-repository=/models
```

> ⚠️ Funciona em CPU — não é preciso GPU para a demo (usar backend ONNX Runtime CPU).

### 3.2 Demo 2 — BentoML: do modelo ao serviço em poucas linhas

- Definir um `@bentoml.service` em Python servindo o mesmo modelo
- Mostrar o adaptive batching na configuração
- `bentoml build` + `bentoml containerize` → o "Bento" como artefato portátil
- Comparar a DX com o Triton: mesmo problema, filosofias diferentes

### 3.3 Demo 3 — vLLM (se houver GPU disponível; senão, mostrar gravado ou via Colab)

- Subir um LLM pequeno (ex.: Qwen 1.5B / Llama 3B) com API OpenAI-compatible:

```bash
docker run --gpus all -p 8000:8000 vllm/vllm-openai:latest \
  --model Qwen/Qwen2.5-1.5B-Instruct
```

- Disparar N requisições concorrentes e observar o **continuous batching** em ação (tokens/s agregado cresce, TPOT individual estável)
- Alternativa sem GPU: **Ollama** local para o conceito, deixando claro que é ferramenta de dev, não de produção em escala

### 3.4 Boas práticas para fechar

- Meça antes de otimizar: estabeleça baseline de p50/p95/p99 e tokens/s
- Escolha a GPU pela **memória e banda**, não só pelo preço
- Quantize com validação de qualidade no SEU benchmark
- Defina SLOs de inferência (TTFT/TPOT para LLMs) e monitore desde o dia 1 (Aula 11)
- Não construa cluster antes de esgotar uma GPU: quantização + engine certa + batching resolvem a maioria dos casos
- Prefira API gerenciada até que privacidade, customização ou escala justifiquem self-hosting
