# 📘 Aula 21 — Servindo Modelos Pesados

## Material de Estudo Prévio (Monitor)

Este material tem como objetivo **preparar para a aula de Servindo Modelos Pesados**, oferecendo uma base conceitual sólida para acompanhar, complementar e aprofundar a discussão conduzida pelo apresentador.

⚠️ **Este conteúdo não é um guia de instruções**, mas sim um **material de estudo prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do CEIA/UFG.

---

## 🎯 Objetivo da Aula

Ao final desta aula, espera-se que os participantes compreendam:

- O que caracteriza um **modelo pesado** e por que servi-lo é diferente de servir um modelo comum
- As métricas fundamentais de inferência: **latência (p50/p95/p99), throughput** e, para LLMs, **TTFT e TPOT**
- O papel do **hardware** na inferência: tipos de GPUs, arquiteturas, memória e precisões numéricas
- Técnicas de **aceleração de inferência**: quantização, compilação de grafos, batching e caching
- Frameworks de serving de propósito geral: **Triton Inference Server** e **BentoML**
- Por que servir **LLMs** exige engines especializadas: **vLLM**, **SGLang**, **TensorRT-LLM**
- Como a inferência escala para **clusters**: paralelismo de modelo, *disaggregated serving* e orquestração (NVIDIA Dynamo)

---

## 🧠 Contexto: O que é um "Modelo Pesado"?

### Nem todo modelo pesado é um LLM

Quando falamos em "modelos pesados", a primeira associação hoje é com LLMs. Mas a categoria é muito mais ampla, e **modelos pesados não-LLM continuam sendo a maioria em produção**:

| Categoria | Exemplos | Por que é pesado |
|---|---|---|
| Visão computacional | YOLO (versões grandes), Segment Anything (SAM), ViT-Huge | Milhões/bilhões de parâmetros, entrada de alta resolução |
| Áudio / Fala | Whisper Large, modelos de TTS neurais | Processamento sequencial de áudio longo |
| Modelos generativos de imagem | Stable Diffusion, FLUX | Dezenas de passos de denoising por imagem |
| Embeddings / Rerankers | Modelos de embedding grandes, cross-encoders | Alto volume de requisições, batches grandes |
| Sistemas de recomendação | Deep Learning Recommendation Models (DLRM) | Tabelas de embedding gigantes (centenas de GB) |
| LLMs | Llama, Qwen, DeepSeek, GPT, Claude | Bilhões de parâmetros + geração autoregressiva |

### Por que "FastAPI + model.predict()" não é suficiente?

Nas aulas anteriores servimos modelos com uma API simples (Flask/FastAPI carregando o modelo em memória). Para modelos pesados, essa abordagem quebra por vários motivos:

1. **O modelo não cabe (ou mal cabe) na memória**: um LLM de 70B parâmetros em FP16 ocupa ~140 GB só de pesos — não cabe em nenhuma GPU única comum.
2. **Uma requisição por vez desperdiça a GPU**: GPUs são máquinas de paralelismo massivo. Processar uma requisição por vez usa uma fração mínima da capacidade.
3. **Latência importa, e muito**: um modelo de fraude precisa responder em milissegundos; um chatbot precisa começar a responder em menos de 1 segundo.
4. **Custo**: GPUs de datacenter custam dezenas de milhares de dólares (ou dezenas de dólares/hora na nuvem). Utilização baixa = dinheiro queimado.
5. **Python é um gargalo**: o GIL e o overhead do interpretador limitam a concorrência de um servidor Python ingênuo.

> **A pergunta central da aula:** como extrair o máximo de requisições por segundo de um hardware caro, sem estourar o orçamento de latência?

---

## 📏 Fundamentos: Latência, Throughput e SLOs

### Latência vs Throughput

- **Latência**: tempo para atender **uma** requisição (do request à resposta).
- **Throughput**: quantas requisições (ou tokens, ou imagens) o sistema processa **por segundo**.

