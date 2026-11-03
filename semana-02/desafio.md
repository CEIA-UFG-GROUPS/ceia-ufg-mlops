# Desafio — Semana 02: Servidor HTTP que serve o modelo

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Expor o modelo de sentimento por HTTP usando apenas a biblioteca padrão, entendendo cada peça antes de usar um framework.

---

## O que entregar

- `server.py` que sobe um servidor HTTP e responde com a classificação de um texto
- Instruções de execução no `README.md`, incluindo host e porta
- Exemplos de chamada com `curl` (caso de sucesso e caso de erro)
- Pull request com a descrição do que foi testado

> **TODO (host):** detalhar formato, nomes de arquivo e qualquer restrição extra.

---

## Critérios de aceite

- [ ] O servidor sobe com um único comando
- [ ] Responde corretamente a pelo menos um caminho de sucesso e um de erro
- [ ] É acessível a partir de outra máquina da mesma rede (ou do lab)
- [ ] O código não depende de framework web externo

> **TODO (host):** ajustar os critérios conforme o que foi efetivamente coberto no lab.

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-02/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 02 — <resumo em poucas palavras>`;
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
