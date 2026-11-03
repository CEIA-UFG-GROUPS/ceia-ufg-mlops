# Desafio — Semana 08: Serviço parametrizado com secret gerenciado

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Rodar a mesma imagem em staging e prod, com toda configuração vindo do ambiente e os segredos vindo do Secret Manager.

---

## O que entregar

- Camada de configuração na aplicação (ex.: Pydantic Settings), sem valores hardcoded
- Ao menos um secret criado no Secret Manager e consumido pelo serviço
- Dois serviços no Cloud Run: `staging` e `prod`, com a mesma imagem
- `/health` verificando dependências reais
- `.env.example` documentando todas as variáveis (sem valores reais)

> **TODO (host):** detalhar formato, nomes de arquivo e qualquer restrição extra.

---

## Critérios de aceite

- [ ] Não existe credencial nem URL de ambiente hardcoded no código
- [ ] O secret é lido em runtime, não no build da imagem
- [ ] Staging e prod usam a mesma tag de imagem e configs distintas
- [ ] `/health` retorna erro se uma dependência essencial estiver fora

> **TODO (host):** ajustar os critérios conforme o que foi efetivamente coberto no lab.

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-08/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 08 — <resumo em poucas palavras>`;
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
