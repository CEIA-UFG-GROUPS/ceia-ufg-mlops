# 📘 Aula 03 — Git, GitHub, GitFlow e Estruturação de Repositórios em MLOps

## Material de Estudo Prévio (Monitor)

Este material prepara o monitor para a aula (Git, GitHub, GitFlow e estruturação de repositórios em ML/MLOps) e serve como **estudo prévio** alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do CEIA/UFG.

---

## 🎯 Objetivo da Aula

Ao final desta aula, espera-se que os participantes compreendam:

- O que é **Git** e por que o controle de versão é essencial em projetos de Machine Learning
- A diferença entre **Git (ferramenta)** e **GitHub (plataforma de hospedagem de repositórios)**
- Conceitos de **branching** (ramificação) e merges, incluindo a estratégia **GitFlow** de gerenciamento de branches
- Boas práticas de **versionamento de código** em projetos de ML, incluindo versionamento de artefatos como dados e modelos
- A importância de uma boa **organização de repositório** (estrutura de pastas, convenções) para reprodutibilidade e colaboração
- Como aplicar essas práticas em pipelines de MLOps (ex.: integrações contínuas, deploys controlados por versão, repositórios como fonte da verdade)

---

## 🧠 Contexto: Por que Versionamento e Repositórios são Críticos em ML?

### Desafios do Desenvolvimento Tradicional vs. Projetos de ML

Em **software tradicional**, o código é o principal ativo versionado e releases são bem definidas. Em **Machine Learning**, o resultado depende de **código, dados, parâmetros e modelo**, com maior risco de erros silenciosos e necessidade de rastrear versões e ambiente para **reprodutibilidade**.

> **"Se não está no controle de versão, não existe."** — ditado popular em desenvolvimento de software, enfatizando a importância de versionar tudo que for relevante

Em resumo, em projetos de ML a falta de controle de versão e organização não causa apenas pequenas falhas: pode **comprometer a validade de todo o experimento ou modelo produzido**. Por isso, adotar Git/GitHub e estruturar bem os repositórios é fundamental para garantir **reprodutibilidade, colaboração eficiente e integração contínua no pipeline de MLOps.**

---

## 🛠️ Git e Controle de Versão

### Conceitos Básicos do Git

**Git** é um sistema de **controle de versão distribuído**. Isso significa que cada colaborador possui uma cópia completa do repositório (histórico de arquivos) localmente, e as mudanças podem ser sincronizadas entre diferentes repositórios. Os conceitos-chave incluem:

- **Repositório (repository)**: um diretório de projeto versionado pelo Git, contendo todo o histórico de commits do projeto. Pode ser local ou remoto (por exemplo, no GitHub).
- **Commit (commit)**: um **registro de alterações no repositório**. Cada commit agrupa um conjunto de modificações em arquivos, com uma mensagem descritiva e um identificador único (hash). Commits permitem voltar no tempo ou entender o histórico de mudanças.
- **Branch (ramo)**: uma **linha do tempo paralela** de commits. O Git permite criar branches facilmente para trabalhar em funcionalidades isoladas, experimentos ou correções, sem afetar a linha principal de desenvolvimento até que se faça um merge.
- **Merge (mesclagem)**: a operação de **unir o histórico** de um branch com outro, integrando as mudanças. Git mantém um histórico detalhado, tornando possível combinar trabalho paralelo e resolver conflitos caso a mesma parte do código tenha sido alterada em branches diferentes.

**Por que usar Git em ML?**

- **Rastreabilidade e reversão**: ligar resultados a commits/tags e voltar a versões estáveis.
- **Colaboração e automação**: trabalho em paralelo com branches e integração com CI/CD.

### Comandos Git Essenciais

**Comandos essenciais**: `git init`, `git clone`, `git status`, `git add`, `git commit`, `git push`, `git pull`, `git branch`, `git merge`.
O monitor pode explicar detalhes conforme o nível da turma.

### Branches e Merges no Git

No Git, criar e gerenciar **branches** é muito leve, o que incentiva seu uso para organizar o trabalho. Algumas boas práticas de branching em projetos de ML:

- **Crie uma branch para cada nova funcionalidade ou experimento**: por exemplo, `feature/novo-modelo-xgboost` ou `experimento/aumentar-dataset`. Assim, você isola o desenvolvimento até ter resultados claros.
- **Use nomes descritivos** para branches: isso ajuda o time a entender o propósito de cada branch (p. ex., `correcao/preprocessamento-nulos` já indica que ali trabalha-se em corrigir tratamento de valores nulos).
- **Mescle com frequência** as branches de volta à principal assim que a funcionalidade estiver pronta/testada: evita divergências longas que causem conflitos complexos. Lembre-se do lema **“commit cedo, commit sempre”** – integrar cedo minimiza surpresas.
- **Resolva conflitos de merge com calma**: ao ocorrerem conflitos (duas alterações incompatíveis na mesma linha de um arquivo, em branches distintas), converse com o autor da outra mudança se necessário e teste o resultado da mesclagem para garantir que o pipeline de ML continua funcionando.

