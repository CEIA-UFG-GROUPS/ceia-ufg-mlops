# 📘 Aula 14 — Validação de Dados e Testes Unitários em ML (Great Expectations / Pytest)

## Material de Estudo Prévio

Esta é a primeira aula do 2º semestre dedicada à **qualidade verificável**. Até
aqui o grupo montou infraestrutura (Kubernetes, MCP); a partir de agora tudo o
que for construído — tracking (Aula 15), DVC (Aula 16), pipelines (Aula 17),
registry (Aula 19), CI/CD (Aula 20) — depende de uma pergunta que ainda não foi
respondida: **como você sabe que o dado que entrou no treino presta, e que o
código que o transformou faz o que diz fazer?**

⚠️ **Este conteúdo não é um guia de instruções**, mas um **material de estudo
prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do
CEIA/UFG.

---

## 🎯 Objetivos da aula

Ao final, você deverá conseguir:

- explicar por que testar um sistema de ML é diferente de testar software comum;
- posicionar cada teste na pirâmide: unitário, contrato de dados, integração,
  comportamental pós-treino;
- escrever um **contrato de dados** versionado e traduzi-lo em expectativas
  executáveis;
- distinguir expectativa **por linha** de expectativa **estatística** — e saber
  qual falha detecta o quê;
- usar Great Expectations 1.x (context → suite → validation definition) sem
  cair em tutoriais da API 0.x;
- escrever testes de ML com Pytest: fixtures, `parametrize`, casos de fronteira,
  property-based com Hypothesis;
- aplicar testes comportamentais (funcionalidade mínima, invariância,
  expectativa direcional) sobre o modelo treinado;
- reconhecer **vazamento de dados** como bug que nenhuma métrica agregada acusa;
- justificar por que uma validação que não devolve `exit != 0` não é um gate.

---

## 🧠 Por que ML falha em silêncio

Software tradicional falha alto: exceção, HTTP 500, teste vermelho. Sistema de
ML falha **baixo** — continua respondendo, com números plausíveis e errados.

```text
┌──────────────────────────────────────────────────────────────┐
│  Pipeline verde + acurácia estável  ≠  sistema correto       │
├──────────────────────────────────────────────────────────────┤
│  Falhas típicas que nenhum teste de software pega:           │
│  • upstream renomeia uma coluna → feature vira NaN → imputer │
│    preenche com a média → modelo "funciona" com sinal morto  │
│  • unidade muda de reais para centavos → tudo dentro da faixa│
│  • scaler ajustado em treino+teste → métrica offline ótima   │
│  • rótulo novo (`2`) num campo binário → classe ignorada     │
│  • distribuição desloca 60% e nenhum valor sai do range      │
└──────────────────────────────────────────────────────────────┘
```

A raiz é estrutural. Um sistema de ML é composto por **três artefatos mutáveis**
e não apenas um:

```text
comportamento = f(código, dados, configuração)
```

Testar só o código cobre um terço do risco. É por isso que "temos cobertura de
90%" não significa nada sobre a corretude do modelo: os outros dois vértices
não têm cobertura nenhuma.

> **O antipadrão da aula:** o script de validação que imprime tudo vermelho e
> termina com `exit 0`. Se a verificação não interrompe o pipeline, ela é
> documentação, não controle.

---

## 🧱 A pirâmide de testes em ML

```text
                    ┌───────────────────────────┐
              (raro)│  Testes comportamentais   │  pós-treino: MFT,
                    │  sobre o modelo treinado  │  invariância, direcional
                    ├───────────────────────────┤
          (algumas) │  Integração do pipeline   │  gera → valida → treina
                    ├───────────────────────────┤
        (muitas)    │  Contrato / validação     │  schema, ranges, nulos,
                    │  de dados                 │  unicidade, distribuição
                    ├───────────────────────────┤
      (a maioria)   │  Testes unitários de      │  funções puras, fronteiras,
                    │  transformação            │  casos de borda
                    └───────────────────────────┘
```

A base é larga porque é barata: milissegundos, determinística, aponta a linha
culpada. O topo é estreito porque cada teste precisa de um modelo treinado —
mais lento e mais frágil. Inverter essa pirâmide (só testes fim-a-fim) produz
uma suíte que demora, quebra por motivos aleatórios e acaba desabilitada.

