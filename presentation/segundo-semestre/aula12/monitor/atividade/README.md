# 🧪 Atividade Prática — Aula 12

O **repositório da demo** prometido no slide 35: um serviço de inferência
containerizado, os YAMLs que o colocam de pé num cluster local e um alvo de
`make` para cada um dos **8 atos** do roteiro (slide 26).

Roda em **cluster local** (minikube ou kind), **CPU-only**, sem nuvem e sem
cartão de crédito.

> ⚠️ **Trava de contexto.** Todo alvo que escreve no cluster usa
> `kubectl --context mlops-aula12` explicitamente e passa por `make guard`.
> Se o seu `kubectl` estiver apontando para um cluster de trabalho, o lab
> avisa e **mesmo assim não toca nele**. Aplicar YAML no cluster errado é o
> incidente mais comum com `kubectl` — o lab foi desenhado para não ensinar
> esse hábito.

## 📂 Estrutura

```text
atividade/
├── README.md
├── Makefile                  # um alvo por ato da demo
├── app/
│   ├── main.py               # FastAPI: /predict, /health, /ready, /quebrar
│   ├── requirements.txt
│   └── Dockerfile            # ARG VER → assa APP_VERSION na imagem
├── k8s/
│   ├── 00-namespace.yaml
│   ├── 01-configmap.yaml     # ConfigMap + Secret (com o aviso do base64)
│   ├── 02-deployment.yaml    # ★ o arquivo mais comentado do lab
│   ├── 03-service.yaml
│   ├── 04-hpa.yaml           # opcional (precisa do metrics-server)
│   └── quebrado/
│       └── deployment-quebrado.yaml   # Ato 8: 3 defeitos em escada
└── desafio/
    └── qdrant.yaml           # StatefulSet + PVC (desafio da semana)
```

## 🛠️ Pré-requisitos

| Ferramenta | Versão testada |
|---|---|
| Docker | 29.4.0 |
| minikube | 1.38.1 |
| kubectl | 1.36.3 (cluster 1.34.0) |
| make | qualquer |

`kind` funciona igualmente bem — troque `minikube ... image load` por
`kind load docker-image` nos alvos `cluster` e `load`.

## 🚀 Preparação (uma vez)

```bash
make cluster    # sobe o minikube no profile mlops-aula12 (~2 min)
make load       # constrói inferencia:v1 e v2 e carrega no cluster
```

`make cluster` usa `--keep-context`: o contexto ativo do seu shell **não** é
alterado. Isso é proposital.

> 💡 **Por que `imagePullPolicy: Never`?** Não há registry aqui. As imagens
> vão para dentro do nó via `minikube image load`. Sem essa linha, o kubelet
> tentaria buscar `inferencia:v1` no Docker Hub e falharia com
> `ErrImageNeverPull`. Em produção você usaria um registry e uma tag imutável.

## 🎬 Os 8 atos

`make help` lista tudo. Cada ato é independente e pode ser repetido.

### Ato 1 — O cluster e o YAML

```bash
make ato1
```

```text
NAME           STATUS   ROLES           AGE   VERSION   INTERNAL-IP
mlops-aula12   Ready    control-plane   18s   v1.34.0   192.168.49.2
```

### Ato 2 — Apply e ver nascer

```bash
make ato2
```

```text
deployment "inferencia" successfully rolled out
NAME                          READY   STATUS    RESTARTS   AGE   IP
inferencia-764d874d65-7jq6w   1/1     Running   0          10s   10.244.0.3
inferencia-764d874d65-9srhg   1/1     Running   0          10s   10.244.0.5
inferencia-764d874d65-zgfw9   1/1     Running   0          10s   10.244.0.4
```

Rode `kubectl --context mlops-aula12 -n aula12 get pods -w` num terminal
paralelo antes do apply, para a turma ver `Pending → ContainerCreating →
Running 0/1 → Running 1/1`. O `0/1` é a readinessProbe segurando o tráfego.

### Ato 3 ★ — Matar um pod e vê-lo voltar

```bash
make ato3
```

```text
── matando inferencia-764d874d65-7jq6w
pod "inferencia-764d874d65-7jq6w" deleted from aula12 namespace
── depois (repare no AGE do novo pod):
NAME                          READY   STATUS    RESTARTS   AGE
inferencia-764d874d65-5l92n   0/1     Running   0          4s     ← nasceu agora
inferencia-764d874d65-9srhg   1/1     Running   0          20s
inferencia-764d874d65-zgfw9   1/1     Running   0          20s
```

