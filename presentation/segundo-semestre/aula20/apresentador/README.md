# CI/CD for Machine Learning (Continuous Machine Learning / CD4ML)

Este documento organiza a apresentação da aula e serve como **guia conceitual** para o expositor.
A estrutura abaixo é uma sugestão a ser seguida para garantir clareza, progressão lógica e alinhamento com o grupo.

> 💡 **Fluxo sugerido**: partir do CI/CD de *software* visto na **Aula 10 (1º semestre — CI/CD Básicos)** e mostrar por que ele é insuficiente para ML — o artefato agora é um modelo probabilístico, os dados mudam, e “passou no lint” não prova valor de negócio. Introduzir a tríade **CI / CD / CT** e o loop fechado do **CD4ML** (Thoughtworks). Percorrer a anatomia de um pipeline em GitHub Actions com quality gates (dados → treino → métricas → segurança → registry). Fazer a demo do lab: abrir um PR que degrada o modelo, ver o check vermelho + comentário de *model-diff*, corrigir, mergear e registrar. Fechar com uma seção **honesta** sobre a ferramenta **CML** (o que ela fazia bem, e por que depender dela hoje é um risco de MLOps em si) e a extensão para LLMs (prompt versioning + eval-as-a-gate).

---

## 1️⃣ Motivação

### 1.1 Por que CI/CD de software não basta para ML?

- **Dois artefatos, dois contratos**: no software clássico, o artefato é um binário/imagem cujo comportamento é determinístico dado o código. Em ML, o artefato é um modelo cujo comportamento depende de **código + dados + hiperparâmetros + ambiente**.
- **Testes verdes ≠ modelo útil**: unit tests e linters não detectam regressão de F1, vazamento de feature, drift silencioso ou pickle malicioso.
- **O custo de um merge ruim**: promover um *challenger* pior que o `@champion` (Aula 19) pode gerar perda financeira imediata — o pipeline precisa **bloquear** isso, não só “avisar”.

### 1.2 O que o grupo vai sair sabendo fazer

- Distinguir **CI**, **CD** (entrega/deploy) e **CT** (*Continuous Training*) e descrever o loop fechado CD4ML.
- Ler a anatomia de um workflow GitHub Actions orientado a ML: `needs:`, artifacts, comentário de PR, job só em `main`.
- Definir quality gates (dados, métricas, segurança) com **exit code ≠ 0** como contrato de merge.
- Relacionar promoção via **Model Registry** (aliases) como contrato de CD — sem reexplicar a Aula 19.
- Avaliar risco de dependência em ferramentas estagnadas (caso **CML**).

### 1.3 Conexão com outras aulas (ponte, sem retreinar)

- **Aula 10 (1º sem.)**: YAML básico, Docker, secrets — aqui subimos para gates de *modelo*.
- **Aula 19**: registry / `@champion` / `@challenger` — o CD *aponta* o alias; não reimplementamos MLflow.
- **Aula 22**: Canary/Blue-Green/Shadow — mecânica de tráfego *depois* do gate passar.
- **Aula 23**: drift/Evidently — tipicamente o **gatilho** de CT que dispara o pipeline desta aula.

---

## 2️⃣ Como Funciona

### 2.1 CI vs CD vs CT — o loop fechado

```text
┌──────────────────────────────────────────────────────────────────────────┐
│                         LOOP CD4ML (visão de aula)                       │
├──────────────────────────────────────────────────────────────────────────┤
│  CI  → valida código/dados/modelo a cada PR (bloqueia regressão)         │
│  CT  → (re)treina quando há sinal (novo dado, drift, schedule)           │
│  CD  → promove artefato aprovado via registry/GitOps para serving        │
│                                                                          │
│   PR/commit ──► gates ──► register @challenger ──► deploy progressivo    │
│       ▲                         │                        │               │
│       └──────── monitor/drift ──┴── (Aula 23 dispara CT) ┘               │
└──────────────────────────────────────────────────────────────────────────┘
```

