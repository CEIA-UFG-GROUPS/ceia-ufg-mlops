# Semana 01 — Linux + Bash + Git

> **Encontro 2 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

A base de tudo que vem depois: viver no terminal, automatizar com bash e trabalhar em equipe com o fluxo de branch, commit e pull request.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Navegar e manipular arquivos no terminal com confiança
- Entender permissões (`chmod`, `chown`) e quando elas quebram um deploy
- Encadear `grep`, `sed`, `awk`, `cut`, `sort` e `uniq` com pipes para transformar um arquivo de dados
- Escrever um script bash com shebang, `set -euo pipefail`, argumentos, condicionais, loops e funções
- Conectar-se a máquinas remotas por SSH e mover arquivos (`scp`, `rsync`)
- Executar o fluxo completo de Git: branch, `.gitignore`, commit, push, pull request e review

---

## Pré-requisitos

- Semana 00 concluída (ambiente, SSH e GitHub funcionando)
- Acesso a um terminal **bash**: WSL, Linux ou macOS
  — no Windows, WSL ou Git Bash; PowerShell e `cmd` **não** rodam o lab
- `git`, `awk`, `sed`, `grep` e `curl` disponíveis (`for c in git awk sed grep curl; do command -v $c; done`)
- Repositório do grupo clonado e `ssh -T git@github.com` respondendo com o seu usuário

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- Filosofia Unix: programas pequenos, pipes e texto como interface
- Árvore de diretórios, caminhos absolutos vs relativos, variáveis de ambiente e `PATH`
- Permissões e usuários: por que `Permission denied` aparece tanto
- stdin, stdout, stderr: os três canos que todo comando tem
- SSH: chaves pública/privada, `authorized_keys` e `~/.ssh/config`
- Modelo mental do Git: working tree, staging area, commits e branches

### 💻 Mão na massa (~60 min)

- Tour pelo terminal: `ls`, `cd`, `find`, permissões e redirecionamentos
- Inspecionar um CSV sujo de reviews com `head`, `wc`, `cut`, `grep`, `sort` e `uniq`
- Montar a limpeza na mão, no pipe, antes de virar script: `sed`, `awk`, `sort -u`
- Escrever `preparar_dataset.sh` incrementalmente: shebang → `set -euo pipefail` → argumentos → validação → limpeza → split → estatísticas
- Versionar: branch, `.gitignore` para os dados gerados, commit, push e pull request

### 🎯 Desafio (~15 min)

Escrever o seu próprio script bash que prepara o dataset de sentimento (limpeza, split treino/teste e estatísticas) e entregá-lo via pull request.

Enunciado completo em [`desafio.md`](./desafio.md).

---

## Passo a passo

Todos os comandos rodam em **bash**, a partir de `semana-01/codigo/`.

> **Windows:** abra o **WSL** ou o **Git Bash**. Nada aqui funciona no PowerShell.
> Se o `chmod +x` não "pegar" (comum em pastas montadas do Windows, como `/mnt/c/...`),
> chame o script como `bash preparar_dataset.sh ...` em vez de `./preparar_dataset.sh ...`.

### Bloco 1 — o terminal e o arquivo sujo (~18 min)

1. **Chegar na pasta do lab e se situar.**

   ```bash
   cd semana-01/codigo
   pwd
   ls -la
   ```

   *Esperado:* o `pwd` termina em `semana-01/codigo` e o `ls -la` lista
   `dados/`, `exemplos/`, `preparar_dataset.sh`, `README.md` e o `.gitignore`
   (que só aparece por causa do `-a`). Repare na primeira coluna: `d` no começo
   é diretório, `-` é arquivo comum.