### Pré-treino × pós-treino

| | Pré-treino | Pós-treino |
|---|---|---|
| Precisa de modelo? | Não | Sim |
| O que valida | Dados e transformações | Comportamento aprendido |
| Custo | Muito baixo | Médio |
| Exemplos | schema, faixas, nulos, fronteiras de binning, ausência de vazamento | expectativa direcional, invariância, funcionalidade mínima, calibração |
| Falha significa | "não treine com isso" | "não promova isso" |

Essa separação vem da literatura de teste de ML — em especial o **ML Test
Score** (Breck et al., *"The ML Test Score: A Rubric for ML Production
Readiness and Technical Debt Reduction"*, IEEE Big Data 2017), que organiza 28
testes em quatro eixos: **dados/features**, **desenvolvimento de modelo**,
**infraestrutura** e **monitoramento**. Vale ler a rubrica inteira: quase toda
equipe descobre que pontua bem em "infraestrutura" e mal em "dados".

---

## 📋 Validação de dados: o que exatamente se valida

Não existe "validar os dados" em geral. Existem dimensões, cada uma com um
custo e um tipo de falha característico:

| Dimensão | Pergunta | Exemplo de expectativa | Pega |
|---|---|---|---|
| **Schema** | As colunas são as combinadas? | conjunto exato de colunas | renomeação/adição silenciosa upstream |
| **Tipo** | `int64` continua `int64`? | `expect_column_values_to_be_of_type` | coerção por nulo, CSV lido como `object` |
| **Nulidade** | Este campo pode faltar? | `expect_column_values_to_not_be_null` | join que passou a não casar |
| **Faixa (por linha)** | O valor é possível? | `expect_column_values_to_be_between` | idade 150, taxa 1,4 |
| **Domínio** | O valor está no conjunto permitido? | `expect_column_values_to_be_in_set` | rótulo novo, categoria inédita |
| **Unicidade** | A chave é chave? | `expect_column_values_to_be_unique` | duplicação por reprocessamento |
| **Volume** | O lote tem tamanho plausível? | `expect_table_row_count_to_be_between` | extração parcial, partição vazia |
| **Distribuição** | A forma continua a mesma? | média, desvio, quantis, KL | mudança de unidade, drift, mudança de população |
| **Frescor** | O dado é de quando? | max(timestamp) recente | pipeline parado há 3 dias |

### A distinção que mais rende em aula

**Faixa por linha** e **expectativa estatística** detectam falhas diferentes, e
confundi-las é a causa mais comum de contrato inútil:

```text
renda_anual × 1,6  →  todo valor continua em [5.000, 500.000]  ✅
                   →  média sai de ~66.800 para ~106.800       ❌
```

Na atividade, o defeito `drift` faz **23 das 24 expectativas passarem**. Só a
expectativa de média acusa. Um contrato feito apenas de `between` por linha
teria dado verde para um dataset em que a variável mudou de escala.

O inverso também vale: a média pode estar perfeita com metade das linhas
corrompidas em direções opostas. As duas famílias são complementares — nenhuma
substitui a outra.

### Contrato de dados, não `assert` espalhado

A Aula 20 (CI/CD) tem um passo `02_validate_data.py` com `assert`s escritos à
mão. Funciona, e é honesto para um pipeline pequeno. O que não escala:

| `assert` no script | Contrato declarativo |
|---|---|
| A regra vive dentro do código do pipeline | A regra vive em arquivo próprio, versionado |
| Só o autor sabe o que é esperado | Pessoa de negócio consegue ler e revisar em PR |
| Duplicado em cada pipeline que usa o dado | Uma fonte da verdade, vários consumidores |
| Mudança de regra se esconde num diff de código | Mudança de regra é um diff de contrato, com dono |
| Relatório = `AssertionError` na primeira falha | Relatório = todas as falhas, com contagem e valor observado |

O contrato precisa de **dono, versão e processo de mudança**. Sem isso vira um
YAML que ninguém atualiza e que todo mundo aprende a ignorar — a versão
declarativa do teste comentado.

---

## 🔧 Great Expectations 1.x na prática

> ⚠️ **A API mudou de forma incompatível.** Grande parte do material na
> internet é da linha 0.x e **não roda** na 1.x. Se um tutorial começa com
> `great_expectations init` ou `PandasDataset`, ele é anterior à reescrita.

| Conceito 0.x | Equivalente 1.x |
|---|---|
| `great_expectations init` + `great_expectations.yml` | `gx.get_context(mode="ephemeral" \| "file" \| "cloud")` |
| `Datasource` no YAML | `context.data_sources.add_pandas(...)` |
| `PandasDataset` / `validator.expect_*` | `ExpectationSuite` + objetos `gxe.Expect*` |
| `Checkpoint` como YAML | `ValidationDefinition` (+ `Checkpoint` para ações) |
| `expectation_suite.json` no repositório | Suíte construída em código a partir do seu contrato |

O vocabulário mínimo:

```text
 Data Context ──► Data Source ──► Data Asset ──► Batch Definition
      │                                                │
      │            Expectation ──► Expectation Suite   │
      │                                │               │
      └──────────► Validation Definition ◄─────────────┘
                            │
                            ▼
                   ValidationResult  (success, statistics, results[])
```

- **Data Context**: raiz de configuração. `ephemeral` não escreve nada em
  disco — é o modo certo para CI e para sala de aula.
- **Expectation**: uma asserção declarativa e nomeada sobre os dados.
- **Suite**: o conjunto de expectativas — a materialização do contrato.
- **Validation Definition**: liga *quais dados* a *qual suíte*.
- **Checkpoint**: envolve validações com ações (Data Docs, notificações).
- **Data Docs**: relatório HTML navegável, útil para stakeholder; **não** é
  substituto do exit code.

Na atividade, o contrato YAML é traduzido em 24 expectativas por
`src/contract.py`. A vantagem pedagógica é ver que a ferramenta é o *backend*:
trocar Great Expectations por Pandera mexeria num arquivo, não no contrato.

---

## 🧰 Panorama de ferramentas (versões consultadas em 2026-08-17)

| Ferramenta | Modelo | Onde brilha | Custo de adoção | Versão |
|---|---|---|---|---|
| **Great Expectations** | Suítes declarativas + Data Docs | Contrato rico, relatório para stakeholder, muitos backends | Médio; API 1.x quebrou a 0.x | **1.20.0** |
| **Pandera** | Schema como código (DataFrame/pydantic) | Validação inline em função Python, tipagem estática | Baixo; muito idiomático em pandas/polars | **0.32.1** |
| **Soda Core** | Checks em DSL (SodaCL) sobre SQL | Data warehouse, times de dados, agendamento | Médio; orientado a banco | **4.21.0** |
| **PyDeequ / Deequ** | Métricas + constraints em Spark | Volume grande, sugestão automática de constraints | Alto (JVM/Spark) | **1.6.0** |
| **dbt tests** | Testes no modelo de transformação | Quem já vive em dbt; testes junto do SQL | Baixo *se* já usa dbt | **1.12.2** |
| **whylogs** | Perfis estatísticos leves | Perfilar sem mover dados; drift ao longo do tempo | Baixo | **1.6.4** |
| **Deepchecks** | Suítes prontas de dados + modelo | Diagnóstico rápido, relatório visual | Baixo | **0.19.1** |
| **Evidently** | Drift e monitoramento | Produção e monitoramento contínuo (**Aula 23**) | Baixo | **0.7.21** |
| **TFX Data Validation** | Schema inferido + skew | Ecossistema TensorFlow/TFX | Alto fora do TFX | **1.21.0** |

Critério de escolha honesto: **onde o dado vive**. Se está em warehouse, Soda
ou dbt tests ganham por ficarem perto do SQL. Se é DataFrame dentro de um job
Python, Pandera é o de menor atrito. Great Expectations paga o custo quando
você precisa de contrato explícito, relatório auditável e múltiplos backends —
que é exatamente o cenário desta aula.

**Validação × monitoramento:** validação é ponto de decisão *antes* de treinar
ou servir (`exit != 0`). Monitoramento observa a série temporal *depois* do
deploy (Aula 23). As duas usam estatística parecida com propósitos opostos.

---

## 🧪 Pytest para quem testa ML

O que costuma faltar em quem já usa pytest para software comum:

| Recurso | Uso específico em ML |
|---|---|
| `@pytest.fixture(scope="session")` | Treinar o modelo **uma vez** para toda a suíte; sem isso a suíte fica lenta e ninguém a roda |
| `@pytest.mark.parametrize` | Varrer fronteiras de binning e um caso por defeito de dado |
| `pytest.approx` | Comparar float sem `==` frágil |
| `tmp_path` | Testar leitura/escrita de artefato sem sujar o repositório |
| `monkeypatch` | Isolar variável de ambiente, semente, relógio |
| `pytest.raises(match=...)` | Garantir que entrada inválida falha **alto** e com a mensagem certa |
| `-k` / markers | Separar testes rápidos dos que treinam modelo |
| **Hypothesis** | Property-based: a biblioteca procura o contraexemplo por você |
| `pytest-xdist` (**3.8.0**) | Paralelizar quando a suíte cresce |
| `pytest-cov` (**7.1.0**) | Cobertura — útil, mas cobre só o vértice "código" |

### Property-based em uma frase

Em vez de escrever exemplos, você escreve a **propriedade invariante** e deixa
o Hypothesis gerar centenas de entradas — inclusive as que você não pensaria
(`0.0`, `-0.0`, números enormes, `nan`):

```python
@given(divida=st.floats(min_value=0, max_value=1e7, allow_nan=False),
       renda=st.floats(min_value=0, max_value=1e7, allow_nan=False))
def test_comprometimento_sempre_em_zero_um(divida, renda):
    assert 0.0 <= comprometimento_renda(divida, renda) <= 1.0
```

Renda zero é o caso que a suíte de exemplos esquece e que a produção encontra.

### Determinismo é requisito testável

Se `train_model(seed=42)` duas vezes não produz predições idênticas, você não
tem experimento reproduzível — e nenhuma comparação entre runs (Aula 15) tem
significado. Isso é uma asserção, não uma esperança:

```python
np.testing.assert_array_equal(a.predict_proba(x), b.predict_proba(x))
```

---

## 🎭 Testes comportamentais: o modelo faz o que deveria?

ROC AUC de 0,76 não diz se o modelo entendeu o problema. A referência aqui é
**CheckList** (Ribeiro et al., *"Beyond Accuracy: Behavioral Testing of NLP
Models with CheckList"*, ACL 2020 — melhor artigo do ano), cuja taxonomia
transfere bem para dados tabulares:

| Tipo | Definição | Exemplo no lab |
|---|---|---|
| **Funcionalidade mínima (MFT)** | Casos tão óbvios que qualquer especialista acerta | score 830 + endividamento 0,05 tem que ter risco menor que score 320 + endividamento 0,90 |
| **Invariância (INV)** | Mudança que **não** deveria alterar a saída | reordenar o lote não pode mudar a predição de cada linha |
| **Expectativa direcional (DIR)** | Mudança que deveria alterar a saída em um **sentido conhecido** | aumentar `score_credito` tem que **reduzir** o risco, monotonicamente |

Um modelo que inverte o sinal do score é uma falha grave — e passa
tranquilamente por um limiar de AUC se a inversão for compensada por outras
variáveis correlacionadas. Teste comportamental é o que pega.

Parente próximo: **teste metamórfico** — em vez de um resultado esperado
(caro), você afirma uma *relação* entre entradas transformadas e suas saídas.
Útil justamente quando "a resposta certa" não é conhecível.

---

## 💧 Vazamento de dados: o bug que nenhuma métrica denuncia

Ajustar o scaler (ou o imputer, ou o encoder) sobre **treino + teste** é o bug
de pré-processamento mais comum em ML aplicado. E ele é insidioso porque:

1. os dados estão íntegros → o contrato aprova;
2. a métrica offline **melhora** (ou, como no lab, nem muda);
3. nenhum `assert` de schema tem opinião sobre isso;
4. a degradação só aparece em produção, com outra escala.

No lab, `--leaky-scaler` produz `exit 0`, contrato 24/24 e **ROC AUC idêntico**
(0,7636). O único mecanismo que pega é um teste unitário que compara as
estatísticas do scaler com as de `fit_scaler(train)`:

```python
def test_prepare_dataset_ajusta_scaler_apenas_no_treino(split):
    train, test = split
    *_, scaler = prepare_dataset(train, test, leaky=False)
    np.testing.assert_allclose(scaler.mean_, fit_scaler(train).mean_)
```

Generalizando: **limiar de métrica não substitui teste de código.** Toda vez
que a corretude depende de *como* o número foi calculado, e não do número, só
o teste unitário alcança.

Parentes do mesmo bug: feature construída com informação do futuro
(*target leakage*), split aleatório em dado temporal, e registro do mesmo
cliente nos dois lados do split — motivo pelo qual o lab divide por hash do
`id_cliente`, não por `random_state`.

---

## 🔗 Onde isso encosta em versionamento e reprodutibilidade

A leitura designada (Huyen, *Designing Machine Learning Systems*, Cap. 6,
seção **"Experiment Tracking and Versioning"**, pp. 162–168) trata do outro
lado desta moeda. Vale explicitar a ponte, porque as duas ideias só funcionam
juntas:

- Huyen argumenta que reproduzir um resultado exige versionar **código, dados
  e configuração** — e observa que versionar dados é qualitativamente mais
  difícil que versionar código (o que conta como "mudança"? diff de um
  Parquet de 200 GB?).
- Versionar sem validar produz **uma versão confiável de um dado ruim**: você
  reproduz o erro com precisão.
- Validar sem versionar produz um veredito **sem endereço**: "os dados
  passaram" — quais dados?

A junção é o que a aula chama de **linhagem de evidência**: contrato `v1`
(versão) + relatório JSON de validação (veredito) + commit do código (o que
transformou) + run de tracking (Aula 15). Cada peça sozinha é insuficiente.

> Observação de coerência do cronograma: as páginas 162–168 cobrem
> especificamente *experiment tracking e versionamento* — assunto que a **Aula
> 15** aprofunda. Para validação de dados e teste propriamente ditos, os
> complementos diretos são Huyen Cap. 4 (*Training Data*, sobre problemas de
> amostragem e rótulo) e Cap. 8 (*Data Distribution Shifts and Monitoring*,
> pp. 225–261, já usado na Aula 23), além do ML Test Score e do CheckList
> listados nas referências.

---

## 📊 Casos de uso práticos

1. **A coluna que virou centavo.** Um time de risco recebe `renda_anual` de um
   serviço que passou a enviar em centavos. Nenhum valor sai da faixa
   permitida, nenhum nulo aparece, o schema é idêntico. O modelo é retreinado,
   a acurácia cai 2 pontos — dentro do ruído histórico — e vai para produção.
   Três semanas depois, a taxa de aprovação de crédito despenca. Uma única
   expectativa de média teria falhado no dia zero. **Lição:** faixa por linha
   não é validação de distribuição.

2. **O gate decorativo.** Uma equipe adiciona validação de dados ao pipeline e
   comemora o relatório HTML bonito no artefato do build. O script termina com
   `print(report)` e sem `sys.exit`. Durante quatro meses, todo lote com
   duplicatas passou; o `job` ficou verde o tempo todo. A auditoria descobre
   que "existia validação" e que ela nunca bloqueou nada. **Lição:** verificação
   sem exit code é documentação, e nenhum dashboard conserta isso.

3. **A refatoração de fronteira.** Alguém "melhora" o binning de idade trocando
   `< 30` por `<= 30`. A mudança move ~2% dos clientes de faixa. Não há erro,
   não há exceção, a métrica se mexe menos que o ruído entre sementes. Só um
   teste parametrizado nas fronteiras (`18, 29, 30, 44, 45, 59, 60`) acusa.
   **Lição:** em ML, o teste de fronteira é o que separa refatoração de
   mudança de comportamento — porque o modelo absorve a diferença sem
   reclamar.

---

## 🧪 Atividade prática

Em [`atividade/`](./atividade/):

```bash
pip install -r requirements.txt
export GX_ANALYTICS_ENABLED=false
python -m src.generate_data --variant clean
python -m src.generate_data --variant corrupted
python -m src.run_gate --dataset clean;     echo exit=$?   # PASS, 0
python -m src.run_gate --dataset corrupted; echo exit=$?   # FAIL, 1
./run_tests.sh -q                                          # 55 passed
```

Stack: **Great Expectations 1.20.0** + **Pytest 9.1.1** + **Hypothesis** —
offline, CPU-only, sem API key. Três demonstrações valem a projeção:

1. `--defect drift` isolado: **23/24 expectativas passam** e o dataset ainda
   está errado;
2. `--dataset corrupted`: o modelo **não é treinado** e o relatório traz
   `"model": null` em vez de métrica sem sentido;
3. `--leaky-scaler`: gate **PASS**, AUC **idêntico**, e o teste unitário
   `test_prepare_dataset_detecta_vazamento` é o único a acusar o bug.

---

## 💬 Pontos para reflexão pré-aula

1. Seu contrato de dados atual está escrito em algum lugar, ou mora na cabeça
   de uma pessoa?
2. Se `renda` mudasse de reais para centavos hoje, qual verificação sua
   quebraria — e em quanto tempo?
3. Quem é o dono do contrato quando o time de dados e o time de ML discordam
   sobre o que é "válido"?
4. Um contrato calibrado a partir dos dados que você tem hoje é validação ou
   *overfitting de contrato*?
5. Qual a diferença prática entre uma expectativa de média que falha e um
   alerta de drift (Aula 23)? Quando cada um deve bloquear alguma coisa?
6. Se seu gate imprime FAIL e devolve `exit 0`, o que exatamente o CI garantiu?
7. Quantos dos 28 itens do ML Test Score seu projeto atual passaria?

---

## 📚 Referências

- Huyen, C. *Designing Machine Learning Systems*. Cap. 6, "Model Development
  and Offline Evaluation", seção **"Experiment Tracking and Versioning"**,
  pp. 162–168 *(leitura designada)*; complementos: Cap. 4 "Training Data" e
  Cap. 8 "Data Distribution Shifts and Monitoring", pp. 225–261.
- Breck, E. et al. *"The ML Test Score: A Rubric for ML Production Readiness
  and Technical Debt Reduction"*. IEEE Big Data, 2017.
- Ribeiro, M. T. et al. *"Beyond Accuracy: Behavioral Testing of NLP Models
  with CheckList"*. ACL 2020 (Best Paper).
- Sculley, D. et al. *"Hidden Technical Debt in Machine Learning Systems"*.
  NeurIPS 2015 — origem do argumento de que dados são dívida técnica.
- [Great Expectations — documentação 1.x](https://docs.greatexpectations.io/)
- [Great Expectations — galeria de expectativas](https://greatexpectations.io/expectations/)
- [Pytest — documentação](https://docs.pytest.org/)
- [Hypothesis — property-based testing](https://hypothesis.readthedocs.io/)
- [Pandera](https://pandera.readthedocs.io/) · [Soda Core](https://docs.soda.io/)
  · [Deepchecks](https://docs.deepchecks.com/) · [whylogs](https://whylogs.readthedocs.io/)

---

## 🔗 Conexões com outras aulas

- **Aula 13:** MCP — a aula anterior; aqui saímos de integração para qualidade.
- **Aula 15:** Experiment Tracking — a leitura designada aponta para lá; o run
  precisa registrar *qual versão do contrato* aprovou os dados.
- **Aula 16:** DVC — versionar o dataset que o contrato aprovou.
- **Aula 17:** Pipelines (Airflow/Prefect) — a validação vira uma **task** que
  falha e interrompe a DAG.
- **Aula 18:** Feature Store — contrato no ponto de entrada das features.
- **Aula 19:** Model Registry — o quality gate de promoção é o mesmo padrão
  aplicado ao modelo.
- **Aula 20:** CI/CD — o passo `02_validate_data.py` de lá é a versão com
  `assert` do que aqui vira contrato declarativo.
- **Aula 23:** Monitoramento e drift — as mesmas estatísticas, agora ao longo
  do tempo e depois do deploy.
- **Aula 25:** LLMOps — golden set e gate `exit != 0` são este mesmo desenho
  aplicado a saída de linguagem.
- **Aula 26:** projeto final — o contrato e a suíte devem ser reaproveitados,
  não reescritos.
