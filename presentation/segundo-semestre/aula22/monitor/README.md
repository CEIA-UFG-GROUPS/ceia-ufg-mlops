# 📘 Aula 22 — Estratégias de Deploy (Canary, Blue-Green, Shadow Deployment)

## Material de Estudo Prévio

Este material tem como objetivo **preparar para a aula de Estratégias de Deploy**, oferecendo uma base conceitual sólida para acompanhar, complementar e aprofundar a discussão conduzida pelo apresentador.

⚠️ **Este conteúdo não é um guia de instruções**, mas sim um **material de estudo prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do CEIA/UFG.

---

## 🎯 Objetivo da Aula

Ao final desta aula, espera-se que os participantes compreendam:

- Por que o deploy "Big Bang" (substituição total e instantânea) é uma estratégia de alto risco para modelos de ML
- As mecânicas de **Blue-Green Deployment**, **Canary Release** e **Shadow Deployment**, e as diferenças entre elas
- Como o **Model Registry** (Aula 19) viabiliza tecnicamente essas estratégias através de aliases mutáveis
- Como a **observabilidade** (Aula 11) é indispensável para decidir, com dados, se um modelo novo deve ser promovido ou revertido
- Os trade-offs de custo, complexidade e velocidade de feedback entre as diferentes estratégias

---

## 🧠 Contexto: Por que o Deploy de Modelos de ML é Diferente?

### O Problema do Deploy "Big Bang"

Em software tradicional, um deploy que substitui 100% do tráfego instantaneamente já é arriscado. Para modelos de Machine Learning, esse risco é ainda maior:

1. **Comportamento probabilístico**: um modelo pode ter ótimas métricas offline (acurácia, F1-Score) no conjunto de teste e ainda assim se comportar mal com a distribuição real e viva de dados de produção (data drift, edge cases não vistos no treino).
2. **Ausência de "certo ou errado" imediato**: diferente de um bug de software que gera um erro 500 óbvio, um modelo de ML pode retornar uma predição "plausível", porém incorreta, sem nenhum sinal de erro técnico.
3. **Impacto direto em métricas de negócio**: um modelo de recomendação pior reduz silenciosamente a taxa de conversão; um modelo de fraude pior aumenta silenciosamente o prejuízo financeiro — muitas vezes sem qualquer log de erro.

### A Pergunta Central: Como Reduzir o "Blast Radius" de um Deploy Ruim?

> **Blast Radius**: o alcance do impacto de uma falha. Um deploy "Big Bang" tem blast radius de 100% dos usuários. As estratégias desta aula existem para **limitar esse alcance** e permitir reversão rápida.

---

## ⚙️ As Três Estratégias Principais

### 1. Blue-Green Deployment

```text
        Antes da troca                          Depois da troca
┌──────────────┐                        ┌──────────────┐
│  Roteador    │──100%──► BLUE (v1)     │  Roteador    │──100%──► GREEN (v2)
│ (Load Bal.)  │          (produção)    │ (Load Bal.)  │          (produção)
└──────────────┘                        └──────────────┘
                  GREEN (v2) standby ──►                    BLUE (v1) standby ◄──
                  (totalmente pronto,                       (mantido para rollback
                   sem tráfego)                              instantâneo)
```

- **Como funciona**: dois ambientes de produção completos e idênticos — `Blue` (versão atual) e `Green` (versão nova) — coexistem. O `Green` é totalmente implantado e testado (health checks, smoke tests) **antes** de receber qualquer tráfego real.
- **O corte de tráfego**: quando o `Green` é validado, o roteador (load balancer, API Gateway, DNS) redireciona **instantaneamente** 100% do tráfego para ele.
- **Rollback trivial**: como o `Blue` continua de pé (não é desligado imediatamente), reverter é apenas apontar o roteador de volta — reversão em segundos, sem necessidade de reconstruir nada.
- **Custo**: exige manter **duas infraestruturas completas** rodando ao mesmo tempo, mesmo que temporariamente — o dobro de recursos computacionais durante a janela de transição.

