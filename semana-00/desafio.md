# Desafio — Semana 00: Repositório pessoal + hello world

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Garantir que cada pessoa tem um repositório próprio do projeto do semestre e consegue executar código tanto no ambiente local quanto na máquina 4090 do lab.

---

## O que entregar

- Repositório pessoal criado no GitHub (público ou com acesso para o grupo)
- `README.md` com nome, ambiente usado e versões (Python, Docker, driver da GPU)
- Um `hello_world.py` que imprime a versão do Python e se há GPU disponível
- Print ou saída de terminal do `hello_world.py` rodando na máquina do lab

> **TODO (host):** detalhar formato, nomes de arquivo e qualquer restrição extra.

---

## Critérios de aceite

- [ ] O repositório existe e o link foi postado no Discord
- [ ] O script roda sem erro no ambiente local
- [ ] O script roda sem erro na máquina 4090 e detecta a GPU
- [ ] O pull request foi aberto a partir de uma branch (não direto na `main`)

> **TODO (host):** ajustar os critérios conforme o que foi efetivamente coberto no lab.

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-00/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 00 — <resumo em poucas palavras>`;
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
