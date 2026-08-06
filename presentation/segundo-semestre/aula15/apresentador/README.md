# Experiment Tracking com MLflow e W&B

## README do Apresentador

Este documento organiza a apresentação da Aula 15. O objetivo é mostrar como uma
execução de treinamento deixa de ser um evento descartável e passa a ser um
registro consultável, comparável e reproduzível.

> **Fio condutor sugerido:** começar com a pergunta “qual execução gerou este
> modelo e com quais dados?”, acompanhar três tentativas do mesmo classificador
> e terminar mostrando que MLflow e W&B registram os runs, enquanto DVC cuida
> da referência aos dados.

## 1️⃣ Motivação

### 1.1 O problema do experimento descartável

- Um `python train.py` que termina no terminal não deixa uma trilha confiável.
- Planilhas e nomes como `modelo_final_v7_agora_sim` não escalam para equipes.
- Sem registro de parâmetros, métricas e artefatos, não é possível explicar por
  que um modelo venceu outro.
- A pergunta empresarial é de rastreabilidade: **quem executou, quando, com
  qual código, quais dados e qual resultado?**

### 1.2 Reprodutibilidade em ML

Use a equação como mapa da aula:

```text
resultado = f(código, dados, parâmetros, ambiente)
```

- Git versiona código.
- DVC ou outra solução de dados identifica os dados.
- O ambiente deve ser fixado por dependências/container.
- MLflow/W&B registram o run, seus parâmetros, métricas e artefatos.

### 1.3 O que a turma deve sair sabendo fazer

- Definir o que é um experimento e o que é um run.
- Instrumentar um treino com parâmetros, métricas e artefatos.
- Comparar runs e justificar a escolha de um candidato.
- Identificar a diferença entre Tracking, DVC e Model Registry.
- Escolher entre MLflow e W&B levando em conta operação, colaboração e contexto.

## 2️⃣ Como Funciona

### 2.1 Anatomia de um run

| Elemento | Pergunta respondida | Exemplo no laboratório |
|---|---|---|
| Experimento | Qual tarefa está sendo investigada? | `aula15_wine_tracking` |
| Run | Qual execução específica aconteceu? | `rf-depth-5-seed-42` |
| Parâmetros | O que foi escolhido antes do treino? | `max_depth`, `seed` |
| Métricas | O que aconteceu durante/depois? | `accuracy`, `macro_f1` |
| Artefatos | Quais arquivos foram produzidos? | modelo, relatório, matriz |
| Tags/metadados | Como localizar e contextualizar? | commit, dataset digest |

Enfatize que um número sozinho não é evidência suficiente: `macro_f1=0.94`
precisa estar associado a um dataset, uma divisão, um código e um conjunto de
parâmetros.

### 2.2 MLflow Tracking

- **Run**: execução individual do código de treinamento.
- **Experiment**: agrupamento de runs relacionados.
- **Backend store**: metadados de runs, parâmetros e métricas.
- **Artifact store**: modelos, imagens, relatórios e outros arquivos.
- **Tracking URI**: endereço do armazenamento local ou servidor central.
- API essencial: `start_run`, `log_param(s)`, `log_metric(s)`,
  `log_artifact(s)`, `set_tag(s)` e `log_input`.
- A UI permite filtrar, ordenar e comparar runs.

No laboratório, o MLflow é usado para Tracking. Não registrar modelos no Model
Registry nesta aula; esse fluxo será aprofundado na Aula 19.

### 2.3 Weights & Biases

- **Project** agrupa as execuções de uma tarefa.
- **Run** representa uma execução e seu histórico.
- `config` guarda hiperparâmetros e contexto.
- `run.log` registra métricas por passo/época.
- **Artifacts** versionam e conectam datasets, modelos e resultados.
- O dashboard favorece colaboração, visualizações e comparação de execuções.

Mostre que o modo offline é útil para desenvolvimento ou ambientes sem rede,
mas não oferece a mesma colaboração até que os dados sejam sincronizados.

### 2.4 MLflow × W&B

| Critério | MLflow | W&B |
|---|---|---|
| Modelo mental | Tracking open source e desacoplado | Plataforma colaborativa de runs |
| Execução local | Muito simples, com arquivos ou servidor | Possível em modo offline |
| Comparação visual | UI de experimentos e filtros | Dashboards muito ricos e customizáveis |
| Artefatos | Artifact store configurável | Artifacts com linhagem e versões |
| Operação empresarial | Self-hosting e integrações | SaaS, cloud privado ou opções enterprise |
| Melhor pergunta | “Como hospedo e integro o tracking?” | “Como o time explora e compartilha runs?” |