Existem estratégias de merge (merge commit, fast-forward, rebase). Para o grupo, basta dominar o merge básico e combinar uma convenção simples, discutindo com a turma conforme a familiaridade.

---

## 🌐 GitHub e Colaboração em Equipe

GitHub (assim como alternativas GitLab, Bitbucket, Azure DevOps) é uma plataforma de **hospedagem de repositórios Git na nuvem** que facilita a colaboração. Enquanto o Git é a ferramenta de controle de versão, o GitHub oferece:

- **Repositório remoto como fonte da verdade**
- **Controle de acesso e permissões**
- **Interface visual com histórico e diffs**
- **Ferramentas de colaboração** (issues e CI/CD)

Em suma, o GitHub amplia o Git com uma camada social e organizacional, fundamental para times. Em grupos de estudo ou equipes de MLOps, centralizar o trabalho no GitHub garante que todos tenham acesso às últimas versões e possam contribuir de forma controlada.

### Pull Requests e Revisão de Código

Um dos recursos mais importantes do GitHub para colaboração é o **Pull Request (PR)**. Um Pull Request é aberto quando alguém deseja **mesclar mudanças de uma branch para outra** (geralmente de uma branch de feature para a branch principal, como `main` ou `develop`). Ele permite que:

- Os colaboradores e monitores revisem o código proposto **antes** de incorporá-lo. É possível comentar em trechos específicos do código, sugerir modificações e discutir abordagens.
- Rodem-se **checks automáticos** ligados ao PR: por exemplo, uma pipeline de CI pode ser acionada para executar testes unitários ou validações de estilo, garantindo que a contribuição não quebra nada.
- O histórico de discussão e comentários fique registrado, servindo como documentação do raciocínio por trás de certas mudanças (útil para aprendizagem no contexto do grupo de estudos!).

Como monitor, é interessante incentivar a prática de revisão de código via PR mesmo em projetos de estudo. Alguns benefícios:

- **Qualidade de código**: revisões detectam bugs, melhoram clareza e aderência a padrões.
- **Disseminação de conhecimento**: ao revisar, os membros do grupo aprendem partes do projeto em que talvez não tenham trabalhado diretamente e compartilham melhores práticas uns com os outros.
- **Controle de contribuições**: o monitor (ou mantenedores) podem aprovar ou solicitar mudanças, mantendo uma certa **coerência** no repositório.

Além dos PRs, o GitHub oferece **Code Review** com aprovação formal (reviewers aprovam ou requerem mudanças) e **Merge automático** quando a PR é aprovada e cumpre certos requisitos (por exemplo, passes nos testes). Isso simula um ambiente profissional em que nada vai para a branch principal sem validação.

### Fluxos de Trabalho Colaborativos

Existem basicamente dois modelos de colaboração usando Git/GitHub:

- **Modelo de Repositório Centralizado (ou colaborador direto)**: Todos trabalham no mesmo repositório do GitHub, normalmente com uma branch principal protegida (onde só o monitor ou mantenedores podem fazer merge). Os colaboradores criam branches diretamente no repositório central e abrem PRs para mesclar. Este modelo é comum em equipes internas e em grupos pequenos de estudo, onde todos têm acesso de escrita ao repo principal.
- **Modelo Fork & Pull (forking workflow)**: Cada contribuidor faz um **fork** (cópia) do repositório para sua conta, faz as alterações em seu repositório pessoal e então abre um PR para o repositório original. Esse modelo é utilizado em projetos open-source e pode ser adotado se for desejável limitar permissões (ex.: em um grupo grande, ou para convidar contribuições externas). O monitor neste caso atua como mantenedor que revisa e aceita PRs de vários forks.

Independentemente do modelo:

- **Comunicação** é chave: usar as issues para discutir mudanças antes de implementá-las evita retrabalho. Ex.: antes de alguém refatorar uma função de preprocessamento, abrir uma issue ou discussão no repositório para alinhar se é desejável.
- **Conventional Commits/Messages**: incentivar padrões em mensagens de commit e descrições de PR (por exemplo, prefixos como feat:, fix:, docs: indicando o tipo de mudança) pode ajudar a gerar changelogs e entender o histórico facilmente.
- **Resolução de Conflitos em equipe**: eventualmente, dois membros podem editar a mesma parte do código em paralelo. Nesses casos, ao tentar mesclar, ocorrerá um conflito. É importante não entrar em pânico: Git sinaliza os conflitos nos arquivos envolvidos, e os desenvolvedores devem conversar e decidir qual versão do trecho conflituoso prevalece ou como combinar as contribuições. Isso também faz parte do aprendizado colaborativo.

