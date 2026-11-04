#!/usr/bin/env bash
#
# preparar_dataset.sh — prepara o dataset de análise de sentimento da Semana 01.
#
# Lê um CSV bruto no formato `texto,rotulo`, limpa as sujeiras típicas de um
# dump de produção (linhas vazias, espaços sobrando, caixa inconsistente,
# duplicatas, linhas malformadas), divide em treino/teste de forma
# estratificada e imprime as estatísticas do resultado.
#
# Uso:
#   ./preparar_dataset.sh dados/reviews_brutos.csv [diretorio_de_saida]
#
# Grupo de estudos MLOps/DevOps — CEIA/UFG
# ---------------------------------------------------------------------------

# `set -e`          : aborta no primeiro comando que falhar
# `set -u`          : aborta ao usar variável não definida (pega typo de nome)
# `set -o pipefail` : um pipe falha se QUALQUER etapa dele falhar, não só a última
set -euo pipefail

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

# Proporção do split: 1 a cada N linhas de CADA classe vai para o teste.
# 5 => 20% teste / 80% treino.
readonly A_CADA=5

# `sort` muda de resultado conforme o locale. Fixar a ordenação (LC_COLLATE) em C
# deixa o resultado determinístico: o mesmo CSV sempre gera o mesmo train/test.
# Atenção: fixamos só a ORDENAÇÃO. Fixar `LC_ALL=C` também trocaria o LC_CTYPE e
# quebraria o tratamento de acentos em UTF-8 no passo 2.3.
export LC_COLLATE=C

# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

uso() {
  cat <<'FIM'
Uso: ./preparar_dataset.sh <csv_bruto> [diretorio_de_saida]

  <csv_bruto>            CSV com cabeçalho `texto,rotulo`
  [diretorio_de_saida]   onde gravar train.csv e test.csv (padrão: ./saida)

Exemplo:
  ./preparar_dataset.sh dados/reviews_brutos.csv
  ./preparar_dataset.sh dados/reviews_brutos.csv /tmp/dataset
FIM
}

# Mensagem de erro vai para o stderr (>&2) e encerra com código != 0.
# Isso é o que permite `./preparar_dataset.sh ... || echo "falhou"` funcionar.
erro() {
  printf 'ERRO: %s\n' "$*" >&2
  exit 1
}

# Conta as linhas de um arquivo (0 se ele não existir).
contar() {
  wc -l < "$1" | tr -d ' '
}

# Imprime a distribuição de classes de um CSV com cabeçalho.
estatisticas() {
  local arquivo="$1"
  local total
  total=$(( $(contar "$arquivo") - 1 ))

  printf '  %-10s %3d linhas\n' "$(basename "$arquivo")" "$total"

  # tail -n +2  => pula o cabeçalho
  # cut -d, -f2 => pega só a coluna do rótulo
  # sort | uniq -c => o "group by" do shell
  tail -n +2 "$arquivo" \
    | cut -d, -f2 \
    | sort \
    | uniq -c \
    | sort -rn \
    | while read -r quantidade rotulo; do
        printf '    %-9s %3d  (%s%%)\n' \
          "$rotulo" "$quantidade" \
          "$(awk -v q="$quantidade" -v t="$total" 'BEGIN { printf "%.1f", (t > 0 ? 100 * q / t : 0) }')"
      done
}

# ---------------------------------------------------------------------------
# 1. Argumentos e validação
# ---------------------------------------------------------------------------

# `${1:-}` evita que o `set -u` exploda quando o script roda sem argumento.
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  uso
  exit 0
fi

