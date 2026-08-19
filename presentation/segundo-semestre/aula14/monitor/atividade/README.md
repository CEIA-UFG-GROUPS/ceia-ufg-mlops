# 🧪 Atividade Prática — Aula 14

Mini **gate de qualidade de dados e de código**: contrato versionado em YAML,
validação com **Great Expectations 1.x**, testes unitários e comportamentais
com **Pytest** (+ Hypothesis) e um CLI que **quebra o CI** quando reprova.
Tudo **CPU-only**, **offline** após o `pip install`, **sem API key**.

> 🎯 O contraste que a aula quer mostrar: um mesmo pipeline **passa** com dados
> conformes e **falha com `exit 1`** quando o upstream muda — e um bug de
> vazamento passa por **todas** as métricas, sendo pego apenas pelo teste
> unitário.

## 📂 Estrutura

```text
atividade/
├── README.md
├── requirements.txt
├── pytest.ini
├── run_tests.sh
├── contracts/
│   └── credito_v1.yaml        # contrato de dados (fonte da verdade)
├── data/                      # gerado (gitignored)
├── reports/                   # gerado (gitignored)
├── src/
│   ├── common.py              # paths, IO, ambiente offline
│   ├── contract.py            # YAML → ExpectationSuite (GE 1.x)
│   ├── generate_data.py       # dataset sintético + injeção de defeitos
│   ├── features.py            # transformações (a unidade sob teste)
│   ├── model.py               # modelo + checagens comportamentais
│   ├── validate_data.py       # runner do Great Expectations
│   └── run_gate.py            # gate: dados → modelo → exit code
├── tests/
│   ├── conftest.py            # fixtures de sessão
│   ├── test_contract.py       # o contrato também é testado
│   ├── test_features.py       # unitários + fronteiras + property-based
│   ├── test_data_quality.py   # GE dentro do pytest
│   ├── test_model_behavior.py # pós-treino: direcional / invariância / MFT
│   └── test_gate_cli.py       # regressão de exit code
└── docker/
    ├── Dockerfile
    └── docker-compose.yml
```

Execute todos os comandos a partir de `monitor/atividade/`.

## 🔄 Fluxo do gate

```text
                    ┌──────────────────┐
   CSV bruto ──────►│ contrato (YAML)  │
                    └────────┬─────────┘
                             │ 24 expectativas
                    ┌────────▼─────────┐
                    │ Great Expectations│──reprova──► exit 1 (não treina)
                    └────────┬─────────┘
                             │ aprova
                    ┌────────▼─────────┐
                    │ split + treino   │
                    └────────┬─────────┘
                             │
          ┌──────────────────┼──────────────────┐
          ▼                  ▼                  ▼
    ROC AUC mínimo    expectativa        invariância +
                      direcional         funcionalidade mínima
          └──────────────────┬──────────────────┘
                             ▼
                    gate PASS (0) / FAIL (1)
```

Dados antes do modelo: treinar sobre dados que violam o contrato produz métrica
bonita e modelo errado.

## 🛠️ Pré-requisitos

- Python 3.11+ (testado com 3.12.12)
- CPU; sem GPU; sem chave de API
- Após o `pip install`, tudo roda sem rede

## 🚀 Passo a passo

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
export GX_ANALYTICS_ENABLED=false
```

### 1. Gerar os dados

```bash
python -m src.generate_data --variant clean
python -m src.generate_data --variant corrupted
```

### 2. Validação de dados isolada

```bash
python -m src.validate_data --dataset clean; echo "exit=$?"
```

```text
[PASS] contrato=credito v1 linhas=4000 expectativas=24/24 (100.0%)
📄 relatório: reports/data_validation_clean.json
exit=0
```

```bash
python -m src.validate_data --dataset corrupted; echo "exit=$?"
```

```text
[FAIL] contrato=credito v1 linhas=4000 expectativas=15/24 (62.5%)
  - [NO] expect_column_values_to_not_be_null (score_credito) observado=None
  - [NO] expect_column_values_to_be_between (score_credito) observado=None
  - [NO] expect_table_columns_to_match_set (<tabela>) observado=['credit_score', …]
  - [NO] expect_column_values_to_be_unique (id_cliente) unexpected=21
  - [NO] expect_column_values_to_be_between (idade) unexpected=24
  - [NO] expect_column_values_to_not_be_null (renda_anual) unexpected=100
  - [NO] expect_column_mean_to_be_between (renda_anual) observado=106827.83…
  - [NO] expect_column_values_to_be_of_type (score_credito) observado=None
  - [NO] expect_column_values_to_be_in_set (inadimplente) unexpected=30