2. **Ler as permissões em voz alta.**

   ```bash
   ls -l preparar_dataset.sh dados/reviews_brutos.csv
   ```

   *Esperado:* algo como `-rw-r--r--`. Leia os 9 bits em três grupos — dono,
   grupo, outros. Não tem `x` em lugar nenhum, então o script **ainda não é
   executável**. Prove:

   ```bash
   ./preparar_dataset.sh
   ```

   *Esperado:* `bash: ./preparar_dataset.sh: Permission denied`. Esse é o erro
   número um de quem está começando. Conserte:

   ```bash
   chmod +x preparar_dataset.sh
   ls -l preparar_dataset.sh
   ```

   *Esperado:* agora `-rwxr-xr-x`. (`chmod 755` faz exatamente o mesmo: `7 = rwx`,
   `5 = r-x`.)

3. **Espiar o dataset bruto.**

   ```bash
   head -n 8 dados/reviews_brutos.csv
   wc -l dados/reviews_brutos.csv
   ```

   *Esperado:* o cabeçalho `texto,rotulo`, algumas linhas de review e **54**
   linhas no total (1 cabeçalho + 53 de dados). Já dá para ver uma linha em
   branco logo no começo.

4. **Separar as colunas e contar as classes — ingenuamente.**

   ```bash
   cut -d, -f2 dados/reviews_brutos.csv | sort | uniq -c | sort -rn
   ```

   *Esperado:* uma bagunça.

   ```
        23 negativo
        22 positivo
         4                              <- vazios (linhas em branco + um rótulo faltando)
         1 talvez
         1 rotulo                       <- o cabeçalho entrou na conta
         1 produto sem rótulo nenhum    <- linha sem vírgula: o cut devolveu tudo
         1  produto bom                 <- vírgula a mais: o campo 2 virou pedaço do texto
         1                              <- linha que só tem espaços
   ```

   Cada linha dessa saída é um problema diferente, e **nenhum** deles é visível
   em um `head`. Treinar um modelo com isso daria lixo. O lab de hoje é
   consertar, item por item.

   > Leia o pipe da esquerda para a direita: `cut` pega o 2º campo → `sort`
   > agrupa os iguais → `uniq -c` conta → `sort -rn` ordena do maior.
   > `uniq` só enxerga repetições **adjacentes**: sem o `sort` antes, ele não conta nada.

5. **Caçar as sujeiras uma a uma, com `grep`.**

   ```bash
   grep -c "^$" dados/reviews_brutos.csv               # linhas realmente vazias
   grep -c "^[[:space:]]*$" dados/reviews_brutos.csv   # vazias OU só com espaços
   grep -n "^[[:space:]]" dados/reviews_brutos.csv     # começam com espaço
   grep -n -i "BARULHO" dados/reviews_brutos.csv       # mesma frase, caixas diferentes
   awk -F, 'NF != 2 { print NR": ["$0"]" }' dados/reviews_brutos.csv   # campos errados
   ```

   *Esperado:* `3` e depois `4` — a diferença é a linha 37, que **parece** vazia
   mas tem três espaços. `grep -c "^$"` não a pega; é o tipo de sujeira que passa
   batido. Em seguida, as linhas 14, 30 e 37 começando com espaço; a mesma frase
   do "barulho insuportável" em duas caixas (duas linhas distintas para o
   computador, a mesma para você); e as 6 linhas em que `NF` (*number of fields*)
   é diferente de 2:

   ```
   6: []
   19: []
   25: [entrega rápida, produto bom,positivo]
   37: [   ]
   46: [produto sem rótulo nenhum]
   49: []
   ```

   ```bash
   grep -c "parou de funcionar depois de três dias" dados/reviews_brutos.csv
   ```

   *Esperado:* `2` — review duplicado.

> ✅ **checkpoint 1 — todo mundo chegou até aqui?**
> Todo mundo com o `preparar_dataset.sh` executável (`-rwxr-xr-x`) e já tendo
> visto a contagem bagunçada do passo 4.

### Bloco 2 — a limpeza no pipe, antes de virar script (~18 min)

A regra de ouro do bash: **monte o pipe na mão, veja funcionar, só depois salve
em um script.** Vamos construir a limpeza em camadas.

6. **Tirar o cabeçalho e as linhas vazias.**

   ```bash
   tail -n +2 dados/reviews_brutos.csv | sed '/^$/d' | wc -l
   ```

   *Esperado:* `50` (as 53 linhas de dados menos as 3 em branco). `tail -n +2`
   significa "a partir da linha 2" — é assim que se pula um cabeçalho.

