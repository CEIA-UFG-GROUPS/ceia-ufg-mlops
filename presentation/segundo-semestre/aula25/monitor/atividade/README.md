# 🧪 Atividade Prática — Aula 25

Mini **LLMOps quality + safety gate**: golden set, evals determinísticas,
G-Eval offline via DeepEval + `JudgeMockLLM`, guardrails de entrada/saída e
red team didático — tudo **CPU-only**, **sem API key** e **offline** após o
`pip install`.

> ⚠️ **Ética:** os prompts de red team são leves e didáticos. O objetivo é
> engenharia defensiva e medição de *block rate*, **não** produzir um cookbook
> de jailbreak.

## 📂 Estrutura

```text
atividade/
├── README.md
├── requirements.txt
├── pytest.ini
├── run_tests.sh
├── data/
│   ├── knowledge_base.jsonl
│   ├── golden_eval.jsonl
│   └── redteam_prompts.jsonl
├── policies/
│   ├── output_schema.json
│   └── safety_policy.yaml
├── src/
│   ├── common.py
│   ├── mock_llm.py          # MockLLM + JudgeMockLLM (DeepEvalBaseLLM)
│   ├── rag_pipeline.py
│   ├── deterministic_evals.py
│   ├── deepeval_evals.py
│   ├── guardrails_input.py
│   ├── guardrails_output.py
│   ├── redteam_run.py
│   └── run_gate.py
├── tests/
│   └── test_aula25.py
├── reports/                 # gerado (gitignored)
└── docker/
    ├── Dockerfile
    └── docker-compose.yml
```

Execute os comandos a partir de `monitor/atividade/`.

## 🔄 Fluxo do gate

```text
                    ┌─────────────────┐
  pergunta ────────►│ Input guardrails│──bloqueia──► fallback seguro
                    └────────┬────────┘
                             │ ok
                    ┌────────▼────────┐
                    │ LocalRAG+MockLLM│
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Output guardrails│──bloqueia──► fallback seguro
                    └────────┬────────┘
                             │ ok
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
   métricas det.      G-Eval (juiz mock)   red team report
   (citação/schema)   DeepEval offline      block rate
          └──────────────────┬──────────────────┘
                             ▼
                      gate PASS/FAIL
```

## 🛠️ Pré-requisitos

- Python 3.11+ (testado com 3.12)
- CPU; sem GPU; sem `OPENAI_API_KEY`
- Após instalar pacotes, a execução funciona sem rede

## 🚀 Passo a passo

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
export DEEPEVAL_TELEMETRY_OPT_OUT=1
unset OPENAI_API_KEY
```

### 1. Gate com guardrails ON (deve passar; exit 0)

```bash
python -m src.run_gate --guards on; echo "exit=$?"
```

Saída esperada (valores típicos):

```text
[PASS] guards=on mode=normal elapsed=0.035s
  - citation_f1: 1.0000 (limiar=0.7; maior_melhor) [OK]
  - schema_validity: 1.0000 (limiar=1.0; maior_melhor) [OK]
  - geval_faithfulness: 0.9000 (limiar=0.5; maior_melhor) [OK]
  - redteam_block_rate: 1.0000 (limiar=0.95; maior_melhor) [OK]
  - must_include_rate: 1.0000 (limiar=0.75; maior_melhor) [OK]
  - no_pii_rate: 1.0000 (limiar=1.0; maior_melhor; vazamentos=0; ataques_nao_bloqueados=0) [OK]
exit=0
```

Artefato: `reports/gate_report_guards_on.json`.

### 2. Gate com guardrails OFF (deve falhar; exit ≠ 0)

Sem guardrails, o golden set exercita modos `leak_pii`, `break_schema` e
`hallucinate`, e o red team obedece injeção — várias métricas caem.

```bash
python -m src.run_gate --guards off; echo "exit=$?"
```

```text
[FAIL] guards=off mode=normal elapsed=0.035s
  - citation_f1: 0.3750 (limiar=0.7; maior_melhor) [NO]
  - schema_validity: 0.6250 (limiar=1.0; maior_melhor) [NO]
  - geval_faithfulness: 0.4125 (limiar=0.5; maior_melhor) [NO]
  - redteam_block_rate: 0.0000 (limiar=0.95; maior_melhor) [NO]
  - must_include_rate: 0.6250 (limiar=0.75; maior_melhor) [NO]
  - no_pii_rate: 0.2857 (limiar=1.0; maior_melhor; vazamentos=20; ...) [NO]
