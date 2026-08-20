"""Tradução do contrato YAML em uma ExpectationSuite do Great Expectations.

O ponto didático: o contrato é declarativo e legível por quem entende do
negócio; o mapeamento para a ferramenta fica em um único lugar. Trocar o
Great Expectations por Pandera ou Deequ mexeria neste arquivo, não no contrato.
"""

from __future__ import annotations

from typing import Any

import great_expectations as gx
from great_expectations import expectations as gxe

from .common import ensure_offline_env

# Chaves de coluna que o tradutor entende. Uma chave desconhecida é erro:
# contrato com typo silencioso é pior que contrato ausente.
SUPPORTED_COLUMN_KEYS = {
    "dtype",
    "nullable",
    "unique",
    "between",
    "in_set",
    "mean_between",
    "stdev_between",
}


def build_expectations(contract: dict[str, Any]) -> list[Any]:
    """Constrói a lista de Expectations a partir do contrato."""
    expectations: list[Any] = []

    table = contract["table"]
    expectations.append(gxe.ExpectTableColumnsToMatchSet(column_set=list(table["columns"])))

    row_count = table.get("row_count")
    if row_count:
        expectations.append(
            gxe.ExpectTableRowCountToBeBetween(
                min_value=row_count.get("min"),
                max_value=row_count.get("max"),
            )
        )

    for column, rules in contract["columns"].items():
        unknown = set(rules) - SUPPORTED_COLUMN_KEYS
        if unknown:
            raise ValueError(f"Coluna '{column}': chaves não suportadas {sorted(unknown)}")

        if "dtype" in rules:
            expectations.append(
                gxe.ExpectColumnValuesToBeOfType(column=column, type_=rules["dtype"])
            )
        if rules.get("nullable") is False:
            expectations.append(gxe.ExpectColumnValuesToNotBeNull(column=column))
        if rules.get("unique") is True:
            expectations.append(gxe.ExpectColumnValuesToBeUnique(column=column))
        if "between" in rules:
            expectations.append(
                gxe.ExpectColumnValuesToBeBetween(
                    column=column,
                    min_value=rules["between"]["min"],
                    max_value=rules["between"]["max"],
                )
            )
        if "in_set" in rules:
            expectations.append(
                gxe.ExpectColumnValuesToBeInSet(column=column, value_set=rules["in_set"])
            )
        if "mean_between" in rules:
            expectations.append(
                gxe.ExpectColumnMeanToBeBetween(
                    column=column,
                    min_value=rules["mean_between"]["min"],
                    max_value=rules["mean_between"]["max"],
                )
            )
        if "stdev_between" in rules:
            expectations.append(
                gxe.ExpectColumnStdevToBeBetween(
                    column=column,
                    min_value=rules["stdev_between"]["min"],
                    max_value=rules["stdev_between"]["max"],
                )
            )

    return expectations


def build_suite(contract: dict[str, Any]) -> tuple[Any, Any]:
    """Devolve `(context, suite)` prontos para uma validação em memória.

    Usa contexto `ephemeral`: nada é escrito em disco, o que mantém o lab
    reproduzível e sem estado residual entre execuções.
    """
    ensure_offline_env()
    context = gx.get_context(mode="ephemeral")

    # Silencia a barra de progresso de métricas (ruído no log de CI).
    from great_expectations.data_context.types.base import ProgressBarsConfig

    context.variables.progress_bars = ProgressBarsConfig(
        globally=False, metric_calculations=False
    )

    suite_name = f"{contract['name']}_v{contract['version']}"
    suite = context.suites.add(gx.ExpectationSuite(name=suite_name))
    for expectation in build_expectations(contract):
        suite.add_expectation(expectation)
    return context, suite


def expectation_types(contract: dict[str, Any]) -> list[str]:
    """Lista os tipos de expectativa geradas — útil em testes de contrato."""
    return [expectation.configuration.type for expectation in build_expectations(contract)]
