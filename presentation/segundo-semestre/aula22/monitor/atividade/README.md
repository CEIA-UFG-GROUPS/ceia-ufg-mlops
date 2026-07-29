# 🧪 Atividade Prática — Aula 22: Estratégias de Deploy (Canary, Blue-Green, Shadow Deployment)

Prática guiada com um **Gateway de tráfego** (FastAPI) na frente de dois serviços de modelo — `champion` (produção, estável) e `canary` (candidato, ainda em validação) — que implementa as três estratégias de deploy estudadas na aula. Trocar de estratégia é apenas uma variável de ambiente: **muda-se o comportamento sem alterar uma linha de código**.

---

## 🎯 O que você vai fazer

1. **Canary Release** — rotear uma fração pequena do tráfego para o modelo candidato e observar a distribuição real de respostas.
2. **Blue-Green Deployment** — fazer o corte atômico de 100% do tráfego entre `champion` e `canary` trocando uma única variável de ambiente.
3. **Shadow Deployment** — espelhar o tráfego real para o modelo candidato sem que sua resposta chegue ao usuário, medindo a taxa de divergência entre as duas versões.
4. **Discutir os trade-offs** de risco, custo e velocidade de rollback de cada estratégia com dados reais gerados pela própria atividade.

---

## 📂 Estrutura de Diretórios

```text
atividade/
├── README.md                   # este arquivo
├── requirements.txt            # dependências (FastAPI, uvicorn, httpx)
├── src/
│   ├── model_service.py        # Script 1: serviço de modelo genérico (champion ou canary via env vars)
│   ├── gateway.py               # Script 2: gateway que implementa canary/blue_green/shadow
│   └── load_test_client.py     # Script 3: cliente de carga que tabula a distribuição de respostas
└── docker/
    ├── Dockerfile               # imagem única reaproveitada pelos 3 serviços
    └── docker-compose.yml       # stack com model-champion + model-canary + gateway
```

---

## 🛠️ Exercício 1 — Canary Release

Suba a stack com a estratégia padrão (`canary`, 10% de tráfego para o candidato):

```bash
cd atividade/docker
docker compose up --build -d
```

Rode o cliente de carga a partir da pasta `atividade/` (em outro terminal, com o ambiente virtual ativado — veja a seção de instalação local abaixo):

```bash
python -m src.load_test_client
```

**Saída esperada** (aproximada — a alocação é probabilística):
```text
Estratégia ativa no gateway: canary
Resultado após 200 requisições ao Gateway (http://localhost:8000):
  v1-champion: 179 respostas (89.5%)
  v2-canary: 21 respostas (10.5%)
```

Aumente a porcentagem do canário e reinicie apenas o gateway, sem rebuildar os modelos:

```bash
CANARY_PERCENT=50 docker compose up -d gateway
python -m src.load_test_client
```

---

## 🛠️ Exercício 2 — Blue-Green Deployment

Troque a estratégia do gateway para `blue_green`, com o ambiente ativo em `blue` (champion):

```bash
DEPLOY_STRATEGY=blue_green ACTIVE_COLOR=blue docker compose up -d gateway
python -m src.load_test_client
```

Todas as respostas devem vir de `v1-champion` (100%). Agora simule o **corte atômico de tráfego** para o ambiente `green` (canary), como se ele tivesse acabado de ser validado:

```bash
DEPLOY_STRATEGY=blue_green ACTIVE_COLOR=green docker compose up -d gateway
python -m src.load_test_client
```

Repare que a troca é instantânea — 100% do tráfego migra de uma vez. Para simular um **rollback de emergência**, basta voltar `ACTIVE_COLOR=blue` e reiniciar o gateway novamente.

---

## 🛠️ Exercício 3 — Shadow Deployment

Troque a estratégia para `shadow`. Neste modo, toda resposta ao usuário vem do `champion`; o `canary` roda em paralelo apenas para comparação:

```bash
DEPLOY_STRATEGY=shadow docker compose up -d gateway
python -m src.load_test_client
```

**Saída esperada**:
```text
Estratégia ativa no gateway: shadow
Resultado após 200 requisições ao Gateway (http://localhost:8000):
  v1-champion: 200 respostas (100.0%)

[Shadow] Comparações realizadas: 200
[Shadow] Taxa de divergência champion vs. shadow: 12.50%
```

Observe: **100% das respostas retornadas ao usuário vêm do champion** (zero risco de exposição), mas o gateway já sabe, através da comparação em segundo plano, que o candidato diverge em ~12% dos casos — informação valiosa para decidir se ele está pronto para avançar a um Canary Release.

---

## 🐍 Instalação Local (para rodar o `load_test_client.py`)

```bash
cd atividade
python -m venv .venv
source .venv/bin/activate   # No Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 💬 Perguntas para Discutir no Encontro

1. **No Exercício 1, mesmo com `CANARY_PERCENT=10`, a distribuição real observada raramente é exatamente 90/10.** Por que isso acontece, e por que isso importa para decidir o tamanho da janela de observação de um Canary Release real?
2. **No Exercício 2, a troca de `ACTIVE_COLOR` é instantânea e afeta 100% do tráfego imediatamente.** Que tipo de bug essa estratégia detectaria pior do que um Canary Release, e por quê?
3. **No Exercício 3, a taxa de divergência do Shadow Deployment não impede nenhuma requisição de ser respondida pelo champion.** Como você usaria essa métrica de divergência para decidir, de forma automatizada, se o candidato pode avançar para um Canary Release?
4. **O gateway implementado aqui roda em um único processo Python.** Em produção, ferramentas como Istio/Envoy (Shadow, via `VirtualService` com `mirror`) e KServe/Argo Rollouts (Canary, via `canaryTrafficPercent` e `AnalysisTemplate`) assumem esse papel. O que muda arquiteturalmente ao mover essa lógica do nível da aplicação para o nível da malha de rede (Service Mesh)?

---

## ⚠️ Solução de Problemas

| Sintoma | Causa provável / Solução |
|---|---|
| `docker compose up -d gateway` não aplica a nova estratégia | Variáveis de ambiente só são lidas na inicialização do processo — confirme que o container do `gateway` foi realmente recriado (`docker compose ps` deve mostrar um `Up` recente) e não apenas reaproveitado. |
| `python -m src.load_test_client` retorna erro de conexão | Confirme que os três serviços estão saudáveis com `docker compose ps` — o `gateway` depende de `model-champion` e `model-canary` estarem com `healthcheck` OK. |
| Taxa de divergência do Shadow sempre igual a 0% ou 100% | Verifique se `ERROR_RATE` dos serviços não foi sobrescrita sem querer — os valores padrão (`0.03` no champion, `0.15` no canary) já produzem divergência realista o suficiente para a atividade. |

---

📖 **Material Teórico da Aula**: veja o [README do Monitor](../README.md) e o [Deep Research](../deep_research.md) para aprofundar KServe, Argo Rollouts, Envoy/Istio e Seldon Core 2.