Esses dois objetivos **competem entre si**. A ferramenta clássica para aumentar throughput é o **batching** (agrupar requisições para processar juntas na GPU) — mas esperar para formar o batch **aumenta a latência individual**. Todo sistema de serving vive nesse trade-off.

### Percentis: por que a média mente

- **p50 (mediana)**: metade das requisições é mais rápida que isso.
- **p95 / p99**: o que os usuários "azarados" experimentam. É aqui que os problemas aparecem.
- SLOs de latência são quase sempre definidos em percentis: *"p99 < 200ms"*.

Um sistema com média de 50ms e p99 de 3s é um sistema **ruim** — e a média nunca mostraria isso.

### Tipos de Batching

| Tipo | Como funciona | Onde aparece |
|---|---|---|
| **Static batching** | Cliente envia o batch pronto | Pipelines offline/batch |
| **Dynamic batching** | Servidor espera alguns ms e agrupa requisições que chegam | Triton, BentoML (adaptive batching) |
| **Continuous batching** | Requisições entram e saem do batch **a cada iteração** de geração | vLLM, SGLang, TensorRT-LLM (específico de LLMs) |

O *continuous batching* (também chamado *in-flight batching*) foi um dos grandes saltos de eficiência do serving de LLMs: como cada sequência termina em um momento diferente, o batch é recomposto a cada token gerado, em vez de esperar a sequência mais longa terminar.

### Métricas específicas de LLMs

A geração autoregressiva cria métricas próprias:

- **TTFT (Time To First Token)**: tempo até o primeiro token da resposta. Domina a **percepção de responsividade** em chat.
- **TPOT / ITL (Time Per Output Token / Inter-Token Latency)**: tempo médio entre tokens. Define a "velocidade de digitação" da resposta.
- **Tokens/s por GPU**: a métrica de eficiência (e custo) mais importante do lado do provedor.
- **Goodput**: throughput **que respeita o SLO** — de nada adianta gerar muitos tokens se as requisições estouram a latência prometida.

### Cold Start

Modelos pesados demoram para carregar (baixar dezenas de GB + alocar na GPU + compilar kernels). Isso torna **autoscaling** e **scale-to-zero** muito mais difíceis do que em microsserviços comuns — um novo replica pode levar **minutos** para ficar pronto.

---

## 🖥️ Hardware de Inferência: GPUs, Arquiteturas e Precisões

### CPU vs GPU vs Aceleradores

- **CPU**: serve bem modelos clássicos (sklearn, XGBoost) e modelos pequenos quantizados. Barata e elástica.
- **GPU**: obrigatória para deep learning pesado. Paralelismo massivo + memória de alta largura de banda (HBM).
- **Aceleradores dedicados**: Google TPU, AWS Inferentia/Trainium, Groq LPU — alternativas com melhor custo por token em cenários específicos, ao custo de lock-in de ecossistema.

### O catálogo NVIDIA (o que você vai encontrar na nuvem)

| GPU | Arquitetura | VRAM | Perfil de uso |
|---|---|---|---|
| T4 | Turing (2018) | 16 GB | Inferência leve/legada, barata |
| A10G / L4 | Ampere / Ada Lovelace | 24 GB | Inferência de médio porte, visão, diffusion, LLMs pequenos |
| L40S | Ada Lovelace | 48 GB | Inferência versátil, gráficos + IA |
| A100 | Ampere (2020) | 40/80 GB HBM2e | Treino e inferência séria, ainda muito comum |
| H100 / H200 | Hopper (2022) | 80 / 141 GB HBM3(e) | Padrão atual para LLMs, FP8 nativo |
| B200 / GB200 | Blackwell (2024+) | 192 GB HBM3e | Fronteira: FP4, racks NVL72 para modelos gigantes |

**Pontos a entender (mais importantes do que decorar a tabela):**

