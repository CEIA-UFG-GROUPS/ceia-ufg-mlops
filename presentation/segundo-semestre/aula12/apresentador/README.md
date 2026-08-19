# Kubernetes em 60 Minutos

## README do Apresentador

Esta é a **aula de abertura do 2º semestre** e a base de infraestrutura para
quase tudo o que vem depois: MCP (13), pipelines (17), serving pesado (21),
estratégias de deploy (22) e o projeto final (26) assumem que a turma sabe o
que é um pod, um Deployment e um Service.

O deck já existe e está pronto: **36 slides, 60 minutos**, gerado por
`~/MLOps/apresentacao-k8s/` (`gerar_slides.py` → `Kubernetes em 60 Minutos.pptx`).
Este README é o **companheiro de execução** — mapa de tempo, runbook da demo
com saídas reais, plano de corte e perguntas prováveis. O material do monitor
(`../monitor/`) é o estudo prévio da turma.

> 💡 **A tese da aula, em uma frase:** o cluster não executa ordens, ele
> persegue um estado. Tudo — reconciliação, rolling update, self-healing,
> operators — decorre daí. Se a turma sair só com isso, a aula funcionou.

---

## 1️⃣ Mapa de tempo

| Bloco | Slides | Janela | Papel |
|---|---|---|---|
| Abertura | 1–4 | 00:00–03:00 | A dor que eles já viveram |
| **1 — De Docker a orquestração** | 5–8 | 03:00–10:00 | Por que Compose não basta; custo de GPU |
| **2 — O modelo mental** | 9–14 | 10:00–19:00 | ★ Declarativo e loop de reconciliação |
| **3 — Os objetos** | 15–24 | 19:00–32:00 | Vocabulário mínimo; ★ probes |
| **Demo ao vivo** | 25–27 | 32:00–48:00 | 8 atos; o miolo da aula |
| **4 — MLOps** | 28–33 | 48:00–54:00 | ★ CRD/Operator; ★ quando NÃO usar |
| Fechamento | 34–36 | 54:00–60:00 | 3 lembretes + perguntas |

**Dois pit stops de perguntas** já estão no roteiro: slide 14 (17:30–19:00) e o
fechamento. Avise na abertura que você vai parar — evita interrupção no meio do
bloco 2, que é o único que não pode ser fatiado.

### Os quatro slides inegociáveis

| Slide | Conteúdo | Por que não pode cair |
|---:|---|---|
| **11** | Loop de reconciliação | É a aula inteira. Se atrasar, corte outra coisa. |
| **21** | Probes (readiness/liveness/startup) | O slide mais MLOps do deck: modelo demora a carregar. |
| **29** | CRD e Operator | Explica por que Kubeflow/KServe/Ray existem *aqui*. |
| **33** | Quando NÃO usar | Sem isso a aula vira propaganda e perde credibilidade. |

### Plano de corte (se atrasar)

Na ordem: **19** (Ingress) → **24** (YAML completo) → **31** (banco vetorial/GPU)
→ **13** (arquitetura do control plane, reduzir a 30 s). Nunca corte 11, 21, 29
ou 33. Se a demo atrasar, corte os **atos 4 e 6** — não os atos 3 e 7.

---

## 2️⃣ Runbook da demo (32:00–48:00)

Repositório: [`../monitor/atividade/`](../monitor/atividade/). Um alvo de `make`
por ato. **Tudo abaixo foi executado e as saídas são reais.**

### Pré-voo (faça 30 min antes, não na hora)

```bash
cd ../monitor/atividade
make cluster        # ~2 min na primeira vez
make load           # build v1/v2 + carga no cluster
make ato2           # deixe já aplicado e derrube com 'make limpar' antes de começar
kubectl config current-context      # confira ANTES de qualquer coisa
```

- [ ] Cluster de pé e imagens carregadas
- [ ] Fonte do terminal em ~18 pt
- [ ] Dois terminais: um para comandos, outro com `get pods -w`
- [ ] Print do Ato 3 salvo como plano B (slide 27 pede um print seu)
- [ ] Wi-Fi irrelevante: nada aqui depende de rede depois do `make load`

### Os 8 atos

