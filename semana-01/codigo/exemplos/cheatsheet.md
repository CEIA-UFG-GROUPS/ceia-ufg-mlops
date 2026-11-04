# Cheatsheet — Semana 01

Os comandos usados no lab, em uma página. Tudo roda em **bash** (WSL, Linux ou macOS).

---

## Navegação e arquivos

```bash
pwd                      # onde eu estou
ls -lah                  # listar: longo (-l), ocultos (-a), tamanhos legíveis (-h)
cd semana-01/codigo      # caminho relativo
cd ~/projetos            # ~ = seu home
cd -                     # volta para o diretório anterior
mkdir -p a/b/c           # cria a árvore toda, sem reclamar se já existir
cp origem destino        # copiar  (-r para diretórios)
mv origem destino        # mover / renomear
rm arquivo               # apagar  (-r para diretórios; NÃO vai para a lixeira)
find . -name "*.csv"     # procurar por nome, recursivo
du -sh .                 # tamanho total deste diretório
```

| Atalho | O que é |
| --- | --- |
| `.` | diretório atual |
| `..` | diretório pai |
| `~` | seu home (`/home/usuario`) |
| `/` | raiz do sistema |

---

## Ver conteúdo

```bash
cat arquivo.csv          # despeja o arquivo inteiro
head -n 5 arquivo.csv    # 5 primeiras linhas
tail -n 5 arquivo.csv    # 5 últimas linhas
tail -n +2 arquivo.csv   # tudo A PARTIR da linha 2 (pula o cabeçalho)
less arquivo.csv         # paginado; sai com q
wc -l arquivo.csv        # conta linhas
file arquivo.csv         # que tipo de arquivo é
```

---

## Permissões

```bash
ls -l script.sh          # -rw-r--r--  => dono lê/escreve, resto só lê
chmod +x script.sh       # torna executável
chmod 644 arquivo        # dono rw, grupo r, outros r
chmod 755 script.sh      # dono rwx, grupo rx, outros rx
chown usuario:grupo arq  # muda dono (precisa de sudo)
```

Leitura dos 9 bits: `rwx` do **dono**, `rwx` do **grupo**, `rwx` dos **outros**.
Em octal: `r=4`, `w=2`, `x=1` — então `rwx = 7`, `rw- = 6`, `r-x = 5`.

> `Permission denied` ao rodar `./script.sh` quase sempre é falta do bit `x`.

---

## Pipes e redirecionamento

```bash
comando > arquivo        # stdout SOBRESCREVE o arquivo
comando >> arquivo       # stdout ACRESCENTA ao arquivo
comando 2> erros.log     # stderr para um arquivo
comando > tudo.log 2>&1  # stdout e stderr para o mesmo lugar
comando < arquivo        # arquivo como stdin
comando1 | comando2      # stdout do primeiro vira stdin do segundo
comando | tee saida.txt  # mostra na tela E grava no arquivo
```

| Descritor | Nome | Número |
| --- | --- | --- |
| entrada | stdin | 0 |
| saída | stdout | 1 |
| erro | stderr | 2 |

---

## Ferramentas de texto

```bash
grep "positivo" reviews.csv            # linhas que contêm o padrão
grep -c "positivo" reviews.csv         # só a contagem
grep -v "^$" reviews.csv               # INVERTE: tudo que NÃO é linha vazia
grep -i "ótimo" reviews.csv            # ignora caixa
grep -n "erro" app.log                 # mostra o número da linha

cut -d, -f1 reviews.csv                # campo 1, separador vírgula
cut -d, -f2 reviews.csv                # campo 2 (o rótulo)

sort arquivo.txt                       # ordena
sort -u arquivo.txt                    # ordena e remove duplicatas
sort -rn                               # numérico (-n) e invertido (-r)
uniq -c                                # conta repetições (exige entrada ORDENADA)

sed 's/antigo/novo/'                   # substitui a 1ª ocorrência da linha
sed 's/antigo/novo/g'                  # substitui todas
sed '/^$/d'                            # apaga linhas vazias
sed 's/^[[:space:]]*//'                # apara espaços no início
sed 's/.*/\L&/'                        # tudo minúsculo (GNU sed, respeita acentos)

awk -F, '{ print $2 }'                 # campo 2, separador vírgula
awk -F, 'NF == 2'                      # só linhas com exatamente 2 campos
awk -F, '$2 == "positivo"'             # filtra por valor do campo
awk '{ n++ } END { print n }'          # conta linhas
awk -F, '{ c[$2]++ } END { for (k in c) print k, c[k] }'   # group by
```

**O idioma do shell:** um comando por tarefa, ligados por pipe.

```bash
tail -n +2 reviews.csv | cut -d, -f2 | sort | uniq -c | sort -rn
#     ^ pula header     ^ só o rótulo  ^ ordena ^ conta  ^ do maior
```

