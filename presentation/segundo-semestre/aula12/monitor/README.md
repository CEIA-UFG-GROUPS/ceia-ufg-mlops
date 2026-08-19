# 📘 Aula 12 — Kubernetes: orquestração de containers para MLOps

## Material de Estudo Prévio

Esta é a **aula de abertura do 2º semestre** e a fundação de infraestrutura do
resto da trilha. Você já sabe empacotar um modelo em container (Aula 05, 1º
semestre). Falta a parte que ninguém coloca no README: **manter aquilo no ar**
quando a máquina reinicia às 3 da manhã, quando o tráfego decuplica numa terça
e quando você precisa trocar a versão do modelo sem derrubar o endpoint.

⚠️ **Este conteúdo não é um guia de instruções**, mas um **material de estudo
prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do
CEIA/UFG.

A aula é expositiva com **demonstração ao vivo de 16 minutos**. Ler este
material antes muda a demo de "mágica" para "eu entendi o que aconteceu".

---

## 🎯 Objetivos da aula

Ao final, você deverá conseguir:

- explicar o que o Docker resolve e o que ele **não** resolve;
- distinguir modelo **imperativo** de **declarativo** — e dizer quem fica
  responsável pelo estado depois que o comando termina;
- descrever o **loop de reconciliação** e usá-lo para prever o comportamento do
  cluster em situações que você nunca viu;
- ler qualquer YAML de Kubernetes reconhecendo Pod, Deployment e Service;
- configurar **readiness, liveness e startup probes** — e explicar por que um
  modelo de 30 a 90 segundos de carregamento torna isso obrigatório;
- explicar `requests` vs `limits` e por que é daí que vem o desperdício de
  cluster;
- diagnosticar um pod quebrado com `get` → `describe` → `logs`;
- explicar o que são **CRD** e **Operator** e por que KServe, Kubeflow e Ray
  existem no Kubernetes e não em outro orquestrador;
- argumentar **quando não usar** Kubernetes.

---

## 🧠 O problema: o que o Docker não resolve

| Docker resolve | Docker **não** resolve |
|---|---|
| Empacotamento (dependência, versão de Python, driver CUDA) | Em qual máquina o container deve rodar |
| Reprodutibilidade (mesma imagem no notebook e no servidor) | Quantas cópias manter no ar |
| Isolamento (dois modelos com `torch` incompatíveis convivem) | O que fazer quando ele morre — e ele vai morrer |
| | Como atualizar sem derrubar o serviço |
| | Como escalar quando a carga sobe |

### "Mas eu uso Docker Compose"

Compose orquestra vários containers **numa máquina só**. Quando a máquina cai,
cai tudo — não existe segunda máquina para onde ir. Kubernetes transforma **N
máquinas num pool com um cérebro em cima**.

### Por que isso pega justo em MLOps

Orquestração aqui não é elegância de arquitetura, é **controle de custo**:

- **GPU parada dói no bolso.** Uma A100 ociosa custa o mesmo que uma saturada.
- **Inferência tem carga irregular.** Pico às 10h, deserto às 3h — pagar pelo
  pico o dia inteiro é desperdício.
- **Treino e inferência são opostos.** Um é batch e tolera fila; o outro é
  online e não tolera latência. Disputam o mesmo hardware.
- **Modelo é artefato versionado.** Trocar versão em produção deveria ser tão
  banal quanto um merge — com rollback.

---

## ⚙️ O modelo mental (o bloco que importa)

### Imperativo × declarativo

```text
IMPERATIVO — você dá a ordem          DECLARATIVO — você descreve o destino
$ docker run -d --name api \          spec:
    -p 8000:8000 inferencia:v1          replicas: 3
# pronto. e se morrer? problema seu.    image: inferencia:v1
                                      # o cluster mantém isso verdadeiro.
```

A diferença **não é a sintaxe**. É quem fica responsável por manter o estado
depois que o comando termina: no imperativo, você; no declarativo, o cluster.

### O loop de reconciliação

Um *controller* roda em loop, para sempre:

```text
      ┌──────────────────────┐
      │  1. ESTADO DESEJADO  │  o que está no seu YAML (replicas: 3)
      └──────────┬───────────┘
                 ▼
      ┌──────────────────────┐
      │  2. COMPARA          │  desejado vs. real
      └──────────┬───────────┘
                 ▼
      ┌──────────────────────┐
      │  3. ESTADO REAL      │  o que de fato roda (2 pods)
      └──────────┬───────────┘
                 │  age para fechar a diferença
                 └──────────► cria o 3º pod ──┐
                 ▲                            │
                 └────────────────────────────┘
```

