# Desafio — Semana 10: Relatório de carga do serviço

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Saber, com números, quanto o serviço aguenta e qual ambiente faz mais sentido para o caso de uso.

---

## O que entregar

- Script de carga versionado (locust ou k6)
- `relatorio-carga.md` com cenário, metodologia e resultados
- Tabela comparando Cloud Run e 4090 local (throughput, p95, erros, custo estimado)
- Gráficos ou prints do dashboard durante o teste
- Uma recomendação justificada ao final

> **TODO (host):** detalhar formato, nomes de arquivo e qualquer restrição extra.

---

## Critérios de aceite

- [ ] O cenário de teste está descrito o suficiente para ser reproduzido
- [ ] O relatório usa percentis, e não apenas média
- [ ] Identifica pelo menos um gargalo concreto
- [ ] A recomendação final é sustentada pelos dados apresentados

> **TODO (host):** ajustar os critérios conforme o que foi efetivamente coberto no lab.

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-10/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 10 — <resumo em poucas palavras>`;
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