7. **Aparar os espaços e sumir com a linha que só tem espaço.**

   ```bash
   tail -n +2 dados/reviews_brutos.csv \
     | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' \
     | sed '/^$/d' \
     | wc -l
   ```

   *Esperado:* `49`. A linha que continha só `   ` virou linha vazia depois do
   `sed` e caiu no filtro seguinte. Ordem importa: aparar **antes** de remover vazias.

   > A barra invertida no fim da linha quebra um comando longo em várias linhas.
   > Não pode ter nada depois dela — nem um espaço.

8. **Normalizar a caixa.**

   ```bash
   tail -n +2 dados/reviews_brutos.csv \
     | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' \
     | sed '/^$/d' \
     | sed 's/.*/\L&/' \
     | grep -n "barulho insuport"
   ```

   *Esperado:* as **duas** linhas do "barulho insuportável" agora idênticas. O
   `\L&` é do GNU sed: `&` é "tudo que casou" e `\L` manda para minúsculo —
   respeitando acentos, coisa que `tr 'A-Z' 'a-z'` não faz em UTF-8.

9. **Validar a estrutura com `awk`.**

   ```bash
   tail -n +2 dados/reviews_brutos.csv \
     | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' \
     | sed '/^$/d' \
     | sed 's/.*/\L&/' \
     | awk -F, -v OFS=, '
         NF != 2 { next }
         {
           texto = $1; rotulo = $2
           gsub(/^[[:space:]]+|[[:space:]]+$/, "", texto)
           gsub(/^[[:space:]]+|[[:space:]]+$/, "", rotulo)
           if (texto == "") next
           if (rotulo != "positivo" && rotulo != "negativo") next
           print texto, rotulo
         }' \
     | wc -l
   ```

   *Esperado:* `45`. Saíram 4 linhas malformadas: a de 3 campos
   (`entrega rápida, produto bom,positivo`), a de rótulo vazio, a de rótulo
   `talvez` e a que não tinha vírgula.

   Note o `gsub` nos **campos**: o `sed` do passo 7 aparou a *linha*, mas
   `texto   ,negativo` ainda tinha espaço colado na vírgula. Aparar linha e
   aparar campo são coisas diferentes.

10. **Deduplicar e conferir o resultado.**

    Repita o pipe do passo 9 trocando o `wc -l` final por `sort -u | wc -l`.

    *Esperado:* `40`. Caíram 5 duplicatas — incluindo as que só eram duplicatas
    **depois** de normalizar caixa e espaços. Agora a contagem por classe:

    ```bash
    # (mesmo pipe) ... | sort -u | cut -d, -f2 | sort | uniq -c
    ```

    *Esperado:*

    ```
         20 negativo
         20 positivo
    ```

    Compare com a bagunça do passo 4. **Essa** é a diferença que o pipe fez.

> ✅ **checkpoint 2 — todo mundo chegou até aqui?**
> Todo mundo com 40 linhas limpas, 20 de cada classe.
> Quem se perdeu no pipe pode seguir a partir do script pronto no próximo bloco.

### Bloco 3 — virar script (~16 min)

11. **Criar o esqueleto.** Em um arquivo novo, `meu_preparar.sh`:

    ```bash
    #!/usr/bin/env bash
    set -euo pipefail

    printf 'oi — %s argumento(s), o primeiro é: %s\n' "$#" "${1:-nenhum}"
    ```

    ```bash
    chmod +x meu_preparar.sh
    ./meu_preparar.sh dados/reviews_brutos.csv
    bash -n meu_preparar.sh && echo "sintaxe ok"
    ```

    *Esperado:* a mensagem com o caminho do CSV, e `sintaxe ok`. As duas linhas
    do topo valem o lab inteiro:

    | Linha | Para que serve |
    | --- | --- |
    | `#!/usr/bin/env bash` | shebang: diz ao sistema quem executa este arquivo |
    | `set -e` | aborta no primeiro comando que falhar |
    | `set -u` | aborta ao usar variável não definida (pega typo de nome) |
    | `set -o pipefail` | um pipe falha se **qualquer** etapa falhar, não só a última |