Um pod morreu? Real virou 2, desejado é 3. Ele cria outro. **Ninguém foi
acordado.** Este é o mecanismo por trás de self-healing, rolling update,
autoscaling e operators — tudo é o mesmo loop com lógicas diferentes.

### Você já faz isso

O princípio não é novo:

- **Terraform** — você descreve a infra desejada, ele calcula o plano e converge.
- **GitOps** — o repositório é a fonte da verdade; o cluster persegue a `main`.
- **CI/CD** — o pipeline já é um controller: detecta divergência entre código e
  artefato publicado e corrige.

Kubernetes aplica o mesmo padrão a **containers em execução**.

### Arquitetura mínima (não precisa decorar)

| Control plane — o cérebro | Nodes — onde o trabalho acontece |
|---|---|
| **API Server** · única porta de entrada; tudo passa aqui, inclusive você | **kubelet** · agente do nó; garante que os containers dele estão de pé |
| **etcd** · onde o estado desejado é guardado | **container runtime** · containerd; é o que de fato roda a imagem |
| **Scheduler** · decide em qual nó cada pod vai rodar | **kube-proxy** · rede e roteamento dos Services |
| **Controller Manager** · onde os loops moram | |

---

## 🧱 Os objetos que você realmente usa

### Pod

A menor unidade — **não é o container, é a caixa em volta dele**. Um ou mais
containers que compartilham rede e volume, sempre no mesmo nó. Recebe IP
próprio e é **efêmero**: morre, e o substituto nasce com outro nome e outro IP.

Você quase nunca cria um pod direto. Em ML o padrão multi-container aparece
cedo: um `initContainer` baixa o peso do modelo do S3 e só então o container da
API sobe.

### Deployment

É o que você de fato escreve: *"mantenha N cópias disto no ar"*.

- Gerencia um **ReplicaSet** por baixo, que é quem conta os pods.
- **Rolling update de graça**: sobe os novos, espera ficarem prontos, derruba os
  antigos.
- **Rollback de graça**: `kubectl rollout undo`.

### Service

Pods morrem e renascem com IP novo — IP de pod é inútil para quem chama. O
Service é um **nome DNS e um IP estáveis** na frente de um grupo de pods, com
load balancing incluído. Ele encontra os pods por **label**, não por nome: é
por isso que continua correto quando o pod é substituído.

| Tipo | Alcance |
|---|---|
| `ClusterIP` | Só dentro do cluster. Padrão, cobre a maioria dos casos. |
| `NodePort` | Abre uma porta em cada nó. Útil em laboratório. |
| `LoadBalancer` | O cloud provisiona um balanceador real e dá um IP público. |

### Ingress

Um ponto de entrada HTTP para vários serviços, com roteamento por caminho e
host (`/predict`, `/embed`, `/docs`). Evita pagar um load balancer por
microserviço e centraliza TLS. **Precisa de um Ingress Controller instalado**
(nginx, Traefik) — o objeto sozinho não faz nada.

### ConfigMap e Secret

Configuração fora da imagem — o mesmo 12-factor que você já aplica. Viram
variável de ambiente ou arquivo montado. Trocar config não exige rebuild.

> ⚠️ **Secret é base64, não criptografia.** Qualquer pessoa com permissão de
> leitura no namespace lê o valor. Em produção: **External Secrets** (puxa do
> Vault/Secrets Manager) ou **Sealed Secrets** (criptografado, pode ir para o
> Git).

### Probes — o assunto mais MLOps daqui

Um modelo grande leva **30 a 90 segundos** para carregar na memória. O
Kubernetes precisa saber disso.

| Probe | Pergunta | Efeito de falhar |
|---|---|---|
| **readinessProbe** | "Já posso receber tráfego?" | O Service **para de mandar** requisição para este pod |
| **livenessProbe** | "Ainda estou vivo?" | O pod é **reiniciado** |
| **startupProbe** | "Ainda estou subindo?" | Dá prazo generoso só na subida, sem afrouxar as outras duas |

Sem readinessProbe bem configurada, **todo deploy gera pico de 503** — porque o
tráfego chega antes do modelo carregar. E o erro clássico é apontar liveness e
readiness para o mesmo endpoint: um modelo lento vira loop infinito de restart.

### requests, limits e GPU

```yaml
resources:
  requests:          # o que é RESERVADO; o scheduler só usa isto para decidir
    cpu: 500m
    memory: 2Gi
  limits:            # o teto; estourar memória mata o container (OOMKilled)
    memory: 4Gi
    nvidia.com/gpu: 1
```