**GitHub Issues & Projetos**: Como monitor, você pode usar issues para distribuir tarefas (ex.: Issue 1: Atualizar README com instruções de setup, Issue 2: Implementar função X). Ferramentas de projeto (Project Boards) permitem acompanhar o status (To do / Doing / Done). Essa organização alia-se bem com GitFlow (cada issue pode virar uma branch de feature) ou com PRs (cada PR fecha uma issue ao ser mesclado).

Em resumo, GitHub fornece não só o lugar para guardar o código, mas todo um **ambiente de colaboração**. Cabe ao monitor incentivar o uso dessas ferramentas para que o grupo de estudo vivencie práticas de desenvolvimento de software profissional aplicadas ao ciclo de vida de Machine Learning.

---

## 🔀 Estratégias de Branching: GitFlow e Alternativas

Quando se trabalha em equipe, definir uma estratégia de branching clara é importante para organizar o ciclo de desenvolvimento. Em projetos MLOps, isso pode incluir como lidamos com branches de experimentação, de produção, de hotfixes em modelos em produção, etc.

### GitFlow: Visão Geral

**GitFlow** é uma estratégia de branching popularizada por Vincent Driessen (2010) para gerenciar o desenvolvimento e lançamentos em projetos que requerem versões formais. É caracterizada por múltiplos ramos permanentes e ramos de suporte de curta duração. Os principais componentes do GitFlow são:

- **Branch `main`**: é o ramo principal que contém sempre o código de produção (estável). Nele ficam as versões já lançadas do software/modelo. Idealmente cada **release** de produto é marcada com uma tag (ex.: `v1.0.0`).
- **Branch `develop`**: é o ramo de desenvolvimento integrado. Nele são mescladas as features em desenvolvimento e é a base para o próximo lançamento. Representa o estado "pré-produção" com as últimas implementações já integradas e testadas conjuntamente.
- **Branches de *feature***: ramos criados a partir de `develop` para desenvolver novas funcionalidades ou experimentos de ML. Por exemplo, `feature/novo-algoritmo-arvore` poderia ser uma branch onde se está implementando um novo modelo de árvore de decisão. Após concluir e testar localmente a feature, ela é **mergeada de volta em `develop`**.
- **Branches de *release***: quando chega o momento de preparar uma nova versão (por exemplo, um pacote de modelos v2.0), cria-se um ramo de release a partir de `develop` (ex.: `release/2.0`). Nele, apenas ajustes finais, testes e correções de bugs são realizados – **novas features não entram aqui**. Ao terminar, essa branch é mesclada em `main` (marcando o lançamento oficial) e de volta em `develop` (para que `develop` receba eventuais correções feitas). Em seguida, a branch de release é deletada.
- **Branches de *hotfix***: são ramos para corrigir problemas críticos encontrados em produção. São criados a partir de `main` (por exemplo, `hotfix/corrigir-leak-dados`) e, após a correção, mesclados tanto em `main` (gerando possivelmente um release imediato, ex: v1.0.1) quanto em `develop` (para que a correção também faça parte do próximo release).

**Fluxo do GitFlow resumido**: O trabalho cotidiano acontece em branches de feature derivadas de `develop`. Releases planejam a junção e estabilização do que está em `develop` para `main`. Hotfixes cuidam de apagar incêndios em `main` sem esperar o próximo ciclo de release.

**Vantagens do GitFlow:**

- Permite um **controle rigoroso de versões** em produção, adequado quando há necessidade de lançar versões oficiais (por exemplo, uma API de modelo versionada, releases de um pacote de ML interno, etc.).
- Suporta múltiplas versões em paralelo – por exemplo, pode-se estar preparando a versão 2.0 em uma branch release enquanto corrige-se algo urgente na 1.0 via hotfix.
- A separação entre `develop` e `main` cria um ambiente onde o código integrado (`develop`) pode ser testado exaustivamente antes de ir para produção. Isso pode ser associado a um ambiente de staging para modelos (deploy de teste com dados reais) enquanto `main` reflete o ambiente de produção real.

**Desvantagens do GitFlow:**

- É mais complexo e pode gerar overhead em times muito ágeis ou em ML contínuo, onde uma estratégia simples costuma funcionar melhor.

**Exemplo rápido**: `main` mantém produção, `develop` integra features, `release/x.y` prepara versões e `hotfix` corrige urgências, sempre mesclando de volta em `main` e `develop`.

### Trunk-Based Development (Fluxo Simples)

Em contraste ao GitFlow, muitas equipes adotam uma estratégia mais simples conhecida como **Trunk-Based Development**(desenvolvimento baseado em tronco, ou às vezes chamado **GitHub Flow** quando usando GitHub). As características dessa abordagem:

- Existe apenas uma **branch principal (geralmente `main`)**, que sempre contém o código pronto para produção (ou próximo disso).
- Desenvolvedores criam branches curtas para cada mudança ou feature quando necessário, mas essas branches duram pouco tempo e são logo mescladas de volta em `main`. Muitas vezes, pequenas mudanças são feitas diretamente na branch principal através de PRs de curta vida.
- Não há branch `develop` permanente nem branches de release; o controle de versão de lançamento é feito via **tags** ou simplesmente utilizando a própria `main` quando se deseja um marco.

**Vantagens:**

- **Simples e ágil**: menos branches para gerenciar.
- **Integração contínua**: mudanças pequenas entram com frequência, reduzindo divergências longas.

**Desvantagens:**

- Requer **disciplina em testes e qualidade**: como tudo vai para a branch principal rapidamente, é crucial que haja uma boa suíte de testes automatizados e validações (por exemplo, checar se o novo modelo não caiu a acurácia abaixo do esperado antes de aprovar o PR). Sem isso, corre-se risco de quebrar a versão principal frequentemente.
- Pode ser confuso gerenciar lançamentos em produção sem um ramo separado: muitas equipes acabam usando tags para marcar versões ou mantendo uma branch estável separada se necessário, aproximando-se de um mini-GitFlow.
- Em times muito grandes, merges muito frequentes na mesma branch podem causar gargalos de integração (embora a filosofia trunk-based argumente que times grandes devem se coordenar em partes independentes ou usar feature flags).

**GitHub Flow** é uma variante muito utilizada, especialmente em projetos open source: basicamente trunk-based, porém todas as mudanças passam por uma Pull Request antes de entrar no main (mesmo pequenas). Não há develop; a estabilidade é garantida via revisão de PR e automação.

Para projetos de MLOps, a escolha entre GitFlow e trunk-based pode depender de quão formal é o ciclo de releases de modelos:

- Se você tem **iterações rápidas, experimentação constante** e deployment contínuo de modelos (por exemplo, em um sistema online de aprendizado contínuo), trunk-based pode ser mais apropriado.
- Se você tem **releases mais cadenciados e controlados** (por exemplo, um pacote de modelos entregue a um cliente a cada mês, ou uma aplicação que só pode atualizar modelo após validação/regulamentação), GitFlow proporciona mais controle e rastreabilidade de versões específicas.

### Qual Estratégia Usar?

**Não existe resposta única** – muitas equipes adotam misturas dos dois. Alguns padrões comuns:

- Manter apenas `main` e usar branches de feature curtas (GitHub flow puro) é ótimo para início de projetos e grupos pequenos. No contexto do nosso grupo de estudos, pode ser a forma inicial: todos trabalhando em melhorar um único pipeline de forma incremental.
- À medida que o projeto cresce, pode-se introduzir um branch `develop` para evitar que código não testado vá direto para produção, adotando um GitFlow simplificado. Por exemplo, talvez não sejam necessários branches de release formais no grupo de estudos, mas ter `main` (para código considerado estável) e `develop` (para integrações em andamento) já ajuda a organizar entregas para quem eventualmente consome o resultado fora do grupo.
- O importante é garantir que a equipe **entenda e siga a estratégia escolhida**. Como monitor, vale discutir os prós e contras com os participantes:
- **Frequência de deploy**: se a intenção é fazer deploy contínuo dos modelos, trunk-based encaixa. Se os modelos passam por etapas de aprovação fora do time, GitFlow encaixa melhor.
- **Tamanho do time**: times maiores frequentemente formalizam mais (GitFlow), times pequenos e coesos preferem agilidade (trunk).
- **Ferramentas de CI/CD disponíveis**: se há pipelines que automatizam testes e validações robustas, trunk-based flui bem. Sem muita automação de teste, um develop branch manualmente testado pode evitar bugs em `main`.

Em suma, **escolha uma estratégia e documente-a no repositório** (por exemplo, no README ou Wiki do projeto). Deixe claro como nomear branches, quando deletá-las, quem aprova PRs, etc. Essa clareza evita confusão e conflitos durante o desenvolvimento colaborativo.

---

## 📁 Boas Práticas de Organização de Repositórios de ML

Organizar o repositório de forma lógica é especialmente importante em projetos de Machine Learning, porque precisamos lidar com diferentes tipos de artefatos (código, dados, modelos, notebooks, configurações, etc.). Abaixo estão **boas práticas** de organização e manutenção de repositórios que o monitor deve conhecer e incentivar:

- **README e Documentação**: Todo repositório deve ter um arquivo `README.md` bem escrito, explicando o objetivo do projeto, instruções de configuração do ambiente, como reproduzir resultados (por exemplo, passos para treinar o modelo), e contatos. Uma boa documentação inicial facilita a entrada de novos colaboradores e até mesmo dos participantes do grupo a re-executar partes do projeto no futuro.
- **Estrutura de pastas semântica**: Separe diferentes tipos de artefatos em pastas específicas. Por exemplo, códigos fonte (scripts, módulos Python) ficam em uma pasta `src/` ou similar; notebooks exploratórios em `notebooks/`; dados em bruto e processados em `data/`; modelos exportados em `models/`; configurações em `configs/` ou no README; documentos ou relatórios em `docs/` ou `reports/`. Essa separação torna fácil encontrar o que se procura e evita misturar arquivos de naturezas diferentes.
- **Nomenclatura consistente**: Defina convenções de nomes para arquivos, funções, classes e até branches. Por exemplo, arquivos Python em snake_case, classes em PascalCase, notebooks prefixados por número de ordem (`01_exploration.ipynb`, `02_training.ipynb`), branches de feature prefixadas por `feature/`. Coerência nos nomes evita confusões e conflitos.
- **Evitar arquivos e dados temporários no repositório**: Não versionar arquivos gerados que possam ser recriados a partir do código/dados fonte. Exemplo: não é necessário subir arquivos CSV processados se eles podem ser produzidos pelo script de preprocessamento; não versionar outputs de notebook nem arquivos de log. Use o `.gitignore` para ignorar arquivos que não devem ir para o Git (ex.: grandes datasets, checkpoints temporários, credenciais, etc.).
- **Versionar configurações e dependências**: Em ML, o ambiente e parâmetros são tão importantes quanto o código. Inclua no repositório arquivos como `requirements.txt` ou `environment.yml` (no caso de conda) listando as bibliotecas e versões necessárias para rodar o projeto. Considere também versionar configurações de hiperparâmetros ou paths em arquivos YAML/JSON de config. Dessa forma, alguém pode instalar as mesmas versões de libs e obter resultados consistentes.
- **Scripts de automação**: Para facilitar a vida, pode-se incluir scripts do tipo `Makefile` ou shell scripts (`scripts/treinar_modelo.sh`) que automatizam tarefas comuns (como preparar dados, treinar, avaliar). Isso documenta o processo e reduz erros manuais.
- **Testes automatizados**: Sempre que possível, incluir testes (em Python, por ex., usando `unittest` ou `pytest`) para funções críticas do pipeline de ML. Testes podem pegar bugs em preprocessamento, assegurar que métricas não pioraram, etc. Um repositório de MLOps maduro inclui testes de unidade para componentes e até testes de integração (como rodar uma pequena porção do treinamento para verificar fim a fim).

### Exemplo de Estrutura de Pastas

A seguir, um exemplo de estrutura de repositório para um projeto de Machine Learning, inspirado em um template de referência (Cookiecutter Data Science). Os nomes podem variar conforme a preferência, mas a ideia é cobrir as principais áreas:

```text
├── README.md          <- Descrição do projeto, instruções e documentação principal
├── data
│   ├── raw            <- Dados brutos originais (ex: arquivos CSV não processados)
│   ├── interim        <- Dados intermediários (ex: após alguma transformação, para uso interno)
│   ├── processed      <- Dados finais já prontos para modelagem ou uso em produção
│   └── external       <- Dados de fontes externas (ex: de terceiros) utilizados no projeto
├── notebooks          <- Notebooks Jupyter utilizados para exploração e experimentos
│                         (pode-se adotar convenção de nome: 1_Exploracao.ipynb, 2_Treinamento.ipynb, etc.)
├── models             <- Modelos treinados, artefatos de modelo, outputs de treino (ex: arquivos .pkl)
├── src                <- Código fonte do projeto (módulos, scripts de pipeline, etc.)
│   ├── data           <- Scripts para obtenção e pré-processamento de dados
│   ├── features       <- Scripts para transformação de dados brutos em features para o modelo
│   ├── models         <- Scripts para treinamento de modelos e para gerar predições com modelos treinados
│   └── visualization  <- Scripts para criação de visualizações (graficos, etc.) das análises ou resultados
├── tests              <- Testes automatizados (unitários/integrados) para garantir funcionamento do código
├── docs               <- Documentação extra do projeto (ex: whitepapers, manuais de usuário)
├── references         <- Referências diversas, datasheets de datasets, materiais de apoio
├── reports            <- Relatórios gerados com análises, resultados e métricas
│   └── figures        <- Imagens e gráficos gerados que são utilizados nos relatórios
├── requirements.txt   <- Lista de dependências Python (gerada com `pip freeze > requirements.txt`, por ex.)
├── environment.yml    <- (Opcional) Definição de ambiente Conda para reproduzir o setup
├── .gitignore         <- Arquivos e padrões ignorados pelo Git (ex: `*.pyc`, credenciais, grandes datasets)
└── .github/workflows  <- (Opcional) Configurações de CI/CD (ex: pipelines do GitHub Actions para testes/deploy)
```

