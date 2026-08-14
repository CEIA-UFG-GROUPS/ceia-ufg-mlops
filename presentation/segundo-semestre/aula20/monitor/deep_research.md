# Entrega Contínua para Modelos de Aprendizado de Máquina: CI, CD, CT e o Risco Sistêmico de Dependências

A literatura e a prática industrial de MLOps convergem na observação de que pipelines de integração contínua desenhados para software determinístico são estruturalmente insuficientes quando o artefato sob versão é um estimador estatístico cujo comportamento emerge da combinação de código, dados, hiperparâmetros e ambiente de execução^^. O presente texto examina, em profundidade e em língua técnica, o desenho contemporâneo de **Continuous Delivery for Machine Learning (CD4ML)**, a tríade **CI / CD / CT**, a operacionalização desses conceitos em GitHub Actions, a economia de onde treinar, a dimensão de cadeia de suprimentos (*model supply chain*), as pressões do **Regulamento (UE) 2026/1744**, a extensão do mesmo raciocínio a sistemas com Grandes Modelos de Linguagem, e — deliberadamente — o estudo de caso da ferramenta **CML** como lição sobre risco de dependência em plataformas de MLOps.

## Genealogia: de CI clássico a CD4ML e ao eixo que quebra a analogia

A integração contínua clássica nasceu para responder a uma pergunta de engenharia de software: *esta mudança de código introduz regressão detectável por testes automatizados?* Humble e Farley generalizaram o raciocínio até a **entrega contínua**, na qual cada artefato aprovado torna-se candidato legítimo a produção mediante um funil de validações^^. Thoughtworks, ao formular o **CD4ML**, deslocou o objeto do funil: além do binário construído a partir do código, o pipeline passa a incorporar experimentação reproduzível, validação de dados, comparação de desempenho preditivo e mecanismos de implantação alinhados a risco de negócio^^. Google Cloud, em sua taxonomia de maturidade de MLOps, descreve níveis crescentes de automação em que o re-treinamento contínuo e a entrega do modelo deixam de ser eventos manuais e passam a ser reações a sinais de dados, de desempenho ou de calendário^^.

A implicação pedagógica é direta. A **Aula 10** do primeiro semestre estabelece o vocabulário de Actions, imagens Docker e segredos. A Aula 20 assume esse substrato e desloca a pergunta central: não basta perguntar se o *build* passou; é preciso perguntar se o *candidato* respeita um contrato quantitativo perante uma *baseline* — e se há evidência auditável dessa decisão.

O ponto em que a analogia com software se rompe é o **eixo de dados**. Em um microsserviço convencional, o mesmo commit, compilado no mesmo ambiente, produz o mesmo comportamento funcional (salvo estado externo). Em aprendizado de máquina, o mesmo commit de código de treino, alimentado por outro recorte temporal da Feature Store ou por um lote com vazamento sutil de rótulos, materializa um estimador diferente — com outra superfície de erro, outro perfil de fairness e outra assinatura de risco regulatório. Por isso o CI de ML não pode limitar-se a *lint* e *unit tests*: precisa tratar snapshot de dados, métricas e digest do artefato como cidadãos de primeira classe do contrato de merge. O survey de Eken et al. (ACM Computing Surveys 58(2), Art. 39, set/2025, DOI 10.1145/3747346) sintetiza essa convergência empírica da indústria em torno de automação, linhagem e governança^^.

## CI, CD e CT como Dimensões Distintas do Mesmo Loop

É frequente, em discussões informais, colapsar “CI/CD de ML” numa única sigla. A precisão analítica exige três eixos:

1. **Continuous Integration (CI)** — a cada alteração proposta (tipicamente um *pull request*), executam-se validações de código, de esquema de dados e de métricas do modelo. O produto epistemológico do CI é um veredito binário com artefatos anexos: passou ou não passou, com evidência.
2. **Continuous Training (CT)** — decide *quando* e *com quais dados* um novo candidato deve ser materializado. Gatilhos comuns incluem chegada de lotes rotulados, janelas temporais, ou alertas de *drift* (tratados na Aula 23). O CT frequentemente aciona um orquestrador (Aula 17); esta aula não revisita Operators de Airflow/Prefect, mas posiciona o CT como o motor que alimenta o CI de modelos.
3. **Continuous Delivery / Deployment (CD)** — promove o artefato aprovado. Em ML moderno, a promoção raramente é “copiar o `.joblib` para o servidor”; é atualizar um **alias** no Model Registry (`@challenger`, eventualmente `@champion` — Aula 19) e, em arquiteturas maduras, deixar que um controlador GitOps reconcilie o estado desejado no cluster (Argo CD, Flux) com estratégias progressivas de tráfego (Aula 22).