GPU entra como recurso qualquer, mas **não é fracionável por padrão**: um
container ocupa a placa inteira. É isso que torna agendamento de ML diferente.

> Reservar 4 CPUs para um serviço que usa 200m é pagar hardware ocioso o mês
> inteiro. **A maior parte do desperdício em cluster vem daqui**, não do
> Kubernetes.

### O resto, em uma linha cada

| Objeto | Para quê |
|---|---|
| **Namespace** | Isolamento lógico: `dev`, `staging`, `prod` — ou um por time |
| **Job** | Roda até terminar e morre. Treino, batch inference, reindexação |
| **CronJob** | O mesmo, agendado. Retreino toda madrugada de domingo |
| **PVC** | Disco que sobrevive ao pod. Dados do Qdrant, cache de modelos |
| **StatefulSet** | Identidade e disco estáveis por réplica. É como banco roda aqui |
| **HPA** | Escala réplicas sozinho, por CPU ou métrica custom |

---

## 🚀 Kubernetes no mundo MLOps

### CRD e Operator — a chave de tudo

Kubernetes deixa você **estender a própria API** com objetos do seu domínio:

- **CRD** (Custom Resource Definition) cria um tipo novo, ex.: `kind: InferenceService`.
- **Operator** é o controller que sabe o que fazer com esse tipo — o mesmo loop
  de reconciliação, agora com a sua lógica.

Você escreve 10 linhas de `InferenceService`; o operator gera Deployment,
Service, HPA e rota. **É por isso que Kubeflow, KServe, Argo e Ray existem aqui
e não em outro orquestrador.**

### O ecossistema

| Servir modelos | Treinar e orquestrar |
|---|---|
| **KServe** · autoscaling até zero, canary entre versões, servidores prontos para PyTorch/sklearn/ONNX | **Kubeflow Pipelines** · pipelines de ML como objetos do cluster |
| **Seldon Core** · pipelines de inferência e testes A/B | **Argo Workflows** · DAG genérico em YAML; mais simples e muito usado |
| **Ray Serve** · inferência composta e stateful | **Ray on Kubernetes** · treino distribuído e tuning |

Bancos vetoriais (Qdrant, Milvus, Weaviate) rodam como **StatefulSet + PVC** —
o mesmo padrão de qualquer banco. Para GPU: **NVIDIA device plugin** expõe as
placas ao scheduler; **taints e tolerations** reservam os nós caros; **MIG** e
**time-slicing** dividem uma placa.

### Como isso vira rotina

Ninguém aplica YAML na mão em produção:

- **Helm** empacota e versiona seus YAMLs num chart, com variáveis por
  ambiente. É o `apt` do Kubernetes.
- **ArgoCD** observa o repositório e faz o cluster convergir para a `main`.

Merge na `main` → o ArgoCD percebe a divergência → o cluster converge. **É o
CI/CD que vocês já conhecem, com o loop de reconciliação do outro lado.**

E use cluster gerenciado (EKS, GKE, AKS): ninguém deveria operar control plane
próprio para aprender.

---

## 🛑 Quando NÃO usar Kubernetes

Kubernetes cobra um **imposto de complexidade**, e nem sempre compensa.

| Não compensa quando | Passa a compensar quando |
|---|---|
| Um modelo só, tráfego baixo, time pequeno → Cloud Run, SageMaker Endpoint ou uma VM com systemd resolvem melhor | São **vários** serviços |
| Ninguém no time quer operar cluster → sem dono da plataforma, vira dívida técnica | A carga é **elástica** |
| | Times **disputam GPU** |
| | Você precisa do mesmo deploy em **nuvens diferentes** |

**Custo, para quando perguntarem:** control plane gerenciado vai de grátis a
~US$ 75/mês por cluster conforme o provedor; o grosso da conta são os nós. O
desperdício quase nunca vem do Kubernetes — vem de `requests` mal dimensionados.

---

## 📊 Casos de uso práticos

1. **O deploy que gera 503 toda sexta.** Um time serve um modelo de 4 GB que
   leva 45 s para carregar. A readinessProbe aponta para `/` — que responde 200
   assim que o uvicorn sobe, muito antes do modelo estar na memória. A cada
   deploy, o Service manda tráfego para pods que ainda não podem responder. O
   gráfico mostra um pico de erro de ~40 s, sempre. A correção é uma linha:
   readiness apontando para um endpoint que só responde 200 **depois** do
   `load()`. **Lição:** probe mal configurada é indistinguível de instabilidade
   de aplicação.