Essa estrutura cobre os principais componentes. Ao segui-la, obtemos vários benefícios:

- **Facilidade de navegação**: qualquer pessoa que olhar o repositório entende onde estão os notebooks, onde estão os dados, onde estão os códigos reutilizáveis, etc., sem ter que abrir vários diretórios bagunçados.
- **Modularização**: separa claramente as responsabilidades (por exemplo, código de processamento de dados separado do código de modelagem). Isso torna o trabalho em paralelo mais fácil e reduz conflitos (cada um trabalha em arquivos diferentes).
- **Reprodutibilidade**: com dados brutos versionados ou pelo menos referenciados, e scripts que geram dados processados, fica claro como reproduzir os datasets de treino. Com modelos salvos e scripts de inferência, sabe-se exatamente de onde veio cada resultado.
- **Manutenibilidade**: caso o projeto evolua (por exemplo, adiciona-se um novo modelo), há um lugar lógico para colocar cada novo componente sem virar uma massa desorganizada.

Vale notar que nem sempre todos esses diretórios serão usados; cada projeto pode ajustar a estrutura. O importante é **ter um padrão definido** e segui-lo, ao invés de adicionar pastas/arquivos arbitrariamente. Como exercício, o monitor pode comparar essa estrutura com a do projeto do grupo de estudos atual e avaliar o que pode ser melhorado.

### Versionamento de Dados e Modelos

Um desafio especial em MLOps é versionar não apenas o código, mas também **dados e modelos treinados**:

- O Git, por padrão, funciona muito bem com arquivos de código (textuais) de tamanho moderado. Porém, datasets podem ser enormes (gigabytes) e modelos serializados também (centenas de MB). Versionar esses arquivos diretamente no Git não é recomendado – o repositório ficaria pesado e lento.
- Para contornar isso, existem extensões e ferramentas: **Git LFS (Large File Storage)** permite versionar arquivos grandes armazenando-os fora do repositório Git normal e baixando sob demanda. Ferramentas específicas como **DVC (Data Version Control)** criam ponteiros para dados mantidos em storage externo (S3, Google Drive, etc.), integrando com Git para que cada versão de código aponte para uma versão de dataset.
- Em cenários de MLOps mais avançados, utiliza-se também **model registries** (por exemplo, o do **MLflow**) para registrar versões de modelos treinados com metadados, métricas e até link para o commit do código que gerou aquele modelo. Isso permite rastrear qual código e hiperparâmetros resultaram em determinado modelo em produção.

No contexto do nosso grupo de estudo:

- **Não versione no Git dados brutos muito grandes**. Se for necessário compartilhar dados entre os participantes, considere usar um repositório externo (um bucket cloud, um Google Drive compartilhado) e disponibilizar scripts em `src/data` para baixar/carregar esses dados automaticamente. Documente no README como obter os dados.
- Pequenos datasets ou amostras podem ser versionados no Git (ex.: um csv de 5 MB com exemplos). Da mesma forma, modelos pequenos de exemplo podem ser incluídos, mas modelos grandes devem ficar fora (talvez disponibilizados via link).
- **Registre manualmente a versão dos dados usada em cada experimento**: por exemplo, se o dataset for atualizado, anote na documentação ou no nome do arquivo uma versão/data. Melhor ainda, use versionamento semântico se couber (ex: `dataset_v1.0.csv, dataset_v1.1.csv`). Assim, durante a aula, pode-se discutir o impacto de mudanças de dataset.
- Apresente aos participantes ferramentas como DVC, MLflow ou até simples hashes de arquivos para verificar integridade dos dados. Talvez não haja tempo de aprofundar em todas, mas o monitor deve ao menos citar: *"Para projetos reais de ML, é recomendável usar ferramentas de versionamento de dados (como DVC) para complementar o Git, pois o Git sozinho não lida bem com arquivos muito grandes."* Isso dá visão de como escalar as práticas aprendidas.

Resumindo, **versionar código no Git** é o mínimo, **estruturar o repositório** melhora a eficiência, e ter estratégia para **versão de dados/modelos** completa o quadro de reprodutibilidade. Esse é o núcleo de uma boa engenharia em MLOps.

---

## 📝 Sugestões de Atividades e Discussões

Para tornar a aula dinâmica e fixar os conceitos, o monitor pode propor as seguintes atividades ou tópicos de discussão ao grupo:

1. **Mão na massa com Git**: praticar fluxo básico (*clone -> branch -> commit -> PR -> merge*).
2. **Desenhar a estrutura de um projeto de ML**: comparar com o exemplo proposto.
3. **Revisão de um repositório público**: identificar estrutura, README, CI, branches.
4. **Simulação de conflito Git**: resolver conflitos com orientação do monitor.
5. **Lightning talk de ferramentas de MLOps**: pesquisas rápidas sobre DVC, MLflow ou CI/CD em ML.

