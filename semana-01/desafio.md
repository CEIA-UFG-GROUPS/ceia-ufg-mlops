# Desafio — Semana 01: Script de preparação do dataset de sentimento

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Escrever **o seu** `preparar_dataset.sh`: um script bash que pega um CSV bruto de
reviews e devolve um dataset de análise de sentimento pronto para treinar —
limpo, sem duplicatas, dividido em treino/teste e com as estatísticas na tela.

O ponto não é copiar o `codigo/preparar_dataset.sh` do lab. É escrever o seu, do
zero ou partindo do de referência, e **entender cada linha**. No PR você vai ter
que explicar as decisões.

---

## O que entregar

Dentro do seu repositório, em uma pasta `semana-01/` (ou equivalente):

| Arquivo | Requisito |
| --- | --- |
| `preparar_dataset.sh` | O script. Executável (`chmod +x`), com shebang e `set -euo pipefail` |
| `dados/reviews_brutos.csv` | O CSV de entrada (use o do lab ou monte o seu, com sujeira de propósito) |
| `.gitignore` | Ignorando o diretório de saída e qualquer artefato gerado |
| `README.md` | Como rodar, o que o script faz em cada etapa e a saída esperada |

### Contrato do script

```bash
./preparar_dataset.sh <csv_bruto> [diretorio_de_saida]
```

- **Entrada:** CSV com cabeçalho `texto,rotulo`, rótulos `positivo` e `negativo`
- **Saída:** `train.csv` e `test.csv` no diretório indicado (padrão à sua escolha,
  documentado no README), ambos com o mesmo cabeçalho da entrada
- **Na tela:** quantas linhas entraram, quantas foram descartadas e por quê, e a
  contagem por classe em cada arquivo gerado

### A limpeza, no mínimo

- Descartar o cabeçalho e linhas vazias (inclusive as que só têm espaços)
- Aparar espaços nas pontas de **cada campo**, não só da linha
- Normalizar a caixa do texto
- Descartar linhas malformadas: sem 2 campos, com texto vazio ou com rótulo fora
  de `positivo`/`negativo`
- Remover duplicatas — inclusive as que só são duplicatas **depois** de
  normalizar caixa e espaços

### O split

- Proporção treino/teste documentada (sugestão: 80/20)
- **Estratificado:** a proporção entre as classes se mantém nos dois arquivos
- **Determinístico:** rodar duas vezes gera exatamente os mesmos arquivos

---

## Critérios de aceite

Marque cada item depois de verificar com o comando indicado.

**O script roda**

- [ ] `bash -n preparar_dataset.sh` não aponta erro de sintaxe
- [ ] `ls -l preparar_dataset.sh` mostra o bit `x` e a primeira linha é um shebang
- [ ] `./preparar_dataset.sh dados/reviews_brutos.csv` roda do zero e gera `train.csv` e `test.csv`
- [ ] O script começa com `set -euo pipefail` (as três opções, não só o `-e`)

**Falha direito**

- [ ] Sem argumento: imprime o uso e sai com código `!= 0` (`./preparar_dataset.sh; echo $?`)
- [ ] Arquivo inexistente: mensagem clara, **sem** stack trace de comando interno
      (`./preparar_dataset.sh nao_existe.csv; echo $?`)
- [ ] As mensagens de erro vão para o **stderr** (`./preparar_dataset.sh 2>/dev/null` não mostra o erro)
- [ ] Não deixa arquivo pela metade nem lixo temporário quando falha no meio

**Dados limpos**

- [ ] `tail -n +2 saida/train.csv | cut -d, -f2 | sort -u` devolve só `positivo` e `negativo`
- [ ] `tail -n +2 saida/train.csv | sort | uniq -d` não devolve nada (zero duplicatas)
- [ ] Nenhuma linha vazia na saída (`grep -c "^[[:space:]]*$" saida/train.csv` devolve `0`)
- [ ] Nenhum texto com espaço sobrando colado na vírgula (`grep -c "[[:space:]]," saida/train.csv` devolve `0`)
- [ ] Nenhuma linha compartilhada entre treino e teste
      (`comm -12 <(sort saida/train.csv) <(sort saida/test.csv) | grep -v "^texto,rotulo$"` fica vazio)

**Split e reprodutibilidade**

- [ ] A proporção entre as classes é parecida no treino e no teste (estratificado)
- [ ] Rodar duas vezes seguidas gera arquivos idênticos
      (`md5sum saida/*.csv` antes e depois batem)
- [ ] As estatísticas impressas conferem com `wc -l` nos arquivos gerados

**Git**

- [ ] `git status` **não** lista `train.csv` nem `test.csv` como untracked
- [ ] `git check-ignore -v saida/train.csv` aponta a regra do `.gitignore` que pegou
- [ ] O CSV bruto **está** versionado (ele é a entrada, não a saída)
- [ ] O PR tem commits pequenos, com mensagem em PT-BR explicando o porquê
- [ ] O `README.md` permite que um colega rode sem te perguntar nada

**Bônus (não obrigatório)**

- [ ] Passa no [ShellCheck](https://www.shellcheck.net/) sem warnings (`shellcheck preparar_dataset.sh`)
- [ ] Tem `--help` / `-h`
- [ ] A proporção do split é configurável (por argumento ou variável de ambiente)
- [ ] Trata CSV com CRLF (arquivo salvo no Windows) sem quebrar
- [ ] Gera também um `estatisticas.txt` no diretório de saída, com o relatório
- [ ] Suporta mais de duas classes (ex.: `neutro`) sem mudar a lógica do split

---

## Evidências para o PR

Cole na descrição do pull request:

1. A saída **real** do seu script rodando sobre o CSV bruto (o bloco de limpeza e estatísticas)
2. `wc -l dados/reviews_brutos.csv saida/train.csv saida/test.csv`
3. O resultado dos três testes de falha: sem argumento, arquivo inexistente, arquivo vazio
4. `git status --short` mostrando que a saída está ignorada
5. Um parágrafo curto: qual foi a sujeira mais chata de tratar e como você resolveu

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado na Semana 00) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git switch -c semana-01/<seu-usuario>`.
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
- Nesta semana, o teste decisivo é literal: **faça `gh pr checkout <numero>` e rode o script do colega**,
  inclusive com um arquivo que não existe. Se quebrar feio ou se você não conseguir rodar seguindo
  só o README dele, isso é o review.
- Aprove apenas se você conseguiria rodar o projeto seguindo o README.
- Receber review também faz parte da entrega: responda aos comentários antes do encontro seguinte.