Mensagem central: não existe uma guerra obrigatória. Uma equipe pode usar uma
ferramenta para Tracking e outra para necessidades específicas, desde que
defina uma fonte de verdade e evite duplicação sem propósito.

### 2.5 Onde entra o DVC?

- DVC versiona a referência aos dados e aos pipelines; não é apenas uma tabela
  de métricas de runs.
- O `.dvc` é um ponteiro pequeno versionado no Git; o conteúdo fica no cache e
  no remote configurado.
- O run deve registrar ao menos o digest do dataset e, quando disponível, o
  hash/revisão DVC.
- Assim, o grafo fica: `commit Git → ponteiro DVC → dados → run → artefatos`.
- Não repetir o laboratório completo de `dvc push`, `dvc repro` e MinIO; apontar
  para o material da Aula 16.

### 2.6 Boas práticas para mostrar ao vivo

- Use nomes de runs que expliquem a intenção.
- Fixe seeds e registre o split.
- Registre métricas suficientes para a decisão, não qualquer número disponível.
- Salve artefatos que permitam inspeção, não somente o score final.
- Registre commit, digest dos dados e versão das dependências.
- Nunca coloque API keys no código ou no repositório.
- Não confunda “melhor run” com “modelo aprovado para produção”.

## 3️⃣ Quickstart & Demos

### 3.1 Demo 1 — Um treino sem tracking

Comece com um script que imprime apenas:

```text
accuracy=0.97
```

Pergunte: qual modelo? qual divisão? qual seed? qual dado? onde está o modelo?

### 3.2 Demo 2 — Três runs no MLflow

Na pasta `monitor/atividade/`:

```bash
pip install -r requirements.txt
python -m src.prepare_data

python -m src.train --tracker mlflow --model random_forest --n-estimators 50 --max-depth 3 --seed 42
python -m src.train --tracker mlflow --model random_forest --n-estimators 150 --max-depth 5 --seed 42
python -m src.train --tracker mlflow --model logistic_regression --c 1.0 --seed 42
```

Abrir a UI e comparar os três runs. O foco não é decorar a API, mas observar
que cada decisão ficou associada a uma execução.

### 3.3 Demo 3 — O mesmo treino no W&B

```bash
wandb login
python -m src.train --tracker wandb --wandb-mode online --model random_forest --n-estimators 150 --max-depth 5 --seed 42
```

Sem credenciais ou internet:

```bash
python -m src.train --tracker wandb --wandb-mode offline --model random_forest --seed 42
```

Compare `config`, gráficos, artefatos e tags entre as execuções.

### 3.4 Demo 4 — Dataset e DVC

Mostrar que o script registra o digest do `data/wine.csv` e lê um ponteiro
`data/wine.csv.dvc` se ele existir. Explique que, em um projeto DVC real:

```bash
dvc add data/wine.csv
git add data/wine.csv.dvc data/.gitignore
git commit -m "data: versiona dataset wine"
```

O ponto pedagógico é ligar a revisão dos dados ao run; a execução completa do
remote fica na Aula 16.

### 3.5 Para fechar

Peça que cada grupo escolha um run e justifique a escolha usando:

1. métrica principal;
2. estabilidade/reprodutibilidade;
3. parâmetros;
4. dataset e commit;
5. artefatos disponíveis.

## 4️⃣ Perguntas para discussão

1. Um run com F1 maior é necessariamente o melhor candidato?
2. O que desaparece da análise se o dataset não for identificado?
3. Quando o artifact store não deve receber o dataset completo?
4. DVC e W&B Artifacts resolvem exatamente o mesmo problema?
5. Por que Tracking e Model Registry devem ser conceitos separados?
6. O que uma equipe enterprise precisa governar além da métrica?

## 5️⃣ Conexões com outras aulas

- **Git e containers:** código e ambiente são partes da reprodução.
- **Aula 16 — DVC:** dados, ponteiros, remotes e pipelines reprodutíveis.
- **Aula 17 — Pipelines:** instrumentação de runs dentro de um DAG.
- **Aula 19 — Model Registry:** promoção, aliases, quality gates e serving.
- **Aula 11 — Observabilidade:** métricas de treino não substituem métricas de
  produção.

## Referências

- Haviv, A.; Gift, N. *Implementing MLOps in the Enterprise*. Cap. 4,
  “Working with Data and Feature Stores”, pp. 204–213, seção Data Version
  Control.
- [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/)
- [MLflow Dataset Tracking](https://mlflow.org/docs/latest/dataset/)
- [W&B — Create an experiment](https://docs.wandb.ai/models/track/create-an-experiment)
- [DVC — Command reference](https://dvc.org/doc/command-reference/)
