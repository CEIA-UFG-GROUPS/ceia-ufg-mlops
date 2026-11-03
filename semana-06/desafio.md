# Desafio — Semana 06: Primeiro deploy manual no Cloud Run

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Colocar a API de sentimento no ar em uma URL pública do Cloud Run, usando a imagem já publicada no Artifact Registry.

---

## O que entregar

- URL pública do serviço no Cloud Run respondendo em `/health` e `/predict`
- Comando `gcloud run deploy` utilizado, documentado no `README.md`
- Service account dedicada ao serviço, com papéis mínimos
- Alerta de orçamento configurado no projeto

> **TODO (host):** detalhar formato, nomes de arquivo e qualquer restrição extra.

---

## Critérios de aceite

- [ ] A URL responde publicamente, com o contrato definido na Semana 03
- [ ] O deploy usa a imagem do Artifact Registry (e não um build local)
- [ ] O serviço não roda com a service account default do Compute
- [ ] O passo a passo está documentado o suficiente para outra pessoa repetir

> **TODO (host):** ajustar os critérios conforme o que foi efetivamente coberto no lab.

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-06/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 06 — <resumo em poucas palavras>`;
   - descrição do que foi feito, como rodar e o que ficou pendente;
   - evidências (prints, saída de terminal, links do serviço).
5. Poste o link do pull request no canal da semana no **Discord**.

---

## Peer review

- Revise o pull request de **pelo menos 1 colega** antes do próximo encontro.
- Comente de forma específica: aponte o trecho, explique o porquê e sugira uma alternativa.
- Procure por: critérios de aceite atendidos, clareza do README, segredos vazados e reprodutibilidade.
- Aprove apenas se você conseguiria rodar o projeto seguindo o README.
- Receber review também faz parte da entrega: responda aos comentários antes do encontro seguinte.