O fechamento do loop — monitorar, detectar degradação, re-treinar, validar, promover — é o que distingue plataformas de nível de maturidade elevado das pastas compartilhadas de modelos “finais”.

## Anatomia Operacional em GitHub Actions

A escolha pedagógica de GitHub Actions não é idolatria de fornecedor; é reconhecimento de que a unidade de trabalho do cientista e do engenheiro de ML já é o *pull request*. Um desenho mínimo viável de CD4ML em Actions organiza-se em jobs encadeados por `needs:`:

- validação de dados (schema, nulos, faixas);
- treinamento CPU-bound de um candidato leve;
- *quality gate* quantitativo contra `baseline_metrics.json`;
- geração de um relatório markdown de *model-diff*;
- varredura básica de integridade (digest SHA-256; assinatura opcional);
- registro no registry **somente** após push aprovado em `main`.

Dois detalhes de engenharia merecem ênfase. Primeiro, o **comentário no PR** não substitui o *required check*: sem exit code diferente de zero, o time aprende a ignorar o relatório. Segundo, permissões devem seguir o princípio do menor privilégio — `contents: read` na maior parte dos jobs; `pull-requests: write` apenas no job que publica o comentário, usando `GITHUB_TOKEN`, sem actions de terceiros que exijam segredos adicionais^^. Autenticação *keyless* via OIDC permanece o padrão recomendado quando o pipeline precisa publicar artefatos em nuvem^^.

## Economia do CI de ML: onde treinar (e onde não treinar)

Há uma tensão estrutural entre pedagogia e produção. No laboratório desta aula, treinar um RandomForest tabular em CPU dentro do mesmo processo que valida o gate é deliberado: o ciclo completo cabe em poucos segundos e cabe no free tier. Em sistemas reais, contudo, **treinar o modelo de produção dentro do runner de PR** torna-se antipadrão a partir de certo tamanho — não por dogma, mas por aritmética.

Os preços públicos de *larger runners* com GPU no GitHub Actions ilustram a âncora: `linux_4_core_gpu` a **US$ 0,052/min** e `windows_4_core_gpu` a **US$ 0,102/min**, disponíveis apenas em planos **Team ou Enterprise Cloud**^^. Uma hora de experimentação mal parametrizada em `linux_4_core_gpu` já custa da ordem de três dólares americanos *antes* de storage, dados e retrabalho humano; uma semana de PRs que disparam fine-tunes completos transforma o CI em linha de despesa imprevisível. As tarifas de *hosted runners* com *platform charge* vigoram desde **2026-01-01**; a cobrança adicional discutida para *self-hosted* (**US$ 0,002/min**) foi **adiada**, sem data firme publicamente vinculante no momento desta verificação^^.

A arquitetura econômica sensata separa papéis: o **CI do PR** valida contratos baratos (schema, testes de código, eval proxy, comparação de métricas de um candidato já materializado ou de um treino mínimo didático); o **CT** pesado vive no orquestrador (Aula 17) ou em runners/GPU dedicados, com linhagem explícita de dados; o **CD** apenas promove o que já carregou evidência. Confundir os três eixos é a forma mais rápida de tornar o *pull request* financeiramente hostil e, paradoxalmente, menos seguro — porque times passam a desabilitar checks caros em vez de redesenhar o funil.

## Gates de Qualidade como Contratos Sociais e Técnicos

Um *gate* de dados sem métricas de modelo produz falsa segurança: o CSV pode estar “correto” e o estimador, inútil. Um *gate* de métricas sem integridade do artefato produz outra falha: o número no JSON não prova que o binário promovido é o mesmo que foi avaliado. Por isso a sequência dados → treino → métricas → segurança → registro não é cerimônia — é encadeamento causal de confiança.

O limiar (`GATE_THRESHOLD`) é, em última análise, uma decisão de produto. Tolera-se uma queda máxima de F1 (ou de outra métrica primária) porque ruído amostral existe; não se tolera regressão arbitrária porque o custo esperado de um `@champion` degradado supera o custo de um merge atrasado. Ferramentas de fairness e explicabilidade (Aula 24) podem, em organizações reguladas, tornar-se gates adicionais — sem que esta aula precise reensiná-las.

