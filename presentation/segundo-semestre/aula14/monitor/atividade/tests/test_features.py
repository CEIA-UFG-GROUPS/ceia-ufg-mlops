"""Testes unitários das transformações — o andar "pré-treino" da pirâmide.

Nenhum destes testes treina modelo. Todos rodam em milissegundos e apontam a
função culpada, que é exatamente o que um teste unitário deve fazer.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.features import (
    FAIXAS_ETARIAS,
    build_features,
    comprometimento_renda,
    faixa_etaria,
    fit_scaler,
    prepare_dataset,
    split_por_id,
)

# --------------------------------------------------------------------------
# Fronteiras: onde binning quebra
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("idade", "esperado"),
    [
        (18, "jovem"),
        (29, "jovem"),
        (30, "adulto"),  # fronteira fechada à esquerda
        (44, "adulto"),
        (45, "meia_idade"),
        (59, "meia_idade"),
        (60, "senior"),
        (99, "senior"),
    ],
)
def test_faixa_etaria_nas_fronteiras(idade, esperado):
    assert faixa_etaria(idade) == esperado


@pytest.mark.parametrize("invalida", [17, 0, -3])
def test_faixa_etaria_rejeita_idade_fora_do_contrato(invalida):
    with pytest.raises(ValueError, match="abaixo do mínimo"):
        faixa_etaria(invalida)


def test_faixa_etaria_rejeita_nulo():
    with pytest.raises(ValueError, match="nula"):
        faixa_etaria(np.nan)


# --------------------------------------------------------------------------
# Caso de borda que só aparece em produção
# --------------------------------------------------------------------------


def test_comprometimento_renda_com_renda_zero_nao_divide_por_zero():
    assert comprometimento_renda(1200.0, 0.0) == 1.0


def test_comprometimento_renda_satura_em_um():
    assert comprometimento_renda(9000.0, 3000.0) == 1.0


def test_comprometimento_renda_caso_tipico():
    assert comprometimento_renda(750.0, 3000.0) == pytest.approx(0.25)


# --------------------------------------------------------------------------
# Teste baseado em propriedade: Hypothesis procura o contraexemplo por você
# --------------------------------------------------------------------------


@given(
    divida=st.floats(min_value=0, max_value=1e7, allow_nan=False, allow_infinity=False),
    renda=st.floats(min_value=0, max_value=1e7, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=200, deadline=None)
def test_propriedade_comprometimento_sempre_em_zero_um(divida, renda):
    valor = comprometimento_renda(divida, renda)
    assert 0.0 <= valor <= 1.0


@given(idade=st.integers(min_value=18, max_value=120))
@settings(max_examples=200, deadline=None)
def test_propriedade_faixa_etaria_sempre_valida(idade):
    assert faixa_etaria(idade) in FAIXAS_ETARIAS


# --------------------------------------------------------------------------
# Transformação de DataFrame
# --------------------------------------------------------------------------


def test_build_features_nao_muta_a_entrada(df_clean):
    antes = df_clean.copy(deep=True)
    build_features(df_clean)
    pd.testing.assert_frame_equal(df_clean, antes)


def test_build_features_e_idempotente(df_clean):
    uma = build_features(df_clean)
    duas = build_features(build_features(df_clean))
    pd.testing.assert_frame_equal(uma, duas)


def test_build_features_cria_colunas_derivadas(df_clean):
    out = build_features(df_clean)
    assert {"faixa_etaria", "log_renda", "consultas_por_ponto_score"} <= set(out.columns)
    assert out["faixa_etaria"].isna().sum() == 0


# --------------------------------------------------------------------------
# Split: determinismo e ausência de sobreposição
# --------------------------------------------------------------------------


def test_split_nao_sobrepoe_clientes(split):
    train, test = split
    assert set(train["id_cliente"]) & set(test["id_cliente"]) == set()


def test_split_preserva_todas_as_linhas(df_clean, split):
    train, test = split
    assert len(train) + len(test) == len(df_clean)


def test_split_e_deterministico_sob_reordenacao(df_clean):
    """Embaralhar as linhas não pode mover um cliente de lado."""
    a_train, a_test = split_por_id(df_clean)
    embaralhado = df_clean.sample(frac=1.0, random_state=7).reset_index(drop=True)
    b_train, b_test = split_por_id(embaralhado)
    assert set(a_train["id_cliente"]) == set(b_train["id_cliente"])
    assert set(a_test["id_cliente"]) == set(b_test["id_cliente"])


def test_split_rejeita_fracao_invalida(df_clean):
    with pytest.raises(ValueError, match=r"\(0, 1\)"):
        split_por_id(df_clean, test_frac=1.5)


# --------------------------------------------------------------------------
# Vazamento de dados no pré-processamento
# --------------------------------------------------------------------------


def test_prepare_dataset_ajusta_scaler_apenas_no_treino(split):
    train, test = split
    *_, scaler = prepare_dataset(train, test, leaky=False)
    esperado = fit_scaler(train)
    np.testing.assert_allclose(scaler.mean_, esperado.mean_)
    np.testing.assert_allclose(scaler.std_, esperado.std_)


def test_prepare_dataset_detecta_vazamento(split):
    """O ponto da aula: a métrica NÃO denuncia o vazamento — o teste sim.

    Ajustar o scaler em treino+teste move as estatísticas de padronização.
    O ROC AUC praticamente não se mexe, então nenhum limiar de desempenho
    reprovaria esse bug; só uma asserção sobre o próprio pré-processamento.
    """
    train, test = split
    *_, honesto = prepare_dataset(train, test, leaky=False)
    *_, vazado = prepare_dataset(train, test, leaky=True)
    assert not np.allclose(honesto.mean_, vazado.mean_), (
        "vazamento deveria alterar as estatísticas do scaler"
    )


def test_scaler_lida_com_coluna_constante():
    df = pd.DataFrame(
        {
            "idade": [40, 40, 40],
            "renda_anual": [60000.0, 70000.0, 80000.0],
            "score_credito": [600, 650, 700],
            "taxa_endividamento": [0.2, 0.3, 0.4],
            "num_consultas_90d": [1, 2, 3],
        }
    )
    scaler = fit_scaler(df)
    transformado = scaler.transform(df)
    assert np.isfinite(transformado).all(), "desvio zero não pode gerar NaN/inf"
