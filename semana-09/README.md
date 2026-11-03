# Semana 09 — Logging & Monitoramento

> **Encontro 10 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

Enxergar o serviço em produção: logs estruturados, métricas de latência e erro, dashboards e alertas que avisam antes de o usuário reclamar.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Escrever logs estruturados (JSON) com nível e contexto adequados
- Explorar o Cloud Logging com filtros úteis
- Identificar as métricas que importam: latência, taxa de erro, tráfego e saturação
- Montar um dashboard no Cloud Monitoring
- Configurar um alerta que dispara de verdade

---

## Pré-requisitos

- Semana 08 concluída (serviço com ambientes e configuração)
- Serviço rodando no Cloud Run, com tráfego de teste

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- Os três pilares: logs, métricas e traces
- Logs estruturados vs `print`: por que JSON muda tudo na busca
- Os quatro sinais dourados (SRE) aplicados a uma API de modelo
- Métricas que o Cloud Run entrega de graça vs métricas customizadas
- Alerta bom e alerta ruim: acionabilidade e fadiga de alerta

### 💻 Mão na massa (~60 min)

- Trocar os `print` da API por logging estruturado com request id
- Buscar no Cloud Logging por erro, rota e latência
- Instrumentar latência e contagem de erros do `/predict`
- Montar um dashboard com latência p50/p95 e taxa de erro
- Criar um alerta de taxa de erro e provocá-lo intencionalmente
- (Opcional) Subir Prometheus + Grafana via Compose como alternativa local

### 🎯 Desafio (~15 min)

Dashboard com as métricas do serviço e ao menos um alerta funcionando, comprovado por um disparo real.

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

- [Cloud Logging — documentação](https://cloud.google.com/logging/docs)
- [Cloud Monitoring — alertas](https://cloud.google.com/monitoring/alerts)
- [Google SRE Book — Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Prometheus + Grafana (alternativa local)](https://prometheus.io/docs/visualization/grafana/)

> **TODO (host):** acrescentar os links específicos que você usar na condução.

---

## Notas para o host

- Gere tráfego sintético antes do encontro, senão os gráficos ficam vazios
- Disparar o alerta ao vivo é o momento mais didático da sessão
- Deixe claro que logar o texto do usuário pode ser um problema de privacidade
- A parte de Prometheus/Grafana é opcional — só faça se sobrar tempo

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [ ] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