| # | Alvo | O que dizer enquanto roda |
|---|---|---|
| 1 | `make ato1` | "Um nó só, mas o modelo é idêntico com 500." |
| 2 | `make ato2` | Abra o `02-deployment.yaml` e leia **só** `replicas: 3`. |
| 3 ★ | `make ato3` | **O momento da aula.** Ver abaixo. |
| 4 | `make ato4` | "Uma linha. Em produção isso é o HPA fazendo sozinho." |
| 5 | `make ato5` | Balanceamento visível pelo nome do pod na resposta. |
| 6 | `make ato6` | "A imagem não mudou. Só a configuração." |
| 7 ★ | `make ato7` + `make undo` | Rolling update sem queda, e o `undo` que salva a madrugada. |
| 8 | `make ato8` | Debug em escada: `get` → `describe` → `logs`. |

### Ato 3 — o momento que a plateia lembra

```text
── matando inferencia-764d874d65-7jq6w
pod "inferencia-764d874d65-7jq6w" deleted from aula12 namespace
── depois (repare no AGE do novo pod):
NAME                          READY   STATUS    RESTARTS   AGE
inferencia-764d874d65-5l92n   0/1     Running   0          4s   ← nasceu agora
inferencia-764d874d65-9srhg   1/1     Running   0          20s
inferencia-764d874d65-zgfw9   1/1     Running   0          20s
```

Pause. Vá para o **slide 27** e diga a frase: *"eu não mandei criar outro pod;
eu declarei que queria três."* Depois volte e mostre que o novo entrou `0/1` —
**a readinessProbe do slide 21 aparecendo sozinha na tela**. Amarrar os dois
conceitos aqui vale mais que qualquer diagrama.

### ⚠️ Duas armadilhas que estragam a demo ao vivo

1. **`port-forward` não balanceia.** `kubectl port-forward svc/...` fixa **um**
   pod. Se você tentar mostrar load balancing por ele, todas as respostas vêm
   do mesmo pod e parece que o Kubernetes está quebrado. Por isso o `make ato5`
   chama pelo **DNS interno** de dentro do cluster. Saída real:

   ```text
   inferencia-764d874d65-n2d69
   inferencia-764d874d65-8gs6j
   inferencia-764d874d65-zgfw9
   inferencia-764d874d65-n2d69
   ```

2. **Contexto errado do `kubectl`.** O `make guard` recusa e todos os alvos
   passam `--context` explícito, então o lab não escreve em cluster de
   trabalho. Vale mostrar isso em 10 segundos: é uma lição de operação que a
   turma leva para o emprego.

### Ato 6 vs Ato 7 — o contraste que fecha o bloco

| | Ato 6 (`rollout restart`) | Ato 7 (`set image`) |
|---|---|---|
| Muda | `MODEL_VERSION` (ConfigMap) | `APP_VERSION` (imagem) |
| Precisa de rebuild? | **Não** | Sim |
| Depois do `make undo` | continua `-b` | volta para `v1` |

O `undo` **não** desfaz a mudança de configuração. Diga isso em voz alta: são
duas histórias de versão independentes, e confundi-las é fonte real de
incidente.

### Ato 8 — a escada de defeitos (saídas verificadas)

| Conserta | Aparece | Camada culpada |
|---|---|---|
| — | `Pending` · `0/1 nodes are available: 1 Insufficient memory` | Scheduler |
| memória | `ErrImageNeverPull` | kubelet |
| imagem | `Running 0/1` · `Readiness probe failed: HTTP probe failed with statuscode: 404` | Probe |

A moral: `get` diz **que** quebrou, `describe` diz **por quê**, `logs` diz o que
o processo falou. Nessa ordem.

### Se a demo falhar

Tenha o `make ato3` já rodado e printado. Em último caso, narre pelo slide 26 —
o roteiro está todo lá. **Não** tente debugar ao vivo por mais de 60 segundos.

---

## 3️⃣ Perguntas prováveis (e respostas curtas)

