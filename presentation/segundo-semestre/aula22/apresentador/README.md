# Estratégias de Deploy (Canary, Blue-Green, Shadow Deployment) — Guia do Apresentador

Este documento organiza a apresentação da aula e serve como **guia conceitual** para o expositor.
A estrutura abaixo é uma sugestão para garantir clareza, progressão lógica e alinhamento com o grupo.

> 💡 **Fluxo sugerido**: partir do deploy "Big Bang" (derrubar a versão antiga, subir a nova, torcer para que funcione), mostrar por que isso é inaceitável para modelos de ML — cujo comportamento é probabilístico e não pode ser 100% validado só com testes unitários — e evoluir para estratégias que **reduzem o blast radius** de um deploy ruim: Blue-Green, Canary e Shadow Deployment. A aula é sobre **gestão de risco em produção**, não sobre uma ferramenta específica.

---

## 1️⃣ Motivação

### 1.1 Por que isso importa para MLOps?

- **O modelo pode "passar nos testes" e ainda falhar em produção**: métricas offline (acurácia, F1) no conjunto de teste não garantem bom desempenho com a distribuição real e viva de tráfego.
- **O deploy "Big Bang" é uma aposta de tudo ou nada**: substituir 100% do tráfego de uma vez pela nova versão significa que, se o modelo novo tiver um bug ou regressão de qualidade, **todos os usuários** são afetados simultaneamente.
- **A pergunta central desta aula**: como testar um modelo com tráfego real de produção, com o menor risco possível, e com a capacidade de reverter (rollback) em segundos?

### 1.2 O que o grupo vai sair sabendo fazer

- Diferenciar **Blue-Green**, **Canary Release** e **Shadow Deployment** — quando usar cada um e por quê.
- Entender o papel do **Model Registry** (aliases `@champion`/`@challenger`, Aula 19) na implementação dessas estratégias.
- Relacionar estratégias de deploy com métricas de observabilidade (Aula 11) para decidir automaticamente promover ou reverter um modelo.
- Reconhecer os trade-offs de custo, complexidade operacional e velocidade de feedback de cada estratégia.

### 1.3 Conexão com aulas anteriores

- **Aula 19 (Model Registry)**: aliases mutáveis (`@champion`, `@challenger`) são o mecanismo técnico que viabiliza trocar tráfego entre versões sem alterar código.
- **Aula 11 (Logging, Monitoramento e Observabilidade)**: nenhuma estratégia de deploy progressivo funciona sem métricas em tempo real para decidir se o novo modelo está saudável.

---

## 2️⃣ Como Funciona

### 2.1 Blue-Green Deployment

- **Mecânica**: mantêm-se dois ambientes idênticos de produção — `Blue` (versão atual, recebendo 100% do tráfego) e `Green` (nova versão, totalmente implantada mas sem tráfego).
- **Corte de tráfego**: quando o `Green` é validado, o roteador (load balancer/API Gateway) troca **instantaneamente** 100% do tráfego de `Blue` para `Green`.
- **Rollback**: se algo der errado, basta apontar o tráfego de volta para `Blue` — reversão imediata, já que o ambiente antigo continua de pé.
- **Trade-off**: exige manter **duas infraestruturas completas** rodando simultaneamente (custo de dobrar recursos, mesmo que temporariamente).

### 2.2 Canary Release

- **Mecânica**: a nova versão (`canary`) recebe uma **fração pequena** do tráfego real (ex.: 5%), enquanto a versão estável (`champion`) continua servindo o restante (95%).
- **Incremento gradual**: se as métricas do canary forem saudáveis por um período, a fração de tráfego aumenta progressivamente (5% → 25% → 50% → 100%).
- **Detecção precoce**: como apenas uma fração dos usuários é exposta ao risco, um bug é detectado com impacto limitado — o "canário na mina de carvão".
- **Trade-off**: requer infraestrutura de roteamento de tráfego por porcentagem (service mesh como Istio/Linkerd, ou funcionalidades nativas do API Gateway/Kubernetes) e monitoramento estatístico robusto para decidir se o canary é de fato melhor.

### 2.3 Shadow Deployment (Dark Launch)

