"""Great Expectations dentro do pytest — validação de dados vira teste de CI.

Cada defeito injetado precisa fazer falhar a expectativa que foi escrita para
pegá-lo. Sem isto, o contrato pode estar cheio de regras que nunca disparam.
"""

from __future__ import annotations

import pytest

from src.generate_data import DEFECTS, inject
from src.validate_data import validate_dataframe

# defeito → expectativa que ele existe para acionar
DEFEITO_PARA_EXPECTATIVA = {
    "nulls": "expect_column_values_to_not_be_null",
    "ranges": "expect_column_values_to_be_between",
    "schema": "expect_table_columns_to_match_set",
    "dups": "expect_column_values_to_be_unique",
    "labels": "expect_column_values_to_be_in_set",
    "drift": "expect_column_mean_to_be_between",
}


def test_dataset_limpo_passa_no_contrato(df_clean, contract):
    report = validate_dataframe(df_clean, contract)
    assert report["success"] is True, report["failures"]
    assert report["failed"] == 0
    assert report["evaluated"] == 24


def test_cobertura_de_defeitos_esta_completa():
    """Todo defeito do gerador precisa de um teste correspondente."""
    assert set(DEFEITO_PARA_EXPECTATIVA) == set(DEFECTS)


@pytest.mark.parametrize("defeito", sorted(DEFEITO_PARA_EXPECTATIVA))
def test_cada_defeito_aciona_sua_expectativa(df_clean, contract, defeito):
    sujo = inject(df_clean, [defeito])
    report = validate_dataframe(sujo, contract)

    assert report["success"] is False, f"defeito '{defeito}' passou despercebido"
    acionadas = {f["expectation"] for f in report["failures"]}
    assert DEFEITO_PARA_EXPECTATIVA[defeito] in acionadas, (
        f"defeito '{defeito}' falhou, mas não na expectativa esperada: {acionadas}"
    )


def test_quebra_de_schema_cascateia(df_clean, contract):
    """Renomear uma coluna derruba também as regras daquela coluna.

    Vale conhecer o efeito: o relatório mostra 4 falhas para 1 causa raiz, e
    ler a lista de trás para frente leva ao diagnóstico errado.
    """
    report = validate_dataframe(inject(df_clean, ["schema"]), contract)
    colunas_afetadas = {f["column"] for f in report["failures"]}
    assert "score_credito" in colunas_afetadas
    assert report["failed"] > 1


def test_relatorio_e_serializavel_e_util(df_clean, contract):
    """O artefato do gate precisa ser anexável a um PR e legível por humano."""
    report = validate_dataframe(inject(df_clean, ["labels"]), contract)
    falha = next(
        f for f in report["failures"] if f["expectation"] == "expect_column_values_to_be_in_set"
    )
    assert falha["column"] == "inadimplente"
    assert falha["unexpected_count"] > 0
    assert report["success_percent"] < 100.0
