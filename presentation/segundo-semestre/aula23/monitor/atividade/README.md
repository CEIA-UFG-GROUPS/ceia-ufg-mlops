# 🧪 Atividade Prática — Aula 23: Monitoramento e Drift (Evidently AI)

Prática guiada interativa que percorre o **ciclo completo de observabilidade de MLOps e malha fechada (*Closed-Loop Architecture*)**: desde a subida da infraestrutura de inferência em Docker, treinamento da baseline, simulação de tráfego com *Data Drift* e *Concept Drift*, até a construção do monitor com **Evidently AI**, personalização de regras de negócio e execução do pipeline de **Re-treinamento Contínuo (CT)** com *Live Reload* sem downtime!

---

## 🎯 O que você vai construir

```text
 ┌───────────────────────────────────────────────────────────────────────────────────────────┐
 │                                FLUXO DE APRENDIZADO PRÁTICO                               │
 ├───────────────────────────────────────────────────────────────────────────────────────────┤
 │ 1. Subir Infra (Docker)   -> Servidor FastAPI (8000) + Servidor Web Reports (8080)        │
 │ 2. Baseline & Modelo      -> Treinar RandomForest e gerar reference.csv (Passo 1)         │
 │ 3. Simular Tráfego        -> Enviar lotes Normal, Data Drift e Concept Drift (Passo 2)    │
 │ 4. Avaliar no Evidently   -> Criar ColumnMapping, Reports e TestSuite (Passo 3)           │
 │ 5. Desafio Hands-on       -> Personalizar o monitor em Python (Desafio do Aluno)          │
 │ 6. Remediação & CT        -> Re-treinar modelo, atualizar baseline e Live Reload (Passo 4)│
 │ 7. Bônus GenAI / LLM      -> Avaliar desvio semântico de texto em LLMs (Passo 5)          │
 └───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📂 Estrutura de Diretórios

```text
atividade/
├── README.md                           # Guia prático da atividade
├── requirements.txt                    # Dependências Python (dev local)
├── docker/
│   ├── Dockerfile                      # Imagem Python para FastAPI e servidor de relatórios
│   └── docker-compose.yml              # Stack com API FastAPI (8000) + Web Reports (8080)
└── src/
    ├── app.py                          # API FastAPI de inferência e logging assíncrono
    ├── 01_train_baseline.py            # Passo 1: Treina baseline e gera reference.csv
    ├── 02_simulate_traffic.py          # Passo 2: Envia requisições de tráfego com drift simulado
    ├── 03_evaluate_drift.py            # Passo 3: Executa Evidently AI (Report + TestSuite)
    ├── 04_remediation_ct.py            # Passo 4: Pipeline de CT, re-treino e Live Reload
    └── 05_eval_llm_text.py             # Passo 5: Avaliação de texto e LLMs (GenAI)
```

---

## 🛠️ Passo a Passo da Atividade Prática

### 1. Subindo a Infraestrutura de Serviços (Docker Compose)

Abra um terminal na pasta `atividade/docker` e suba os containers em segundo plano:

```bash
cd atividade/docker
docker compose up --build -d
```

Verifique se os serviços estão ativos:
- **API FastAPI de Inferência**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Servidor Web de Relatórios**: [http://localhost:8080](http://localhost:8080)

---

### 2. Configurando o Ambiente Local de Desenvolvimento

No seu terminal (na raiz da pasta `atividade/`), crie e ative o ambiente virtual:

(PowerShell):
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

(Linux/macOS):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 3. Passo 1 — Treinar o Modelo Baseline e Estabelecer a Referência

Execute o script de treinamento baseline:

```bash
python -m src.01_train_baseline
```

**O que este script faz**:
- Gera 2.000 registros estatísticos de concessão de crédito em `data/reference.csv`.
- Treina o modelo `RandomForestClassifier` e salva em `models/credit_model.joblib`.
- Exibe o desempenho inicial do modelo no terminal (Acurácia $\approx 97\%$).

---

### 4. Passo 2 — Simular Tráfego de Produção & Ingerir Logs

Simule a chegada de tráfego de inferência em produção enviando requisições HTTP para a API FastAPI:

```bash
python -m src.02_simulate_traffic
```

**O que observar**:
- O script envia **Lote A** (tráfego normal), **Lote B** (*Data Drift* em renda e endividamento) e **Lote C** (*Concept Drift* severo).
- A API responde a cada requisição e grava assincronamente a carga útil no log de auditoria em `data/production_logs/inference_logs.csv`.

---

### 5. Passo 3 — Avaliar o Drift com Evidently AI

Execute o script de avaliação estatística:

```bash
python -m src.03_evaluate_drift
```

**O que observar**:
- O script lê `reference.csv` e `inference_logs.csv`.
- Gera o relatório visual em `reports/data_drift_report.html` e a `TestSuite` em `reports/test_suite_report.html`.
- O terminal acusará status `🚨 FAIL (Drift Severo Detectado!)`.

**Ação no Navegador**:
Abra o link [http://localhost:8080/data_drift_report.html](http://localhost:8080/data_drift_report.html) no navegador para explorar quais features sofreram desvio!

---

### 🏋️ 6. Desafio Hands-on do Aluno (Exercício de Modificação de Código!)

Neste desafio, o objetivo é entender como **personalizar o monitoramento para regras de negócio reais**. Na prática, testes estatísticos acadêmicos puros (como o KS-Test) muitas vezes são muito sensíveis e geram "falsos alarmes" em produção. A indústria bancária, por exemplo, prefere a métrica **PSI (Population Stability Index)**, que é mais tolerante a pequenas flutuações e foca na estabilidade macro da carteira.

Abra o arquivo `src/03_evaluate_drift.py` no seu editor de código e faça as seguintes modificações para adaptar o monitor a esse cenário real:

1. **Alterar o Teste Estatístico (De Acadêmico para Padrão de Indústria)**:
   No arquivo inicial, a coluna `taxa_endividamento` utiliza o teste padrão Kolmogorov-Smirnov (`stattest="ks"`). Modifique a linha correspondente para utilizar o **PSI** com um limiar de tolerância aceito pelo mercado financeiro (`0.15`):
   ```python
   TestColumnDrift(column_name="taxa_endividamento", stattest="psi", stattest_threshold=0.15)
   ```
2. **Unificar Drift com Qualidade de Dados (Data Quality)**:
   Modelos quebram não apenas por mudança de distribuição (drift), mas também por falhas nos pipelines de dados (ex: sensores falhando, gerando valores nulos). Importe `TestNumberOfMissingValues` e adicione-o à `TestSuite` para barrar execuções se os dados estiverem corrompidos:
   ```python
   # No topo do arquivo, importe a nova métrica:
   from evidently.tests import TestNumberOfColumns, TestShareOfDriftedColumns, TestColumnDrift, TestNumberOfMissingValues

   # Dentro da lista de testes da TestSuite, adicione:
   TestNumberOfMissingValues()
   ```
3. **Re-executar a Validação**:
   Execute novamente `python -m src.03_evaluate_drift` e observe no terminal e nos relatórios em `http://localhost:8080` como a suíte de testes agora avalia o endividamento de forma mais "robusta" sob a régua do PSI, e garante a qualidade dos dados simultaneamente!