Ajuste as atividades ao nível da turma e priorize prática para iniciantes.

---

## 💬 Pontos para Reflexão Pré-Aula

Como monitor, reflita sobre:

1. **Quais são os principais desafios de não usar controle de versão em projetos de ML?**
   - Considere impactos na reproducibilidade: você conseguiria recriar um modelo treinado meses atrás sem histórico?
   - Pense em colaboração: o que poderia dar errado se duas pessoas editam o mesmo código de forma separada (fora do Git)?

2. **Como introduzir Git/GitHub para membros do grupo que talvez nunca tenham usado?**
   - Que analogias ou explicações acessíveis usar para explicar commit, push, pull?
   - Vale a pena demonstrar visualmente (desenhar o fluxo ou usar ferramentas visuais de Git) para facilitar o entendimento?

3. **O que não colocar em um repositório de ML?**
   - Reflita sobre dados sensíveis (privacidade) ou arquivos enormes. Como lidar com esses casos?
   - Pense em técnicas: usar amostras de dados no repo e deixar full dataset fora? Utilizar `.gitignore` e instruir como obter dados externamente?

4. **Como garantir que o repositório continue organizado conforme o projeto evolui?**
   - Que medidas o monitor pode tomar? (ex.: revisar PRs focando também na organização, não só no código)
   - Documentar convenções no README ou Wiki – isso está feito? Está claro para todos?

5. **Branching e fluxo ideais para nosso contexto atual:**
   - Dada a dinâmica do nosso grupo (tamanho, frequência de encontros, objetivos), qual estratégia de branching faz mais sentido começar usando? (Uma branch `main` única? Um `develop` separado? Branches de experimento para cada participante?)
   - Como lidar se alguém quiser testar uma ideia arriscada que pode não ir adiante – encorajar branch à parte e depois descartar se não funcionar?

6. **Integração com Pipelines Automatizados:**
   - Pense em como poderíamos acoplar este repositório a um processo automatizado: por exemplo, *"Seria útil treinar o modelo automaticamente a cada novo commit na branch principal?"* ou *"Executar testes de desempenho quando há merge de uma nova feature?"*.
   - Mesmo que não implementemos agora, imaginar essas integrações ajuda a entender o **papel central do repositório**: ele é a fonte a partir da qual todo o pipeline MLOps desencadeia (desde testes até deploy). Estamos estruturando ele de modo a permitir isso no futuro?

Esses pontos são fundamentais para enriquecer a discussão durante o encontro. Antecipe perguntas que os participantes possam fazer (por exemplo: *"Posso usar Google Drive em vez de Git?"* ou *"Preciso mesmo aprender GitFlow?"*) e esteja pronto para responder com exemplos e analogias. Quanto mais clareza você tiver sobre esses tópicos, mais segurança terá ao conduzir a aula e mais conseguirá instigar reflexões nos colegas.

---

## 📚 Referências

### Livros e Artigos

- **Chacon, S., & Straub, B. (2014).** *Pro Git* (2ª ed.). Apress (livro gratuito online).
  - Guia completo do Git, cobrindo desde o básico de commits e branches até tópicos avançados como rebase, stash e workflows distribuídos.
  - Excelente referência para aprofundar comandos e entender os conceitos por trás do funcionamento do Git (instantâneos, hashes, merges, etc.).
- **Humble, J., & Farley, D. (2010).** *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation*. Addison-Wesley.
  - Clássico sobre integração contínua e entrega contínua. Embora focado em software geral, traz princípios aplicáveis a MLOps, como a importância de controle de versão, ambientes consistentes e pipelines automatizados.
  - Discute estratégias de branching e integração de código frequente, base para entender por que abordagens como trunk-based surgiram para viabilizar deploys rápidos.
- **Sculley, D., et al. (2015).** *Hidden Technical Debt in Machine Learning Systems*. Conference on Neural Information Processing Systems (NeurIPS).
  - Artigo seminal do Google que explora diversos tipos de “dívida técnica” em sistemas de ML. Relevante aqui por destacar problemas de **versão de dados e configurações**: code smell de “Configuration Debt” e “Data Dependency” mostram como a falta de rastreabilidade de dados/modelos leva a sistemas instáveis.
  - Ajuda o monitor a fundamentar a discussão sobre por que precisamos tratar dados/modelos como cidadãos de primeira classe no versionamento, não apenas o código.

### Documentação e Recursos Online

- **Documentação Oficial do Git** — git-scm.com/docs.
- **Guias do GitHub** — docs.github.com.

### Artigos e Blog Posts