## Proveniência, assinatura e a cadeia que a auditoria percorre

A serialização histórica via pickle tornou-se um vetor clássico de execução remota de código quando se carregam artefatos de origens não confiáveis^^. A orientação contemporânea privilegia formatos mais seguros (por exemplo, safetensors) e, no ecossistema scikit-learn didático, joblib com digest criptográfico do arquivo. A cadeia mínima de evidências que uma auditoria competente percorre é linear e implacável: *commit SHA* → identificação do snapshot de dados usado no treino/eval → `metrics.json` confrontado à baseline → **SHA-256** do artefato → (opcionalmente) assinatura criptográfica → entrada imutável de versão e alias no Model Registry.

A OpenSSF anunciou **Model Signing v1.0** em **2025-04-04**, com pacote PyPI `model-signing` na versão **1.1.1 (2025-10-10)**^^. Assinar não é teatro: amarra o digest a uma identidade (chave/OIDC) e torna adulteração detectável. Tampouco é bala de prata. Ferramentas de varredura como `protectai/modelscan` permanecem ativas (último push observado em **2026-02-18**); falhas históricas em scanners — as CVEs reportadas em picklescan e corrigidas na versão **0.0.31 (2025-09-02)** — ilustram que a própria ferramenta de segurança também é dependência e precisa de higiene^^. Em CI maduro, digest + assinatura + gate quantitativo convivem; nenhum dos três sozinho responde à pergunta “podemos confiar neste candidato?”.

## GitOps, Registry e a Fronteira com Serving

O Model Registry (Aula 19) transforma promoção em operação de metadados: o serviço de inferência resolve um alias estável, enquanto versões imutáveis acumulam linhagem. O CD “completo” em Kubernetes frequentemente materializa-se como GitOps: o commit que atualiza o ponteiro do modelo é reconciliado por Argo CD (**v3.5.1** em 2026-08-12) ou Flux2 (**v2.9.4** em 2026-08-07), por vezes com Argo Workflows (**v4.1.1**), Argo Rollouts (**v1.9.1**) e KServe (**v0.20.0**, incluindo o CRD `LLMInferenceService`)^^. Serving pesado (Triton, BentoML, vLLM) permanece na Aula 21; estratégias Canary/Blue-Green/Shadow, na Aula 22. A Aula 20 termina onde o contrato do alias é escrito com evidência.

## Regulação: do calendário jurídico aos requisitos de engenharia

O **Regulamento (UE) 2026/1744** (Digital Omnibus on AI), publicado no Jornal Oficial em **24/07/2026** e em vigor desde **27/07/2026**, atualiza o calendário de obrigações do AI Act^^. A tradução para engenharia não é “escrever um PDF na véspera da auditoria”; é fazer o pipeline **emitir e reter** artefatos que respondam a perguntas forenses.

Práticas proibidas e alfabetização em IA vigem desde **02/02/2025** — o sistema precisa registrar quem opera e sob qual política. Obrigações de GPAI, desde **02/08/2025**, pressionam linhagem de treino e avaliação para modelos de uso geral aplicáveis. Transparência do Artigo 50 aplica-se desde **02/08/2026**, com período de graça para o Art. 50(2) até **02/12/2026** para sistemas já no mercado: o CD precisa saber *qual* versão estava exposta e com qual divulgação. O Anexo III (alto risco) foi postergado para **02/12/2027**; produtos do Anexo I, para **02/08/2028** — horizonte no qual gates de desempenho, fairness (Aula 24) e monitoramento contínuo (Aula 23) deixam de ser “boas práticas” e passam a ser evidência de conformidade operacional.

Frameworks voluntários como ISO/IEC 42001:2023 e NIST AI RMF 1.0 (jan/2023) oferecem linguagem de sistema de gestão, mas não substituem a disciplina de gerar, no próprio CI, hashes, métricas, linhagem e trilhas de quem promoveu o quê. Em termos de requisitos: todo merge que altera comportamento de modelo deve deixar um rastreador reconstruível; todo alias de produção deve apontar para um artefato cujo digest foi calculado no mesmo pipeline que aprovou as métricas.

## LLMs: O Mesmo Esqueleto, Novos Gates