1. **VRAM é o primeiro filtro**: se os pesos + KV cache + ativações não cabem, o modelo simplesmente não roda (ou exige múltiplas GPUs).
2. **Largura de banda de memória > FLOPS para inferência de LLM**: a fase de *decode* (gerar token a token) é **memory-bound** — o gargalo é ler os pesos da HBM a cada token, não fazer contas. Por isso H200 (mais banda) gera tokens mais rápido que H100 mesmo com computação similar.
3. **Interconexão importa em multi-GPU**: NVLink/NVSwitch (centenas de GB/s entre GPUs) vs PCIe. Paralelismo de modelo entre GPUs sem NVLink sofre.
4. **Novas arquiteturas trazem novas precisões**: Hopper introduziu FP8, Blackwell introduziu FP4 — cada geração permite rodar o mesmo modelo com menos memória e mais velocidade.

### Compartilhamento de GPU

- **MIG (Multi-Instance GPU)**: particiona uma A100/H100 em até 7 instâncias isoladas de hardware — bom para servir vários modelos médios com isolamento.
- **Time-slicing**: várias cargas revezam a GPU — simples, mas sem isolamento de memória.
- **MPS (Multi-Process Service)**: processos compartilham a GPU concorrentemente.

### Precisões numéricas

| Precisão | Bytes/parâmetro | Uso típico |
|---|---|---|
| FP32 | 4 | Treino clássico; raramente necessário em inferência |
| FP16 / BF16 | 2 | Padrão de inferência em GPU |
| FP8 | 1 | Inferência em Hopper+, quase sem perda de qualidade |
| INT8 | 1 | Quantização clássica (visão, BERT-like) |
| INT4 / FP4 | 0.5 | LLMs quantizados (AWQ, GPTQ, GGUF); Blackwell nativo |

Regra de bolso para LLMs: **memória dos pesos ≈ nº de parâmetros × bytes por parâmetro**. Um 8B em FP16 ≈ 16 GB; em INT4 ≈ 4,5 GB. É por isso que quantização transforma "preciso de uma A100" em "roda numa L4".

---

## ⚡ Aceleração de Inferência

Antes de escalar horizontalmente (mais GPUs), esprema o máximo de uma GPU. As técnicas principais:

### 1. Quantização

Reduzir a precisão numérica dos pesos (e às vezes ativações) do modelo.

- **PTQ (Post-Training Quantization)**: quantiza depois do treino, sem retreinar. Rápido e geralmente suficiente.
- **QAT (Quantization-Aware Training)**: simula quantização durante o treino. Mais caro, melhor qualidade em precisões agressivas.
- **Métodos populares para LLMs**: **GPTQ**, **AWQ** (ambos INT4, para GPU), **GGUF** (formato do llama.cpp, para CPU/edge).
- **Trade-off**: menos memória e mais velocidade vs possível perda de qualidade (avalie sempre com seu benchmark!).

### 2. Compilação e otimização de grafos

Em vez de executar o modelo operação por operação no framework de treino, **compila-se o grafo** para o hardware alvo:

- **ONNX / ONNX Runtime**: formato aberto de intercâmbio + runtime otimizado multiplataforma (CPU, GPU, mobile). Caminho padrão para levar modelos sklearn/PyTorch/TF para produção enxuta.
- **TensorRT**: compilador da NVIDIA — funde kernels (*kernel fusion*), escolhe algoritmos por GPU, calibra precisões. Ganhos típicos de 2–5x sobre PyTorch puro em visão.
- **torch.compile**: compilação JIT nativa do PyTorch 2.x — ganho relevante com uma linha de código.
- **TensorRT-LLM**: a especialização do TensorRT para LLMs (kernels de atenção otimizados, in-flight batching, FP8/FP4).

### 3. Destilação e Pruning

