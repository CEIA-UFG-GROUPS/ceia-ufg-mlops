# Código — Semana 01 (Linux + Bash + Git)

Script bash que transforma um CSV bruto de reviews em um dataset de análise de
sentimento pronto para treinar: limpo, sem duplicatas e dividido em treino/teste.

```
codigo/
├── dados/
│   └── reviews_brutos.csv   # mini-dataset PT-BR, sujo de propósito
├── exemplos/
│   └── cheatsheet.md        # os comandos do lab em uma página
├── preparar_dataset.sh      # o script de referência
├── .gitignore               # ignora saida/ — dado gerado não se commita
└── saida/                   # criado na execução (train.csv + test.csv)
```

> O `saida/` **não** está no Git de propósito: ele é reproduzível a partir de
> `dados/reviews_brutos.csv` + o script. Esse é o combinado da semana.

---

## Rodar

A partir desta pasta (`semana-01/codigo/`), em **bash** (WSL, Linux ou macOS):

```bash
chmod +x preparar_dataset.sh
./preparar_dataset.sh dados/reviews_brutos.csv
```

Para escolher outro diretório de saída:

```bash
./preparar_dataset.sh dados/reviews_brutos.csv /tmp/dataset
```

Ajuda:

```bash
./preparar_dataset.sh --help
```

> **Windows:** rode pelo **WSL** ou pelo **Git Bash**. PowerShell e `cmd` não
> executam bash. Se o `chmod +x` não "pegar" (acontece em pastas montadas do
> Windows), chame o script como `bash preparar_dataset.sh dados/reviews_brutos.csv`.

---

## Saída esperada

```
==> entrada : dados/reviews_brutos.csv
==> saída   : saida/

Limpeza
  linhas no bruto               53
  - vazias/em branco             4
  - malformadas                  4
  - duplicadas                   5
  = linhas limpas               40

Split (1 a cada 5 de cada classe vai para o teste)
  train.csv   32 linhas
    positivo   16  (50.0%)
    negativo   16  (50.0%)
  test.csv     8 linhas
    positivo    4  (50.0%)
    negativo    4  (50.0%)

Pronto. Arquivos gerados:
  397  saida/test.csv
  1.7K  saida/train.csv
```

O resultado é **determinístico**: rodar duas vezes gera exatamente os mesmos
arquivos (o script fixa `LC_COLLATE=C` para a ordenação não depender do locale).

---

## O que o script faz, em ordem

| Passo | Ferramenta | O que resolve |
| --- | --- | --- |
| Tira cabeçalho e `\r` | `tail -n +2`, `tr -d '\r'` | CSV salvo no Windows (CRLF) |
| Apara espaços e remove linhas vazias | `sed` | `   ` e linhas em branco no meio do arquivo |
| Normaliza a caixa | `sed 's/.*/\L&/'` | `Produto Bom` e `produto bom` viram a mesma linha |
| Valida estrutura | `awk -F,` | descarta linha sem 2 campos, texto vazio ou rótulo fora de `positivo`/`negativo` |
| Remove duplicatas | `sort -u` | o mesmo review repetido no dump |
| Split estratificado | `awk` | 1 a cada 5 **de cada classe** vai para o teste |
| Estatísticas | `cut`, `sort`, `uniq -c` | o "group by" do shell |

---

## O dataset bruto

`dados/reviews_brutos.csv` tem 53 linhas de dados no formato `texto,rotulo`
(rótulos: `positivo` e `negativo`) e foi sujado de propósito:

- linhas em branco e uma linha só com espaços;
- espaços sobrando antes/depois do texto;
- o mesmo review repetido, e repetido com caixa diferente (`BARULHO INSUPORTÁVEL…`);
- uma linha com vírgula a mais (`entrega rápida, produto bom,positivo`);
- uma linha com rótulo vazio e uma com rótulo inválido (`talvez`);
- uma linha sem vírgula nenhuma.

Depois da limpeza sobram **40 reviews únicos**, 20 de cada classe.

> **Simplificação consciente:** o texto dos reviews não contém vírgulas, o que
> permite usar `cut -d,` e `awk -F,` sem um parser de CSV de verdade. CSV com
> campos entre aspas é outro problema — e é por isso que, da Semana 03 em diante,
> esse tipo de coisa passa a ser feito em Python.