12. **Ver o `set -euo pipefail` trabalhando.** Acrescente no fim do script:

    ```bash
    cat arquivo_que_nao_existe.txt | wc -l
    echo "cheguei no fim"
    ```

    ```bash
    ./meu_preparar.sh dados/reviews_brutos.csv; echo "código de saída: $?"
    ```

    *Esperado:* a mensagem de erro do `cat`, **nenhum** `cheguei no fim` e
    `código de saída: 1`. Agora comente a linha `set -euo pipefail` e rode de
    novo: aparece `0` e o `cheguei no fim`, como se nada tivesse dado errado —
    exatamente o pesadelo de pipeline que falha em silêncio. Descomente e apague
    as duas linhas de teste.

13. **Validar os argumentos antes de qualquer coisa.**

    ```bash
    uso() {
      printf 'Uso: %s <csv_bruto> [diretorio_de_saida]\n' "$0"
    }

    erro() {
      printf 'ERRO: %s\n' "$*" >&2      # >&2 manda para o stderr
      exit 1
    }

    if [[ $# -lt 1 || $# -gt 2 ]]; then
      uso >&2
      erro "esperava 1 ou 2 argumentos, recebi $#"
    fi

    ENTRADA="$1"
    SAIDA="${2:-saida}"                 # ${VAR:-padrao} = valor padrão

    [[ -f "$ENTRADA" ]] || erro "arquivo não encontrado: $ENTRADA"
    [[ -r "$ENTRADA" ]] || erro "sem permissão de leitura: $ENTRADA"
    [[ -s "$ENTRADA" ]] || erro "arquivo vazio: $ENTRADA"
    ```

    Teste os caminhos de erro — um script só é confiável quando falha direito:

    ```bash
    ./meu_preparar.sh;                      echo "saída: $?"
    ./meu_preparar.sh nao_existe.csv;       echo "saída: $?"
    ./meu_preparar.sh dados/reviews_brutos.csv; echo "saída: $?"
    ```

    *Esperado:* `1`, `1`, `0`. E as mensagens de erro no **stderr** — prove
    jogando só o stdout fora: `./meu_preparar.sh 2>/dev/null` não mostra nada;
    `./meu_preparar.sh 2>&1 >/dev/null` mostra só os erros.

14. **Colar a limpeza do bloco 2 dentro do script** e gravar o resultado em um
    arquivo temporário, usando `mktemp` + `trap` para a faxina:

    ```bash
    TMP="$(mktemp -d)"
    trap 'rm -rf "$TMP"' EXIT        # roda a faxina mesmo se o script morrer

    tail -n +2 "$ENTRADA" | tr -d '\r' > "$TMP/01.csv"
    # ... os sed/awk/sort -u dos passos 7 a 10, cada um gravando um arquivo ...
    ```

    O `tr -d '\r'` é novo: ele remove o `\r` que o Windows deixa no fim de cada
    linha (CRLF). Sem ele, o rótulo vira `positivo\r` e **nenhuma** comparação
    com `"positivo"` bate — bug clássico, e invisível no `cat`.

15. **Fazer o split estratificado.**

    ```bash
    printf 'texto,rotulo\n' > "$SAIDA/train.csv"
    printf 'texto,rotulo\n' > "$SAIDA/test.csv"

    awk -F, -v treino="$SAIDA/train.csv" -v teste="$SAIDA/test.csv" '
      { n[$2]++ }                                  # conta por classe
      n[$2] % 5 == 0 { print >> teste;  next }     # 1 a cada 5 vai para o teste
                     { print >> treino }
    ' "$TMP/05_unicas.csv"
    ```

    *Esperado:* 32 linhas em `train.csv` e 8 em `test.csv` (sem contar o
    cabeçalho). **Estratificado** quer dizer que a proporção entre as classes se
    mantém nos dois arquivos — por isso o contador `n[$2]` é por rótulo, e não
    global. Com um `NR % 5` global, o acaso poderia mandar só negativos para o teste.