- **Destilação**: treinar um modelo menor (student) para imitar o grande (teacher). Ex.: DistilBERT, e os modelos "mini/flash" dos provedores de LLM.
- **Pruning**: remover pesos/neurônios/camadas pouco importantes. Menos usado em produção que quantização.

### 4. Caching

- **Cache de respostas**: requisições idênticas nem chegam ao modelo.
- **KV cache (LLMs)**: guarda as chaves/valores da atenção dos tokens já processados — é o que torna a geração viável, e também o que **consome a memória** que sobra na GPU.
- **Prefix caching**: reutiliza o KV cache de prefixos repetidos (ex.: system prompt compartilhado por todas as requisições). É a especialidade do SGLang (RadixAttention).

### 5. Decodificação especulativa (LLMs)

Um modelo pequeno "rascunha" vários tokens; o modelo grande **verifica em paralelo** (verificar é mais barato que gerar). Aceita os corretos, descarta o resto. Ganhos de 2–3x em latência de geração sem perda de qualidade.

---

## 📦 Frameworks de Serving de Propósito Geral

Aqui entram os modelos pesados **não-LLM** (visão, áudio, embeddings, recomendação) e pipelines multi-modelo.

### Triton Inference Server (NVIDIA)

O "canivete suíço" do serving de alta performance. Open source, mantido pela NVIDIA.

**Conceitos-chave:**

- **Model repository**: diretório padronizado com modelos + `config.pbtxt` (formato, batching, instâncias).
- **Multi-backend**: serve TensorRT, ONNX Runtime, PyTorch (TorchScript), TensorFlow, Python puro, e até **vLLM** como backend — tudo no mesmo servidor.
- **Dynamic batching**: agrupa requisições automaticamente com tempo máximo de espera configurável.
- **Concurrent model execution**: múltiplas cópias do mesmo modelo (ou modelos diferentes) na mesma GPU.
- **Ensembles / BLS**: pipelines de modelos (ex.: pré-processamento → detecção → classificação) executados **dentro** do servidor, sem ida-e-volta pela rede.
- **Protocolos**: HTTP/REST e gRPC, métricas Prometheus nativas (conexão direta com a Aula 11!).

**Quando usar**: múltiplos modelos, múltiplos frameworks, pipelines de inferência, necessidade de extrair o máximo de GPUs NVIDIA.

**Custo**: complexidade de configuração considerável; experiência de desenvolvimento mais "infra" do que "Python".

### BentoML

O framework com foco em **experiência do desenvolvedor Python**.

**Conceitos-chave:**

- **Service**: você define o serviço de inferência como uma classe Python decorada (`@bentoml.service`) — pré/pós-processamento são código Python normal.
- **Bento**: artefato empacotado (modelo + código + dependências) — "o Docker dos modelos de ML". Gera imagem OCI para deploy em qualquer lugar.
- **Adaptive batching**: batching dinâmico configurável por endpoint, no lado do servidor.
- **Ecossistema**: integração com vLLM (BentoVLLM), diffusers, Triton como runner; BentoCloud para deploy gerenciado.

**Quando usar**: equipes Python-first, APIs de inferência com lógica customizada, empacotamento e portabilidade de modelos, protótipo → produção rápido.

**Custo**: menos performance bruta que Triton/engines especializadas em cenários extremos; a camada de abstração pode "atrapalhar" quando o gargalo é tokens/s.

### Outros nomes do ecossistema

- **TorchServe**: servidor oficial do PyTorch — **em modo manutenção limitada desde 2024/2025**; evite para projetos novos.
- **Ray Serve**: serving distribuído sobre o Ray — ótimo para **composição de modelos** e pipelines Python escaláveis; base do serving de LLM em clusters Ray.
- **KServe** (Kubernetes): CRDs de `InferenceService` no k8s — autoscaling (inclusive scale-to-zero via Knative), canary, transformers. É a camada de **orquestração**, e usa Triton/vLLM/etc. como runtime por baixo.
- **Seldon Core**: alternativa ao KServe no ecossistema k8s.
- **Provedores serverless de GPU** (Modal, Replicate, RunPod, Baseten): terceirizam o problema de infra — pague por segundo de GPU.

