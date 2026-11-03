# Desafio — Semana 09: Dashboard + alerta funcionando

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Ter observabilidade suficiente para responder, em menos de um minuto, se o serviço está saudável.

---

## O que entregar

- API emitindo logs estruturados, com request id e latência
- Dashboard com latência (p50/p95), taxa de erro e volume de requisições
- Ao menos um alerta configurado, com destino definido (e-mail ou Discord)
- Evidência do alerta disparando (print do incidente ou da notificação)
- Seção no `README.md` explicando o que monitorar e o que fazer quando o alerta tocar

> **TODO (host):** detalhar formato, nomes de arquivo e qualquer restrição extra.

---

## Critérios de aceite

- [ ] Os logs são pesquisáveis por campo (e não apenas por texto livre)
- [ ] O dashboard mostra dados reais do serviço
- [ ] O alerta foi disparado ao menos uma vez e a notificação chegou
- [ ] Nenhum dado sensível do usuário aparece nos logs

> **TODO (host):** ajustar os critérios conforme o que foi efetivamente coberto no lab.

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-09/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 09 — <resumo em poucas palavras>`;
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
