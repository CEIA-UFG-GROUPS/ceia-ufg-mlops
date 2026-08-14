# 📘 Aula 20 — CI/CD for Machine Learning (Continuous Machine Learning / CD4ML)

## Material de Estudo Prévio

Este material tem como objetivo **preparar para a aula de CI/CD aplicado a Machine Learning**, oferecendo uma base conceitual e prática sólida para acompanhar, complementar e aprofundar a discussão conduzida pelo apresentador.

⚠️ **Este conteúdo não é um guia de instruções**, mas sim um **material de estudo prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do CEIA/UFG.

---

## 🎯 Objetivo da Aula

Ao final desta aula, espera-se que os participantes compreendam:

- A distinção entre **CI**, **CD** e **CT** e o loop fechado do **CD4ML**.
- A anatomia de um pipeline de ML em **GitHub Actions** (jobs, `needs`, artifacts, comentário de PR, registro só em `main`).
- Quality gates de **dados**, **métricas de modelo** e **integridade** (SHA-256 / assinatura opcional).
- Por que o *model-diff* no PR importa — e como reproduzir o padrão do CML com tooling plain.
- Promoção via **Model Registry** como contrato de CD (ponte para Aula 19; sem retreinar aliases).
- GitOps como caminho conceitual de CD (Argo/Flux/KServe — sem operar o cluster).
- Noções de **supply chain** de modelos e pressão regulatória por **artefatos de evidência**.
- A extensão para **LLMs**: versionar prompts, eval-as-a-gate, orçamentos de custo/latência.
- Avaliar **risco de dependência** em projetos estagnados (estudo de caso CML).

---

## 🧠 Contexto: Do CI/CD de software ao CD4ML

Na **Aula 10 (1º semestre — CI/CD Básicos)** o foco foi automatizar build/teste/imagem Docker. Isso continua necessário, mas em ML o merge precisa responder a outra pergunta:

> “Este *candidato* é melhor (ou pelo menos não pior) que o contrato atual — com evidência reproduzível?”

```text
┌─────────────────────────────────────────────────────────────────┐
│                    SOFTWARE CI/CD (Aula 10)                     │
├─────────────────────────────────────────────────────────────────┤
│ lint → unit test → build image → deploy artefato determinístico │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CD4ML / CI+CD+CT (Aula 20)                   │
├─────────────────────────────────────────────────────────────────┤
│ data gate → train → metric gate → security → registry alias     │
│ (+ CT disparado por schedule / novos dados / drift — Aula 23)   │
└─────────────────────────────────────────────────────────────────┘
```

A diferença estrutural é o **eixo de dados**: o mesmo commit de código, com outro snapshot de treino, produz outro modelo. Por isso o CI de ML precisa versionar evidência (métricas, hash de dados, digest do artefato), não só “verde no lint”.