> **Insight importante**: essas ferramentas **não competem entre si em pé de igualdade** — elas operam em camadas. KServe orquestra → Triton/BentoML servem → TensorRT/ONNX Runtime executam. É comum usar duas ou três juntas.

---

## 🤖 Servindo LLMs: Por que é um Problema Diferente

### A anatomia de uma requisição LLM

1. **Prefill**: o prompt inteiro é processado **em paralelo** (uma passada). Fase **compute-bound**. Define o TTFT.
2. **Decode**: tokens são gerados **um por vez**, cada um exigindo ler todos os pesos da memória. Fase **memory-bound**. Define o TPOT.

Essas duas fases têm perfis de hardware **opostos** — guarde isso, pois é a motivação do *disaggregated serving* mais adiante.

### O problema do KV cache

Cada token processado gera vetores K/V que precisam ficar na GPU durante toda a geração. Para um batch grande com contextos longos, o KV cache pode ocupar **mais memória que os próprios pesos**. Gerenciar essa memória mal = desperdiçar a GPU.

### vLLM

O engine open source mais adotado.

- **PagedAttention**: gerencia o KV cache como memória virtual paginada (blocos não contíguos) — quase zero fragmentação, muito mais sequências simultâneas na mesma GPU.
- **Continuous batching**: recomposição do batch a cada iteração.
- Suporta quantização (AWQ, GPTQ, FP8), tensor parallelism, prefix caching, decodificação especulativa, multimodalidade.
- API compatível com OpenAI — trocar um provedor pago pelo seu vLLM é trocar uma URL.

### SGLang

Concorrente direto do vLLM, com força em **reuso de prefixo**:

- **RadixAttention**: organiza o KV cache numa árvore radix — prefixos compartilhados entre requisições (system prompts, few-shot, turnos de conversa) são reutilizados automaticamente.
- Excelente para **agentes, RAG e workloads estruturados** com muito prompt repetido, e para geração estruturada (JSON constrained decoding).

### TensorRT-LLM

Máxima performance em hardware NVIDIA: kernels compilados por GPU, FP8/FP4, in-flight batching. Benchmarks de 2026 mostram ~15–30% mais throughput que vLLM em H100 — ao custo de complexidade (compilar engines por modelo/GPU) e lock-in NVIDIA.

### TGI (Text Generation Inference)

Do Hugging Face — historicamente importante, mas **em modo manutenção desde dezembro de 2025**. Novos deployments devem usar vLLM ou SGLang.

### Edge / Local

- **llama.cpp / GGUF**: inferência quantizada em CPU/GPU modesta.
- **Ollama**: empacotamento amigável do llama.cpp para uso local/dev.

---

## 🌐 Escalando para Clusters

Quando uma GPU não basta — ou quando um datacenter inteiro serve o mesmo modelo.

### Paralelismo de modelo

| Estratégia | O que divide | Quando usar |
|---|---|---|
| **Tensor Parallelism (TP)** | Cada camada é fatiada entre GPUs | Modelo não cabe em 1 GPU; GPUs com NVLink no mesmo nó |
| **Pipeline Parallelism (PP)** | Camadas diferentes em GPUs/nós diferentes | Modelo não cabe em 1 nó |
| **Expert Parallelism (EP)** | Experts de um MoE em GPUs diferentes | Modelos Mixture-of-Experts (DeepSeek, Mixtral) |
| **Data Parallelism / Réplicas** | Cópias inteiras do modelo | Escalar throughput quando o modelo cabe |

TP exige comunicação intensa a cada camada → só funciona bem com NVLink. PP comunica pouco (só nas fronteiras) → tolera rede entre nós.

### Disaggregated Serving (prefill/decode)

A ideia mais importante do serving de LLM em larga escala (2025–2026):

