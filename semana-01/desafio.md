# Desafio — Semana 01: Script de preparação do dataset de sentimento

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Automatizar, em um único script bash, todo o preparo do dataset que será usado pelo resto do semestre.

---

## O que entregar

- `scripts/prepare_dataset.sh` idempotente (rodar duas vezes não quebra nem duplica dados)
- Saída em `data/` com split treino/teste e proporção documentada
- Seção no `README.md` explicando como rodar e quais variáveis de ambiente existem
- Pull request aberto a partir de uma branch própria

> **TODO (host):** detalhar formato, nomes de arquivo e qualquer restrição extra.

---

## Critérios de aceite

- [ ] O script roda do zero em uma máquina limpa, sem edição manual
- [ ] Usa `set -euo pipefail` e falha com mensagem clara quando algo dá errado
- [ ] Não commita os dados brutos no Git (use o `.gitignore`)
- [ ] Passa no ShellCheck sem erros
- [ ] O pull request tem descrição explicando a abordagem

> **TODO (host):** ajustar os critérios conforme o que foi efetivamente coberto no lab.

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-01/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 01 — <resumo em poucas palavras>`;
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
