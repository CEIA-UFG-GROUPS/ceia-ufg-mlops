# 📘 Aula 16 — Data Version Control (DVC)

## Material de Estudo Prévio (Monitor)

Este material tem como objetivo **preparar para a aula de Data Version Control (DVC)**, oferecendo uma base conceitual sólida para acompanhar, complementar e aprofundar a discussão conduzida pelo apresentador.

⚠️ **Este conteúdo não é um guia de instruções**, mas sim um **material de estudo prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do CEIA/UFG.

---

## 🎯 Objetivo da Aula

Ao final desta aula, espera-se que os participantes compreendam:

- Por que **versionar dados e modelos** é tão importante quanto versionar código
- Por que o **Git sozinho não resolve** o problema (e onde o Git LFS fica no meio do caminho)
- Como o DVC funciona por dentro: **cache content-addressable, arquivos `.dvc` e remotes**
- Como definir **pipelines reprodutíveis** com `dvc.yaml` e `dvc repro`
- Como comparar execuções com **params, metrics, plots e experimentos** (`dvc exp`)
- Onde o DVC se encaixa no ecossistema (**Git LFS, lakeFS, Delta Lake, MLflow/W&B artifacts**) e quando escolher cada um

---

## 🧠 Contexto: Por que Versionar Dados?

### Reprodutibilidade em ML é uma equação de quatro variáveis

Em software tradicional, reproduzir um comportamento exige (quase sempre) apenas o **código** na versão certa. Em Machine Learning, um resultado é função de:

```text
resultado = f(código, dados, parâmetros, ambiente)
```

- **Código** → Git resolve (aulas anteriores)
- **Ambiente** → containers resolvem (aula de Docker)
- **Parâmetros** → arquivos de configuração versionados
- **Dados** → ❓ ← o assunto desta aula

Sem versionar dados, perguntas básicas ficam sem resposta:

- *"Com qual dataset exatamente esse modelo em produção foi treinado?"*
- *"O modelo piorou porque o código mudou ou porque os dados mudaram?"*
- *"Como reproduzo o experimento do paper/relatório de 6 meses atrás?"*

> **Auditoria e regulação**: em domínios como saúde e crédito, provar qual dado treinou qual modelo não é conveniência — é requisito legal.

### Por que não simplesmente commitar os dados no Git?

O Git foi projetado para **arquivos de texto pequenos, com diffs linha a linha**:

1. **Binários não têm diff útil**: cada versão de um CSV de 2 GB é armazenada quase inteira de novo — o repositório incha para sempre (o histórico nunca encolhe).
2. **Clones ficam lentos**: todo `git clone` baixa **todo o histórico**, incluindo cada versão antiga do dataset.
3. **Limites dos servidores**: GitHub bloqueia arquivos > 100 MB e recomenda repositórios < 1–5 GB.
4. **Dados nem sempre podem ir para o mesmo lugar que o código**: privacidade e compliance frequentemente exigem que dados fiquem em storage controlado (ex.: bucket na sua cloud), não num host de git público.

### E o Git LFS?

O **Git LFS** substitui arquivos grandes por ponteiros e guarda o conteúdo num servidor LFS. Resolve parte do problema, mas:

- Exige um **servidor LFS** (nos hosts públicos: quotas de armazenamento/banda pagas)
- Não sabe nada de **ML**: não modela pipelines, métricas, experimentos
- Não usa **seu** object storage naturalmente (S3/GCS/Azure) como fonte primária

O DVC nasce exatamente desse gap: **metadados pequenos no Git, dados grandes em qualquer storage, com uma camada de pipelines e experimentos por cima.**

---

## ⚙️ Como o DVC Funciona por Dentro

### A filosofia: "Git para dados" — sem tocar no Git

O DVC **não substitui o Git; ele o completa**. A divisão de responsabilidades:

| O que | Onde fica | Quem versiona |
|---|---|---|
| Código, configs, params | Repositório Git | Git |
| **Metadados dos dados** (`.dvc`, `dvc.lock`) | Repositório Git | Git |
| **Conteúdo dos dados/modelos** | Cache local + remote (S3, GCS, ...) | DVC |

Um commit/tag do Git passa a ser um **snapshot completo e reprodutível**: código + ponteiros para a versão exata dos dados.

### Arquivos `.dvc`: ponteiros versionáveis

Ao rodar `dvc add data/raw/data.csv`, o DVC:

1. Calcula o **hash MD5** do arquivo
2. Move o conteúdo para o **cache** (`.dvc/cache/files/md5/ab/cdef...`)
3. Cria um link do cache para o workspace (reflink/hardlink/symlink — sem duplicar espaço)
4. Escreve um arquivo-ponteiro `data/raw/data.csv.dvc` (poucas linhas de YAML!) e adiciona o dado real ao `.gitignore`

