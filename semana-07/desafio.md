# Desafio — Semana 07: Deploy automático a cada push na main

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Fazer o caminho do commit até a produção acontecer sozinho, de forma confiável e reversível.

---

## O que entregar

- Workflow que builda, publica e faz deploy no Cloud Run ao merge na `main`
- Smoke test pós-deploy chamando `/health`
- Seção no `README.md` com o procedimento de rollback
- Link do serviço em produção e do run do workflow bem-sucedido

> **TODO (host):** detalhar formato, nomes de arquivo e qualquer restrição extra.

---

## Critérios de aceite

- [ ] Um push na `main` resulta em nova revisão no Cloud Run, sem ação manual
- [ ] O workflow falha (e não promove) se o smoke test não passar
- [ ] O rollback foi testado pelo menos uma vez
- [ ] Nenhuma credencial em texto plano no repositório

> **TODO (host):** ajustar os critérios conforme o que foi efetivamente coberto no lab.

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-07/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 07 — <resumo em poucas palavras>`;
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