- **Driessen, V. (2010).** *“A successful Git branching model”*. *nvie* blog.
  - Post original que introduz o GitFlow. Documento de leitura obrigatória para compreender em detalhe a motivação e funcionamento dessa estratégia de branching.
  - Embora antigo, continua relevante e muitos projetos derivam suas políticas de branching dele. O monitor pode extrair dele figuras ou trechos se precisar explicar visualmente o fluxo GitFlow.
- **Fowler, M. (2015).** *“Feature Branching vs. Continuous Integration”*. martinfowler.com.
  - Artigo de Martin Fowler discutindo os trade-offs entre trabalhar em branches longas (feature branching prolongado, alinhado ao GitFlow) versus integrar continuamente mudanças pequenas (trunk-based).
  - Ajuda a enriquecer o debate sobre estratégias de branching com argumentos de um expert em engenharia de software. Fornece embasamento teórico para questões como “branches curtos x branches longos”, “integração frequente x tardia”, que podem surgir na aula.
- **Google Cloud — *MLOps: Continuous delivery and automation pipelines in machine learning*** (whitepaper/artigo).
  - Publicação do Google Cloud que explora práticas de MLOps, incluindo versionamento de código e dados, automação de pipelines de treinamento e deploy contínuo de modelos.
  - Relevante para conectar o conteúdo da aula com a visão de MLOps de ponta: ilustra como repositórios Git acionam pipelines (CI/CD) que treinam e validam modelos automaticamente, e como equipes estruturam isso na prática em escala de produção.

### Ferramentas e Frameworks

- **Git** — git-scm.com.
  - Sistema de controle de versão distribuído criado por Linus Torvalds. Ferramenta de linha de comando principal utilizada para versionamento de código.
  - Multiplataforma e open-source, Git é a base sobre a qual praticamente todas as outras ferramentas aqui listadas operam.
- **GitHub** — github.com.
  - Plataforma de hospedagem de repositórios Git, com recursos de colaboração (PRs, issues, wiki, Actions/CI).
- **DVC (Data Version Control)** — dvc.org.
  - Ferramenta open-source para controle de versão de dados e modelos, integrando-se ao Git. Permite **trackear arquivos grandes** (datasets, modelos) via metafiles no Git, enquanto os dados em si ficam em armazenamento externo (S3, Azure Blob, Google Drive, etc.).
  - Muito útil em MLOps: com DVC, você consegue sincronizar datas específicos para um commit de código, tornando reprodutível a preparação de dados e treinamento. Pode comentar sobre DVC ao discutir versionamento de dados.
- **MLflow** — mlflow.org.
  - Plataforma de gerenciamento de ciclo de vida de ML (open-source, iniciada pela Databricks). Oferece componentes para *Tracking* de experimentos (log de métricas, parâmetros, etc.), *Model Registry* (registro e versionamento de modelos), dentre outros.
  - No contexto da aula, é relevante pelo **Model Registry**: o MLflow pode versionar modelos treinados com tags e meta-informações, e guardar o hash do commit Git do código que produziu o modelo, fechando o loop de reprodutibilidade.
- **Git LFS (Large File Storage)** — git-lfs.github.com.
  - Extensão oficial do Git para armazenamento de arquivos grandes. Em vez de salvar o conteúdo de arquivos gigantes no histórico do Git (o que o tornaria lento), salva apenas ponteiros e mantém o conteúdo real em um armazenamento separado otimizado.
  - Útil para versionar, por exemplo, pesos de redes neurais ou conjuntos de dados moderados dentro do GitHub. O monitor pode demonstrar ou explicar seu uso simples (`git lfs track "*.bin"` etc.) se houver interesse do grupo em manter alguns artefatos versionados sem degradar a performance do repositório.

---

## 🔗 Conexões com Outras Aulas

Este conteúdo se conecta com:

- **Aula 01 (Introdução ao MLOps)**: O uso de controle de versão e repositórios é um dos pilares fundamentais apresentados na introdução ao MLOps, pois está diretamente ligado à **reprodutibilidade e colaboração** no ciclo de vida de ML. Tudo começa com código versionado de forma adequada.
- **Aula 08 (Deploy de Modelos)**: O deploy de um modelo em produção depende de sabermos exatamente **qual versão de código e de modelo** estamos implantando. Práticas de Git/GitHub (como tags de release ou commit hash) permitem atrelar um deploy a um ponto específico do repositório, garantindo confiança no que está indo para produção.
- **Aula 09 (Pipelines CI/CD)**: A automação de pipelines de treinamento, teste e deployment (CI/CD para ML) gira em torno de gatilhos baseados em versões de repositório. Por exemplo, um commit na branch principal pode disparar um pipeline de re-treinamento; um pull request pode disparar testes unitários do código. Assim, Git + pipelines constituem juntos o **motor de entregas contínuas** em MLOps.

---

🚀 Leitura concluída? Venha para a aula pronto para questionar, complementar e conectar conceitos sobre versionamento de código, colaboração e organização de projetos de ML.
