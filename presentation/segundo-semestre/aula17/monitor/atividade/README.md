# 🧪 Atividade Prática — Aula 17: Pipelines de Treinamento (Airflow/Prefect)

Prática guiada que implementa **o mesmo pipeline de treinamento duas vezes** — uma vez orquestrado pelo **Apache Airflow** (DAG estático, executado em Docker) e outra vez pelo **Prefect** (Flow dinâmico, executado localmente) — para comparar na prática as duas filosofias de orquestração discutidas na aula.

Pipeline: **Ingestão → Validação → Feature Engineering → Treino → Avaliação (Quality Gate) → Registro**.

---

## 🎯 O que você vai fazer

1. **Subir o Airflow** via Docker Compose e observar o DAG `pipeline_treinamento_deteccao_fraude` rodando na UI.
2. **Rodar o mesmo pipeline localmente com Prefect**, sem Docker, e comparar a experiência de desenvolvimento.
3. **Simular falhas transitórias** (na validação de dados e no Quality Gate de avaliação) e observar o comportamento de **retry automático** em ambos os orquestradores.
4. **Inspecionar o "Model Registry" simulado** (`models/registry.json`) gerado pela etapa final do pipeline, conectando com o que foi visto na Aula 19.

---

## 📂 Estrutura de Diretórios

```text
atividade/
├── README.md                          # este arquivo
├── requirements.txt                   # dependências (Prefect + scikit-learn/pandas para uso local)
├── dags/
│   └── pipeline_treinamento_fraude.py # DAG do Airflow (TaskFlow API)
├── src/
│   ├── pipeline_logic.py              # lógica de negócio compartilhada (ingestão/validação/treino/etc.)
│   └── prefect_flow.py                # Flow equivalente em Prefect
├── data/                              # (gerado em runtime) datasets intermediários
├── models/                            # (gerado em runtime) modelos treinados + registry.json
└── docker/
    ├── Dockerfile                     # imagem Airflow Standalone + dependências de ML
    └── docker-compose.yml             # stack com Airflow em modo standalone
```

---

## 🛠️ Parte 1 — Executando com Apache Airflow (Docker)

### 1. Subindo o Airflow Standalone

```bash
cd atividade/docker
docker compose up --build
```

Aguarde a mensagem no log indicando que o Airflow está pronto e anote o usuário/senha gerados automaticamente (procure por uma linha como `Login with username: admin  password: <senha gerada>` no terminal).

### 2. Acessando a UI e disparando o DAG

- Acesse [http://localhost:8080](http://localhost:8080) e faça login com as credenciais do passo anterior.
- Localize o DAG `pipeline_treinamento_deteccao_fraude`, ative-o (toggle) e clique em **Trigger DAG** para disparar uma execução manual.
- Observe a **Grid View**: cada tarefa (`t_ingerir`, `t_validar`, `t_features`, `t_treinar`, `t_avaliar`, `t_registrar`) muda de cor conforme executa.

### 3. Simulando uma Falha Transitória (Retry Automático)

Pare a stack (`Ctrl+C` ou `docker compose down`) e suba novamente definindo a variável de ambiente que ativa a falha simulada na etapa de validação:

```bash
SIMULAR_FALHA_TRANSITORIA=validacao docker compose up --build
```

Dispare o DAG novamente e observe a tarefa `t_validar`: ela tem ~50% de chance de falhar a cada tentativa. Acompanhe na UI como o Airflow executa automaticamente até 2 tentativas extras (`retries=2`) antes de marcar a tarefa como falha definitiva.

Para simular a reprovação no **Quality Gate** (etapa de avaliação), use `SIMULAR_FALHA_TRANSITORIA=avaliacao` — neste caso a tarefa falha de forma determinística (o F1-Score é forçado a `0.0`), e mesmo após os retries o pipeline falha e não chega à etapa de registro — exatamente o comportamento esperado: **um modelo ruim nunca deve ser registrado**.

### 4. Inspecionando os Artefatos Gerados

Os arquivos `data/` e `models/` da pasta `atividade/` são montados dentro do container e ficam visíveis no seu host:

```bash
cat ../models/registry.json
```

Você verá o histórico de versões "registradas" pelo pipeline, cada uma com métricas e o alias `@challenger` — o mesmo conceito de aliases estudado na Aula 19, aqui simulado em um arquivo JSON local.

---

## 🐍 Parte 2 — Executando o Equivalente com Prefect (Local, sem Docker)

### 1. Preparando o Ambiente

```bash
cd atividade
python -m venv .venv
source .venv/bin/activate   # No Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. Rodando o Flow

```bash
python -m src.prefect_flow
```

Repare que a saída no terminal é sequencial e imediata — sem precisar de UI, banco de dados de metadados ou containers. Para simular a mesma falha transitória na validação:

```bash
SIMULAR_FALHA_TRANSITORIA=validacao python -m src.prefect_flow
```

Observe no log do Prefect as tentativas de retry (`retries=2, retry_delay_seconds=5`) configuradas na task `t_validar`.

### 3. (Opcional) Observabilidade do Prefect

Se quiser ver a UI do Prefect (equivalente à Grid View do Airflow), rode `prefect server start` em outro terminal antes de executar o flow — o Prefect detecta automaticamente o servidor local e passa a reportar as execuções para ele.

---

## 💬 Perguntas para Discutir no Encontro

1. **O código em `src/pipeline_logic.py` é idêntico para o Airflow e para o Prefect.** O que isso revela sobre a responsabilidade de um orquestrador de pipelines?
2. **Ao simular `SIMULAR_FALHA_TRANSITORIA=validacao`, o comportamento de retry no Airflow (via UI) e no Prefect (via terminal) alcança o mesmo resultado final por caminhos de observação bem diferentes.** Qual você achou mais fácil de acompanhar, e por quê?
3. **Por que a etapa `t_registrar` nunca é executada quando o Quality Gate falha (`SIMULAR_FALHA_TRANSITORIA=avaliacao`)?** Que problema de produção isso evita?
4. **O Airflow, aqui, precisa de um container completo com scheduler, webserver e banco de metadados. O Prefect roda com um único comando `python`.** Em que cenário essa diferença de "peso operacional" seria decisiva na escolha da ferramenta?

---

## ⚠️ Solução de Problemas

| Sintoma | Causa provável / Solução |
|---|---|
| Não aparece a senha do Airflow no log | Rode `docker compose logs airflow \| grep -i password`, ou verifique o arquivo `standalone_admin_password.txt` dentro do container (`docker exec -it airflow-pipeline-treinamento cat /opt/airflow/standalone_admin_password.txt`). |
| DAG não aparece na UI | Confirme que a pasta `dags/` foi copiada corretamente na imagem — rode `docker compose up --build` novamente para forçar o rebuild. |
| `ModuleNotFoundError: No module named 'src'` ao rodar o Prefect localmente | Execute sempre a partir da pasta `atividade/`, usando `python -m src.prefect_flow` (e não `python src/prefect_flow.py` diretamente). |
| Quality Gate sempre reprova, mesmo sem simular falha | O dataset sintético é gerado com `random_state` fixo, então o F1-Score real deve ficar bem acima de 0.85. Se isso não ocorrer, verifique se `SIMULAR_FALHA_TRANSITORIA` não ficou definida por engano no ambiente. |

---

📖 **Material Teórico da Aula**: veja o [README do Monitor](../README.md) e o [Deep Research](../deep_research.md) para aprofundar os conceitos de DAGs, idempotência, retries e Continuous Training.