if [[ $# -lt 1 || $# -gt 2 ]]; then
  uso >&2
  erro "esperava 1 ou 2 argumentos, recebi $#"
fi

ENTRADA="$1"
SAIDA="${2:-saida}"

[[ -e "$ENTRADA" ]] || erro "arquivo não encontrado: $ENTRADA"
[[ -f "$ENTRADA" ]] || erro "não é um arquivo regular: $ENTRADA"
[[ -r "$ENTRADA" ]] || erro "sem permissão de leitura: $ENTRADA (tente: chmod +r '$ENTRADA')"
[[ -s "$ENTRADA" ]] || erro "arquivo vazio: $ENTRADA"

mkdir -p "$SAIDA"
[[ -w "$SAIDA" ]] || erro "sem permissão de escrita em: $SAIDA"

TREINO="$SAIDA/train.csv"
TESTE="$SAIDA/test.csv"

# Diretório temporário para os passos intermediários da limpeza.
# O `trap` garante a faxina mesmo se o script morrer no meio.
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

printf '==> entrada : %s\n' "$ENTRADA"
printf '==> saída   : %s/\n\n' "$SAIDA"

# ---------------------------------------------------------------------------
# 2. Limpeza, passo a passo
# ---------------------------------------------------------------------------

# 2.1 — tira o cabeçalho e o \r que o Windows deixa no fim das linhas (CRLF).
tail -n +2 "$ENTRADA" | tr -d '\r' > "$TMP/01_sem_cabecalho.csv"
linhas_brutas=$(contar "$TMP/01_sem_cabecalho.csv")

# 2.2 — apara espaços nas pontas da linha e descarta as que ficaram vazias.
sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//' "$TMP/01_sem_cabecalho.csv" \
  | sed '/^$/d' \
  > "$TMP/02_sem_vazias.csv"
linhas_sem_vazias=$(contar "$TMP/02_sem_vazias.csv")

# 2.3 — normaliza a caixa. `\L&` é extensão do GNU sed e respeita acentos
#       ("PÉSSIMO" -> "péssimo"), coisa que `tr A-Z a-z` não faz em UTF-8.
sed 's/.*/\L&/' "$TMP/02_sem_vazias.csv" > "$TMP/03_minusculas.csv"

# 2.4 — valida a estrutura de cada linha e normaliza os espaços internos.
#       Fora: linhas sem exatamente 2 campos, texto vazio ou rótulo desconhecido.
awk -F, -v OFS=, '
  NF != 2 { next }                      # "a, b, c" ou linha sem vírgula
  {
    texto  = $1
    rotulo = $2
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", texto)    # apara o campo
    gsub(/^[[:space:]]+|[[:space:]]+$/, "", rotulo)
    gsub(/[[:space:]]+/, " ", texto)                  # colapsa espaços internos

    if (texto == "") next
    if (rotulo != "positivo" && rotulo != "negativo") next

    print texto, rotulo
  }
' "$TMP/03_minusculas.csv" > "$TMP/04_validas.csv"
linhas_validas=$(contar "$TMP/04_validas.csv")

# 2.5 — remove duplicatas. Depois do 2.3 e do 2.4, "Produto Bom" e "produto bom"
#       viraram a mesma linha e caem aqui.
sort -u "$TMP/04_validas.csv" > "$TMP/05_unicas.csv"
linhas_unicas=$(contar "$TMP/05_unicas.csv")

[[ "$linhas_unicas" -gt 0 ]] || erro "nenhuma linha válida sobrou em $ENTRADA (confira o formato: texto,rotulo)"

printf 'Limpeza\n'
printf '  %-28s %3d\n' 'linhas no bruto'          "$linhas_brutas"
printf '  %-28s %3d\n' '- vazias/em branco'       "$(( linhas_brutas - linhas_sem_vazias ))"
printf '  %-28s %3d\n' '- malformadas'            "$(( linhas_sem_vazias - linhas_validas ))"
printf '  %-28s %3d\n' '- duplicadas'             "$(( linhas_validas - linhas_unicas ))"
printf '  %-28s %3d\n\n' '= linhas limpas'        "$linhas_unicas"

# ---------------------------------------------------------------------------
# 3. Split treino/teste estratificado
# ---------------------------------------------------------------------------

# Estratificado = a proporção entre as classes se mantém nos dois arquivos.
# O awk conta as ocorrências de cada rótulo e manda 1 a cada A_CADA para o teste.
printf 'texto,rotulo\n' > "$TREINO"
printf 'texto,rotulo\n' > "$TESTE"

awk -F, -v a_cada="$A_CADA" -v treino="$TREINO" -v teste="$TESTE" '
  { n[$2]++ }
  n[$2] % a_cada == 0 { print >> teste;  next }
                      { print >> treino }
' "$TMP/05_unicas.csv"

# ---------------------------------------------------------------------------
# 4. Estatísticas
# ---------------------------------------------------------------------------

printf 'Split (1 a cada %d de cada classe vai para o teste)\n' "$A_CADA"
estatisticas "$TREINO"
estatisticas "$TESTE"

printf '\nPronto. Arquivos gerados:\n'
ls -lh "$TREINO" "$TESTE" | awk '{ printf "  %s  %s\n", $5, $NF }'
