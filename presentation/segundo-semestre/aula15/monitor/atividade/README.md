# 🧪 Atividade Prática — Aula 15: Experiment Tracking

Esta atividade registra o mesmo treinamento em **MLflow** e **Weights & Biases**.
O modelo é um classificador sobre o dataset Wine do `scikit-learn`; o foco é
comparar runs, não obter a melhor solução de modelagem.

## 🎯 O que você vai fazer

1. Gerar o dataset local sem download externo.
2. Registrar parâmetros, métricas, artefatos e metadados em MLflow.
3. Repetir o treinamento no W&B online ou offline.
4. Comparar pelo menos três configurações.
5. Relacionar o digest do dataset e um ponteiro DVC ao run.

## 📁 Estrutura

```text
atividade/
├── README.md
├── requirements.txt
├── .gitignore
├── notebooks/
│   └── aula15_pratica_colab.ipynb
├── src/
│   ├── __init__.py
│   ├── common.py
│   ├── prepare_data.py
│   ├── train.py
│   └── compare_runs.py
├── tests/
│   └── test_tracking.py
└── docker/
    ├── Dockerfile
    └── docker-compose.yml
```

> Execute os comandos a partir da pasta `atividade/`, e não a partir de
> `src/`. O comando `python -m src.train` depende desse diretório de trabalho.

## 🛠️ Execução local

Crie um ambiente virtual e instale as dependências:

```bash
python -m venv .venv
# PowerShell
.\.venv\Scripts\Activate.ps1
# Linux/macOS
# source .venv/bin/activate
pip install -r requirements.txt
```

Gere o dataset:

```bash
python -m src.prepare_data
```

### MLflow sem servidor

Sem configurar `MLFLOW_TRACKING_URI`, o MLflow grava runs em SQLite em
`.mlflow/mlflow.db`, evitando o backend de arquivos legado das versões atuais.

```bash
python -m src.train --tracker mlflow --model random_forest --n-estimators 50 --max-depth 3 --seed 42
python -m src.train --tracker mlflow --model random_forest --n-estimators 150 --max-depth 5 --seed 42
python -m src.train --tracker mlflow --model logistic_regression --c 1.0 --seed 42

mlflow ui --backend-store-uri sqlite:///./.mlflow/mlflow.db --port 5000
```

Abra <http://localhost:5000> e compare os runs no experimento
`aula15_wine_tracking`.

### MLflow com Docker

Para usar um Tracking Server local com backend SQLite e artefatos persistentes:

```bash
docker compose -f docker/docker-compose.yml up -d --build
$env:MLFLOW_TRACKING_URI = "http://localhost:5000"  # PowerShell
# export MLFLOW_TRACKING_URI=http://localhost:5000  # Linux/macOS
python -m src.train --tracker mlflow --model random_forest --n-estimators 150 --max-depth 5 --seed 42
```

UI: <http://localhost:5000>.

Para encerrar:

```bash
docker compose -f docker/docker-compose.yml down
```

### W&B online

O modo online exige uma conta e uma API key. Nunca salve a chave em arquivos
versionados.

```bash
wandb login
python -m src.train --tracker wandb --wandb-mode online --model random_forest --n-estimators 150 --max-depth 5 --seed 42
```

O projeto padrão é `ceia-ufg-aula15`; personalize-o com `--wandb-project` ou
`WANDB_PROJECT`.

### W&B offline

O modo offline não exige login nem conexão:

```bash
python -m src.train --tracker wandb --wandb-mode offline --model random_forest --seed 42
```

Os arquivos ficam em `wandb/`. Se a política do projeto permitir sincronização
posterior:

```bash
wandb sync wandb/offline-run-*
```

## 🔍 O que é registrado

Cada run registra:

- **Parâmetros:** modelo, seed, test size, `n_estimators`, `max_depth` ou `C`.
- **Métricas:** accuracy, macro-F1 e tempo de treino.
- **Artefatos:** `model.joblib`, relatório JSON e matriz de confusão PNG.
- **Tags:** commit Git, digest SHA-256 do dataset, tracker e metadados DVC.
- **Dataset:** no MLflow, também é usado `mlflow.log_input` quando disponível;
  no W&B, o CSV é anexado como Artifact do tipo `dataset`.

## 🔗 Integração opcional com DVC

Não execute `dvc init` dentro deste repositório do curso. Para testar a
associação em um workspace isolado, gere o arquivo e rode:

```bash
python -m src.prepare_data
dvc add data/wine.csv
```

Deixe `data/wine.csv.dvc` ao lado do dataset e execute novamente o treinamento.
O script lerá o `md5` do ponteiro e o registrará como tag. O fluxo completo de
remote, `dvc push`, `dvc pull` e `dvc repro` está na atividade da Aula 16.

## 📊 Comparar runs via CLI

Com o servidor MLflow ativo ou usando o diretório local:

```bash
python -m src.compare_runs --tracking-uri sqlite:///./.mlflow/mlflow.db --metric macro_f1
```

Se o servidor Docker estiver ativo:

```bash
python -m src.compare_runs --tracking-uri http://localhost:5000 --metric macro_f1
```

Escolha o melhor run considerando, além da métrica, a seed, os parâmetros, o
dataset e os artefatos. Um score maior isolado não é um quality gate completo.

## ✅ Validação

```bash
python -m unittest discover -s tests -v
```

Os testes verificam digest determinístico, criação de run MLflow, presença dos
parâmetros/métricas/artefatos e execução W&B offline.

## 💬 Perguntas para discussão

1. Por que duas métricas iguais podem representar experimentos diferentes?
2. Qual informação do run conecta o resultado ao dataset?
3. O artifact store substitui o DVC? Por quê?
4. O que mudaria se o W&B fosse o sistema principal da equipe?
5. Qual run você escolheria e que evidência usaria para defendê-lo?

## ⚠️ Solução de problemas

| Sintoma | Causa provável / solução |
|---|---|
| `No module named src` | Execute a partir de `monitor/atividade/`. |
| UI MLflow vazia | Use a mesma `MLFLOW_TRACKING_URI` ao treinar e ao abrir a UI. |
| W&B pede login no modo offline | Confira `--wandb-mode offline` e a variável `WANDB_MODE`. |
| Docker não inicia | Verifique se a porta 5000 está livre e veja `docker compose logs`. |
| DVC reclama de repositório aninhado | Use um workspace isolado; não rode `dvc init` no repo do curso. |