**A frase do slide 27 vai aqui:** *"eu não mandei criar outro pod; eu declarei
que queria três."* Repare que o pod novo entra `0/1` — o loop de reconciliação
e a readinessProbe aparecem na mesma tela.

### Ato 4 — Escalar

```bash
make ato4     # replicas=6
```

Volte para 3 com `kubectl --context mlops-aula12 -n aula12 scale
deployment/inferencia --replicas=3`.

### Ato 5 — Service e chamada real

```bash
make ato5
```

```text
── de DENTRO do cluster, via DNS do Service (balanceia de verdade):
inferencia-764d874d65-n2d69
inferencia-764d874d65-8gs6j
inferencia-764d874d65-zgfw9
inferencia-764d874d65-n2d69
inferencia-764d874d65-5l92n
inferencia-764d874d65-zgfw9
inferencia-764d874d65-9srhg
inferencia-764d874d65-9srhg
```

O serviço devolve o próprio nome do pod, então o balanceamento fica visível.

> ⚠️ **Pegadinha que estraga a demo ao vivo.** `kubectl port-forward
> svc/inferencia` **não** passa pelo balanceamento do Service: ele escolhe
> **um** pod e mantém o túnel nele. Se você "mostrar o balanceamento" pelo
> port-forward, todas as respostas vêm do mesmo pod e parece que o Kubernetes
> está quebrado. Por isso o `make ato5` chama pelo DNS interno
> (`http://inferencia`), de dentro do cluster.
>
> Para acessar de fora mesmo assim (útil para abrir o `/docs` no navegador):
> ```bash
> make forward     # noutro terminal; bloqueia
> make curl        # e repare: sempre o mesmo pod
> ```

### Ato 6 — Trocar config sem rebuild

```bash
make ato6
```

Antes: `"model_version": "credito-2026.08-a"`, `"app_version": "v1"`
Depois: `"model_version": "credito-2026.08-b"`, `"app_version": "v1"`

```json
{"servico":"inferencia","app_version":"v1","model_version":"credito-2026.08-b",
 "pod":"inferencia-5666dc8fff-mdxwd","pronto":true}
```

**A imagem não mudou.** `MODEL_VERSION` vem do ConfigMap; `APP_VERSION` está
assada na imagem. São dois eixos de versionamento diferentes, e o próximo ato
mexe no outro.

> `kubectl rollout restart` é necessário porque variáveis de ambiente vindas
> de ConfigMap **não** são atualizadas em containers já em execução. Só um
> ConfigMap montado como *volume* atualiza sozinho (com atraso de até ~1 min).

### Ato 7 ★ — Rolling update e rollback

```bash
make ato7     # inferencia:v1 → v2
```

```text
Waiting for deployment "inferencia" rollout to finish: 5 out of 6 new replicas have been updated...
deployment "inferencia" successfully rolled out
── histórico:
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
3         <none>
```

Agora `"app_version": "v2"` — e `"model_version"` continua `-b`.

```bash
make undo     # o comando que salva a madrugada
```

Volta para `"app_version": "v1"`, **mantendo** `"model_version": "credito-2026.08-b"`.
Isso é o ponto: rollback de imagem não desfaz mudança de configuração. São
histórias de versão independentes, e confundir as duas é fonte real de
incidente.

Com `maxUnavailable: 0` no manifesto, nenhuma requisição cai durante a troca.
Experimente pôr `maxUnavailable: 2` e repetir com o `watch` aberto.

### Ato 8 — Quebrar e debugar

```bash
make ato8
```

O manifesto `k8s/quebrado/deployment-quebrado.yaml` tem **três defeitos em
escada**. Conserte um e o próximo aparece — que é exatamente como debugar
Kubernetes funciona na vida real.

| Etapa | O que você vê | Onde está o problema | Comando que revela |
|---|---|---|---|
| 1 | `Pending` | **Scheduler**: `0/1 nodes are available: 1 Insufficient memory` | `describe pod` |
| 2 | `ErrImageNeverPull` | **kubelet**: a tag `inferencia:v99` não existe no nó | `describe pod` |
| 3 | `Running` mas `0/1` | **Probe**: `Readiness probe failed: HTTP probe failed with statuscode: 404` | `describe pod` |