- Prefill é compute-bound; decode é memory-bound. Rodar os dois na mesma GPU cria interferência (um prefill grande "trava" os decodes em andamento).
- Solução: **GPUs dedicadas a prefill** e **GPUs dedicadas a decode**, com o KV cache transferido entre elas via rede/NVLink.
- Permite dimensionar e otimizar cada frota separadamente (ex.: menos workers de prefill, decode em GPUs com mais banda de memória).

### NVIDIA Dynamo

Framework open source (2025) de **orquestração de inferência distribuída** — a camada acima dos engines:

- Coordena vLLM / SGLang / TensorRT-LLM em múltiplos nós
- **Disaggregated serving** nativo (prefill/decode separados)
- **Roteamento KV-aware**: manda a requisição para o worker que já tem o prefixo em cache
- **KV cache multi-tier**: transborda cache da GPU para CPU RAM / SSD
- Planejamento dinâmico de recursos e autoscaling

### Outras peças do quebra-cabeça em k8s

- **llm-d, KServe + vLLM, Ray Serve**: caminhos alternativos para servir LLMs em Kubernetes com roteamento inteligente e autoscaling.
- **Desafios operacionais**: cold start de dezenas de GB, autoscaling por métricas de fila de tokens (não CPU!), balanceamento *cache-aware*, custo por token como métrica de negócio.

---

## 🧭 Como Escolher? (Árvore de Decisão)

```text
O modelo é um LLM/modelo generativo autoregressivo?
├── NÃO
│   ├── Modelo leve (sklearn/XGBoost/rede pequena)?
│   │   └── FastAPI + ONNX Runtime resolve (Aulas anteriores)
│   ├── Um ou poucos modelos, equipe Python, DX importa?
│   │   └── BentoML
│   └── Muitos modelos / multi-framework / pipelines / máxima perf em GPU?
│       └── Triton (+ TensorRT/ONNX Runtime como backends)
└── SIM
    ├── Uso local / edge / prototipagem?
    │   └── Ollama / llama.cpp (GGUF)
    ├── Produção em 1 nó (1–8 GPUs)?
    │   ├── Workloads gerais / chat → vLLM
    │   ├── Muito prefixo repetido / agentes / JSON → SGLang
    │   └── Espremer última gota de H100/B200 → TensorRT-LLM
    └── Produção multi-nó / larga escala?
        └── Engine (vLLM/SGLang/TRT-LLM) + orquestração
            (NVIDIA Dynamo, llm-d, KServe, Ray Serve)
```

E sempre antes de tudo: **dá para usar uma API gerenciada?** Servir modelo próprio só se justifica com requisitos de privacidade, customização (fine-tuning), latência ou custo em escala.

---

## 📊 Casos de Uso Práticos

### Caso 1: Detecção de objetos em vídeo (varejo)

- **Modelo**: YOLO grande + tracker, 30 FPS por câmera, centenas de câmeras.
- **Stack típica**: TensorRT (INT8) + Triton com dynamic batching + ensembles para pré-processamento.
- **Métrica-chave**: throughput (streams por GPU); latência tem folga (~100ms).

### Caso 2: Transcrição de áudio (Whisper) em escala

- **Modelo**: Whisper Large v3.
- **Stack típica**: versão otimizada (CTranslate2/faster-whisper ou TensorRT) atrás de Triton ou BentoML; fila para processamento assíncrono.
- **Métrica-chave**: custo por hora de áudio; RTF (real-time factor).

### Caso 3: Chatbot interno com RAG

- **Modelo**: LLM open source 8–70B + modelo de embeddings.
- **Stack típica**: vLLM (ou SGLang, pelo reuso do system prompt) com API OpenAI-compatible; embeddings em serviço separado (Triton/BentoML/infinity).
- **Métricas-chave**: TTFT < 1s, custo por 1M tokens, p99 sob pico.