exit=1
```

### 3. Gate completo

```bash
python -m src.run_gate --dataset clean; echo "exit=$?"
```

```text
[PASS] dataset=clean elapsed=0.142s
  - contrato_de_dados: 24/24 expectativas; falhas=0 (máximo tolerado=0) [OK]
  - desempenho_minimo: roc_auc=0.7636 (limiar=0.7) [OK]
  - expectativa_direcional: risco decresce quando score_credito cresce [OK]
  - invariancia_ordem: predição por linha independe da ordem do lote [OK]
  - funcionalidade_minima: perfil ruim tem risco maior que perfil bom [OK]
exit=0
```

```bash
python -m src.run_gate --dataset corrupted; echo "exit=$?"
```

```text
[FAIL] dataset=corrupted elapsed=0.148s
  - contrato_de_dados: 15/24 expectativas; falhas=9 (máximo tolerado=0) [NO]
  - desempenho_minimo: não avaliado — contrato de dados reprovou [NO]
exit=1
```

> Gate de release de verdade: **FAIL ⇒ `exit != 0`**, senão o CI mentiria.
> Repare que o modelo **não é treinado** quando os dados reprovam — e o
> relatório traz `"model": null` em vez de uma métrica sem significado.

### 4. Suíte de testes (a camada de CI)

```bash
./run_tests.sh -q
```

Esperado: **55 passed**. Em ambientes com plugins globais de pytest (ex.: ROS),
use sempre `./run_tests.sh` — ele define `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`.
Alternativa equivalente:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 GX_ANALYTICS_ENABLED=false pytest -q
```

## 🔬 Demonstrações dirigidas

### A. Um defeito por vez

Cada defeito foi desenhado para acionar **uma** expectativa. O mais didático é
o `drift`:

```bash
python -m src.generate_data --variant corrupted --defect drift
python -m src.validate_data --dataset corrupted
```

```text
[FAIL] contrato=credito v1 linhas=4000 expectativas=23/24 (95.83%)
  - [NO] expect_column_mean_to_be_between (renda_anual) observado=106775.59…
```

**23 de 24 passam.** Nenhum valor está fora da faixa `[5000, 500000]`, nenhum
nulo, nenhum tipo errado — e ainda assim a distribuição andou 60%. Validação
linha a linha não pega deslocamento de distribuição; expectativa estatística
pega.

| `--defect` | O que injeta | Expectativa acionada |
|---|---|---|
| `nulls` | 2,5% de nulos em `renda_anual` | `expect_column_values_to_not_be_null` |
| `ranges` | idades 150 e 7 | `expect_column_values_to_be_between` |
| `schema` | renomeia `score_credito` → `credit_score` | `expect_table_columns_to_match_set` |
| `dups` | repete um `id_cliente` em 20 linhas | `expect_column_values_to_be_unique` |
| `labels` | rótulo `2` em 30 linhas | `expect_column_values_to_be_in_set` |
| `drift` | `renda_anual` × 1,6 | `expect_column_mean_to_be_between` |

> ⚠️ `schema` **cascateia**: sumindo a coluna `score_credito`, as regras dela
> também falham (4 falhas para 1 causa raiz). Ler a lista de falhas de baixo
> para cima leva ao diagnóstico errado — sempre procure a quebra de schema
> primeiro. O teste `test_quebra_de_schema_cascateia` documenta esse efeito.

### B. O bug que nenhuma métrica pega

```bash
python -m src.run_gate --dataset clean --leaky-scaler; echo "exit=$?"
```

```text
[PASS] dataset=clean elapsed=0.146s
  - contrato_de_dados: 24/24 expectativas; falhas=0 (máximo tolerado=0) [OK]
  - desempenho_minimo: roc_auc=0.7636 (limiar=0.7) [OK]
  …
exit=0
```

O scaler foi ajustado sobre **treino + teste**. O contrato de dados aprova
(os dados estão íntegros), o ROC AUC é **idêntico** ao do caminho honesto
(0,7636) e o gate devolve `exit 0`. Quem pega isso é um teste unitário que
inspeciona o próprio pré-processamento:

```bash
./run_tests.sh -q -k vazamento -v
```

`test_prepare_dataset_detecta_vazamento` compara as estatísticas do scaler com
as de `fit_scaler(train)` e falha quando divergem. **Moral:** limiar de métrica
não substitui teste de código.

## ⏱️ Tempos medidos (2026-08-17, CPU, offline)

| Comando | Wall clock | `elapsed_seconds` interno | exit |
|---|---|---|---|
| `python -m src.generate_data --variant clean` | ~0,24 s | — | 0 |
| `python -m src.run_gate --dataset clean` | ~1,9 s | ~0,14 s | 0 |
| `python -m src.run_gate --dataset corrupted` | ~2,6 s | ~0,15 s | 1 |
| `./run_tests.sh -q` | ~14,7 s | — | 0 |

A suíte inteira roda em ~15 s: barato o bastante para rodar a cada commit, que
é a condição para os testes serem de fato executados.

## 🐳 Docker (one-shot, CPU-only)

```bash
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml run --rm data-gate \
  python -m src.generate_data --variant clean
docker compose -f docker/docker-compose.yml run --rm data-gate \
  python -m src.run_gate --dataset clean
docker compose -f docker/docker-compose.yml run --rm data-gate ./run_tests.sh -q
```

## 🎯 Desafio hands-on

1. **Aperte o contrato.** Adicione `stdev_between` a `score_credito` em
   `contracts/credito_v1.yaml`, rode o gate e ajuste os limites até que o
   dataset limpo passe. Depois pense: você acabou de calibrar a regra pelos
   dados que tem — quando isso é legítimo e quando é *overfitting de contrato*?
2. **Crie um defeito novo.** Implemente `--defect` `outliers_renda` em
   `src/generate_data.py`, registre-o em `DEFECTS` e adicione a entrada em
   `DEFEITO_PARA_EXPECTATIVA` (`tests/test_data_quality.py`). O teste
   `test_cobertura_de_defeitos_esta_completa` falha até você fazer as duas
   coisas — de propósito.
3. **Quebre uma feature.** Troque `idade < 30` por `idade <= 30` em
   `faixa_etaria` e veja qual teste acusa. Sem os casos de fronteira, essa
   mudança passaria despercebida.
4. **Suba o rigor do modelo.** Eleve `min_roc_auc` para `0.90` no contrato e
   observe o gate reprovar um modelo que estava "funcionando". Discuta: limiar
   é decisão de produto ou de engenharia?
5. **(Opcional)** Adicione uma expectativa customizada de negócio — por
   exemplo, `taxa_endividamento` alta deveria ser rara entre `score_credito`
   alto — e discuta por que regras multivariadas são muito mais caras de manter.

## ⚠️ Solução de problemas

| Sintoma | Causa / solução |
|---|---|
| `No module named src` | Rode a partir de `monitor/atividade/`. |
| `FileNotFoundError: …credito_clean.csv` | Rode antes `python -m src.generate_data --variant clean`. |
| pytest sem testes / erro ROS `launch_testing` | Use `./run_tests.sh` ou `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`. |
| Barra de progresso "Calculating Metrics" polui o log | `ensure_offline_env()` + `ProgressBarsConfig` já cuidam disso; confira `GX_ANALYTICS_ENABLED=false`. |
| GE tenta criar pasta `gx/` | O lab usa `get_context(mode="ephemeral")`; nada é persistido. Se aparecer, alguém trocou o modo. |
| `test_numero_de_expectativas_e_estavel` falha | Você mudou o contrato — atualize o número **conscientemente**, é essa a função do teste. |

## 📦 Versões pinadas (verificadas nesta atividade)

```text
great_expectations==1.20.0
pandas==3.0.5
scikit-learn==1.9.0
PyYAML==6.0.3
pytest==9.1.1
hypothesis==6.165.10
```

> ℹ️ A API do Great Expectations **1.x** é incompatível com a de 0.x: não há
> mais `great_expectations init`, `DataContext` em YAML no disco nem
> `PandasDataset`. O fluxo atual é
> `get_context() → data_sources → ExpectationSuite → ValidationDefinition.run()`.
> Tutoriais anteriores a 2024 vão falhar aqui.
