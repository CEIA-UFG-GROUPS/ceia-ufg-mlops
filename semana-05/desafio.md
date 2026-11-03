# Desafio — Semana 05: CI verde + imagem no Artifact Registry

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Garantir que nenhum código entre na `main` sem passar nos testes, e que cada merge gere uma imagem rastreável no registry.

---

## O que entregar

- `.github/workflows/ci.yml` rodando testes e lint em cada pull request
- Workflow (ou job) que builda e publica a imagem no Artifact Registry no merge
- Badge do CI no `README.md`
- Print ou link da imagem publicada, com a tag do commit

> **TODO (host):** detalhar formato, nomes de arquivo e qualquer restrição extra.

---

## Critérios de aceite

- [ ] O CI roda automaticamente ao abrir um pull request
- [ ] O pipeline falha quando um teste quebra
- [ ] A imagem aparece no Artifact Registry com tag rastreável até o commit
- [ ] Nenhuma credencial foi commitada no repositório

> **TODO (host):** ajustar os critérios conforme o que foi efetivamente coberto no lab.

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-05/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 05 — <resumo em poucas palavras>`;
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
