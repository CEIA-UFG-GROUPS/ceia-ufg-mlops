# Semana 10 — Load testing & performance

> **Encontro 11 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

Descobrir onde o serviço quebra antes que ele quebre sozinho: locust/k6, métricas de throughput e latência, e a comparação entre a 4090 local e o Cloud Run.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Projetar um teste de carga realista para a API de sentimento
- Usar locust ou k6 para gerar carga e coletar métricas
- Interpretar throughput, latência (p50/p95/p99) e taxa de erro sob carga
- Identificar gargalos (CPU, GPU, I/O, cold start, concorrência)
- Comparar custo e desempenho entre a 4090 local e o Cloud Run

---

## Pré-requisitos

- Semana 09 concluída (métricas e dashboard disponíveis)
- Serviço no Cloud Run e uma versão rodando na máquina 4090

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- Tipos de teste: smoke, load, stress, soak e spike
- Por que a média mente: percentis e distribuição de latência
- Concorrência, filas e a Lei de Little em termos práticos
- Cold start e autoscaling do Cloud Run
- Custo por requisição: serverless vs máquina dedicada com GPU

### 💻 Mão na massa (~60 min)

- Escrever um cenário de carga em locust (ou k6) chamando `/predict`
- Rodar um smoke test e depois aumentar a carga em degraus
- Observar as métricas da Semana 09 durante o teste
- Repetir o mesmo cenário contra a 4090 local
- Ajustar concorrência e recursos do Cloud Run e medir o efeito

### 🎯 Desafio (~15 min)

Produzir um relatório de carga do serviço, comparando Cloud Run e 4090 local com dados e uma recomendação.

Enunciado completo em [`desafio.md`](./desafio.md).

---

## Passo a passo

> **TODO (host):** detalhar aqui o passo a passo do lab, na ordem em que ele será conduzido.
> Sugestão de formato: um passo numerado por ação, com o comando exato e o resultado esperado.
>
> 1. `> TODO` — passo 1
> 2. `> TODO` — passo 2
> 3. `> TODO` — passo 3
>
> Marque os pontos de checkpoint (`checkpoint: todo mundo chegou até aqui?`) a cada 15-20 minutos.

---

## Código

O código de apoio desta semana vive em [`codigo/`](./codigo/).

> **TODO (host):** incluir ali os arquivos de apoio (scripts, configs, exemplos) usados no lab,
> junto de um `README.md` curto dentro de `codigo/` explicando como executá-los.

---

## Recursos e links

- [Locust — documentação](https://docs.locust.io/)
- [k6 — documentação](https://grafana.com/docs/k6/latest/)
- [Cloud Run — dicas de performance](https://cloud.google.com/run/docs/tips/general)
- [Latency numbers every programmer should know](https://colin-scott.github.io/personal_website/research/interactive_latency.html)

> **TODO (host):** acrescentar os links específicos que você usar na condução.

---

## Notas para o host

- Avise a turma para não apontar carga para o serviço de um colega sem combinar antes
- Cuidado com custo: carga alta no Cloud Run consome crédito rápido — defina um teto
- Padronize o cenário de teste para que os relatórios sejam comparáveis
- Tenha os resultados de uma rodada prévia prontos, caso a rede do lab atrapalhe

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [ ] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
