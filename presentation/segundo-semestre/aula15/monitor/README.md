# 📘 Aula 15 — Experiment Tracking com MLflow e W&B

## Material de Estudo Prévio

Este material prepara a discussão sobre experiment tracking e sua relação com
versionamento de dados. O objetivo não é decorar comandos, mas entender que um
experimento de ML precisa deixar evidências suficientes para ser comparado,
reproduzido e auditado.

## 🎯 Objetivos da aula

Ao final, você deverá conseguir:

- explicar o que é um experimento e o que é um run;
- diferenciar parâmetros, métricas, artefatos e tags;
- instrumentar um treinamento com MLflow e W&B;
- comparar execuções e identificar o melhor candidato segundo um critério;
- explicar por que o run também precisa apontar para o dataset e o código;
- distinguir Experiment Tracking, DVC e Model Registry.

## 🧠 O problema: o resultado não é apenas o score

Em Machine Learning, um resultado pode ser representado como:

```text
resultado = f(código, dados, parâmetros, ambiente)
```

Se você guardar apenas `F1 = 0.94`, não sabe se o resultado veio de uma mudança
no código, nos dados, no split, no hiperparâmetro ou no ambiente. Um sistema de
tracking transforma a execução em um objeto consultável.

Um run bem identificado responde:

- qual tarefa foi executada;
- quando e por quem;
- com qual código e seed;
- sobre qual dataset;
- com quais parâmetros;
- com quais métricas;
- quais arquivos foram produzidos.

## ⚙️ Conceitos essenciais

### Experimento

Um agrupamento lógico de runs que investigam o mesmo problema. Exemplo:
`aula15_wine_tracking`.

### Run

Uma execução concreta do treinamento. Alterar um hiperparâmetro ou a seed deve
produzir uma nova execução identificável, e não sobrescrever a anterior.

### Parâmetros

Valores definidos antes ou durante a configuração do treinamento: algoritmo,
seed, tamanho do teste, profundidade da árvore, número de estimadores e assim
por diante.

### Métricas

Valores numéricos observados durante ou depois da execução. Uma métrica precisa
de contexto: split, passo, classe e direção de otimização.

### Artefatos

Arquivos produzidos ou anexados ao run: modelo, matriz de confusão, relatório,
curvas, logs e amostras. O artefato permite inspecionar o resultado além do
número resumido.

### Tags e metadados

Informações usadas para localizar e explicar runs: commit Git, dataset digest,
versão DVC, baseline, responsável e propósito do experimento.

## 🔬 MLflow Tracking

O MLflow organiza o trabalho em experimentos e runs. A API registra parâmetros,
métricas, tags, entradas de dados e artefatos. A UI permite filtrar e comparar
execuções.

Uma configuração enterprise costuma separar:

```text
código de treino ──► Tracking Server ──► backend de metadados
                              │
                              └────────► artifact store
```

No laboratório, o servidor roda localmente com Docker. A aula usa o MLflow para
Tracking; o Model Registry será estudado posteriormente.

## 📊 W&B

No W&B, um projeto agrupa runs e o dashboard organiza os resultados visualmente.
`config` guarda parâmetros, `run.log` registra métricas e Artifacts conectam
datasets, modelos e resultados.

O modo online é adequado para colaboração. O modo offline permite executar sem
credenciais ou rede; depois, os dados podem ser sincronizados conforme a
política da equipe.

## 🔗 Por que DVC aparece nesta aula?

O trecho indicado de Haviv & Gift destaca que dados também precisam de controle
de versão e linhagem. O DVC complementa Git ao manter metadados pequenos no
repositório e o conteúdo dos dados em cache/remote.

O tracking e o DVC respondem perguntas diferentes:

| Pergunta | Camada principal |
|---|---|
| Qual código foi executado? | Git |
| Quais bytes do dataset foram usados? | DVC ou sistema de dados |
| Quais parâmetros e métricas resultaram? | MLflow/W&B |
| Qual modelo foi aprovado para servir? | Model Registry |

O laboratório calcula um digest do dataset e registra a revisão DVC quando um
ponteiro `.dvc` está disponível. Isso cria uma ligação explícita entre dados e
run sem repetir o laboratório de DVC da Aula 16.

## 🧪 Atividade prática

Consulte [`atividade/README.md`](./atividade/README.md). O exercício usa o
dataset Wine do `scikit-learn` e executa o mesmo classificador com MLflow e W&B.

Execução mínima:

```bash
python -m src.prepare_data
python -m src.train --tracker mlflow --seed 42
python -m src.train --tracker wandb --wandb-mode offline --seed 42
```

Depois, compare pelo menos três configurações e responda: qual run você
escolheria e quais evidências sustentam a decisão?

## 💬 Pontos para reflexão

1. Por que uma métrica sem a versão do dataset é insuficiente?
2. O que deve ser uma métrica e o que deve ser um artefato?
3. Qual é a diferença entre armazenar um modelo como artefato e promovê-lo no
   Model Registry?
4. Em que cenário W&B online oferece uma vantagem clara sobre MLflow local?
5. Quais dados sensíveis nunca deveriam ser enviados a um serviço externo?
6. Como você detectaria que dois runs não são comparáveis?

## 📚 Referências

- Haviv, A.; Gift, N. *Implementing MLOps in the Enterprise*. Cap. 4,
  “Working with Data and Feature Stores”, pp. 204–213, seção Data Version
  Control.
- [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/)
- [MLflow Dataset Tracking](https://mlflow.org/docs/latest/dataset/)
- [W&B Experiments](https://docs.wandb.ai/models/track/create-an-experiment)
- [DVC — fluxo de comandos](https://dvc.org/doc/command-reference/)

## 🔗 Conexões com outras aulas

- **Aula 16:** DVC, remotes e pipelines reprodutíveis.
- **Aula 17:** tracking dentro de pipelines de treinamento.
- **Aula 19:** Model Registry, aliases e promoção.
- **Aula 11:** diferença entre métricas offline de treino e observabilidade em
  produção.

> **Pergunta para levar ao encontro:** se um resultado não pode ser reproduzido
> a partir do código, dos dados, dos parâmetros e do ambiente registrados, ele é
> evidência ou apenas uma observação?
