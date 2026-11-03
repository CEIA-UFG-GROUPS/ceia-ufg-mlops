# Desafio — Semana 04: API containerizada + segundo serviço via Compose

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Rodar a API de sentimento inteiramente em container, junto de um segundo serviço, sem instalar nada além do Docker.

---

## O que entregar

- `Dockerfile` da API (preferencialmente multi-stage)
- `.dockerignore` coerente
- `docker-compose.yml` com a API e ao menos um segundo serviço (cache, banco ou worker)
- Instruções no `README.md` para subir tudo com um comando

> **TODO (host):** detalhar formato, nomes de arquivo e qualquer restrição extra.

---

## Critérios de aceite

- [ ] `docker compose up` sobe o ambiente completo
- [ ] A API responde em `/predict` a partir do container
- [ ] Os dois serviços se comunicam pelo nome do serviço, não por IP fixo
- [ ] A imagem final não carrega dependências de build desnecessárias

> **TODO (host):** ajustar os critérios conforme o que foi efetivamente coberto no lab.

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-04/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 04 — <resumo em poucas palavras>`;
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