### 2. Canary Release

```text
┌──────────────┐   95% tráfego   ┌─────────────────┐
│              │────────────────►│ Champion (v1)   │
│   Roteador   │                 └─────────────────┘
│ (por %)      │    5% tráfego   ┌─────────────────┐
│              │────────────────►│ Canary (v2)     │
└──────────────┘                 └─────────────────┘
```

- **Como funciona**: a nova versão recebe apenas uma **fração pequena e controlada** do tráfego real (ex.: 5%), enquanto a versão estável continua respondendo à maioria dos usuários.
- **Progressão gradual**: se as métricas do canary (erro, latência, métricas de negócio) permanecerem saudáveis por um período de observação, a fração de tráfego aumenta progressivamente — um padrão comum é 5% → 25% → 50% → 100%.
- **Nome de onde vem**: referência ao "canário na mina de carvão" — um sinalizador antecipado de problema, exposto a um risco limitado antes de afetar todo o sistema.
- **Requisitos técnicos**: roteamento de tráfego por porcentagem (via service mesh como Istio/Linkerd, ou funcionalidades nativas de Ingress/API Gateway do Kubernetes), e testes estatísticos (ex.: teste de hipótese, intervalo de confiança) para decidir com rigor se o canary é de fato melhor, e não apenas "sorte" de amostragem.

### 3. Shadow Deployment (Dark Launch)

```text
┌──────────────┐
│  Requisição  │
│    Real      │
└──────┬───────┘
       │
       ├──────────────► Champion (v1) ──► Resposta retornada ao usuário ✅
       │
       └──────────────► Shadow (v2)   ──► Resposta descartada, apenas logada 🔍
                                            (comparada com a resposta do Champion)
```

- **Como funciona**: uma cópia de cada requisição real de produção é enviada **também** para a nova versão do modelo, que processa a requisição em paralelo. A resposta do shadow **nunca é retornada ao usuário** — apenas registrada e comparada com a resposta da versão em produção.
- **Zero risco de experiência**: como o usuário nunca vê ou é afetado pela resposta do modelo em shadow, essa é a estratégia mais segura para validar comportamento com tráfego real antes de qualquer exposição.
- **Uso típico**: medir a taxa de divergência entre as predições do modelo novo e do modelo atual sobre o mesmo conjunto de requisições reais — se a divergência for alta, investiga-se antes de avançar para um Canary.
- **Custo**: dobra o processamento computacional (cada requisição é processada duas vezes) e exige infraestrutura de duplicação de tráfego que não impacte a latência percebida pelo usuário real.

---

## 🧭 Matriz de Decisão

| Estratégia | Risco ao Usuário | Custo de Infra | Velocidade de Rollback | Cenário Ideal |
|---|---|---|---|---|
| **Blue-Green** | Médio (corte abrupto) | Alto (2 ambientes completos) | Instantâneo | Releases pouco frequentes, já bem validadas em staging |
| **Canary** | Baixo (fração controlada) | Médio (roteamento por %) | Rápido | Releases frequentes, risco de regressão sutil detectável com tráfego real |
| **Shadow** | Nenhum | Alto (processamento em dobro) | N/A (nunca está "no ar") | Modelos de altíssimo risco (financeiro, saúde, segurança), validação prévia a qualquer exposição |

```text
Preciso implantar uma nova versão de modelo?
├── O risco de erro é altíssimo (financeiro/legal/segurança)?
│   └── SIM ──► Comece com SHADOW DEPLOYMENT (zero risco ao usuário)
│              └── Depois de validado ──► avance para CANARY
└── Releases são frequentes e preciso de feedback rápido com tráfego real?
    └── SIM ──► CANARY RELEASE (fração pequena, incremento gradual)
└── Tenho recursos para 2 ambientes completos e quero rollback instantâneo?
    └── SIM ──► BLUE-GREEN DEPLOYMENT
```

