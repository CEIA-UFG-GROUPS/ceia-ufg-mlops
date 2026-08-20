# Validação de Dados e Testes Unitários em ML

## README do Apresentador

Esta aula abre a trilha de **qualidade verificável** do 2º semestre. Tudo o que
vem depois — tracking (15), DVC (16), pipelines (17), registry (19), CI/CD (20)
— assume que existe uma resposta para "como você sabe que este dado presta?".
A turma deve sair sabendo escrever um contrato de dados, traduzi-lo em
expectativas executáveis e transformar isso num gate que **quebra o CI**.

> 💡 **Fluxo sugerido**: abrir com o dataset que passa em 23 de 24 expectativas
> e ainda assim está errado (`--defect drift`). Depois mostrar o gate completo
> PASS/FAIL com exit code na tela. Só então subir para a teoria: pirâmide de
> testes, pré/pós-treino, contrato como código, panorama de ferramentas,
> testes comportamentais. Fechar com o `--leaky-scaler`: gate verde, AUC
> idêntico, bug real — e o teste unitário sendo o único a pegar.

---

## 1️⃣ Motivação

### 1.1 O pipeline verde que entrega o modelo errado

- Falha de ML é **silenciosa**: nada lança exceção, os números continuam
  plausíveis.
- `comportamento = f(código, dados, configuração)` — cobertura de teste cobre
  um vértice de três.
- A Aula 20 já usa `assert`s de dados dentro do pipeline; aqui a pergunta é
  **por que aquilo não escala** e o que substitui.

### 1.2 O que a turma deve sair sabendo fazer

- Escrever um contrato de dados versionado, com dono e política de mudança.
- Distinguir expectativa **por linha** de expectativa **estatística**.
- Usar Great Expectations **1.x** (a 0.x quebrou — metade dos tutoriais não roda).
- Escrever testes com fixtures de sessão, `parametrize` em fronteiras e
  property-based com Hypothesis.
- Aplicar MFT / invariância / expectativa direcional sobre o modelo treinado.
- Explicar por que vazamento de pré-processamento não aparece em métrica alguma.
- Justificar `exit != 0` como o que separa gate de decoração.

---

## 2️⃣ Como funciona

### 2.1 A pirâmide

```text
   pós-treino   │ comportamental (MFT, INV, DIR)      │ poucos, mais lentos
                │ integração do pipeline              │
   pré-treino   │ contrato / validação de dados       │
                │ unitários de transformação          │ muitos, milissegundos
```

| | Pré-treino | Pós-treino |
|---|---|---|
| Precisa de modelo? | Não | Sim |
| Falha significa | "não treine com isso" | "não promova isso" |
| Custo | Muito baixo | Médio |

Referência de base: **ML Test Score** (Breck et al., IEEE Big Data 2017) —
28 testes em dados/features, modelo, infra e monitoramento.

### 2.2 O que se valida (e o que cada família pega)

| Dimensão | Expectativa típica | Falha que só ela pega |
|---|---|---|
| Schema / tipo | conjunto exato de colunas | renomeação upstream |
| Nulidade | `not_be_null` | join que parou de casar |
| Faixa por linha | `be_between` | idade 150 |
| Domínio | `be_in_set` | rótulo `2` num campo binário |
| Unicidade | `be_unique` | duplicação por reprocessamento |
| Volume | `row_count_between` | extração parcial |
| **Distribuição** | `mean_between`, quantis | **mudança de unidade / drift** |

**Demo-chave:** `--defect drift` multiplica `renda_anual` por 1,6. Todo valor
segue dentro de `[5.000, 500.000]`. **23/24 passam.** Só a expectativa de média
acusa.

### 2.3 Contrato declarativo × `assert` no script

| `assert` no pipeline | Contrato em arquivo |
|---|---|
| Regra escondida no código | Regra revisável em PR por quem entende do negócio |
| Duplicada em cada consumidor | Fonte da verdade única |
| Para na primeira falha | Relatório com todas as falhas e valores observados |
| Sem dono | `owner:` e `version:` explícitos |

### 2.4 Great Expectations 1.x — vocabulário mínimo

```text
Data Context → Data Source → Data Asset → Batch Definition
                    Expectation → Expectation Suite
                          ↓
                 Validation Definition → ValidationResult
```

⚠️ Avisar a turma: **`great_expectations init`, `PandasDataset` e checkpoint em
YAML são 0.x** e não existem mais. O lab usa `get_context(mode="ephemeral")`,
que não escreve nada em disco.

### 2.5 Ferramentas (versões consultadas em 2026-08-17)

| Ferramenta | Nota de ensino | Versão |
|---|---|---|
| **Great Expectations** | Lab oficial; contrato rico + Data Docs | 1.20.0 |
| **Pandera** | Menor atrito em pandas/polars; schema como código | 0.32.1 |
| **Soda Core** | Warehouse/SQL, DSL própria | 4.21.0 |
| **PyDeequ** | Spark; sugere constraints automaticamente | 1.6.0 |
| **dbt tests** | Barato *se* o time já vive em dbt | 1.12.2 |
| **whylogs** | Perfis leves, sem mover dado | 1.6.4 |
| **Deepchecks** | Suítes prontas, diagnóstico rápido | 0.19.1 |
| **Evidently** | Monitoramento/drift — **Aula 23**, não aqui | 0.7.21 |
| **TFX Data Validation** | Só faz sentido dentro do TFX | 1.21.0 |