2. **A conta de GPU que ninguém explicava.** Um cluster com 4 nós A100 rodando
   a 12% de utilização média. A investigação mostra `requests: nvidia.com/gpu: 1`
   em serviços de inferência leve que jamais saturam a placa — e como GPU não é
   fracionável por padrão, cada um monopoliza uma A100 inteira. A correção
   combina time-slicing para as cargas leves e taints para reservar os nós
   inteiros ao treino. **Lição:** o desperdício mora nos `requests`, não na
   ferramenta.

3. **O rollback que não voltou.** Um deploy quebra a produção; o time roda
   `kubectl rollout undo` e a imagem volta para a versão anterior — mas o
   incidente continua. Motivo: junto com a imagem, alguém tinha alterado o
   ConfigMap, e `rollout undo` **não** reverte ConfigMap. **Lição:** imagem e
   configuração são histórias de versão independentes; é por isso que GitOps
   versiona as duas no mesmo commit.

---

## 🧪 Atividade prática

Em [`atividade/`](./atividade/) está o repositório da demo — os YAMLs e o
Dockerfile prontos para rodar num cluster local:

```bash
make cluster     # minikube em profile dedicado
make load        # build inferencia:v1 e v2 + carga no cluster
make ato2        # deploy
make ato3        # ★ mate um pod e veja o loop de reconciliação agir
make ato5        # balanceamento visível pelo nome do pod
make ato7        # rolling update; depois 'make undo'
make ato8        # três defeitos em escada para diagnosticar
make limpar      # ou 'make destruir' para apagar o cluster
```

Todo alvo usa `--context` explícito e passa por uma trava que impede aplicar em
cluster errado. Vale ler o `Makefile`: essa proteção é uma lição de operação.

**Desafio da semana:** subir um Qdrant com PVC e provar que a coleção sobrevive
a `kubectl delete pod qdrant-0` (`make desafio`).

---

## 💬 Pontos para reflexão pré-aula

1. Se a VM que roda seu modelo reiniciar agora, quem levanta o container de volta?
2. Qual a diferença prática entre "o comando terminou" e "o estado está mantido"?
3. Seu modelo demora quanto para carregar? O que acontece com o tráfego nesse
   intervalo?
4. Por que o Service encontra os pods por *label* e não por IP?
5. Quanto de CPU e memória seu serviço realmente usa — e quanto você reservaria?
6. Se `rollout undo` não reverte ConfigMap, como você garantiria um rollback
   completo?
7. O seu caso de uso passa no teste do slide 33, ou uma VM com systemd
   resolveria melhor?

---

## 📚 Referências

- [Kubernetes — Concepts](https://kubernetes.io/docs/concepts/)
- [Kubernetes Basics — tutorial oficial](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- [killercoda.com/kubernetes](https://killercoda.com/kubernetes) — cenários
  gratuitos no navegador, sem instalar nada. **Comece por aqui.**
- [kind](https://kind.sigs.k8s.io/) · [minikube](https://minikube.sigs.k8s.io/) — cluster local
- Burns, B.; Beda, J.; Hightower, K. *Kubernetes: Up and Running*, 3ª ed.
- Gift, N.; Deza, A. *Practical MLOps*, Cap. 3 "Containers and Edge Devices".
- Treveil et al. *Introducing MLOps*, Cap. 6 "Deploying to Production".
- [KServe](https://kserve.github.io/website/) · [Kubeflow](https://www.kubeflow.org/)
  · [Argo Workflows](https://argo-workflows.readthedocs.io/)
- [Ícones oficiais dos objetos](https://github.com/kubernetes/community/tree/master/icons)

> ℹ️ O cronograma não atribuiu leitura de livro a esta aula. As referências
> acima cobrem a lacuna; a documentação oficial é suficiente para acompanhar.

---

## 🔗 Conexões com outras aulas

- **Aula 05 (1º sem):** Docker, Compose e networks — o pré-requisito direto.
- **Aula 08 (1º sem):** computação em nuvem; aqui o cluster gerenciado.
- **Aula 13:** servidor MCP — vira um Deployment + Service como qualquer outro.
- **Aula 14:** validação de dados e testes — o gate que roda antes deste deploy.
- **Aula 17:** Airflow/Prefect — `KubernetesPodOperator`; Argo Workflows nativo.
- **Aula 19:** Model Registry — promover modelo é trocar imagem/tag.
- **Aula 21:** Triton/BentoML/vLLM — `requests`/`limits` e `nvidia.com/gpu`.
- **Aula 22:** Canary, Blue-Green e Shadow — o rolling update é o caso simples.
- **Aula 23:** monitoramento — Prometheus e Grafana rodam no cluster.
- **Aula 26:** projeto final E2E — o alvo natural de tudo isto.