---

## 🌐 Conexão com Model Registry e Observabilidade

Nenhuma dessas estratégias funciona isoladamente — elas dependem de duas peças construídas em aulas anteriores:

- **Model Registry (Aula 19)**: os aliases mutáveis (`@champion`, `@challenger`, `@canary`) são o mecanismo técnico que permite trocar qual versão do modelo está recebendo tráfego, **sem alterar código de inferência**. Promover `@challenger` para `@champion` é uma operação atômica de metadados.
- **Observabilidade (Aula 11)**: sem métricas de latência, erro e — principalmente — **métricas de negócio e qualidade** em tempo real, não é possível decidir com confiança se um canary deve avançar ou ser revertido. A decisão de promoção/rollback é, na prática, uma decisão orientada por dados de observabilidade.

```text
┌─────────────────┐   (1. Novo modelo registrado)   ┌─────────────────┐
│  Model Registry │────────────────────────────────►│  Deploy Canary  │
│  (@challenger)  │                                  │   (5% tráfego)  │
└─────────────────┘                                  └────────┬────────┘
                                                                │ (2. Métricas coletadas)
                                                                ▼
                                                      ┌─────────────────┐
                                                      │  Observabilidade │
                                                      │  (Aula 11)       │
                                                      └────────┬────────┘
                                                                │ (3. Decisão automatizada)
                              ┌─────────────────────────────────┴─────────────────────────────────┐
                              ▼                                                                     ▼
                  ┌─────────────────────┐                                             ┌─────────────────────┐
                  │ Métricas saudáveis  │                                             │  Métricas degradadas │
                  │ Promove @champion   │                                             │  Rollback para 0%    │
                  └─────────────────────┘                                             └─────────────────────┘
```

---

## 📊 Casos de Uso Práticos

### Caso 1: Detecção de Fraude em Cartão de Crédito (Fintech)

- **Cenário**: modelo de altíssimo risco financeiro e regulatório.
- **Estratégia**: **Shadow Deployment** primeiro — o modelo candidato roda em paralelo por semanas, comparando decisões com o modelo em produção, sem nunca bloquear uma transação real. Só depois de validado avança para um Canary de 1-5%.

### Caso 2: Sistema de Recomendação de E-Commerce

- **Cenário**: releases frequentes (semanais), risco de negócio moderado (queda de conversão, não risco de segurança).
- **Estratégia**: **Canary Release** progressivo (5% → 25% → 50% → 100%), com decisão de promoção automatizada baseada em taxa de cliques e conversão monitoradas pela stack de observabilidade.

### Caso 3: Migração de Infraestrutura de Serving (ex.: TensorFlow Serving → vLLM)

- **Cenário**: não é uma mudança de modelo, mas de toda a stack de serving — risco de instabilidade de infraestrutura, não apenas de qualidade do modelo.
- **Estratégia**: **Blue-Green Deployment** — os dois ambientes completos (stack antiga e nova) são validados com testes de carga antes do corte, e o rollback instantâneo protege contra falhas de infraestrutura da nova stack.

---

## 🧪 Atividade Prática (Visão Geral)

Para consolidar os conceitos desta aula, a atividade prática guia os alunos na implementação de um roteador de tráfego simples:

1. **Simulação de Canary**: implementar um roteador Python/FastAPI que distribui tráfego entre duas versões de um modelo com base em uma porcentagem configurável.
2. **Simulação de Shadow**: implementar o padrão de "chamar em paralelo, logar divergência, nunca expor a resposta do shadow ao usuário".
3. **Critério de Promoção**: escrever uma função simples que decide, com base em métricas simuladas (taxa de erro, latência), se o canary deve avançar de porcentagem ou ser revertido a 0%.
4. **Discussão de Blue-Green**: desenhar (sem necessariamente implementar) como um `docker-compose` com dois serviços e um proxy reverso simularia uma troca Blue-Green local.