### Caso 4: Plataforma de inferência multi-tenant

- **Cenário**: dezenas de modelos de times diferentes compartilhando um cluster de GPUs.
- **Stack típica**: Kubernetes + KServe/Dynamo, MIG para isolamento de modelos médios, autoscaling por fila, observabilidade completa (Aula 11).
- **Métricas-chave**: utilização média das GPUs (>70% é bom), custo por requisição por tenant.

---

## 🧪 Atividade Prática

A pasta [`atividade/`](./atividade/) contém um laboratório completo que percorre a progressão da aula na prática — **baseline de latência → batching → ONNX/quantização INT8 → BentoML com adaptive batching → vLLM com continuous batching** — em dois formatos equivalentes:

- **Notebook auto-contido** ([`atividade/notebooks/aula21_pratica_colab.ipynb`](./atividade/notebooks/aula21_pratica_colab.ipynb)): roda no Google Colab (GPU T4 gratuita opcional) ou localmente.
- **Código-fonte + Docker** ([`atividade/src/`](./atividade/src/) e [`atividade/docker/`](./atividade/docker/)): o mesmo experimento como um deploy de verdade, com build multi-stage e compose (profile de GPU para o vLLM).

Instruções completas no [`atividade/README.md`](./atividade/README.md).

---

## 💬 Pontos para Reflexão Pré-Aula

Reflita sobre:

1. **Por que aumentar o batch melhora o throughput mas piora a latência?** Em que ponto parar?
2. **Por que a geração de tokens em LLMs é limitada pela memória e não pela computação?** O que isso implica na escolha da GPU?
3. **Quando vale a pena quantizar um modelo?** Como você validaria que a perda de qualidade é aceitável?
4. **Triton e BentoML resolvem o mesmo problema?** Em que situações cada um brilha? Eles podem ser usados juntos?
5. **O que o continuous batching do vLLM tem que o dynamic batching do Triton não tem?** Por que essa diferença só importa para modelos autoregressivos?
6. **Por que separar prefill e decode em GPUs diferentes (disaggregated serving)?** Que novo problema (transferência de KV cache) isso cria?
7. **Servir o próprio LLM vs usar uma API (OpenAI, Anthropic, etc.)**: a partir de que escala/requisito o self-hosting se paga?
8. **Como as métricas da Aula 11 (observabilidade) se aplicam aqui?** O que você colocaria num dashboard de um serviço vLLM?

Esses pontos são fundamentais para enriquecer a discussão durante o encontro.

---

## 📚 Referências

### Artigos fundamentais