<details>
<summary>👉 Resposta (tente antes)</summary>

1. `resources.requests.memory: 64Gi` — nenhum nó de laboratório tem isso.
   Corrija para `64Mi`.
2. `image: inferencia:v99` — a tag não foi carregada. Corrija para `v1`.
3. `readinessProbe.httpGet.path: /pronto` — o endpoint é `/ready`.

Sequência para reproduzir a escada sem editar o arquivo:

```bash
K="kubectl --context mlops-aula12 -n aula12"
$K set resources deployment/inferencia-quebrada --requests=memory=64Mi
$K set image deployment/inferencia-quebrada api=inferencia:v1
# o pod fica Running 0/1 para sempre: a probe é o defeito que sobra
$K delete deployment inferencia-quebrada
```
</details>

**A lição de diagnóstico:** `get` diz **que** quebrou, `describe` diz **por
que** (os eventos do scheduler e do kubelet), `logs` diz o que o processo falou
antes de morrer. Nessa ordem, sempre.

### Bônus — liveness reiniciando o pod

```bash
make forward   # noutro terminal
curl -s -X POST localhost:8080/quebrar
kubectl --context mlops-aula12 -n aula12 get pods -w
```

O endpoint derruba a liveness de propósito; em ~30 s o `RESTARTS` sobe. É a
diferença entre readiness (*tira do Service*) e liveness (*reinicia o pod*),
demonstrada em vez de explicada.

## 🎯 Desafio da semana

Slide 35: **subir um Qdrant com PVC e provar que a coleção sobrevive à morte do
pod.**

```bash
make desafio
kubectl --context mlops-aula12 -n aula12 port-forward svc/qdrant 6333:6333
```

Noutro terminal:

```bash
# 1. cria a coleção
curl -X PUT localhost:6333/collections/aula12 \
  -H 'content-type: application/json' \
  -d '{"vectors":{"size":4,"distance":"Cosine"}}'

# 2. mata o pod
kubectl --context mlops-aula12 -n aula12 delete pod qdrant-0

# 3. espera voltar, refaz o port-forward e confere que a coleção continua lá
curl -s localhost:6333/collections
```

Perguntas para levar à aula seguinte:

1. Por que `StatefulSet` e não `Deployment`? (identidade e disco **por réplica**)
2. O que acontece com o PVC se você apagar o StatefulSet? (ele **sobrevive** —
   `volumeClaimTemplates` não é removido junto; isto já causou perda e já
   causou conta alta)
3. Por que o Service é `clusterIP: None`?

## 🧹 Limpeza

```bash
make limpar     # apaga o namespace aula12; o cluster continua de pé
make destruir   # apaga o cluster local inteiro
```

## ⚠️ Solução de problemas

| Sintoma | Causa / solução |
|---|---|
| `⛔ Contexto ativo é '...'` | Apenas um aviso: os alvos usam `--context` e não tocaram no outro cluster. Para alinhar o shell: `kubectl config use-context mlops-aula12`. |
| `❌ Cluster inacessível` | Rode `make cluster`. |
| `ErrImageNeverPull` | Faltou `make load` depois de reconstruir a imagem. |
| Pod eternamente `0/1 Running` | A readinessProbe está falhando. `describe pod` mostra o código HTTP. |
| Pod `Pending` | Recurso insuficiente ou nó indisponível — sempre `describe pod` primeiro. |
| `CrashLoopBackOff` | `logs <pod> --previous` mostra o que o processo disse antes de morrer. |
| Todas as respostas do mesmo pod | Você está usando `port-forward`. Veja o aviso do Ato 5. |
| `make desafio` demora muito | O pull da imagem do Qdrant depende da sua rede; a demo principal não precisa dele. |

## 📌 Comandos que valem decorar

```bash
kubectl get pods -w                  # acompanhar em tempo real
kubectl describe pod <nome>          # os EVENTOS — 80% dos diagnósticos
kubectl logs <nome> [-f] [--previous]
kubectl exec -it <nome> -- sh
kubectl rollout status/history/undo deployment/<nome>
kubectl scale deployment/<nome> --replicas=N
kubectl get events --sort-by=.lastTimestamp
kubectl config current-context       # ANTES de qualquer apply
```
