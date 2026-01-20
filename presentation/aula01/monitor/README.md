# 📘 Aula 01 — Introdução ao MLOps  
## Material de Estudo Prévio (Monitor)

Este material tem como objetivo **preparar o monitor para a aula de Introdução ao MLOps**, oferecendo uma base conceitual sólida para acompanhar, complementar e aprofundar a discussão conduzida pelo apresentador.

⚠️ **Este conteúdo não é um guia de instruções para o monitor**, mas sim um **material de estudo prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do CEIA/UFG.

---

## 🎯 Objetivo da Aula

Ao final desta aula, espera-se que os participantes compreendam:

- O que é **MLOps** e por que ele surgiu
- As principais **dificuldades de colocar modelos de ML em produção**
- A relação entre **DevOps, DataOps e MLOps**
- O papel do **ML Engineer** no ecossistema atual
- MLOps como **prática técnica e comportamento organizacional**

---

## 🧠 Contexto: De DevOps a MLOps

### DevOps
DevOps (Development Operations) é uma **cultura de cooperação entre times**, não restrita apenas ao desenvolvimento de software, que busca:

- Entrega contínua de valor
- Automação de processos
- Comunicação eficiente entre áreas

Em sistemas tradicionais:
- APIs REST possuem ciclos bem definidos de desenvolvimento, testes e deploy
- CRUD em bancos de dados foi amplamente simplificado por ORMs
- Artefatos de código são reaproveitáveis, independentemente dos dados armazenados

Esse cenário muda drasticamente com **Machine Learning**.

---

## ⚠️ Por que ML é diferente?

Modelos de Machine Learning:

- Dependem diretamente **dos dados usados no treinamento**
- Conversam simultaneamente com **dados e infraestrutura**
- Podem **errar silenciosamente**, sem gerar falhas no sistema
- São difíceis de testar com abordagens tradicionais
- Tornam avaliação e validação tarefas não triviais

Além disso, o ciclo envolve múltiplos perfis:
- Engenharia de Dados
- Ciência de Dados
- Engenharia de Software
- DevOps / Plataforma

Essa complexidade torna inviável tratar ML como apenas “mais um software”.

---

## 🤖 O que é MLOps?

MLOps surge da necessidade de:

- Levar modelos de ML para produção de forma confiável
- Automatizar não só código, mas **dados e modelos**
- Aplicar princípios do DevOps ao ciclo de vida do ML

> **“MLOps automatiza ML usando metodologias do DevOps”**

Enquanto DevOps automatiza software, MLOps automatiza:
- Dados
- Treinamento
- Deploy
- Monitoramento
- Auditoria de modelos

---

## 🔁 Ciclo de Vida em MLOps

Um pipeline típico de MLOps envolve:

1. **Train** — Treinamento do modelo
2. **Deploy** — Disponibilização em produção
3. **Monitor** — Avaliação contínua de performance
4. **Audit** — Rastreabilidade de dados, código e decisões

Esse ciclo precisa ser **reprodutível, observável e automatizado**.

---

## 🏗️ Camadas de Automação

### 🔹 Data Automation (DataOps)
Foco no fluxo de dados:
- Coleta
- Limpeza
- Versionamento
- Frequência de atualização
- Data Lakes

Ferramentas comuns:
- Apache Airflow
- AWS Glue
- Pipelines de ETL

---

### 🔹 Platform Automation
Uso de plataformas de alto nível para ML:

- AWS SageMaker
- GCP AI Platform
- Azure ML Studio

Vantagens:
- Redução de retrabalho
- Pipelines já testados em escala
- Integração nativa com cloud e hardware especializado (GPUs)

---

## 🧰 Ferramentas e Metodologias Relacionadas

Algumas tecnologias frequentemente associadas a MLOps:

- **CI/CD**: GitHub Actions
- **Task Runners**: Makefile
- **Containers**: Docker
- **Orquestração**: Kubernetes
- **Serverless**: Lambda, Cloud Functions
- **Big Data**: Spark, Databricks, Snowflake

> A necessidade de muitos dados e hardware especializado cria uma forte **sinergia com cloud computing**.

---

## 👨‍💻 ML Engineer x Data Scientist

Pontos importantes para discussão:

- Ciência está mais associada à **pesquisa**
- Engenharia está mais associada à **produção**
- Atribuições frequentemente se sobrepõem
- Salários são similares
- Ambas exigem hard skills em:
  - Cloud
  - Dados
  - Machine Learning

Certificações refletem essa demanda:
- AWS: Machine Learning Specialist
- GCP: Professional Machine Learning Engineer
- Azure: Data Scientist Associate

---

## 🧩 MLOps como Comportamento

Assim como DevOps, MLOps não é apenas um conjunto de ferramentas.

> **“DevOps is a behavior, just like data science.”**

MLOps combina:
- DevOps
- Dados
- Modelos
- Negócio

E exige:
- Automação
- Comunicação técnica eficaz
- Visão sistêmica do ciclo de ML

---

## 💬 Pontos para Reflexão Pré-Aula

Como monitor, reflita sobre:
- Por que testes tradicionais falham para ML?
- Onde os dados “entram” como parte do código?
- O que acontece quando um modelo erra em produção?
- Qual o custo de não monitorar um modelo?
- MLOps resolve problemas técnicos, organizacionais ou ambos?

Esses pontos são fundamentais para enriquecer a discussão durante o encontro.

---

## 📚 Referências e Continuidade

Este conteúdo serve como **base conceitual** para as próximas aulas, que irão aprofundar:

- Versionamento de dados e modelos
- Pipelines de treinamento
- Deploy e serving
- Monitoramento e retraining
- Integração com outros domínios (ex: NLP)

---

🚀 **Leitura concluída? Venha para a aula pronto para questionar, complementar e conectar conceitos.**
