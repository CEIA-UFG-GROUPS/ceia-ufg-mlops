"""Modelo leve de análise de sentimento: TF-IDF + Regressão Logística.

O modelo é treinado em memória no startup da API, a partir do mini-dataset
embutido neste arquivo. O treino leva alguns milissegundos e não baixa nada
da internet — o foco da Semana 03 é a API, não o modelo. Isso mantém o lab
rodando mesmo sem rede e sem GPU.

Este arquivo é reaproveitado sem alteração da Semana 04 em diante: quando a
API virar container, o que muda é o empacotamento, não o modelo.
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


def acuracia_treino(modelo: Pipeline) -> float:
    """Acurácia no próprio conjunto de treino.

    Serve apenas como sanidade ("o modelo aprendeu alguma coisa?"), nunca como
    métrica de qualidade: avaliação de verdade vem nas semanas seguintes.
    """
    textos = [texto for texto, _ in DATASET_TREINO]
    rotulos = [rotulo for _, rotulo in DATASET_TREINO]
    return float(modelo.score(textos, rotulos))


def classificar(
    modelo: Pipeline,
    texto: str,
    limiar_neutro: float = LIMIAR_NEUTRO_PADRAO,
) -> tuple[str, float]:
    """Classifica um texto e devolve (sentimento, score).

    O score é a probabilidade da classe vencedora, entre 0 e 1.
    """
    probabilidades = modelo.predict_proba([texto])[0]
    indice_vencedor = int(probabilidades.argmax())
    score = float(probabilidades[indice_vencedor])
    sentimento = str(modelo.classes_[indice_vencedor])

    if score < limiar_neutro:
        sentimento = "neutro"

    return sentimento, round(score, 4)
