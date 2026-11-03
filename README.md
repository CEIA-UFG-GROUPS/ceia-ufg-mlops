# 🛠️ Grupo de Estudos Hands-On — MLOps na prática (CEIA/UFG, 2026)

Grupo de estudos **100% mão na massa**: a cada encontro, um lab independente que começa e termina no
mesmo dia, com código rodando no fim. Nada de semestre inteiro de slides — conceito curto, prática
longa e um desafio para fixar.

O fio condutor do semestre é um único domínio: **análise de sentimento (NLP)**. Toda semana mexe no
mesmo tipo de problema, então o contexto não se perde — o que muda é a camada de engenharia ao redor
dele, do script bash ao serviço monitorado em produção.

---

## 🎯 Princípios

| Princípio | Como isso aparece na prática |
| --- | --- |
| **Lab independente** | Cada semana abre e fecha um tema. Quem faltou não fica para trás. |
| **Conceito curto** | No máximo 15 minutos de exposição. O resto é teclado. |
| **Domínio recorrente** | Sempre análise de sentimento. Muda a engenharia, não o problema. |
| **Rodízio de hosts** | Toda semana alguém diferente conduz. Ensinar é a melhor forma de aprender. |
| **Entrega no Git** | O desafio vira pull request. Sem PR, não houve entrega. |
| **Peer review** | Cada pessoa revisa pelo menos o PR de um colega. |
| **Infra de verdade** | GCP com créditos educacionais + máquinas 4090 do laboratório. |

---

## ⏱️ Formato das sessões

Cada encontro tem cerca de **90 minutos**, sempre na mesma estrutura:

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ **Conceito** | ~15 min | O mínimo de teoria para o lab fazer sentido. Sem aprofundamento. |
| 💻 **Mão na massa** | ~60 min | Todo mundo codando junto, acompanhando o host, no mesmo ritmo. |
| 🎯 **Desafio** | ~15 min | Apresentação do desafio da semana e combinados de entrega. |

O desafio é feito **fora do encontro** e entregue até a sessão seguinte.

---

## 🔁 Rodízio de hosts

Não existe professor fixo. Cada semana tem um **host**, que:

1. Prepara o lab com antecedência, seguindo o template de `semana-XX/README.md`;
2. Roda o lab inteiro do zero antes do encontro, cronometrando;
3. Posta os pré-requisitos no Discord com pelo menos 3 dias de antecedência;
4. Conduz a sessão e mantém o ritmo da turma;
5. Preenche a seção *Passo a passo* e sobe o conteúdo de `codigo/`.

A inscrição para hostear acontece na Semana 00. Quem nunca apresentou tem prioridade, e hostear em
dupla é permitido (e incentivado para os temas mais pesados).

---

## 📬 Entrega e avaliação

Não há prova. A avaliação é **o que foi entregue no Git**:

1. O desafio é resolvido no **repositório pessoal** de cada participante (ou em um fork do repo do grupo);
2. A entrega é um **pull request** a partir de uma branch `semana-XX/<seu-usuario>`;
3. O link do PR é postado no canal da semana no **Discord**;
4. Cada pessoa faz **peer review** de pelo menos 1 colega antes do encontro seguinte;
5. Os **critérios de aceite** de cada desafio estão no `desafio.md` da semana.

O que se espera de um bom review: apontar o trecho, explicar o porquê, sugerir alternativa. E só
aprovar se você conseguiria rodar o projeto seguindo o README.

---

## ☁️ Infraestrutura

Modelo híbrido, escolhido por tema:

- **GCP (créditos educacionais)** — Cloud Run, Artifact Registry, Secret Manager, Cloud Logging e
  Monitoring. É onde o serviço vai parar em produção.
- **Máquinas 4090 do laboratório** — acesso por SSH, usadas para o que precisa de GPU e para comparar
  custo e desempenho contra o serverless (Semana 10).

Regras de convivência: alertas de orçamento configurados desde a Semana 06, nada de credencial
commitada e tudo que foi ligado no lab é desligado no fim dele.

---

## 💬 Comunicação

Todo o dia a dia acontece no **Discord**:

- Um canal por semana (`#semana-00`, `#semana-01`, ...) para dúvidas, links e entrega dos PRs;
- Canal geral para avisos e organização do rodízio;
- Avisos de pré-requisito saem com pelo menos 3 dias de antecedência.

---

## 🗓️ Cronograma — 1º semestre (Fundamentos + DevOps)

| Semana | Tema | Foco do lab | Desafio |
| --- | --- | --- | --- |
| [00](./semana-00/) | Onboarding (ao vivo) | Contas GCP + créditos, ambiente local (WSL/Docker), acesso às 4090, Git/GitHub, Discord | Criar o repositório pessoal e rodar um hello world |
| [01](./semana-01/) | Linux + Bash + Git | Terminal, permissões, SSH, scripting; fluxo branch → commit → PR | Script bash que prepara o dataset de sentimento |
| [02](./semana-02/) | Como a web funciona I (Redes) | Internet, HTTP/HTTPS, DNS, portas, cliente-servidor | Servidor HTTP simples que serve o modelo |
| [03](./semana-03/) | Como a web funciona II (APIs) | REST, JSON, status codes, TLS; API com FastAPI | Endpoint `/predict` que retorna o sentimento |
| [04](./semana-04/) | Docker | Imagens, containers, Dockerfile, Compose, networks, volumes | Containerizar a API + 2º serviço via Compose |
| [05](./semana-05/) | CI + Artifact Registry | GitHub Actions (pytest, lint, build) + imagem versionada no GCP | CI verde e imagem publicada no merge |
| [06](./semana-06/) | GCP fundamentos | Projetos, IAM, `gcloud`, Cloud Run vs Compute Engine, billing | 1º deploy manual no Cloud Run |
| [07](./semana-07/) | CD serverless | Actions → build → deploy automático no Cloud Run; env vars | Deploy automático a cada push na `main` |
| [08](./semana-08/) | Config, secrets e ambientes | Env vars, Secret Manager, staging vs prod, health checks | Serviço parametrizado com secret gerenciado |
| [09](./semana-09/) | Logging & Monitoramento | Logs estruturados, Cloud Logging/Monitoring, métricas, alertas | Dashboard + um alerta funcionando |
| [10](./semana-10/) | Load testing & performance | locust/k6, throughput e latência; 4090 local vs Cloud Run | Relatório de carga do serviço |
| [11](./semana-11/) | Demo Day | Mini-projeto integrador: CI/CD → deploy GCP → monitorado | Entrega integradora + peer review final |

O 2º semestre será planejado na retrospectiva da Semana 11, com base no que a turma construiu.

---

## 📂 Estrutura do repositório

```text
.
├── README.md              # este arquivo
├── semana-00/
│   ├── README.md          # roteiro do host (objetivos, agenda, passo a passo, notas)
│   ├── desafio.md         # enunciado do desafio e critérios de aceite
│   └── codigo/            # scripts, configs e exemplos usados no lab
├── semana-01/
│   └── ...
└── semana-11/
    └── ...
```

Todas as semanas seguem exatamente a mesma estrutura, então dá para entrar em qualquer pasta e saber
onde está cada coisa.

---

## 🚀 Como participar

1. Entre no Discord e se apresente no canal geral;
2. Faça a **Semana 00** (mesmo que tenha entrado depois) — é ela que deixa o ambiente pronto;
3. Antes de cada encontro, leia o `README.md` da semana e cumpra os pré-requisitos;
4. Participe do lab com o teclado, não só com os olhos;
5. Entregue o desafio via pull request e revise o de um colega;
6. Escolha uma semana para hostear.

### Pré-requisitos gerais

- Python básico (ler e escrever um script simples);
- Disposição para usar o terminal;
- Conta Google e conta GitHub;
- Nenhum conhecimento prévio de cloud, Docker ou CI/CD é necessário.

---

## 🏫 Instituição

**Centro de Excelência em Inteligência Artificial (CEIA)**
**Universidade Federal de Goiás (UFG)**

> O material antigo do grupo de estudos (formato expositivo, aulas em `presentation/`) continua
> disponível na branch `main` deste repositório.

---

## 📜 Licença

Conteúdo destinado a fins **educacionais e acadêmicos**. A licença específica será definida conforme
a necessidade do grupo.