- **Mecânica**: a nova versão recebe uma **cópia** do tráfego real de produção, processa as requisições em paralelo, mas **suas respostas nunca são retornadas ao usuário** — apenas logadas e comparadas com a versão atual.
- **Zero risco para o usuário**: como o usuário nunca vê a resposta do modelo em shadow, não há risco de regressão de experiência — é a estratégia mais segura para validar um modelo antes de qualquer exposição real.
- **Uso típico**: comparar diretamente as predições do modelo novo vs. o modelo em produção no mesmo conjunto de requisições reais, medindo divergência antes de sequer considerar promoção.
- **Trade-off**: dobra o custo computacional (toda requisição é processada duas vezes) e exige infraestrutura para capturar, duplicar e comparar tráfego sem afetar a latência percebida pelo usuário.

### 2.4 Matriz de Comparação

| Estratégia | Risco para o Usuário | Custo de Infraestrutura | Velocidade de Rollback | Melhor Uso |
|---|---|---|---|---|
| **Blue-Green** | Médio (corte abrupto de 100%) | Alto (2 ambientes completos) | Instantâneo (troca de roteamento) | Releases pouco frequentes, com validação prévia completa |
| **Canary** | Baixo (fração controlada) | Médio (roteamento por %) | Rápido (reduzir % para 0) | Modelos com risco de regressão sutil, releases frequentes |
| **Shadow** | Nenhum (resposta não é exibida) | Alto (processamento duplicado) | N/A (nunca está "no ar") | Validação inicial de modelos de alto risco antes de qualquer exposição |

### 2.5 Como o Model Registry Viabiliza Essas Estratégias

- Aliases mutáveis do Model Registry (`@champion`, `@challenger`, `@canary`) permitem que o código de inferência consulte sempre `models:/Modelo@champion`, sem hardcode de versão.
- Promover um modelo de `@challenger` para `@champion` é uma operação atômica de metadados — não exige rebuild de código nem novo deploy de infraestrutura.
- A decisão de promoção pode ser **automatizada**: um pipeline de CI/CD compara métricas de negócio entre `@champion` e `@challenger`/`@canary` e promove automaticamente se os critérios forem satisfeitos.

---

## 3️⃣ Quickstart & Demos

> 💡 **Instruções para ao vivo**: as demos podem ser simuladas localmente com dois serviços FastAPI (`v1` e `v2`) atrás de um roteador simples em Python, sem necessidade de Kubernetes/Istio para ilustrar o conceito.

### 3.1 Demo 1 — Roteamento Canary Simples (Python)

```python
import random

CANARY_TRAFFIC_PERCENT = 5  # 5% do tráfego vai para o modelo novo

def rotear_requisicao(request):
    if random.randint(1, 100) <= CANARY_TRAFFIC_PERCENT:
        return chamar_modelo("canary", request)
    return chamar_modelo("champion", request)
```

### 3.2 Demo 2 — Shadow Deployment: comparação sem exposição

```python
def processar_requisicao(request):
    resposta_producao = chamar_modelo("champion", request)

    # Shadow: roda em paralelo, mas nunca retorna ao usuário
    try:
        resposta_shadow = chamar_modelo("shadow_candidate", request)
        logar_divergencia(request, resposta_producao, resposta_shadow)
    except Exception as e:
        logar_erro_shadow(e)  # falha no shadow NUNCA deve afetar o usuário

    return resposta_producao  # sempre retorna a resposta do modelo em produção
```

### 3.3 Demo 3 — Discussão ao vivo: promoção automática via Model Registry

- Mostrar como um pipeline de CI/CD consultaria métricas de negócio do `@canary` (Aula 11) e, se aprovadas, chamaria `client.set_registered_model_alias("Modelo", "champion", version=nova_versao)` (Aula 19).

---

## 4️⃣ Quando Usar (e Quando NÃO Usar)

### Usar ✅
- **Blue-Green**: quando é possível manter dois ambientes completos temporariamente e o rollback instantâneo é prioridade.
- **Canary**: quando releases são frequentes e é preciso limitar o impacto de uma regressão sutil que só aparece com tráfego real.
- **Shadow**: quando o risco de um erro do modelo é muito alto (financeiro, saúde, segurança) e é preciso validar com dados reais antes de qualquer exposição.

### Não usar ❌
- Ambientes de prototipagem/POC sem tráfego real de produção significativo.
- Quando a equipe não tem observabilidade (Aula 11) suficiente para comparar as versões de forma confiável — sem métricas, nenhuma dessas estratégias funciona.
- Shadow Deployment quando o custo de processar 2x o tráfego é proibitivo e o risco do modelo é baixo (nesse caso, Canary já é suficiente).

> **Regra prática:** quanto maior o risco de um erro do modelo (financeiro, legal, de segurança), mais a estratégia deve se aproximar do Shadow Deployment antes de qualquer Canary com tráfego real exposto ao usuário.
