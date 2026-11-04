"""Modelo leve de análise de sentimento: TF-IDF + Regressão Logística.

Versão enxuta do classificador que acompanha o grupo de estudos inteiro. É o
mesmo modelo da Semana 04 (`semana-04/codigo/app/modelo.py`), com uma única
diferença de interface: aqui `classificar(texto)` já cuida de treinar o modelo
na primeira chamada, para que o servidor da Semana 02 possa ficar focado em
HTTP e não em ciclo de vida de modelo.

O treino acontece em memória, leva alguns milissegundos, não baixa nada da
internet e roda em CPU. É de propósito: o assunto da semana é **rede**, não ML.

> Nota: esta é a versão "de laboratório". A versão que vira produto — com
> ciclo de vida explícito, validação de contrato, versionamento do artefato e
> empacotamento — aparece nas semanas seguintes (Semana 03: FastAPI,
> Semana 04: Docker, Semana 05 em diante: CI/CD).
"""

from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

NOME_MODELO = "tfidf+logreg"

# Mini-dataset de treino em PT-BR. Pequeno de propósito: dá para ler, entender
# e editar durante o lab. Para melhorar o modelo, acrescente exemplos aqui.
DATASET_TREINO: list[tuple[str, str]] = [
    # --- positivos ---
    ("adorei o produto, chegou antes do prazo", "positivo"),
    ("atendimento excelente, recomendo demais", "positivo"),
    ("muito bom, superou minhas expectativas", "positivo"),
    ("entrega rápida e tudo certo", "positivo"),
    ("funciona perfeitamente, estou satisfeito", "positivo"),
    ("qualidade ótima pelo preço que paguei", "positivo"),
    ("experiência maravilhosa do início ao fim", "positivo"),
    ("comprei de novo e continuo gostando", "positivo"),
    ("o suporte resolveu meu problema rapidinho", "positivo"),
    ("melhor compra que fiz esse ano", "positivo"),
    ("produto de alta qualidade, vale cada centavo", "positivo"),
    ("curso bem explicado, aprendi bastante", "positivo"),
    ("interface simples e muito fácil de usar", "positivo"),
    ("amei, chegou bem embalado e novo", "positivo"),
    ("site rápido, checkout sem complicação", "positivo"),
    ("recomendo, serviço impecável", "positivo"),
    ("o time foi super atencioso comigo", "positivo"),
    ("estou impressionado com o resultado", "positivo"),
    ("perfeito, exatamente como anunciado", "positivo"),
    ("preço justo e entrega no prazo", "positivo"),
    ("gostei muito da experiência", "positivo"),
    ("material de ótima qualidade, bem acabado", "positivo"),
    ("a api responde rápido e sem erros", "positivo"),
    ("documentação clara, consegui integrar fácil", "positivo"),
    ("nota dez, voltarei a comprar", "positivo"),
    ("superou o esperado, estou muito feliz", "positivo"),
    ("funciona bem, sem travar", "positivo"),
    ("pedido impecável, nada a reclamar", "positivo"),
    ("excelente custo benefício", "positivo"),
    ("resolveu meu problema, obrigado", "positivo"),
    # --- negativos ---
    ("odiei o produto, veio quebrado", "negativo"),
    ("atendimento péssimo, ninguém responde", "negativo"),
    ("muito ruim, não recomendo", "negativo"),
    ("entrega atrasada e sem explicação", "negativo"),
    ("não funciona, estou frustrado", "negativo"),
    ("qualidade horrível pelo preço cobrado", "negativo"),
    ("experiência terrível do início ao fim", "negativo"),
    ("comprei e me arrependi na hora", "negativo"),
    ("o suporte não resolveu nada", "negativo"),
    ("pior compra que fiz esse ano", "negativo"),
    ("produto frágil, quebrou em dois dias", "negativo"),
    ("curso confuso, não aprendi quase nada", "negativo"),
    ("interface travada e difícil de usar", "negativo"),
    ("detestei, chegou amassado e sujo", "negativo"),
    ("site lento, o checkout deu erro", "negativo"),
    ("não recomendo, serviço decepcionante", "negativo"),
    ("o time foi grosseiro comigo", "negativo"),
    ("estou decepcionado com o resultado", "negativo"),
    ("péssimo, nada parecido com o anunciado", "negativo"),
    ("caro demais e entregou atrasado", "negativo"),
    ("não gostei da experiência", "negativo"),
    ("material barato, acabamento ruim", "negativo"),
    ("a api cai toda hora e devolve erro", "negativo"),
    ("documentação confusa, perdi horas tentando", "negativo"),
    ("nota zero, nunca mais compro aqui", "negativo"),
    ("ficou abaixo do esperado, estou chateado", "negativo"),
    ("trava o tempo todo, inutilizável", "negativo"),
    ("pedido errado e ninguém me ajudou", "negativo"),
    ("custo benefício horrível", "negativo"),
    ("não resolveu meu problema, perdi dinheiro", "negativo"),
]