Referências âncora: [CD4ML (Fowler/Thoughtworks)](https://martinfowler.com/articles/cd4ml.html); maturidade GCP em [MLOps continuous delivery](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning); survey Eken et al., ACM Computing Surveys 58(2), Art. 39, set/2025, DOI 10.1145/3747346.

---

## ⚙️ Conceitos Fundamentais

### CI × CD × CT

| Conceito | Papel no loop | Exemplo nesta aula |
|---|---|---|
| **CI** | Validar cada mudança antes do merge | Gate de F1 vs baseline no PR |
| **CT** | (Re)treinar sob gatilho | Drift (Aula 23) → orquestrador (Aula 17) → este pipeline |
| **CD** | Entregar artefato aprovado | Registrar `@challenger`; GitOps aponta alias |

### Loop fechado CI / CD / CT

```text
 ┌──────────────┐   push/PR · schedule · novo lote · alerta drift (Aula 23)
 │   GATILHOS   │─────────────────────────────────────────────────────────┐
 └──────────────┘                                                         │
        ▲                                                                 ▼
        │                                                        ┌────────────────┐
        │                                                        │  CI (gates)    │
        │                                                        │ data→train→    │
        │                                                        │ métrica→sec    │
        │                                                        └───────┬────────┘
        │                                                                │ aprovado
        │                                                                ▼
 ┌──────┴───────┐     promove alias      ┌──────────────┐     treina     ┌──────────┐
 │ MONITORAMENTO│◄── serving / métricas ─│  CD (GitOps) │◄── Registry ──│    CT    │
 │ (Aula 23)    │                        │  Aula 21/22  │   @challenger │ (Aula 17)│
 └──────────────┘                        └──────────────┘               └──────────┘
```

Leitura: o **CI** decide se o candidato merece existir no histórico; o **CT** materializa candidatos quando há sinal; o **CD** expõe o alias aprovado; o **monitoramento** devolve gatilhos ao início do loop.

### Anatomia do workflow `ml-ci.yml` (jobs reais do lab)

```text
 on: pull_request ──────────────────────────────┐
 on: push (main/master) ──────────────────┐     │
                                          │     │
                                          ▼     ▼
                               ┌─────────────────────────┐
                               │ 01 data-validate        │
                               │ gera + valida schema    │
                               │ artifact: data-csv      │
                               └───────────┬─────────────┘
                                           │ needs:
                                           ▼
                               ┌─────────────────────────┐
                               │ 02 train-and-gate       │
                               │ treina + gate + SHA-256 │
                               │ artifact: ml-reports    │
                               │ (falha = bloqueia merge)│
                               └─────┬─────────────┬─────┘
                     always()+PR     │             │  só push main
                                     ▼             ▼
                      ┌──────────────────┐   ┌──────────────────┐
                      │ 03 comment-pr    │   │ 04 register-main │
                      │ model-diff no PR │   │ @challenger +    │
                      │ (mesmo se gate   │   │ evidência        │
                      │  falhou)         │   └──────────────────┘
                      └──────────────────┘
```

Pontos a internalizar: `needs:` encadeia contratos entre jobs; o comentário de PR **não** substitui o exit code do gate; o registro só ocorre no caminho feliz de `main`.

### Anatomia do quality gate de modelo

```text
 baseline_metrics.json          metrics.json (candidato)
         │                              │
         └──────────►  Δf1  ◄───────────┘
                        │
              Δf1_queda ≤ GATE_THRESHOLD ?
                   │              │
                  sim            não
                   │              │
              exit 0          exit 1  (+ pr_comment.md)
```

### Cadeia de evidências (o que uma auditoria percorre)

```text
 commit SHA (Git)
      │
      ▼
 hash / snapshot do dataset (treino + teste usados no gate)
      │
      ▼
 metrics.json  ←→  baseline_metrics.json   (decisão quantitativa)
      │
      ▼
 SHA-256 do artefato (models/candidate.joblib)
      │
      ├─► assinatura OpenSSF model-signing (opcional)
      │
      ▼
 registry/models.json  →  aliases @challenger / @champion
      │
      ▼
 (produção) serving resolve o alias — Aulas 19/21/22
```

Se qualquer elo faltar, o rollback vira achismo: “qual binário estava no ar?” deixa de ter resposta.

### Tabela de gates

| Fase | Ferramenta (neste lab) | Artefato de saída | Critério de falha (exit ≠ 0) |
|---|---|---|---|
| Dados | asserts Pandas (`02_validate_data`) | `data/train.csv`, `data/test.csv` válidos | schema, nulos ou faixas inválidas |
| Treino | scikit-learn RandomForest | `models/candidate.joblib`, `reports/metrics.json` | falha de execução / dependência |
| Modelo | comparação vs baseline | `reports/gate_result.json` | queda da métrica primária (`f1`) > `GATE_THRESHOLD` |
| Model-diff | markdown plain | `reports/pr_comment.md` | (não falha sozinho — documenta) |
| Segurança | hashlib (+ `model-signing` opcional) | `reports/security_report.json` | artefato ausente; assinatura ausente **não** falha (degradação graciosa) |
| Registro | JSON local estilo Aula 19 | `registry/models.json` | gate não passou; só em `MODE=main` / push `main` |

### O que roda onde (e quando se justifica)

| Onde | O que tipicamente roda | Quando se justifica | Âncora de custo (Actions) |
|---|---|---|---|
| **Laptop / script local** | Lab completo CPU (`run_ci_local.sh`) | Aprender gates, demo offline, debug | Zero cloud |
| **Runner Actions CPU** (`ubuntu-latest`) | CI do lab: dados → gate → comentário | PRs frequentes, modelos leves, free tier | Hosted com *platform charge* desde **2026-01-01** |
| **Larger runner GPU** | Treino/eval pesado (não é o lab) | Fine-tune / batches grandes | `linux_4_core_gpu` **US$ 0,052/min**; `windows_4_core_gpu` **US$ 0,102/min**; exige **Team ou Enterprise Cloud** |
| **Self-hosted** | Filas internas / GPUs on-prem | Controle de dados / FinOps próprio | Cobrança separada de **US$ 0,002/min** foi **adiada** (sem data firme) |
| **Orquestrador** (Airflow/Prefect — Aula 17) | CT: schedules, dependências de dados | Re-treino recorrente / DAGs complexas | Custo da infra do orquestrador |
| **Cluster K8s + GitOps** | CD + serving (Aulas 21/22) | Produção com reconciliação declarativa | Nós + control plane |

Regra prática: **treinar modelo grande dentro do job de PR é antipadrão** — o CI deve validar o candidato (ou um proxy barato); o CT pesado vive no orquestrador/GPU com linhagem explícita.

### Formatos e integridade do artefato

| Formato / mecanismo | Risco principal | Quando usar | Como verificar no CI |
|---|---|---|---|
| **pickle** arbitrário | RCE ao carregar de fonte não confiável | Evitar em ingressos externos | Bloquear download; preferir formatos seguros ([HF security-pickle](https://huggingface.co/docs/hub/security-pickle)) |
| **joblib** (este lab) | Ainda é ecossistema pickle-like; OK em artefato **próprio** e hasheado | Modelos sklearn internos | SHA-256 no `security_report.json` |
| **safetensors** | Baixo risco de execução de código | Pesos de redes / HF | Validar magic/header + digest |
| **OpenSSF Model Signing** | Processo/chave mal configurados | Produção / auditoria | Assinar no job de `main`; falha de assinatura pode ser hard-gate em prod |
| **Scanners** (ex.: picklescan, modelscan) | Falsos negativos; o próprio scanner pode ter CVEs | Camada adicional, não única | Atualizar scanner: CVEs do picklescan corrigidas em **0.0.31 (2025-09-02)**; `protectai/modelscan` ativo (push **2026-02-18**) |

OpenSSF **Model Signing v1.0** anunciado em **2025-04-04**; pacote PyPI `model-signing` **1.1.1 (2025-10-10)**.

### GitOps — versões de referência (ago/2026)

| Projeto | Versão | Papel no CD | O que esta aula **não** ensina |
|---|---|---|---|
| Argo CD | **v3.5.1 (2026-08-12)** | Reconcilia manifesto → cluster | Operar o painel |
| Argo Workflows | **v4.1.1 (2026-08-14)** | Pipelines nativos K8s | Autoria de Workflows |
| Argo Rollouts | **v1.9.1 (2026-07-17)** | Progressão Canary etc. | Mecânica de tráfego (**Aula 22**) |
| Flux2 | **v2.9.4 (2026-08-07)** | GitOps alternativo | Instalação do controllers |
| KServe | **v0.20.0 (2026-08-06)** | `InferenceService` / `LLMInferenceService` | Serving profundo (**Aula 21**) |

Aqui o GitOps é o **caminho conceitual** de CD depois que o registry recebe o alias; a mecânica de quanto tráfego vai para o canário é Aula 22.

### EU AI Act → o que o pipeline precisa persistir

| Data | Obrigação / marco | O que o pipeline passa a precisar produzir/persistir |
|---|---|---|
| **02/02/2025** | Práticas proibidas + AI literacy | Política + registro de quem opera o sistema |
| **02/08/2025** | Obrigações GPAI | Linhagem de treino/eval para modelos de uso geral aplicáveis |
| **27/07/2026** | **Reg. (UE) 2026/1744** em vigor (OJ 24/07/2026) | Calendário atualizado do Digital Omnibus on AI |
| **02/08/2026** | Transparência Art. 50 | Evidências de divulgação; logs de versão em produção |
| até **02/12/2026** | Graça Art. 50(2) p/ sistemas já no mercado | Plano de adequação + trilha do que já estava deployado |
| **02/12/2027** | Anexo III high-risk | Gates + registro + monitoramento contínuo auditáveis |
| **02/08/2028** | Anexo I (produtos) high-risk | Integração com conformidade de produto |

Frameworks **voluntários** de apoio: ISO/IEC 42001:2023 (AIMS) e NIST AI RMF 1.0 (jan/2023) — não substituem evidência no CI.

### CML — estudo de caso de risco de dependência

O título histórico da disciplina cita “Continuous Machine Learning”. A ferramenta **CML** (`iterative/cml`) popularizou reports de métricas/plots como comentário de PR (`cml comment create`) e o provisionamento de runners efêmeros com GPU (`cml runner launch`, via Terraform). Fatos verificados em 2026-08-14:

- O repositório **não está arquivado**, mas a atividade parou: release **v0.20.6 (2024-10-24)** e último commit em `main` na mesma data; há ~86 issues abertas e ~4.1k stars (Apache-2.0).
- Em **2025-11-18**, lakeFS anunciou stewardship do **DVC**. O FAQ compromete-se com DVC, DVCLive e a extensão VS Code, e **não menciona CML**. Não há comunicado oficial de descontinuação do CML; o que existe é **ausência de manutenção visível** em um projeto separado do DVC. Essa ambiguidade — “não arquivado, porém parado” — é exatamente o tipo de sinal que a avaliação de risco de dependência em MLOps precisa ler.
- Em contraste, DVC OSS segue ativo (PyPI **3.67.1**, 2026-03-31), enquanto `iterative/mlem` **está arquivado** (último push 2023-09-13; última release 0.4.14 em 2023-07-13).

O lab desta aula reproduz o *padrão* pedagógico (`reports/pr_comment.md` + comentário no PR) **sem** acoplar o curso ao binário CML.

### Supply chain & evidência (síntese)

O digest SHA-256 do artefato + o registro de aliases formam o mínimo viável de proveniência. Assinatura criptográfica e scanners são camadas adicionais — úteis, mas nunca substitutas de um gate quantitativo com exit code.

### LLMs no mesmo desenho

Troque “F1 vs baseline” por “score de eval vs limiar”; versionar **prompt + modelo + dataset de eval**. Prompt Registry e tracing GenAI no MLflow são **OSS** (MLflow **3.15.1** em 2026-08-03; linha 3.0.0 desde **2025-06-10**). *Deployment Jobs* do MLflow são integração **Databricks-managed** — contexto de plataforma, não feature self-hosted universal. Orçamentos de **custo/latência** entram como gates extras no mesmo esqueleto CI.

---

## 🧭 Comparativo rápido de abordagens

| Abordagem | Prós | Contras | Quando |
|---|---|---|---|
| Actions + scripts Python (este lab) | Portátil, auditável, free tier CPU | Você monta os gates | Ensino / times pequenos |
| CML | DX histórico de report em PR | Projeto estagnado | Legado — migrar o padrão |
| Plataforma cloud (SageMaker/Vertex/Azure) | Gates + registry gerenciados | Lock-in / custo | Produção enterprise |
| GitOps (Argo/Flux) + KServe | CD declarativo | Curva K8s | Pós-registry (Aula 21/22) |

---

## 📊 Casos de Uso Práticos

1. **Fintech (crédito/fraude)**: um PR “otimiza” hiperparâmetros e derruba o F1 em 3 pontos. O job `train-and-gate` falha, o comentário de *model-diff* mostra a tabela baseline vs candidato, e o merge fica bloqueado até a regressão ser revertida — o `@champion` em produção permanece intacto.
2. **Time de LLM / GenAI**: o gate primário deixa de ser F1 e passa a ser um score de eval offline + teto de custo (tokens/mês) e latência p95. Versionar só o modelo e esquecer o prompt quebra a linhagem: o “mesmo” checkpoint com outro system prompt é outro sistema.
3. **Incidente de auditoria / rollback**: após uma promoção suspeita, a cadeia commit SHA → hash dos dados → SHA-256 do `.joblib` → entrada em `registry/models.json` permite identificar exatamente qual artefato servia tráfego e restaurar o alias anterior sem caçar binários em pastas `FINAL_v2`.

---

## 🧪 Atividade Prática

Para consolidar os conceitos, execute o lab:

👉 [Atividade prática — gates CD4ML](./atividade/README.md)

Você irá:

1. Rodar o pipeline local (`scripts/run_ci_local.sh`) e medir o caminho feliz.
2. Forçar regressão (`CI_DEGRADE=1`) e inspecionar `reports/pr_comment.md`.
3. (Opcional) Copiar o lab para um repo GitHub e ver o check + comentário no PR.
4. Registrar o candidato com aliases no estilo da Aula 19.

O script resolve o interpretador sozinho (`.venv` local, `python3` ou `PYTHON=…`) — não depende do comando `python` existir no PATH do sistema.

---

## 💬 Pontos para Reflexão Pré-Aula

1. Por que um pipeline que só roda `pytest` + `docker build` ainda deixa passar um modelo pior que o `@champion`?
2. Qual é a diferença entre **falhar o job** (exit ≠ 0) e **apenas comentar** métricas no PR?
3. Se o CML não recebe commit há mais de um ano, o que isso ensina sobre o *bill of materials* do seu stack de MLOps?
4. Quem deve “possuir” o limiar `GATE_THRESHOLD` — ciência de dados, plataforma ou negócio?
5. Como Art. 50 / high-risk do EU AI Act mudam o que o pipeline precisa *persistir* além do binário do modelo?
6. Em LLMs, o que é análogo à baseline de F1 — e o que quebra se você versionar só o modelo e esquecer o prompt?
7. Em que ponto o treino dentro do runner de PR deixa de ser econômico frente a um larger runner GPU ou a um DAG no orquestrador?

---

## 📚 Referências

1. **Humble, J. & Farley, D.** *Continuous Delivery*. Addison-Wesley.
2. **CD4ML** — Thoughtworks / Martin Fowler: https://martinfowler.com/articles/cd4ml.html
3. **Gift, N. & Deza, A.** *Practical MLOps* — Cap. 4 “Continuous Delivery for Machine Learning Models”, pp. 173–210.
4. **Treveil et al.** *Introducing MLOps* — Cap. 6 “Deploying to Production”, pp. 104–120.
5. **Google Cloud** — MLOps continuous delivery & automation pipelines: https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning
6. **Eken et al. (2025).** Survey on MLOps, ACM Computing Surveys 58(2), Art. 39. DOI 10.1145/3747346.
7. **CML** — https://cml.dev · releases: https://github.com/iterative/cml/releases/tag/v0.20.6
8. **DVC joins lakeFS FAQ** — https://dvc.org/blog/dvc-joins-lakefs-your-questions-answered/
9. **OpenSSF Model Signing v1.0** — https://openssf.org/blog/2025/04/04/launch-of-model-signing-v1-0-openssf-ai-ml-working-group-secures-the-machine-learning-supply-chain/
10. **EUR-Lex** — Regulamento (UE) 2026/1744: https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng
11. **GitHub Actions** — OIDC: https://docs.github.com/en/actions/concepts/security/openid-connect · pricing: https://docs.github.com/en/billing/reference/actions-runner-pricing
12. **JFrog** — CVEs picklescan / fix 0.0.31: https://jfrog.com/blog/unveiling-3-zero-day-vulnerabilities-in-picklescan/
13. **Hugging Face** — Security pickle: https://huggingface.co/docs/hub/security-pickle

---

## 🔗 Conexões com Outras Aulas

- **Aula 10 (1º semestre — CI/CD Básicos)**: fundação Actions/Docker/secrets; esta aula adiciona gates de *modelo*.
- **Aula 17 (Pipelines / Airflow·Prefect)**: CT *dispara* o orquestrador; não reensinamos Operators.
- **Aula 18 (Feature Store)**: ponte de dados versionados para treino reproduzível.
- **Aula 19 (Model Registry)**: aliases `@champion`/`@challenger` — contrato de promoção.
- **Aula 21 (Serving)**: Triton/BentoML/vLLM — fora do escopo; só após artefato aprovado.
- **Aula 22 (Canary/Blue-Green/Shadow)**: mecânica de tráfego pós-gate.
- **Aula 23 (Drift / Evidently)**: drift como gatilho típico de CT.
- **Aula 24 (Explainability/Fairness)**: gate opcional de fairness — menção única.
