"""Gate de qualidade da Aula 14: contrato de dados + comportamento do modelo.

Sequência deliberada — dados primeiro. Treinar sobre dados que violam o
contrato produz métrica bonita e modelo errado; o gate recusa a gastar o treino
e devolve `exit != 0` na hora.
"""

from __future__ import annotations

import argparse
import time
from typing import Any

import pandas as pd

from .common import DATA_DIR, REPORTS_DIR, ensure_offline_env, load_contract, write_json
from .features import split_por_id
from .model import behavioral_checks, train_model
from .validate_data import format_report, validate_dataframe


def run_gate(*, dataset: str = "clean", leaky: bool = False) -> dict[str, Any]:
    ensure_offline_env()
    started = time.perf_counter()
    contract = load_contract()
    gate_cfg = contract.get("gate", {})

    path = DATA_DIR / f"credito_{dataset}.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} não existe. Rode antes: "
            f"python -m src.generate_data --variant {dataset}"
        )
    df = pd.read_csv(path)

    data_report = validate_dataframe(df, contract)
    max_failed = int(gate_cfg.get("max_failed_expectations", 0))
    data_pass = data_report["failed"] <= max_failed

    stages: dict[str, dict[str, Any]] = {
        "contrato_de_dados": {
            "pass": data_pass,
            "detalhe": (
                f"{data_report['successful']}/{data_report['evaluated']} expectativas; "
                f"falhas={data_report['failed']} (máximo tolerado={max_failed})"
            ),
        }
    }

    model_report: dict[str, Any] | None = None
    if data_pass:
        train, test = split_por_id(df)
        model = train_model(train, test, leaky=leaky)
        checks = behavioral_checks(model)
        min_auc = float(gate_cfg.get("min_roc_auc", 0.0))

        stages["desempenho_minimo"] = {
            "pass": model.roc_auc >= min_auc,
            "detalhe": f"roc_auc={model.roc_auc:.4f} (limiar={min_auc})",
        }
        for name, check in checks.items():
            stages[name] = {"pass": bool(check["pass"]), "detalhe": str(check["detalhe"])}

        model_report = {
            "roc_auc": round(model.roc_auc, 4),
            "linhas_treino": int(len(train)),
            "linhas_teste": int(len(test)),
            "leaky_scaler": leaky,
            "behavioral": checks,
        }
    else:
        # Sem dados válidos não existe métrica de modelo confiável para reportar.
        stages["desempenho_minimo"] = {
            "pass": False,
            "detalhe": "não avaliado — contrato de dados reprovou",
        }

    overall = all(stage["pass"] for stage in stages.values())
    report = {
        "dataset": dataset,
        "overall_pass": overall,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "stages": stages,
        "data_validation": data_report,
        "model": model_report,
    }
    write_json(REPORTS_DIR / f"gate_report_{dataset}.json", report)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Gate de dados + modelo — Aula 14")
    parser.add_argument("--dataset", choices=["clean", "corrupted"], default="clean")
    parser.add_argument(
        "--leaky-scaler",
        action="store_true",
        help="Demonstra o bug de vazamento no pré-processamento (não use em produção).",
    )
    args = parser.parse_args()

    report = run_gate(dataset=args.dataset, leaky=args.leaky_scaler)
    status = "PASS" if report["overall_pass"] else "FAIL"
    print(
        f"[{status}] dataset={report['dataset']} elapsed={report['elapsed_seconds']}s"
    )
    for name, stage in report["stages"].items():
        mark = "OK" if stage["pass"] else "NO"
        print(f"  - {name}: {stage['detalhe']} [{mark}]")
    if not report["data_validation"]["success"]:
        print(format_report(report["data_validation"]))
    print(f"📄 relatório: reports/gate_report_{report['dataset']}.json")
    # Gate de release: qualquer estágio reprovado quebra o CI.
    raise SystemExit(0 if report["overall_pass"] else 1)


if __name__ == "__main__":
    main()