---

### 7. Passo 4 — Executar o Pipeline de Remediação & Continuous Training (CT)

Quando o monitor acusa status `FAIL`, o pipeline de retreinamento automático deve ser acionado. Execute:

```bash
python -m src.04_remediation_ct
```

**O que observar**:
1. O script rotula as novas inferências de produção.
2. Unifica o histórico antigo com os novos padrões do mercado.
3. Re-treina o `RandomForestClassifier` e atualiza `data/reference.csv`.
4. Dispara uma requisição HTTP `POST /reload` para a API FastAPI recarregar o novo modelo em memória sem cair!
5. Re-executa o Evidently AI, que agora acusa status **`🟢 PASS (SISTEMA RESTAURADO E RE-ALINHADO!)`**.

---

### 8. Passo 5 (Bônus GenAI) — Avaliação de Text Drift & LLM

Para testar o monitoramento em modelos de linguagem (LLM/GenAI):

```bash
python -m src.05_eval_llm_text
```

Abra [http://localhost:8080/text_eval_report.html](http://localhost:8080/text_eval_report.html) no seu navegador para observar a análise de desvio de tom, tamanho e vocabulário nas respostas geradas.

---

## 💬 Perguntas para Discutir no Encontro

1. **Por que o recarregamento dinâmico (`POST /reload`) na API FastAPI permite atualizar o modelo em produção sem derrubar as conexões dos clientes ativos?**
2. **Ao executar a remediação (`04_remediation_ct.py`), por que foi necessário atualizar o dataset `reference.csv` para que a suíte de testes voltasse a passar?**
3. **Se um modelo apresentar apenas Data Drift ($P(X)$), mas o Concept Drift ($P(Y|X)$) for zero, é estritamente obrigatório re-treinar o modelo imediatamente?**
4. **Como o teste de PSI se comporta em relação ao tamanho da amostra quando comparado com o teste Kolmogorov-Smirnov (KS)?**

---

## ⚠️ Solução de Problemas

| Sintoma | Causa provável / Solução |
|---|---|
| `ConnectionRefusedError: http://localhost:8000` | A API FastAPI no Docker não está rodando. Execute `cd docker && docker compose up -d` ou rode localmente com `uvicorn src.app:app --port 8000`. |
| Relatórios HTML não abrem na porta 8080 | Verifique se o container `evidently_reports_server` está ativo com `docker ps`. |
| `ModuleNotFoundError: No module named 'src'` | Execute os scripts a partir do diretório raiz `atividade/` usando a sintaxe `python -m src.01_train_baseline`. |
| `scikit-learn` compilation error / `cp314` Ninja error | Você está utilizando uma versão muito recente/alpha do Python (ex.: Python 3.14) sem pacotes binários (*wheels*) pré-compilados no PyPI. **Solução recomendada**: Utilize o Docker (`docker compose up -d`), ou crie o ambiente virtual usando Python 3.10, 3.11 ou 3.12 (`python3.11 -m venv .venv`). |

---

📖 **Material Teórico da Aula**: veja o [README do Monitor](../README.md) para aprofundar os conceitos teóricos de observabilidade, drift e ferramentas do ecossistema.