```yaml
# data/raw/data.csv.dvc — isto é o que vai para o Git
outs:
  - md5: a304afb96060aad90176268345e10355
    size: 234510
    path: data.csv
```

### Cache content-addressable: a mesma ideia do Git

O cache é indexado **pelo hash do conteúdo**, não pelo nome do arquivo. Consequências elegantes:

- **Deduplicação automática**: 10 versões do dataset onde só 1 arquivo mudou → só o arquivo mudado é armazenado de novo
- **Trocar de versão é instantâneo**: `dvc checkout` apenas refaz links para os hashes que o `.dvc` da versão atual aponta
- É literalmente o mesmo princípio dos objetos do Git — aplicado a arquivos grandes

### Remotes: o "GitHub dos dados"

```bash
dvc remote add -d storage s3://meu-bucket/dvc
dvc push   # envia o cache para o remote
dvc pull   # baixa do remote o que o workspace atual precisa
```

Suporte a **S3, GCS, Azure Blob, SSH, HTTP, WebDAV, Google Drive, MinIO e diretório local**. O fluxo em equipe espelha o do Git:

```text
colega A: git push  +  dvc push
colega B: git pull  +  dvc pull   → mesmo código, MESMOS dados
```

### O fluxo de "viagem no tempo"

```bash
git checkout v1.0    # restaura código + ponteiros .dvc da época
dvc checkout         # materializa os dados que esses ponteiros indicam
```

---

## 🔁 Pipelines Reprodutíveis: `dvc.yaml` e `dvc repro`

### O problema

Um experimento raramente é um script só: é **preparar → treinar → avaliar**. Rodar tudo na mão gera erros ("esqueci de re-gerar as features") e desperdício ("retreinei tudo só porque mudei o gráfico").

### Stages, deps e outs

O `dvc.yaml` declara o pipeline como um **DAG** de estágios:

```yaml
stages:
  prepare:
    cmd: python src/prepare.py
    deps: [src/prepare.py, data/raw/data.csv]
    params: [prepare.test_size]
    outs: [data/prepared]
  train:
    cmd: python src/train.py
    deps: [src/train.py, data/prepared]
    params: [train.n_estimators, train.max_depth]
    outs: [models/model.pkl]
  evaluate:
    cmd: python src/evaluate.py
    deps: [src/evaluate.py, models/model.pkl, data/prepared]
    metrics:
      - eval/metrics.json: {cache: false}
```

### `dvc repro`: memoização por hash

O comando `dvc repro`:

1. Monta o DAG a partir dos `deps`/`outs`
2. Compara os **hashes** de cada dependência com os registrados no `dvc.lock`
3. **Re-executa apenas os estágios afetados** — mudou só um parâmetro de treino? `prepare` é pulado (*"didn't change, skipping"*)

O `dvc.lock` (versionado no Git) registra os hashes exatos de cada dep/out de cada estágio — é o **certificado de reprodutibilidade** do pipeline.

> Pense no `dvc repro` como um **Makefile ciente de dados**: `make` compara timestamps; DVC compara conteúdo.

---

## 📊 Params, Metrics, Plots e Experimentos

### Parâmetros e métricas como cidadãos de primeira classe

- **`params.yaml`**: hiperparâmetros declarados fora do código; `dvc params diff` mostra o que mudou entre versões
- **`metrics`**: arquivos JSON/YAML de métricas; `dvc metrics show` e `dvc metrics diff` comparam execuções
- **`plots`**: dados tabulares (CSV/JSON) renderizados como gráficos comparáveis (ex.: matriz de confusão, curvas PR/ROC) com `dvc plots show/diff`

### Experimentos (`dvc exp`)

Rodar variações sem poluir o histórico do Git:

```bash
dvc exp run --set-param train.n_estimators=300
dvc exp show     # tabela: experimento × params × métricas
dvc exp apply    # promove o vencedor para o workspace
dvc exp push     # compartilha experimentos
```

Cada experimento é armazenado como referência Git escondida — barato de criar, fácil de descartar. O **DVC Studio** oferece uma interface web colaborativa sobre esses experimentos (papel análogo ao do MLflow Tracking, que vimos em aulas anteriores — os dois podem coexistir: DVC versiona dados/pipeline, MLflow registra experimentos/modelos).

### Data Registry

Um repositório DVC pode servir de **catálogo de datasets** para outros projetos:

```bash
dvc list https://github.com/org/data-registry data/
dvc import https://github.com/org/data-registry data/nlp/corpus.csv
dvc get    https://github.com/org/data-registry data/nlp/corpus.csv  # sem vínculo
```

`dvc import` mantém o vínculo com a origem (dá para atualizar com `dvc update`) — reuso de dados com procedência rastreável.

---

## 🗺️ Ecossistema: DVC e as Alternativas

