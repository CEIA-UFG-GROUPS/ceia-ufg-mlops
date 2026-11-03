# Semana 11 — Demo Day

> **Encontro 12 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

Entrega integradora: cada pessoa (ou dupla) apresenta seu serviço de análise de sentimento indo de CI/CD a deploy no GCP, monitorado e testado sob carga.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Integrar tudo do semestre em um único projeto funcional
- Apresentar decisões técnicas e trade-offs com clareza
- Demonstrar o sistema ao vivo, do commit ao deploy
- Dar e receber peer review técnico de forma construtiva
- Fechar o semestre com um repositório que serve de portfólio

---

## Pré-requisitos

- Semanas 00 a 10 concluídas
- Serviço em produção no Cloud Run, com CI/CD, observabilidade e relatório de carga

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- Como apresentar um sistema técnico em 10 minutos
- O que um revisor procura em um projeto de ML em produção
- Retrospectiva: o que funcionou e o que muda no segundo semestre

### 💻 Mão na massa (~60 min)

- Apresentações individuais ou em dupla (aprox. 10 min + 5 min de perguntas)
- Demo ao vivo: commit -> CI -> deploy -> requisição -> dashboard
- Rodada de peer review final, usando a rubrica combinada
- Retrospectiva coletiva do semestre

### 🎯 Desafio (~15 min)

Sem desafio novo: a entrega é o próprio mini-projeto integrador apresentado no Demo Day.

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

- [Google SRE Workbook — Postmortem Culture](https://sre.google/workbook/postmortem-culture/)
- [Google SRE Book — Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)

> **TODO (host):** acrescentar os links específicos que você usar na condução.

---

## Notas para o host

- Cronometre com rigor: 12 apresentações estouram o horário com facilidade
- Divulgue a rubrica de avaliação pelo menos duas semanas antes
- Convide pessoas de fora do grupo (NLP, professores) para a plateia
- Reserve os últimos 20 minutos para a retrospectiva e o planejamento do segundo semestre

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [ ] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
