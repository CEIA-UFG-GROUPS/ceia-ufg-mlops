# LLMOps: Avaliação e Guardrails

## README do Apresentador

Esta é a **penúltima aula** do 2º semestre — logo antes do projeto final ponta a ponta
(Aula 26). O fio condutor é simples: **um LLM convincente não é um LLM liberável**.
A turma deve sair sabendo montar um *quality + safety gate* offline (golden set,
métricas determinísticas, juiz com rubrica, guardrails e red team) e interpretá-lo
como evidência de governança — não como teatro de slides.

> 💡 **Fluxo sugerido**: abrir com um assistente RAG que “parece certo”, mas cita
> fonte inexistente e vaza um CPF sintético. Mostrar o gate **PASS** com
> guardrails ON e o mesmo pipeline **FAIL** com guardrails OFF. Em seguida subir
> o nível: metodologia de evals, LLM-as-a-Judge rigoroso, avaliação agentic/RAG
> além da tríade, taxonomia de injeção + *lethal trifecta*, segurança de MCP e
> artefatos de governança (EU AI Act / NIST). Fechar apontando para o projeto
> final: Aula 26 deve *reusar* este gate, não reinventá-lo.

---

## 1️⃣ Motivação

### 1.1 O demo que passa no olho humano e falha no CI

- Métricas de infraestrutura (latência, HTTP 200) não capturam alucinação,
  citação falsa ou vazamento de PII.
- A Aula 23 tratou drift/TextEvals e LLM-as-a-Judge como *monitoramento*; aqui o
  foco é **avaliação como gate de release** e **guardrails como controle**.
- A Aula 24 escolheu arquitetura (FM vs fine-tuning vs RAG); Aula 25 pergunta:
  **como sabemos que a escolha continua segura e útil após cada mudança?**

### 1.2 O que a turma deve sair sabendo fazer

- Montar e versionar um golden eval set com citações esperadas.
- Separar evals **baratos/determinísticos** de evals **baseados em juiz**.
- Rodar G-Eval-style com rubrica — offline, sem API key.
- Ligar guardrails de entrada/saída (fail-closed) a um relatório de red team.
- Explicar por que “LLM-as-a-Judge” sem calibração humana é evidência fraca.
- Citar riscos MCP (tool poisoning, rug pull, confused deputy) sem reensinar a
  construir o servidor (isso foi Aula 13).

---

## 2️⃣ Como Funciona

### 2.1 Metodologia de avaliação (o núcleo de LLMOps)

```text
┌──────────────┐   ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Golden set   │→  │ Offline eval │→  │ CI gate      │→  │ Online/shadow│
│ versionado   │   │ + red team   │   │ pass/fail    │   │ amostragem   │
└──────────────┘   └──────────────┘   └──────────────┘   └──────────────┘
```

| Dimensão | Offline | Online |
|---|---|---|
| Dados | Golden set / synthetic | Produção amostrada |
| Rótulo | Esperado conhecido | Humano / proxy / juiz |
| Uso | Gate de release | Drift, regressão, UX |
| Custo | Previsível | Variável com tráfego |

- **Error analysis** > média cega: fatie por tipo de falha (citação, PII,
  schema, injeção).
- **Tamanho amostral**: intuição — n pequeno detecta falhas grossas; n maior é
  necessário para comparar juízes/modelos (ver RewardBench 2, JudgeBench).
- Evals como **CI gates** espelham quality gates do Model Registry (Aula 19),
  mas com artefatos específicos de GenAI.

### 2.2 LLM-as-a-Judge com rigor

- **Pointwise** (nota 0–10) vs **pairwise** (A≻B): rankings podem não transferir
  (“Reliability without Validity”, arXiv:2606.19544).
- **G-Eval**: critérios + passos + rubrica; score bruto sem calibração humana é
  insuficiente.
- Vieses conhecidos: posição, verbosidade, auto-preferência, sensibilidade a
  prompt do juiz.
- **Meta-avaliação**: meça o juiz contra humanos (kappa, acordo); harnesses como
  Judge Reliability Harness (arXiv:2603.05399).

### 2.3 Avaliação agentic e RAG além da tríade

- Agentic: correção de *tool calls*, trajetórias, multi-turn (τ-bench /
  τ²-bench; τ³-bench é rename no repo Sierra — sem paper dedicado).
- RAG além de faithfulness / context precision / answer relevance:
  - suficiência de contexto;
  - verificação de atribuição/citação;
  - alucinação em nível de *span* (RAGTruth, ACL 2024).
- Tríade introdutória: Aula 23; aqui aprofundamos gates e evidências.

### 2.4 Guardrails e ameaças

```text
  request ──► input guard ──► modelo/agent ──► output guard ──► resposta
                 │                 │                 │
                 ▼                 ▼                 ▼
            injecção/tools    inline policy     PII/schema/budget
```