---

## Variáveis e scripting

```bash
#!/usr/bin/env bash                # shebang: quem executa este arquivo
set -euo pipefail                  # e: aborta no erro | u: var indefinida é erro
                                   # pipefail: erro em qualquer etapa do pipe conta

nome="dataset"                     # sem espaço ao redor do =
echo "$nome"                       # SEMPRE entre aspas duplas
echo "arquivo: ${nome}_v2.csv"     # chaves quando colar texto na variável
total=$(wc -l < arquivo.csv)       # captura a saída de um comando
contagem=$(( 10 - 4 ))             # aritmética

echo "$1" "$2"                     # argumentos posicionais
echo "$#"                          # quantidade de argumentos
echo "${1:-padrao}"                # valor padrão se $1 não existir
```

```bash
if [[ -f "$arquivo" ]]; then       # -f existe e é arquivo | -d diretório
  echo "achei"                     # -r legível | -w gravável | -x executável
elif [[ -z "$texto" ]]; then       # -z vazio | -n não vazio
  echo "vazio"
else
  echo "não achei"
fi

for arquivo in dados/*.csv; do
  echo "processando $arquivo"
done

while read -r linha; do
  echo "$linha"
done < arquivo.txt

minha_funcao() {
  local parametro="$1"             # `local` deixa a variável presa à função
  printf 'oi %s\n' "$parametro"
}
minha_funcao "mundo"

erro() { printf 'ERRO: %s\n' "$*" >&2; exit 1; }   # mensagem no stderr + exit != 0
```

| Ideia | Como se faz |
| --- | --- |
| Só continuar se der certo | `comando1 && comando2` |
| Rodar se falhar | `comando1 \|\| erro "deu ruim"` |
| Ver o código de saída | `echo $?` (0 = sucesso) |
| Checar sintaxe sem executar | `bash -n script.sh` |
| Ver o script executando linha a linha | `bash -x script.sh` |
| Diretório temporário com faxina | `TMP=$(mktemp -d); trap 'rm -rf "$TMP"' EXIT` |

---

## SSH

```bash
ssh-keygen -t ed25519 -C "seu@email"      # gera o par de chaves
cat ~/.ssh/id_ed25519.pub                 # a PÚBLICA — essa você compartilha
ssh usuario@servidor                      # conecta
ssh -i ~/.ssh/outra_chave usuario@host    # usa uma chave específica
scp arquivo.csv usuario@host:/caminho/    # copia para a máquina remota
rsync -avz pasta/ usuario@host:/destino/  # sincroniza (só o que mudou)
ssh -T git@github.com                     # testa a autenticação no GitHub
```

> A chave **privada** (`id_ed25519`, sem `.pub`) nunca sai da sua máquina e
> precisa de permissão `600`. `chmod 600 ~/.ssh/id_ed25519`.

---

## Git

```bash
git init                                   # cria o repositório
git clone git@github.com:user/repo.git     # clona via SSH
git status                                 # o que mudou
git diff                                   # o que mudou, linha a linha
git add arquivo                            # vai para a staging area
git add -p                                 # escolhe pedaço por pedaço
git commit -m "feat: mensagem clara"
git log --oneline --graph -10              # histórico resumido

git switch -c semana-01/meu-usuario        # cria e entra na branch
git switch main                            # volta para a main
git branch                                 # lista as branches
git push -u origin semana-01/meu-usuario   # primeiro push da branch
git push                                   # os próximos
git pull                                   # traz o que mudou no remoto

git restore arquivo                        # desfaz mudança não commitada
git restore --staged arquivo               # tira da staging, mantém a mudança
git rm --cached arquivo                    # para de rastrear (mantém no disco)
git check-ignore -v arquivo                # qual regra do .gitignore pegou isto
```

**Os três lugares onde um arquivo pode estar:**

```
working tree  --git add-->  staging area  --git commit-->  repositório
```

**`.gitignore` — o que entra e o que não entra:**

```gitignore
saida/              # dado gerado pelo script: reproduzível, fica fora
*.log
.env                # segredo: NUNCA
__pycache__/
```

> Se o arquivo já foi commitado, pôr no `.gitignore` não adianta — é preciso
> `git rm --cached` primeiro.

**Pull request pela CLI do GitHub:**

```bash
gh pr create --title "Semana 01 — preparação do dataset" --body "..."
gh pr list
gh pr view --web
```

---

## Quando travar

```bash
man grep                 # manual completo (sai com q)
grep --help              # resumo das flags
type comando             # é builtin, alias ou binário?
history | grep ssh       # o que eu digitei antes mesmo?
Ctrl+C                   # mata o comando atual
Ctrl+R                   # busca reversa no histórico
Ctrl+L                   # limpa a tela
```

E <https://explainshell.com/> para colar um comando inteiro e ver o que cada
pedaço faz.
