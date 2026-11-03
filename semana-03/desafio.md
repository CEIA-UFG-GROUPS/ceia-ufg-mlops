# Desafio — Semana 03: Endpoint /predict de análise de sentimento

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Entregar uma API funcional que classifica o sentimento de um texto, com contrato JSON claro e tratamento de erro adequado.

---

## O que entregar

- Endpoint `POST /predict` recebendo `{"text": "..."}` e devolvendo rótulo e score
- Endpoint `GET /health` retornando o status do serviço
- `requirements.txt` ou `pyproject.toml` com as dependências fixadas
- Pelo menos um teste automatizado (pytest) cobrindo sucesso e erro de validação

> **TODO (host):** detalhar formato, nomes de arquivo e qualquer restrição extra.

---

## Critérios de aceite

- [ ] A API sobe localmente com um comando documentado
- [ ] `/predict` retorna 200 com resposta válida e 422 para payload inválido
- [ ] `/health` retorna 200
- [ ] Os testes passam com `pytest`
- [ ] A documentação em `/docs` reflete o contrato real

> **TODO (host):** ajustar os critérios conforme o que foi efetivamente coberto no lab.

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-03/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 03 — <resumo em poucas palavras>`;
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