---

## 💬 Pontos para Reflexão Pré-Aula

Ao estudar este material, reflita sobre as seguintes questões para enriquecer a discussão em sala:

1. **Por que passar em testes offline (acurácia, F1-Score) não é suficiente para garantir que um modelo terá bom desempenho em produção?**
2. **Qual é a principal diferença entre Canary Release e Shadow Deployment em termos de risco para o usuário final?**
3. **Por que o Blue-Green Deployment exige o dobro de infraestrutura, e em que cenário esse custo extra vale a pena?**
4. **Como o Model Registry (Aula 19) torna possível migrar tráfego entre versões de modelo sem reescrever código de inferência?**
5. **Sem uma stack de observabilidade robusta (Aula 11), por que nenhuma dessas estratégias de deploy progressivo funciona de forma confiável?**
6. **Em que situação você combinaria Shadow Deployment seguido de Canary Release para o mesmo modelo, em vez de escolher apenas uma estratégia?**

---

## 📚 Referências

### Artigos e Publicações

1. **Humble, J. & Farley, D. (2010).** *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation*. Addison-Wesley. (Capítulos sobre Blue-Green Deployment e releases progressivos).
2. **Sato, D. (2014).** *CanaryRelease*. martinfowler.com — [https://martinfowler.com/bliki/CanaryRelease.html](https://martinfowler.com/bliki/CanaryRelease.html)
3. **Fowler, M. (2010).** *BlueGreenDeployment*. martinfowler.com — [https://martinfowler.com/bliki/BlueGreenDeployment.html](https://martinfowler.com/bliki/BlueGreenDeployment.html)

### Documentação Oficial

4. **Istio Traffic Management (Canary/Shadow via Service Mesh)** — [https://istio.io/latest/docs/tasks/traffic-management/](https://istio.io/latest/docs/tasks/traffic-management/)
5. **Kubernetes Documentation — Rolling Updates & Deployment Strategies** — [https://kubernetes.io/docs/concepts/workloads/controllers/deployment/](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
6. **AWS — Blue/Green Deployments Whitepaper** — [https://docs.aws.amazon.com/whitepapers/latest/blue-green-deployments/introduction.html](https://docs.aws.amazon.com/whitepapers/latest/blue-green-deployments/introduction.html)

### Livros e Guias da Indústria

7. **Huyen, Chip (2022).** *Designing Machine Learning Systems*. O'Reilly Media. (Capítulo sobre deploy e estratégias de rollout progressivo de modelos).
8. **Google Cloud MLOps Architecture Guide** — [https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

---

## 🔗 Conexões com Outras Aulas

Este conteúdo conecta-se diretamente com o ecossistema do curso de MLOps:

- **Aula 10 (CI/CD Básicos)**: pipelines de CI/CD automatizam a execução e progressão dessas estratégias de deploy (ex.: aumentar automaticamente a porcentagem de um canary).
- **Aula 11 (Logging, Monitoramento e Observabilidade)**: métricas em tempo real são o critério de decisão para promover ou reverter um canary/blue-green.
- **Aula 17 (Pipelines de Treinamento — Airflow/Prefect)**: o modelo que chega até o deploy progressivo é o resultado de um pipeline de Continuous Training orquestrado.
- **Aula 19 (Model Registry)**: aliases mutáveis (`@champion`, `@challenger`, `@canary`) são o mecanismo técnico central que viabiliza essas estratégias sem alterar código.
- **Aula 21 (Servindo Modelos Pesados — Triton/BentoML)**: engines de serving especializadas frequentemente já possuem suporte nativo a roteamento canary/shadow entre versões de modelo.

---

🚀 **Estudo prévio concluído? Prepare suas dúvidas sobre blast radius, rollback e critérios de promoção para debatermos durante nosso encontro!**