1. **Kwon, W. et al. (2023).** *Efficient Memory Management for Large Language Model Serving with PagedAttention* (vLLM). SOSP 2023. — [https://arxiv.org/abs/2309.06180](https://arxiv.org/abs/2309.06180)
2. **Yu, G. et al. (2022).** *Orca: A Distributed Serving System for Transformer-Based Generative Models*. OSDI 2022. — O paper que introduziu o continuous batching.
3. **Zheng, L. et al. (2024).** *SGLang: Efficient Execution of Structured Language Model Programs* (RadixAttention). — [https://arxiv.org/abs/2312.07104](https://arxiv.org/abs/2312.07104)
4. **Leviathan, Y. et al. (2023).** *Fast Inference from Transformers via Speculative Decoding*. ICML 2023.
5. **P/D-Serve: Serving Disaggregated Large Language Model at Scale** — [https://arxiv.org/pdf/2408.08147](https://arxiv.org/pdf/2408.08147)

### Documentação oficial

6. **Triton Inference Server** — [https://docs.nvidia.com/deeplearning/triton-inference-server/](https://docs.nvidia.com/deeplearning/triton-inference-server/)
7. **BentoML** — [https://docs.bentoml.com/](https://docs.bentoml.com/)
8. **vLLM** — [https://docs.vllm.ai/](https://docs.vllm.ai/)
9. **SGLang** — [https://docs.sglang.ai/](https://docs.sglang.ai/)
10. **TensorRT-LLM** — [https://nvidia.github.io/TensorRT-LLM/](https://nvidia.github.io/TensorRT-LLM/)
11. **NVIDIA Dynamo** — [https://github.com/ai-dynamo/dynamo](https://github.com/ai-dynamo/dynamo)
12. **ONNX Runtime** — [https://onnxruntime.ai/](https://onnxruntime.ai/)
13. **KServe** — [https://kserve.github.io/website/](https://kserve.github.io/website/)
14. **Ray Serve** — [https://docs.ray.io/en/latest/serve/](https://docs.ray.io/en/latest/serve/)

### Comparativos e artigos práticos (2025–2026)

15. **KServe — Model Serving Frameworks Overview** — [https://kserve.github.io/website/docs/model-serving/predictive-inference/frameworks/overview](https://kserve.github.io/website/docs/model-serving/predictive-inference/frameworks/overview)
16. **vLLM vs Triton Inference Server (Inferless)** — [https://www.inferless.com/learn/vllm-vs-triton-inference-server-choosing-the-best-inference-library-for-large-language-models](https://www.inferless.com/learn/vllm-vs-triton-inference-server-choosing-the-best-inference-library-for-large-language-models)
17. **Best LLM Inference Engines 2026: vLLM, TensorRT-LLM, TGI e SGLang (Yotta Labs)** — [https://www.yottalabs.ai/post/best-llm-inference-engines-in-2026-vllm-tensorrt-llm-tgi-and-sglang-compared](https://www.yottalabs.ai/post/best-llm-inference-engines-in-2026-vllm-tensorrt-llm-tgi-and-sglang-compared)
18. **vLLM vs TensorRT-LLM vs SGLang: benchmarks em H100 (Spheron)** — [https://www.spheron.network/blog/vllm-vs-tensorrt-llm-vs-sglang-benchmarks/](https://www.spheron.network/blog/vllm-vs-tensorrt-llm-vs-sglang-benchmarks/)
19. **vLLM vs Triton vs KServe no Kubernetes (Kubenatives)** — [https://www.kubenatives.com/p/vllm-vs-triton-vs-kserve-kubernetes](https://www.kubenatives.com/p/vllm-vs-triton-vs-kserve-kubernetes)
20. **NVIDIA Dynamo: throughput distribuído (Luca Berton)** — [https://lucaberton.com/blog/nvidia-dynamo-inference-framework-distributed-serving-2026/](https://lucaberton.com/blog/nvidia-dynamo-inference-framework-distributed-serving-2026/)

### Leituras complementares

21. **Chip Huyen — *AI Engineering* (2025)**, capítulos de inference optimization.
22. **NVIDIA — LLM Inference Sizing & Benchmarking guides** (TTFT, TPOT, goodput).
23. **Databricks — LLM Inference Performance Engineering: Best Practices**.

---

## 🔗 Conexões com Outras Aulas

Este conteúdo se conecta com:

- **Aulas de Deploy e APIs (FastAPI/Docker)**: aqui evoluímos do "servir um modelo" para "servir modelos que não cabem numa máquina"
- **Aula 04 (Containers)**: Triton, vLLM e BentoML são distribuídos e implantados como containers
- **Aula 11 (Logging, Monitoramento e Observabilidade)**: TTFT, TPOT, tokens/s e utilização de GPU são exatamente as métricas que instrumentamos e monitoramos
- **Aulas de Pipelines e Orquestração**: ensembles do Triton e composição no Ray Serve são pipelines de inferência
- **Aulas de LLMOps / NLP**: o serving é a fundação de custo e latência de qualquer aplicação com LLM

---

🚀 **Leitura concluída? Venha para a aula pronto para discutir trade-offs de latência, custo e throughput — e para defender qual stack de serving você escolheria para cada cenário.**