16. **Imprimir as estatísticas e comparar com a referência.**

    ```bash
    for arquivo in "$SAIDA/train.csv" "$SAIDA/test.csv"; do
      echo "$arquivo: $(( $(wc -l < "$arquivo") - 1 )) linhas"
      tail -n +2 "$arquivo" | cut -d, -f2 | sort | uniq -c
    done
    ```

    Agora rode o script de referência e compare:

    ```bash
    ./preparar_dataset.sh dados/reviews_brutos.csv
    ```

    *Esperado:*

    ```
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
    ```

    Rode duas vezes seguidas e compare: o resultado é **idêntico**. O script fixa
    `LC_COLLATE=C` justamente para o `sort` não mudar de ordem conforme o locale
    da máquina — reprodutibilidade começa aqui.

> ✅ **checkpoint 3 — todo mundo chegou até aqui?**
> Todo mundo com `saida/train.csv` (32 linhas) e `saida/test.csv` (8 linhas).

### Bloco 4 — versionar e abrir o pull request (~16 min)

17. **Ver o estrago que o `git status` mostra.**

    ```bash
    cd ../..          # volta para a raiz do repositório
    git status
    ```

    *Esperado:* os arquivos novos do lab aparecendo como *untracked* —
    **incluindo** `semana-01/codigo/saida/`. Esse diretório é dado gerado: ele
    sai do CSV bruto + o script, em segundos. Commitá-lo é poluir o histórico
    com algo reprodutível. Fora.

18. **Conferir o `.gitignore`.**

    O arquivo [`semana-01/codigo/.gitignore`](./codigo/.gitignore) já ignora
    `saida/`. Prove que a regra está pegando:

    ```bash
    git check-ignore -v semana-01/codigo/saida/train.csv
    git status --short semana-01/
    ```

    *Esperado:* o `check-ignore` aponta a linha exata do `.gitignore` que casou,
    e o `status` não lista mais nada dentro de `saida/`.

    > **A pegadinha:** `.gitignore` só vale para arquivo **ainda não rastreado**.
    > Se você já commitou o CSV gerado, a regra não desfaz nada — é preciso
    > `git rm --cached semana-01/codigo/saida/train.csv` primeiro.

19. **Criar a branch da semana.**

    ```bash
    git switch -c semana-01/<seu-usuario>
    git branch
    ```

    *Esperado:* o `*` do `git branch` na branch nova. Trabalhar direto na `main`
    é o que o pull request existe para evitar.

20. **Commitar em pedaços, com mensagem que explica o porquê.**

    ```bash
    git add semana-01/codigo/preparar_dataset.sh semana-01/codigo/.gitignore
    git status --short
    git commit -m "feat(semana-01): script de preparação do dataset de sentimento"
    git log --oneline -3
    ```

    *Esperado:* no `status --short`, só os dois arquivos em verde (staged). Use
    `git diff` (não staged) e `git diff --staged` (staged) para ver o que está
    em cada lugar antes de confirmar.

21. **Publicar a branch.**

    ```bash
    git push -u origin semana-01/<seu-usuario>
    ```

    *Esperado:* o Git imprime um link de "create a pull request". O `-u` liga a
    branch local à remota — nos próximos pushes, `git push` sozinho basta.

22. **Abrir o pull request.** Pelo link que o `push` imprimiu, ou pela CLI:

    ```bash
    gh pr create --fill --base main
    gh pr view --web
    ```

    Na descrição, cole a **saída real** do seu script (o bloco de estatísticas).
    Evidência vale mais que "funcionou aqui".

23. **Revisar o PR de um colega.** Pegue um PR aberto no canal da semana e, de
    verdade, rode:

    ```bash
    gh pr checkout <numero>
    bash -n semana-01/codigo/preparar_dataset.sh
    ./semana-01/codigo/preparar_dataset.sh semana-01/codigo/dados/reviews_brutos.csv
    ./semana-01/codigo/preparar_dataset.sh arquivo_inexistente.csv; echo "saída: $?"
    ```

    Comente apontando o trecho, o porquê e uma alternativa. "Dica: `${2:-saida}`
    evita o `if` do bloco 13" vale mais que "LGTM".