| Ferramenta | Ideia central | Quando faz sentido |
|---|---|---|
| **Git LFS** | Ponteiros no Git + servidor LFS | Poucos arquivos grandes, sem necessidade de pipelines/ML |
| **DVC** | Metadados no Git, dados no seu storage + pipelines/experimentos | Projetos de ML com datasets de arquivos; equipes que já vivem no Git |
| **lakeFS** | "Git para o data lake": branch/merge/commit sobre object storage inteiro | Data lakes grandes, versionamento no nível da plataforma de dados |
| **Delta Lake / Iceberg / Hudi** | Formatos de tabela com *time travel* transacional | Dados **tabulares** em pipelines Spark/warehouse; versionamento por transação |
| **Pachyderm** | Pipelines + versionamento data-driven sobre Kubernetes | Pipelines de dados containerizados em k8s, triggers por mudança de dado |
| **MLflow / W&B artifacts** | Artefatos anexados a experimentos | Rastrear *outputs* de runs; não versionam o dataset de entrada de forma navegável |
| **DagsHub** | Hospedagem que integra Git + DVC + MLflow | "GitHub para ML" com visualização de dados/experimentos |

**Leitura do quadro**: DVC brilha quando os dados são **arquivos** (imagens, áudios, CSVs, parquets) e o fluxo de trabalho é **centrado no Git**. Quando os dados vivem em tabelas gigantes de um lakehouse, formatos de tabela (Delta/Iceberg) ou lakeFS tendem a ser mais naturais. As abordagens **se combinam**: é comum usar Delta Lake na plataforma de dados e DVC nos projetos de ML que consomem extratos dela.

---

## 💡 Boas Práticas

1. **Um snapshot = um commit**: sempre commite os arquivos `.dvc`/`dvc.lock` junto com o código que os gerou; use **tags** para versões importantes de dados/modelos
2. **`dvc push` faz parte do "done"**: código no Git sem dados no remote = snapshot quebrado para o resto do time
3. **Estruture o workspace**: `data/raw` (imutável, `dvc add`), `data/prepared` (gerado, `outs` do pipeline), `models/`, `eval/`
4. **Nunca edite dados rastreados na mão**: mude a origem e re-execute (`dvc repro`), ou use `dvc unprotect` conscientemente
5. **params fora do código**: tudo que você quiser comparar depois deve estar no `params.yaml`
6. **`metrics: cache: false`**: métricas são pequenas — deixe-as no Git para diffs fáceis
7. **Automatize**: CI que roda `dvc repro` + `dvc metrics diff` em PRs (CML — Continuous Machine Learning — leva isso a comentários automáticos no PR)
8. **Cuidado com dados sensíveis**: o remote precisa seguir as mesmas políticas de acesso dos dados originais

---

## 📊 Casos de Uso Práticos

### Caso 1: Time de pesquisa com datasets de imagens

- **Dor**: dataset de 200 GB de imagens; cada pesquisador tinha "sua cópia" levemente diferente
- **Com DVC**: `dvc add data/images/` (diretório inteiro), remote no bucket do laboratório; cada paper referencia uma **tag do Git** — qualquer resultado é reproduzível com `git checkout tag && dvc pull`

### Caso 2: Modelo tabular com retraining mensal

- **Dor**: "o modelo de março era melhor" — mas ninguém sabia qual dado treinou o de março
- **Com DVC**: pipeline `prepare → train → evaluate` em `dvc.yaml`; a cada mês, novo dado + `dvc repro` + commit. `dvc metrics diff` entre tags mostra a evolução; rollback = checkout da tag anterior

### Caso 3: Auditoria de modelo de crédito

- **Dor**: regulador pergunta que dados treinaram o modelo em produção
- **Com DVC**: o hash do `dvc.lock` no commit do deploy identifica **exatamente** os bytes de cada dependência — resposta em minutos, não em semanas

### Caso 4: Hand-off entre times

- **Dor**: time de dados entrega datasets por e-mail/pastas compartilhadas
- **Com DVC**: um **data registry** central; times consomem com `dvc import`, recebem atualizações com `dvc update`, e sabem sempre a procedência

---

## 🧪 Atividade Prática

A pasta [`atividade/`](./atividade/) contém um laboratório completo que percorre o ciclo do DVC na prática — **versionar dados → viajar no tempo → remote (push/pull) → pipeline com `dvc repro` → métricas e experimentos** — em dois formatos equivalentes:

- **Notebook auto-contido** ([`atividade/notebooks/aula16_pratica_colab.ipynb`](./atividade/notebooks/aula16_pratica_colab.ipynb)): roda no Google Colab (não precisa de GPU) ou localmente, usando um remote em diretório local.
- **Código-fonte + Docker** ([`atividade/src/`](./atividade/src/) e [`atividade/docker/`](./atividade/docker/)): o mesmo pipeline com um **remote S3 de verdade (MinIO)** via docker-compose — simulando o fluxo de equipe `git push + dvc push` / `git pull + dvc pull`.

