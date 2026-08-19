# Demo da Aula 12 — um alvo por ato do roteiro (slide 26).
#
# TRAVA DE CONTEXTO: todo alvo que escreve no cluster passa por `guard`, que
# recusa a rodar se o contexto ativo não for o do laboratório. Isso não é
# paranoia: a causa mais comum de incidente com kubectl é aplicar no cluster
# certo com a mão no contexto errado.

PROFILE   ?= mlops-aula12
CONTEXT   ?= $(PROFILE)
NS        ?= aula12
KUBECTL   := kubectl --context $(CONTEXT) -n $(NS)

.DEFAULT_GOAL := help
.PHONY: help guard cluster build load deploy ato1 ato2 ato3 ato4 ato5 ato6 \
        ato7 ato8 desafio status limpar destruir balanceamento forward curl undo

help: ## Lista os alvos disponíveis
	@grep -E '^[a-z0-9-]+:.*?## .*$$' $(MAKEFILE_LIST) \
	  | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

guard: ## Verifica que o contexto ativo é o do laboratório
	@ctx=$$(kubectl config current-context 2>/dev/null); \
	if [ "$$ctx" != "$(CONTEXT)" ]; then \
	  echo "⛔ Contexto ativo é '$$ctx', esperado '$(CONTEXT)'."; \
	  echo "   Os alvos usam --context $(CONTEXT), então nada foi aplicado no cluster errado."; \
	  echo "   Para alinhar o shell: kubectl config use-context $(CONTEXT)"; \
	fi; \
	kubectl --context $(CONTEXT) version --request-timeout=5s >/dev/null 2>&1 \
	  || { echo "❌ Cluster '$(CONTEXT)' inacessível. Rode: make cluster"; exit 1; }

# ── Preparação ────────────────────────────────────────────────────────────
cluster: ## Cria o cluster local (minikube, profile dedicado)
	minikube start --profile $(PROFILE) --driver docker \
	  --kubernetes-version v1.34.0 --cpus 2 --memory 3000 --keep-context

build: ## Constrói as imagens inferencia:v1 e inferencia:v2
	docker build -t inferencia:v1 --build-arg VER=v1 app/
	docker build -t inferencia:v2 --build-arg VER=v2 app/

load: build ## Carrega as imagens dentro do cluster (não há registry aqui)
	minikube --profile $(PROFILE) image load inferencia:v1
	minikube --profile $(PROFILE) image load inferencia:v2

deploy: guard ## Aplica namespace, config, deployment e service
	kubectl --context $(CONTEXT) apply -f k8s/00-namespace.yaml
	kubectl --context $(CONTEXT) apply -f k8s/01-configmap.yaml
	kubectl --context $(CONTEXT) apply -f k8s/02-deployment.yaml
	kubectl --context $(CONTEXT) apply -f k8s/03-service.yaml
	$(KUBECTL) rollout status deployment/inferencia --timeout=120s

# ── Os 8 atos da demo ─────────────────────────────────────────────────────
ato1: guard ## O cluster e o YAML
	kubectl --context $(CONTEXT) get nodes -o wide
	@echo "── objetos do namespace $(NS):"
	-$(KUBECTL) get all

ato2: deploy ## Apply e ver nascer
	$(KUBECTL) get pods -o wide

ato3: guard ## ★ Matar um pod → ele volta sozinho
	@echo "── antes:"; $(KUBECTL) get pods
	@pod=$$($(KUBECTL) get pods -l app=inferencia -o jsonpath='{.items[0].metadata.name}'); \
	 echo "── matando $$pod"; $(KUBECTL) delete pod $$pod
	@sleep 3
	@echo "── depois (repare no AGE do novo pod):"; $(KUBECTL) get pods

ato4: guard ## Escalar para 6 réplicas
	$(KUBECTL) scale deployment/inferencia --replicas=6
	$(KUBECTL) rollout status deployment/inferencia --timeout=120s
	$(KUBECTL) get pods

ato5: guard ## Service e chamada real (balanceamento visível)
	@echo "── de DENTRO do cluster, via DNS do Service (balanceia de verdade):"
	@$(MAKE) --no-print-directory balanceamento
	@echo
	@echo "── de fora: 'make forward' noutro terminal, depois 'make curl'"

balanceamento: guard ## 8 chamadas ao Service pelo DNS interno; repare nos nomes
	@$(KUBECTL) wait --for=condition=ready pod -l app=inferencia --timeout=120s >/dev/null
	@pod=$$($(KUBECTL) get pods -l app=inferencia \
	        --field-selector=status.phase=Running \
	        -o jsonpath='{.items[0].metadata.name}'); \
	$(KUBECTL) exec $$pod -- python -c "import json,urllib.request;\
[print(json.load(urllib.request.urlopen(urllib.request.Request(\
'http://inferencia/predict',\
data=json.dumps({'score_credito':720,'renda_anual':90000,'taxa_endividamento':0.2}).encode(),\
headers={'content-type':'application/json'})))['pod']) for _ in range(8)]"

forward: guard ## Abre o port-forward do Service na porta 8080 (bloqueia)
	$(KUBECTL) port-forward svc/inferencia 8080:80

curl: ## Chama /predict pelo port-forward — SEMPRE o mesmo pod (veja o README)
	@for i in 1 2 3 4 5 6; do \
	  curl -s -X POST localhost:8080/predict \
	    -H 'content-type: application/json' \
	    -d '{"score_credito":720,"renda_anual":90000,"taxa_endividamento":0.2}' \
	  | tr -d '\n'; echo; \
	done

ato6: guard ## Trocar config sem rebuild de imagem
	$(KUBECTL) patch configmap modelo-config \
	  --type merge -p '{"data":{"MODEL_VERSION":"credito-2026.08-b"}}'
	$(KUBECTL) rollout restart deployment/inferencia
	$(KUBECTL) rollout status deployment/inferencia --timeout=120s

ato7: guard ## ★ Rolling update para v2 e rollback
	$(KUBECTL) set image deployment/inferencia api=inferencia:v2
	$(KUBECTL) rollout status deployment/inferencia --timeout=120s
	@echo "── histórico:"; $(KUBECTL) rollout history deployment/inferencia

undo: guard ## Desfaz o último rollout (o comando que salva a madrugada)
	$(KUBECTL) rollout undo deployment/inferencia
	$(KUBECTL) rollout status deployment/inferencia --timeout=120s

ato8: guard ## Quebrar e debugar
	kubectl --context $(CONTEXT) apply -f k8s/quebrado/deployment-quebrado.yaml
	@sleep 5
	$(KUBECTL) get pods -l app=inferencia-quebrada
	@echo "── agora investigue:  kubectl -n $(NS) describe pod <nome>"

desafio: guard ## Sobe o Qdrant com PVC (desafio da semana)
	kubectl --context $(CONTEXT) apply -f desafio/qdrant.yaml
	$(KUBECTL) rollout status statefulset/qdrant --timeout=180s

# ── Utilidades ────────────────────────────────────────────────────────────
status: guard ## Panorama do namespace
	$(KUBECTL) get all,configmap,secret,pvc

limpar: guard ## Remove os objetos da aula (mantém o cluster)
	-kubectl --context $(CONTEXT) delete namespace $(NS)

destruir: ## Apaga o cluster local inteiro
	minikube delete --profile $(PROFILE)