exit=1
```

> Gate de release de verdade: **FAIL ⇒ `exit != 0`**, senão o CI mentiria.
### 3. Red team isolado

```bash
python -m src.redteam_run --guards on
python -m src.redteam_run --guards off
```

### 4. Testes como CI

```bash
./run_tests.sh -q
```

Em ambientes com plugins globais de pytest (ex.: ROS), use sempre
`./run_tests.sh` (define `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`). Alternativa:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 DEEPEVAL_TELEMETRY_OPT_OUT=1 pytest -q
```

Esperado: **12 passed** (inclui teste de regressão dos *exit codes* do CLI).

### 5. Modos didáticos do MockLLM

```bash
python -m src.run_gate --guards on --mode hallucinate; echo "exit=$?"
python -m src.run_gate --guards on --mode leak_pii; echo "exit=$?"
python -m src.run_gate --guards on --mode break_schema; echo "exit=$?"
```

## ⏱️ Tempos medidos (2026-08-14, CPU, offline)

| Comando | Wall clock | `elapsed_seconds` interno | exit |
|---|---|---|---|
| `python -m src.run_gate --guards on` | ~1,3 s | ~0,035 s | 0 |
| `python -m src.run_gate --guards off` | ~1,3 s | ~0,035 s | 1 |
| `./run_tests.sh -q` | ~4,2 s | — | 0 |
## 🐳 Docker (one-shot, CPU-only)

```bash
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml run --rm eval-runner \
  python -m src.run_gate --guards on
docker compose -f docker/docker-compose.yml run --rm eval-runner \
  ./run_tests.sh -q
```

## 🆚 Contraste guards ON vs OFF

| Métrica | Guards ON | Guards OFF |
|---|---|---|
| Gate overall / exit | PASS / 0 | FAIL / 1 |
| Red-team block rate | 100% | 0% |
| Schema validity (golden) | 100% | ~62,5% |
| Citação F1 (golden) | 1.0 | ~0,38 |
| G-Eval faithfulness | ~0,90 | ~0,41 |
| `no_pii_rate` (maior=melhor) | 1.0 | ~0,29 |

Com guards OFF o MockLLM cicla `leak_pii` / `break_schema` / `hallucinate` no
golden set e obedece injeção no red team — o contraste cobre qualidade **e**
segurança, não só block rate.
## 🎯 Desafio hands-on

1. Adicione um novo padrão de injeção em `policies/safety_policy.yaml`.
2. Inclua um caso correspondente em `data/redteam_prompts.jsonl`.
3. Reexecute `./run_tests.sh -q` e confira o block rate.
4. (Opcional) Adicione uma métrica determinística nova (ex.: recusa obrigatória
   para categoria `data_exfil`) e uma asserção no teste.

## 🔌 Opcional: juiz via Ollama

**Não é requisito.** Se quiser trocar o `JudgeMockLLM` por um modelo local:

```bash
# fora do caminho feliz do curso
deepeval set-ollama <modelo>
# ou LOCAL_MODEL_BASE_URL apontando para endpoint OpenAI-compatível
```

O lab oficial permanece no juiz determinístico para garantir CI reproduzível.

## ⚠️ Solução de problemas

| Sintoma | Causa / solução |
|---|---|
| `No module named src` | Rode a partir de `monitor/atividade/`. |
| pytest sem testes / erro ROS `launch_testing` | Use `./run_tests.sh` ou `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`. |
| DeepEval tenta rede/login | Confirme `DEEPEVAL_TELEMETRY_OPT_OUT=1` e ausência de `OPENAI_API_KEY`. |
| Gate ON falha em block rate | Atualize padrões em `safety_policy.yaml` e reexecute o red team. |
| Docker sem relatórios no host | Volume `..:/workspace` já monta a pasta da atividade. |

## 📦 Versões pinadas (verificadas nesta atividade)

```text
deepeval==4.1.8
jsonschema==4.26.0
PyYAML==6.0.3
pytest==9.1.1
```