- **Fail-open** vs **fail-closed**: em segurança, preferir fail-closed.
- Overhead: latência e custo do classificador — meça no gate.
- **Lethal trifecta** (Willison, 2025-06-16): dados privados + conteúdo não
  confiável + comunicação externa.
- OWASP GenAI/LLM Top 10 (edição 2026) e Top 10 for Agentic Applications
  (2025-12-09).
- MCP (spec 2026-07-28): core *stateless*; Roots/Sampling/Logging deprecados.
  Riscos: tool poisoning, rug pull, confused deputy — cruzar com Aula 13.

### 2.5 Ferramentas (versão verificada em 2026-08-14)

| Ferramenta | Nota de ensino |
|---|---|
| **DeepEval 4.1.8** | Lab oficial; juiz local via `DeepEvalBaseLLM` |
| **Ragas 0.4.3** | `evaluate()` depreciado → `@experiment`; repo vibrantlabsai/ragas |
| **MLflow 3.15.1** | API GenAI: `mlflow.genai.evaluate()` |
| **Inspect AI 0.3.258** | UK AI Security Institute |
| **HELM** | maintenance mode desde 2026-06-01 |
| **Guardrails AI Hub** | hard cutoff 2026-08-06 — caso didático de hub hospedado |
| **NeMo Guardrails 0.23.0** | NVIDIA-NeMo/Guardrails |
| **PyRIT / garak** | red team OSS |

---

## 3️⃣ Quickstart & Demos

Na pasta `monitor/atividade/`:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DEEPEVAL_TELEMETRY_OPT_OUT=1
unset OPENAI_API_KEY

python -m src.run_gate --guards on; echo "exit=$?"    # PASS, exit=0
python -m src.run_gate --guards off; echo "exit=$?"   # FAIL, exit=1
./run_tests.sh -q
```

### Demo ao vivo (ordem sugerida)

1. Abrir `data/golden_eval.jsonl` e `policies/safety_policy.yaml`.
2. Rodar gate ON → mostrar `reports/gate_report_guards_on.json`.
3. Rodar gate OFF → block rate de red team cai a ~0%.
4. `python -m src.redteam_run --guards on` vs `--guards off`.
5. Mencionar upgrade opcional com Ollama (`deepeval set-ollama`) — **nunca**
   requisito.

Tempos medidos nesta máquina (CPU, offline, 2026-08-14): gate ~1,3 s wall /
~0,035 s interno; `./run_tests.sh` ~4,2 s (**12 passed**, inclui regressão de
exit code).

---

## 4️⃣ Boas Práticas para Fechar a Aula

1. Golden set versionado + error analysis por fatia de falha.
2. Juiz com rubrica + amostra humana de calibração.
3. Guardrails fail-closed na borda; política como código (`policies/`).
4. Red team didático no CI — não um cookbook de jailbreak.
5. Evidências de governança: relatórios JSON do gate = artefato auditável.
6. Ponte explícita para **Aula 26**: o projeto final deve incorporar este gate.

## 💬 Pontos para Reflexão Pré-Aula

1. Por que um juiz LLM com kappa alto ainda pode ter validade baixa entre tarefas?
2. Fail-open ou fail-closed quando o classificador de PII estoura timeout?
3. O que muda na ameaça se o agente ganha `http_fetch` + acesso a dados privados?
4. Como o cutoff do Guardrails AI Hub ilustra risco de dependência de hub remoto?
5. Que artefato você anexaria a um PR para evidenciar “eval passou”?

## 📚 Referências

- Haviv & Gift, *Implementing MLOps in the Enterprise*, Cap. 8 (LLMs), pp. 526–541.
- DeepEval docs; Ragas migration v0.3→v0.4; Inspect AI; OWASP GenAI LLM Top 10 2026.
- arXiv:2506.01937, 2410.12784, 2606.19544, 2603.05399, 2401.00396, 2501.18837.
- EU AI Act + Digital Omnibus (Reg. UE 2026/1744); NIST AI 600-1.

## 🔗 Conexões com Outras Aulas

- **Aula 13 (2º sem):** construir MCP — aqui só *segurança* MCP.
- **Aula 18:** Feature Store / embeddings / bases de RAG.
- **Aula 19:** Model Registry e quality gates genéricos.
- **Aula 21:** serving (vLLM/Triton/BentoML).
- **Aula 23:** drift, TextEvals, tríade RAG, juiz como monitoramento.
- **Aula 24:** FM vs FT vs RAG; fairness; SHAP/LIME.
- **Aula 11 (1º sem):** logging/observabilidade (LangSmith citado no material).
- **Aula 26:** projeto final E2E — consumir este gate.