Instruções completas no [`atividade/README.md`](./atividade/README.md).

---

## 💬 Pontos para Reflexão Pré-Aula

Reflita sobre:

1. **No seu projeto atual, você conseguiria reproduzir o modelo de 3 meses atrás?** O que exatamente está faltando: código, dados, parâmetros ou ambiente?
2. **Por que armazenar dados pelo hash do conteúdo (e não pelo nome) resolve deduplicação e "viagem no tempo" ao mesmo tempo?**
3. **O que deve ir para `dvc add` e o que deve ser `outs` de um pipeline?** (Dica: o que é *fonte* e o que é *derivado*?)
4. **`dvc repro` vs re-rodar tudo na mão**: quanto tempo/dinheiro a memoização por hash economiza num pipeline com etapa de preparação cara?
5. **DVC vs MLflow**: eles competem ou se complementam? Onde termina o versionamento de dados e começa o experiment tracking?
6. **Quando o DVC NÃO é a ferramenta certa?** Pense em dados tabulares gigantes num lakehouse, dados com atualização contínua (streaming), features online.
7. **Governança**: versionar dados sensíveis cria cópias em cache/remote. Que cuidados isso exige?

Esses pontos são fundamentais para enriquecer a discussão durante o encontro.

---

## 📚 Referências

### Documentação oficial

1. **DVC Documentation** — [https://dvc.org/doc](https://dvc.org/doc)
2. **DVC — Get Started (data versioning e pipelines)** — [https://dvc.org/doc/start](https://dvc.org/doc/start)
3. **DVC — User Guide: Project Structure e Internals (`.dvc`, cache)** — [https://dvc.org/doc/user-guide](https://dvc.org/doc/user-guide)
4. **DVC — Experiment Management (`dvc exp`)** — [https://dvc.org/doc/user-guide/experiment-management](https://dvc.org/doc/user-guide/experiment-management)
5. **DVC Studio** — [https://dvc.org/doc/studio](https://dvc.org/doc/studio)
6. **CML — Continuous Machine Learning** — [https://cml.dev/](https://cml.dev/)

### Ferramentas do ecossistema

7. **Git LFS** — [https://git-lfs.com/](https://git-lfs.com/)
8. **lakeFS** — [https://lakefs.io/](https://lakefs.io/)
9. **Delta Lake** — [https://delta.io/](https://delta.io/)
10. **Apache Iceberg** — [https://iceberg.apache.org/](https://iceberg.apache.org/)
11. **Pachyderm** — [https://www.pachyderm.com/](https://www.pachyderm.com/)
12. **DagsHub** — [https://dagshub.com/](https://dagshub.com/)
13. **MinIO (S3 self-hosted, usado na atividade)** — [https://min.io/](https://min.io/)

### Livros e artigos

14. **Huyen, C. (2022).** *Designing Machine Learning Systems*. O'Reilly. — Capítulos sobre dados de treino e reprodutibilidade
15. **Treveil, M. et al. (2020).** *Introducing MLOps*. O'Reilly. — Versionamento como fundação de governança
16. **Sculley, D. et al. (2015).** *Hidden Technical Debt in Machine Learning Systems*. NeurIPS. — A dependência de dados como a dívida técnica mais cara de ML
17. **Sato, D., Wider, A., Windheuser, C. (2019).** *Continuous Delivery for Machine Learning (CD4ML)*. martinfowler.com — [https://martinfowler.com/articles/cd4ml.html](https://martinfowler.com/articles/cd4ml.html)

---

## 🔗 Conexões com Outras Aulas

Este conteúdo se conecta com:

- **Aulas de Git/versionamento de código**: o DVC estende o mesmo modelo mental (commits, tags, push/pull) para dados
- **Aulas de Experiment Tracking (MLflow)**: params/metrics do DVC e o tracking do MLflow se complementam — dados/pipeline vs runs/registry
- **Aula 04 (Containers)**: a atividade usa Docker para subir um remote S3 (MinIO); reprodutibilidade de ambiente + de dados
- **Aulas de Pipelines de Treinamento**: `dvc.yaml` é a versão "leve e git-nativa" de um orquestrador de pipeline
- **Aula 11 (Observabilidade)**: detectou drift e precisa retreinar? O DVC garante que você sabe **de onde partiu**
- **Aula 21 (Servindo Modelos Pesados)**: o modelo que você serve deve apontar para a tag do Git/DVC que o gerou — linhagem de ponta a ponta

---

🚀 **Leitura concluída? Venha para a aula pronto para discutir: se o seu experimento de ontem não é reproduzível hoje, ele é ciência ou sorte?**