# Abaixo deste limiar de confiança o resultado vira "neutro": melhor admitir
# incerteza do que cravar um sentimento com 51% de confiança.
LIMIAR_NEUTRO_PADRAO = 0.60

# Pipeline treinado, guardado no módulo. Treinar a cada requisição seria lento
# e inútil: o modelo não muda entre uma chamada e outra.
_modelo: Pipeline | None = None


def treinar_modelo() -> Pipeline:
    """Treina e devolve o pipeline TF-IDF + Regressão Logística."""
    textos = [texto for texto, _ in DATASET_TREINO]
    rotulos = [rotulo for _, rotulo in DATASET_TREINO]

    modelo = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                    strip_accents="unicode",
                    lowercase=True,
                ),
            ),
            (
                "clf",
                LogisticRegression(max_iter=1000, C=5.0, random_state=42),
            ),
        ]
    )
    modelo.fit(textos, rotulos)
    return modelo


def carregar_modelo() -> Pipeline:
    """Treina o modelo na primeira chamada e reaproveita nas seguintes.

    O servidor chama isso no startup, antes de abrir a porta, para que a
    primeira requisição não pague o custo do treino.
    """
    global _modelo
    if _modelo is None:
        _modelo = treinar_modelo()
    return _modelo


def modelo_carregado() -> bool:
    """Se o modelo já está em memória — usado pelo `/health`."""
    return _modelo is not None


def acuracia_treino() -> float:
    """Acurácia no próprio conjunto de treino.

    Serve apenas como sanidade ("o modelo aprendeu alguma coisa?"), nunca como
    métrica de qualidade: avaliação de verdade vem nas semanas seguintes.
    """
    modelo = carregar_modelo()
    textos = [texto for texto, _ in DATASET_TREINO]
    rotulos = [rotulo for _, rotulo in DATASET_TREINO]
    return float(modelo.score(textos, rotulos))


def classificar(
    texto: str,
    limiar_neutro: float = LIMIAR_NEUTRO_PADRAO,
) -> tuple[str, float]:
    """Classifica um texto e devolve `(sentimento, score)`.

    O score é a probabilidade da classe vencedora, entre 0 e 1. Abaixo do
    limiar, o rótulo vira `neutro`.
    """
    modelo = carregar_modelo()

    probabilidades = modelo.predict_proba([texto])[0]
    indice_vencedor = int(probabilidades.argmax())
    score = float(probabilidades[indice_vencedor])
    sentimento = str(modelo.classes_[indice_vencedor])

    if score < limiar_neutro:
        sentimento = "neutro"

    return sentimento, round(score, 4)


if __name__ == "__main__":
    # Teste rápido sem servidor nenhum: `python modelo.py`
    for frase in (
        "adorei o atendimento, chegou antes do prazo",
        "pessimo, veio quebrado e atrasado",
        "o pedido chegou",
    ):
        print(f"{classificar(frase)!s:<24} {frase}")