| Sigla | Pergunta que responde | Falha típica se ausente |
|---|---|---|
| **CI** | “Este candidato é *seguro o bastante* para mergear?” | Modelo pior entra em `main` sem evidência |
| **CT** | “Quando e com o quê re-treinamos?” | Treino manual, sem linhagem, sem gatilho |
| **CD** | “Como o artefato aprovado chega à produção?” | Copiar `.joblib` na mão / Big Bang (Aula 22) |

Referência clássica: [CD4ML (Martin Fowler / Thoughtworks)](https://martinfowler.com/articles/cd4ml.html). Níveis de maturidade GCP: [MLOps continuous delivery](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning).

### 2.2 Anatomia de um pipeline CD4ML em GitHub Actions

```text
 pull_request / push(main)
        │
        ▼
 ┌──────────────┐   needs    ┌──────────────────┐   always()   ┌──────────────┐
 │ data-validate│ ─────────► │ train-and-gate   │ ───────────► │ comment-pr   │
 │ schema/nulls │            │ métricas+SHA-256 │              │ model-diff   │
 └──────────────┘            └────────┬─────────┘              └──────────────┘
                                      │ (só push main + gate OK)
                                      ▼
                             ┌──────────────────┐
                             │ register-main    │
                             │ @challenger +    │
                             │ evidência        │
                             └──────────────────┘
```

Pontos pedagógicos a enfatizar ao vivo:

1. **`permissions` mínimo** (conteúdo `read`; `pull-requests: write` só no job de comentário).
2. **`concurrency`** para cancelar runs redundantes no mesmo ref.
3. **Artifact** como contrato entre jobs (`upload`/`download`).
4. **Exit code do gate** = required check que bloqueia merge.
5. **Comentário de PR** = o que o CML popularizou (`cml comment create`), feito com `actions/github-script` + `GITHUB_TOKEN`.

### 2.3 Quality gates: dados → treino → métricas → segurança → registry

| Gate | O que prova | Falha = |
|---|---|---|
| Dados | Schema, nulos, faixas | Dataset quebrado / silent schema drift |
| Modelo | Δ métrica vs baseline ≤ limiar | Regressão de desempenho |
| Segurança | SHA-256 (+ assinatura opcional) | Artefato sem integridade auditável |
| Registry | Só registra se gate passou | Candidato ruim vira alias |

Promoção via registry é um **contrato**: o serving resolve `models:/fraude_credito@champion` (Aula 19). O CD desta aula *escreve* o alias; o *como* o tráfego muda é Aula 22.

### 2.4 GitOps como caminho de CD (conceitual)

- Manifesto Git (Argo CD / Flux) aponta para a versão/alias aprovada.
- Versões de referência (ago/2026): Argo CD **v3.5.1**, Argo Workflows **v4.1.1**, Argo Rollouts **v1.9.1**, Flux2 **v2.9.4**, KServe **v0.20.0** (inclui CRD `LLMInferenceService`).
- Esta aula **não** ensina operar Argo — só posiciona GitOps como CD após o gate.

### 2.5 Supply chain de modelo (básico)

- Preferir **joblib/safetensors** a pickle arbitrário de fontes não confiáveis ([HF security-pickle](https://huggingface.co/docs/hub/security-pickle)).
- OpenSSF **Model Signing v1.0** (anunciado **2025-04-04**); pacote PyPI `model-signing` **1.1.1 (2025-10-10)**.
- `protectai/modelscan` ativo (último push **2026-02-18**); picklescan corrigiu CVEs em **0.0.31 (2025-09-02)**.

### 2.6 Pressão regulatória → artefatos de evidência no pipeline

- Digital Omnibus on AI = **Regulamento (UE) 2026/1744** (OJ **24/07/2026**, vigência **27/07/2026**).
- Transparência Art. 50: desde **02/08/2026** (grace Art. 50(2) até **02/12/2026** para sistemas já no mercado).
- Anexo III high-risk adiado para **02/12/2027**; Anexo I produtos **02/08/2028**.
- ISO/IEC 42001:2023 e NIST AI RMF 1.0 são frameworks **voluntários**.
- Mensagem de aula: o pipeline deve **gerar evidência** (métricas, hash, comentário de PR, registro) — não só “passar”.

### 2.7 Extensão LLM (curta)

- Versionar **prompt** (MLflow Prompt Registry é OSS; MLflow **3.15.1** em 2026-08-03; MLflow 3.0.0 em **2025-06-10**).
- **Eval-as-a-gate**: suíte de casos + limiar de qualidade (análogo ao F1 desta aula).
- Orçamentos de **custo/latência** como gates adicionais.
- *Deployment Jobs* do MLflow são integração **Databricks-managed** — citar só como contexto de plataforma, não como feature OSS self-hosted.

### 2.8 CML: o que foi, e o risco de depender disso hoje

| Fato | Detalhe verificado |
|---|---|
| Projeto | `iterative/cml` — **não arquivado**, porém **estagnado** |
| Última release | **v0.20.6 (2024-10-24)** |
| Último commit em `main` | **2024-10-24** |
| Sinais | ~86 issues abertas; ~4.1k stars; Apache-2.0 |
| O que fazia bem | `cml comment create` (report no PR); `cml runner launch` (runners efêmeros via Terraform) |
| lakeFS + DVC | Anúncio **2025-11-18**: stewardship do **DVC**; FAQ compromete-se com DVC/DVCLive/VS Code e **não menciona CML** |
| Como falar | CML é projeto **separado e estagnado**, sem comunicado oficial de manutenção — **não** diga que foi arquivado nem formalmente excluído do deal |

**Lição de MLOps**: o valor pedagógico (model-diff no PR) permanece; a implementação desta aula usa **tooling plain** (Python + `github-script`) para não acoplar o curso a um projeto parado. Paralelo: `iterative/mlem` **está arquivado** (último push 2023-09-13). DVC OSS segue ativo (PyPI **3.67.1**, 2026-03-31).

---

## 3️⃣ Quickstart & Demos

> 💡 **Ao vivo**: preferir a Camada 2 (`bash scripts/run_ci_local.sh`) se a rede/GitHub falhar; a Camada 1 (PR real) é o momento “aha” se houver conta GitHub.

### 3.1 Demo 1 — Caminho feliz local (~2 s medidos no lab)

```bash
cd presentation/segundo-semestre/aula20/monitor/atividade
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
bash scripts/run_ci_local.sh          # exit 0
MODE=main bash scripts/run_ci_local.sh  # registra @challenger
```

### 3.2 Demo 2 — Quebrar o gate de propósito

```bash
CI_DEGRADE=1 bash scripts/run_ci_local.sh   # exit 1
cat reports/pr_comment.md                   # tabela de regressão
```

### 3.3 Demo 3 — PR no GitHub (Camada 1)

Aluno copia `atividade/` para a **raiz** de um repo próprio (ver README da atividade — caveat obrigatório), abre PR que degrada o modelo, observa check vermelho + comentário, corrige e mergeia.

---

## 4️⃣ Boas Práticas para Fechar a Aula

1. **Gate com exit code** é o contrato — comentário sozinho não bloqueia merge.
2. **Baseline versionada** (`baselines/baseline_metrics.json`) é parte do código, não um número mágico.
3. **Menor privilégio** no Actions; OIDC keyless para nuvem (padrão atual).
4. **Não acoplar** o curso a ferramentas estagnadas — extrair o padrão, trocar a implementação.
5. **CT ≠ CI**: drift (Aula 23) dispara orquestrador (Aula 17); esta aula é o *conteúdo* do pipeline de validação/promoção.
6. **Fairness/explainability** (Aula 24) pode ser um gate opcional — uma menção basta aqui.

### Custos Actions (contexto, sem inventar datas)

- Preços de hosted runners (com platform charge) vigoram desde **2026-01-01**.
- Cobrança separada de **US$0.002/min** para self-hosted foi **adiada** (sem data firme).
- GPU larger runners: `linux_4_core_gpu` **US$0,052/min**, `windows_4_core_gpu` **US$0,102/min** (Team/Enterprise Cloud).