| Pergunta | Resposta |
|---|---|
| "Isso não é overkill para 1 modelo?" | É. Slide 33 responde: Cloud Run/SageMaker/VM resolvem melhor. Compensa com vários serviços, carga elástica ou disputa por GPU. |
| "Quanto custa?" | Control plane gerenciado: de grátis a ~US$ 75/mês por cluster. O grosso são os nós. O desperdício vem de `requests` mal dimensionado, não do Kubernetes. |
| "Docker Swarm / Nomad não fariam?" | Fariam o básico. O ecossistema de ML (KServe, Kubeflow, Ray) foi construído sobre CRDs do Kubernetes — é por isso que ele venceu aqui. |
| "Posso dividir uma GPU?" | Sim: time-slicing (simples, sem isolamento) ou MIG (isolado, só em A100/H100+). Por padrão 1 container ocupa a placa inteira. |
| "Secret é seguro?" | **Não.** É base64. Slide 20. Em produção: External Secrets ou Sealed Secrets. |
| "Preciso saber montar cluster?" | Não. Use EKS/GKE/AKS. Ninguém deveria operar control plane próprio para aprender. |
| "Onde entra o Airflow que vamos ver?" | Aula 17. Airflow/Argo orquestram *tarefas*; o Kubernetes orquestra *containers*. Argo Workflows roda em cima disto. |

---

## 4️⃣ Ganchos para o resto do semestre

Vale plantar explicitamente — a turma cobra coerência:

- **Aula 13 (MCP):** o servidor MCP vira um Deployment + Service como qualquer
  outro serviço.
- **Aula 17 (Airflow/Prefect):** `KubernetesPodOperator`; Argo Workflows é a
  versão nativa.
- **Aula 19 (Model Registry):** promoção de modelo vira mudança de imagem/tag —
  exatamente o Ato 7.
- **Aula 21 (Triton/BentoML/vLLM):** os `requests`/`limits` e `nvidia.com/gpu`
  do slide 22 são o que torna serving pesado viável.
- **Aula 22 (Canary/Blue-Green/Shadow):** o rolling update do Ato 7 é o caso
  mais simples; lá vocês veem os outros.
- **Aula 23 (Monitoramento):** Prometheus e Grafana rodam no cluster.

---

## 5️⃣ Materiais

- **Deck:** `~/MLOps/apresentacao-k8s/Kubernetes em 60 Minutos.pptx` (36 slides).
  Para editar texto: `gerar_slides.py`; para trocar identidade visual:
  `estilo.py`. Notas do apresentador em **Exibir → Modo de Exibição do
  Apresentador** (todas trazem `⏱`, o que dizer e o que cortar).
- **Imagens:** 22 molduras tracejadas aguardam substituição; ícones oficiais em
  `github.com/kubernetes/community/tree/master/icons`.
- **Repositório da demo (slide 35):** [`../monitor/atividade/`](../monitor/atividade/).
  Gere o QR code apontando para a pasta no GitHub antes da aula.
- **Estudo prévio da turma:** [`../monitor/README.md`](../monitor/README.md).

> ℹ️ O `README.md` do gerador cita os slides ★ como "11, 21, 28 e 33"; no deck
> construído o slide de CRD/Operator é o **29** (o 28 é o divisor do bloco).
> As notas dentro do `.pptx` estão corretas.

## 📚 Referências

- [Kubernetes — Concepts](https://kubernetes.io/docs/concepts/) e
  [Basics tutorial](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- Burns, B.; Beda, J.; Hightower, K. *Kubernetes: Up and Running*, 3ª ed.
- Gift, N.; Deza, A. *Practical MLOps*, Cap. 3 "Containers and Edge Devices".
- Treveil et al. *Introducing MLOps*, Cap. 6 "Deploying to Production".
- [KServe](https://kserve.github.io/website/) · [Kubeflow](https://www.kubeflow.org/)
  · [Argo Workflows](https://argo-workflows.readthedocs.io/) · [Ray on K8s](https://docs.ray.io/en/latest/cluster/kubernetes/index.html)
- [killercoda.com/kubernetes](https://killercoda.com/kubernetes) — cenários no navegador

> ℹ️ O cronograma não atribuiu leitura de livro a esta aula (a coluna de
> materiais está vazia na linha de Kubernetes). As referências acima foram
> escolhidas para cobrir a lacuna.
