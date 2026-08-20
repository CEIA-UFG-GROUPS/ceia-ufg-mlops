"""O contrato também é código — logo, também tem teste.

Se ninguém testa o contrato, um typo em `nullabe: false` vira uma expectativa
que nunca foi criada, e o pipeline fica verde sem verificar nada.
"""

from __future__ import annotations

import pytest

from src.common import CONTRACT_PATH, load_contract
from src.contract import build_expectations, expectation_types


def test_contrato_carrega_e_tem_metadados(contract):
    assert contract["name"] == "credito"
    assert isinstance(contract["version"], int)
    assert contract["owner"], "contrato sem dono não é revisável"
    assert CONTRACT_PATH.exists()


def test_toda_coluna_declarada_tem_regra_de_nulos(contract):
    """Nulidade é a falha silenciosa mais comum: exigir declaração explícita."""
    for column, rules in contract["columns"].items():
        assert "nullable" in rules, f"coluna '{column}' não declara `nullable`"


def test_colunas_da_tabela_batem_com_as_colunas_detalhadas(contract):
    assert set(contract["table"]["columns"]) == set(contract["columns"])


def test_mapeamento_gera_as_expectativas_esperadas(contract):
    types = expectation_types(contract)
    for esperado in (
        "expect_table_columns_to_match_set",
        "expect_table_row_count_to_be_between",
        "expect_column_values_to_not_be_null",
        "expect_column_values_to_be_unique",
        "expect_column_values_to_be_between",
        "expect_column_values_to_be_in_set",
        "expect_column_values_to_be_of_type",
        "expect_column_mean_to_be_between",
    ):
        assert esperado in types, f"contrato deixou de gerar {esperado}"


def test_numero_de_expectativas_e_estavel(contract):
    """Guarda contra remoção acidental de regra em refatoração do YAML."""
    assert len(build_expectations(contract)) == 24


def test_chave_desconhecida_no_contrato_falha_alto():
    """Erro de digitação precisa explodir, não ser ignorado em silêncio."""
    quebrado = {
        "name": "x",
        "version": 1,
        "table": {"columns": ["a"]},
        "columns": {"a": {"nulable": False}},  # typo proposital
    }
    with pytest.raises(ValueError, match="não suportadas"):
        build_expectations(quebrado)


def test_contrato_sem_chave_obrigatoria_falha(tmp_path):
    caminho = tmp_path / "ruim.yaml"
    caminho.write_text("name: x\nversion: 1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="obrigatória"):
        load_contract(caminho)
