"""Runner do Great Expectations: valida um DataFrame contra o contrato."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import great_expectations as gx
import pandas as pd

from .common import (
    DATA_DIR,
    REPORTS_DIR,
    ensure_offline_env,
    load_contract,
    write_json,
)
from .contract import build_suite


def validate_dataframe(df: pd.DataFrame, contract: dict[str, Any]) -> dict[str, Any]:
    """Roda a suíte do contrato sobre `df` e devolve um resumo serializável."""
    ensure_offline_env()
    context, suite = build_suite(contract)

    source = context.data_sources.add_pandas("pandas_runtime")
    asset = source.add_dataframe_asset(name=contract["name"])
    batch_definition = asset.add_batch_definition_whole_dataframe("lote_completo")

    validation_definition = context.validation_definitions.add(
        gx.ValidationDefinition(
            data=batch_definition,
            suite=suite,
            name=f"vd_{contract['name']}_v{contract['version']}",
        )
    )
    result = validation_definition.run(batch_parameters={"dataframe": df})

    failures = []
    for item in result.results:
        if item.success:
            continue
        config = item.expectation_config
        failures.append(
            {
                "expectation": config.type,
                "column": config.kwargs.get("column"),
                "kwargs": {
                    k: v for k, v in config.kwargs.items() if k not in ("batch_id", "column")
                },
                "unexpected_count": item.result.get("unexpected_count"),
                "observed_value": item.result.get("observed_value"),
            }
        )

    stats = result.statistics
    return {
        "contract": f"{contract['name']} v{contract['version']}",
        "success": bool(result.success),
        "rows": int(len(df)),
        "evaluated": int(stats["evaluated_expectations"]),
        "successful": int(stats["successful_expectations"]),
        "failed": int(stats["unsuccessful_expectations"]),
        "success_percent": round(float(stats["success_percent"]), 2),
        "failures": failures,
    }


def validate_csv(path: Path, contract: dict[str, Any] | None = None) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"{path} não existe. Rode antes: python -m src.generate_data --variant clean"
        )
    return validate_dataframe(pd.read_csv(path), contract or load_contract())


def format_report(report: dict[str, Any]) -> str:
    status = "PASS" if report["success"] else "FAIL"
    linhas = [
        f"[{status}] contrato={report['contract']} linhas={report['rows']} "
        f"expectativas={report['successful']}/{report['evaluated']} "
        f"({report['success_percent']}%)"
    ]
    for failure in report["failures"]:
        alvo = failure["column"] or "<tabela>"
        detalhe = (
            f"unexpected={failure['unexpected_count']}"
            if failure["unexpected_count"] is not None
            else f"observado={failure['observed_value']}"
        )
        linhas.append(f"  - [NO] {failure['expectation']} ({alvo}) {detalhe}")
    return "\n".join(linhas)


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida um CSV contra o contrato de dados")
    parser.add_argument("--dataset", choices=["clean", "corrupted"], default="clean")
    args = parser.parse_args()

    path = DATA_DIR / f"credito_{args.dataset}.csv"
    report = validate_csv(path)
    write_json(REPORTS_DIR / f"data_validation_{args.dataset}.json", report)
    print(format_report(report))
    print(f"📄 relatório: reports/data_validation_{args.dataset}.json")
    raise SystemExit(0 if report["success"] else 1)


if __name__ == "__main__":
    main()