Critério de escolha: **onde o dado vive**. Warehouse → Soda/dbt. DataFrame em
job Python → Pandera. Contrato explícito + relatório auditável → GE.

### 2.6 Testes comportamentais (CheckList, ACL 2020)

| Tipo | O que afirma | No lab |
|---|---|---|
| **MFT** | Casos óbvios têm que sair certos | perfil bom < risco < perfil ruim |
| **Invariância** | Mudança irrelevante não altera saída | reordenar o lote |
| **Direcional** | Mudança relevante altera no sentido conhecido | ↑ score ⇒ ↓ risco, monotônico |

Um modelo com o sinal do score invertido passa por qualquer limiar de AUC.

### 2.7 Vazamento — o clímax da aula

`--leaky-scaler`: scaler ajustado em treino+teste.

- contrato de dados: **24/24 OK** (os dados estão íntegros);
- ROC AUC: **0,7636 — idêntico** ao caminho honesto;
- gate: **PASS, exit 0**.

O único mecanismo que pega é `test_prepare_dataset_detecta_vazamento`, que
compara as estatísticas do scaler com `fit_scaler(train)`. **Limiar de métrica
não substitui teste de código.**

---

## 3️⃣ Quickstart & demos

Na pasta `monitor/atividade/`:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export GX_ANALYTICS_ENABLED=false

python -m src.generate_data --variant clean
python -m src.generate_data --variant corrupted
python -m src.run_gate --dataset clean;     echo "exit=$?"   # PASS, 0
python -m src.run_gate --dataset corrupted; echo "exit=$?"   # FAIL, 1
./run_tests.sh -q                                            # 55 passed
```

### Ordem sugerida ao vivo

1. Abrir `contracts/credito_v1.yaml` — ler em voz alta; é legível por não-dev.
2. `--defect drift` isolado → **23/24 passam** e o dado está errado.
3. Gate `corrupted` → 9 falhas, modelo **não treinado**, `"model": null`,
   `exit 1`.
4. Mostrar `reports/gate_report_corrupted.json` como artefato de PR.
5. `./run_tests.sh -q -k fronteira -v` → os casos de binning.
6. `--leaky-scaler` → gate verde, AUC igual; então rodar
   `./run_tests.sh -q -k vazamento -v`.
7. Fechar apontando para a Aula 20: este gate é um *step* do workflow de CI.

Tempos medidos nesta máquina (CPU, offline, 2026-08-17): gate ~1,9 s wall /
~0,14 s interno; `./run_tests.sh -q` ~14,7 s (**55 passed**). Docker
(`python:3.12-slim`) reproduz os mesmos números.

---

## 4️⃣ Boas práticas para fechar a aula

1. Contrato de dados versionado, com **dono** e bump de versão em PR.
2. Expectativa por linha **e** expectativa estatística — famílias complementares.
3. Dados antes do modelo: não gaste treino em dado reprovado.
4. Testes rápidos e determinísticos; suíte que demora não é rodada.
5. Fronteiras parametrizadas + property-based onde há invariante.
6. Comportamento (MFT/INV/DIR) além da métrica agregada.
7. **`exit != 0`** — o item que transforma relatório em controle.
8. Ponte explícita: **Aula 15** versiona o que a Aula 14 aprovou; **Aula 20**
   executa este gate no CI.

## 💬 Pontos para reflexão pré-aula

1. Se `renda` virasse centavos hoje, qual verificação sua quebraria — e quando?
2. Quem é o dono do contrato quando dados e ML discordam sobre "válido"?
3. Calibrar o contrato pelos dados de hoje é validação ou overfitting de contrato?
4. Qual a diferença prática entre expectativa de média que falha e alerta de
   drift (Aula 23)?
5. Quantos dos 28 itens do ML Test Score seu projeto passaria hoje?

## 📚 Referências

- Huyen, C. *Designing Machine Learning Systems*, Cap. 6, seção "Experiment
  Tracking and Versioning", pp. 162–168 *(leitura designada)*; complementos:
  Cap. 4 "Training Data" e Cap. 8, pp. 225–261.
- Breck et al., *The ML Test Score* (IEEE Big Data 2017).
- Ribeiro et al., *CheckList* (ACL 2020, Best Paper).
- Sculley et al., *Hidden Technical Debt in ML Systems* (NeurIPS 2015).
- Docs: Great Expectations 1.x, Pytest, Hypothesis, Pandera, Soda Core.

> ℹ️ As pp. 162–168 tratam de *experiment tracking e versionamento* — tema que
> a Aula 15 aprofunda. O material do monitor explicita a ponte: validar sem
> versionar dá um veredito sem endereço; versionar sem validar dá uma versão
> confiável de um dado ruim.

## 🔗 Conexões com outras aulas

- **Aula 13:** MCP (aula anterior).
- **Aula 15:** Experiment Tracking — registrar qual versão do contrato aprovou.
- **Aula 16:** DVC — versionar o dataset aprovado.
- **Aula 17:** validação como task que interrompe a DAG.
- **Aula 19:** quality gate de promoção — mesmo padrão, aplicado ao modelo.
- **Aula 20:** CI/CD — `02_validate_data.py` é a versão com `assert` disto aqui.
- **Aula 23:** drift — mesma estatística, depois do deploy.
- **Aula 25:** golden set + `exit != 0` para saída de linguagem.
- **Aula 26:** projeto final — reusar contrato e suíte.