Em sistemas com LLMs, o “modelo” deixa de ser o único objeto versionável: *prompts*, *tools*, bases de recuperação e suítes de avaliação passam a integrar o contrato. O MLflow, em sua linha 3.x (**3.0.0** em 2025-06-10; **3.15.1** em 2026-08-03), oferece Prompt Registry e tracing GenAI no OSS^^. *Deployment Jobs* do MLflow, contudo, devem ser compreendidos como integração gerenciada no ecossistema Databricks — não como peça self-hosted universal. Gates adicionais típicos incluem qualidade de eval offline, tetos de latência e orçamentos de custo por milhão de tokens. Economicamente, o argumento dos GPU runners aplica-se com força redobrada: disparar evals caras em todo PR sem *caching* de casos nem amostragem estratificada é a versão GenAI do antipadrão de treinar o mundo no CI.

## CML como Lição de Risco de Dependência

Durante anos, a ferramenta **CML** (Continuous Machine Learning) do ecossistema Iterative ofereceu uma experiência atraente: `cml comment create` publicava métricas e gráficos diretamente no *pull request*; `cml runner launch` provisionava runners efêmeros — inclusive com GPU — via Terraform em AWS, GCP, Azure ou Kubernetes^^. Esse encaixe narrativo com CD4ML explica por que calendários acadêmicos ainda ecoam o nome.

A verificação empírica em meados de 2026, porém, impõe sobriedade. O repositório `iterative/cml` **não está arquivado**, mas encontra-se **estagnado**: a release **v0.20.6** data de **2024-10-24**, coincidindo com o último commit observado em `main`; há dezenas de issues abertas (~86) e uma comunidade histórica (~4.1k stars) sob licença Apache-2.0^^. Em **18/11/2025**, lakeFS anunciou a assunção de stewardship do **DVC**; o FAQ correspondente compromete-se com DVC, DVCLive e a extensão VS Code, e **não menciona CML**^^. Não há, até onde os comunicados públicos vão, um ato formal de arquivamento ou uma cláusula explícita de exclusão do CML no acordo — o que existe é um projeto **separado**, sem comunicado oficial de manutenção contínua, cuja última atividade relevante remonta a outubro de 2024. Essa ambiguidade (“não morto no GitHub, porém sem pulso”) é precisamente o objeto da competência de avaliar risco de dependência. Em contraste, o DVC OSS segue ativo (PyPI **3.67.1** em 2026-03-31), enquanto `iterative/mlem` **foi arquivado** (último push em 2023-09-13).

A lição transcende o produto: plataformas de MLOps são composições de dependências com ciclos de vida assíncronos. Ensinar o *padrão* (relatório de diferenças de modelo no PR, runners efêmeros, gates) importa mais do que idolatrar o *binário* que o implementou primeiro. O laboratório desta aula reimplementa o comentário de *model-diff* com Python e `actions/github-script`, precisamente para internalizar o padrão sem herdar a estagnação.

Outros sinais do ecossistema reforçam a mesma higiene: Earthly Cloud encerrou operações em **2025-07-16**, com o OSS correspondente sem manutenção ativa; Dagger figura como alternativa viva no espaço de pipelines como código^^. A conclusão não é cinismo — é engenharia de plataforma: versionar contratos, preferir interfaces estáveis, e tratar abandono silencioso como risco de disponibilidade.

## Síntese

CI/CD para machine learning é, antes de tudo, um sistema de **contratos com evidência**: dados válidos, métricas não regressivas, artefato íntegro, alias promovido, e trilhas que sobrevivem a auditoria. CT fecha o ciclo ao transformar sinais de produção em novos candidatos. CD entrega sem heroísmo manual. A economia do onde treinar separa o CI barato do CT caro. Ferramentas nascem e estagnam; os padrões — gates, *model-diff*, registry, GitOps, proveniência — permanecem. É esse deslocamento, do nome histórico “CML” para a prática moderna de CD4ML consciente de risco, que a Aula 20 se propõe a consolidar.

---

> 🔗 **Nota de escopo**: orquestração detalhada de DAGs (Airflow/Prefect), Feature Store, serving de alta performance, mecânica Canary/Blue-Green/Shadow, estatística de drift e fairness/explicabilidade são desenvolvidas nas Aulas 17–19 e 21–24. Este documento aprofunda apenas o que a Aula 20 *possui*: o pipeline de validação/promoção, a economia do CI de ML, a cadeia de evidências e a leitura crítica de dependências.