> ✅ **checkpoint 4 — todo mundo chegou até aqui?**
> Todo mundo com um pull request aberto e o link postado no Discord.

24. **Limpeza.** Apague os rascunhos do lab (o `saida/` pode ficar: ele está
    ignorado).

    ```bash
    rm -f semana-01/codigo/meu_preparar.sh
    git status --short
    ```

    *Esperado:* nada de inesperado sobrando.

---

## Código

O código de apoio desta semana vive em [`codigo/`](./codigo/) — veja
[`codigo/README.md`](./codigo/README.md) para rodar em um comando.

| Arquivo | O que é |
| --- | --- |
| [`codigo/dados/reviews_brutos.csv`](./codigo/dados/reviews_brutos.csv) | Mini-dataset PT-BR `texto,rotulo`, sujo de propósito (53 linhas) |
| [`codigo/preparar_dataset.sh`](./codigo/preparar_dataset.sh) | Script de referência: valida, limpa, divide treino/teste e imprime estatísticas |
| [`codigo/.gitignore`](./codigo/.gitignore) | Mantém `saida/` fora do Git — dado gerado não se commita |
| [`codigo/exemplos/cheatsheet.md`](./codigo/exemplos/cheatsheet.md) | Todos os comandos do lab em uma página, para consulta rápida |
| [`codigo/README.md`](./codigo/README.md) | Como rodar e a saída esperada |

---

## Recursos e links

- [The Missing Semester of Your CS Education — MIT](https://missing.csail.mit.edu/)
- [GNU Bash Reference Manual](https://www.gnu.org/software/bash/manual/bash.html)
- [Bash Guide for Beginners (TLDP)](https://tldp.org/LDP/Bash-Beginners-Guide/html/)
- [ShellCheck — linter para scripts bash](https://www.shellcheck.net/)
- [explainshell — explica qualquer comando](https://explainshell.com/)
- [Pro Git (livro completo, em português)](https://git-scm.com/book/pt-br/v2)
- [GitHub Docs — Conectar ao GitHub com SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [OpenSSH — manual pages](https://www.openssh.org/manual.html)
- [roadmap.sh — Linux](https://roadmap.sh/linux)
- [GNU Awk User's Guide](https://www.gnu.org/software/gawk/manual/gawk.html)

---

## Notas para o host

- **Material de referência do grupo anterior:** `presentation/primeiro-semestre/aula01` na branch `main` (pode ser reaproveitado)
- O dataset do lab é deliberadamente minúsculo e local: **nada de download durante o encontro**. A rede do lab não é confiável e o assunto do dia é bash, não `curl`
- O passo 12 (`set -euo pipefail` ligado vs desligado) é o momento didático mais importante do dia. É o que separa "script que roda" de "script que você deixa no CI". Não pule
- O passo 4 (contagem bagunçada) e o passo 10 (contagem limpa) são o antes/depois do lab. Deixe os dois na tela lado a lado se der
- Monte o pipe **na mão** junto com a turma antes de abrir o script pronto. Quem vê o script de uma vez só não aprende a construí-lo
- Reserve os 16 minutos finais inteiros para o bloco de Git; é onde as dúvidas realmente aparecem (branch errada, `.gitignore` que não pega, push rejeitado)
- O `\L` do `sed` é extensão GNU. Em macOS (BSD sed) ele não existe — se tiver gente de Mac, o plano B é `awk '{print tolower($0)}'` com `gawk` instalado via Homebrew
- Quem já domina bash pode fazer par com quem está começando, ou atacar os bônus do desafio (ShellCheck, `--help`, proporção configurável)
- Plano B para quem travar no setup: rodar o lab pelo [Play with Docker](https://labs.play-with-docker.com/) ou no GitHub Codespaces do repositório

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [x] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Conferir que todo mundo tem terminal bash funcionando (WSL no Windows) **antes** do encontro
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
