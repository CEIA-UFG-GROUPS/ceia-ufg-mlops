import argparse
import json
import os
import re
import time
import uuid
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .common import (
    activity_root,
    create_session,
    dataset_digest,
    dvc_metadata,
    git_commit,
    write_dataset_csv,
)


def build_model(args: argparse.Namespace) -> Any:
    if args.model == "random_forest":
        return RandomForestClassifier(
            n_estimators=args.n_estimators,
            max_depth=None if args.max_depth == 0 else args.max_depth,
            random_state=args.seed,
            n_jobs=1,
        )
    if args.model == "logistic_regression":
        return Pipeline(
            [
                ("scaler", StandardScaler()),
                (
                    "classifier",
                    LogisticRegression(C=args.c_value, max_iter=2000, random_state=args.seed),
                ),
            ]
        )
    raise ValueError(f"Modelo desconhecido: {args.model}")


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", value).strip("-") or "run"


def run_training(args: argparse.Namespace) -> dict[str, Any]:
    root = activity_root()
    data_path = Path(args.data_path) if args.data_path else root / "data" / "wine.csv"
    data_path = data_path.resolve()
    if not data_path.exists():
        dataframe = write_dataset_csv(data_path)
    else:
        dataframe = pd.read_csv(data_path)

    if "target" not in dataframe.columns:
        raise ValueError("O dataset precisa conter uma coluna target")

    features = dataframe.drop(columns=["target"])
    target = dataframe["target"]
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=args.test_size,
        random_state=args.seed,
        stratify=target,
    )

    model = build_model(args)
    started = time.perf_counter()
    model.fit(x_train, y_train)
    elapsed = time.perf_counter() - started
    predictions = model.predict(x_test)

    metrics = {
        "accuracy": accuracy_score(y_test, predictions),
        "macro_f1": f1_score(y_test, predictions, average="macro"),
        "train_time_seconds": elapsed,
    }
    report = classification_report(y_test, predictions, output_dict=True)

    default_name = f"{args.model}-seed-{args.seed}"
    run_name = args.run_name or default_name
    artifact_root = Path(args.artifact_dir) if args.artifact_dir else root / "artifacts"
    artifact_dir = artifact_root / f"{safe_name(run_name)}-{uuid.uuid4().hex[:8]}"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    model_path = artifact_dir / "model.joblib"
    report_path = artifact_dir / "classification_report.json"
    matrix_path = artifact_dir / "confusion_matrix.png"
    joblib.dump(model, model_path)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    matrix = confusion_matrix(y_test, predictions)
    fig, axis = plt.subplots(figsize=(5, 4))
    image = axis.imshow(matrix, cmap="Blues")
    axis.set_title("Confusion matrix")
    axis.set_xlabel("Predicted label")
    axis.set_ylabel("True label")
    fig.colorbar(image, ax=axis)
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            axis.text(column, row, matrix[row, column], ha="center", va="center")
    fig.tight_layout()
    fig.savefig(matrix_path, dpi=140)
    plt.close(fig)

    dvc_info = dvc_metadata(data_path)
    params = {
        "model": args.model,
        "seed": args.seed,
        "test_size": args.test_size,
        "n_estimators": args.n_estimators if args.model == "random_forest" else "not_applicable",
        "max_depth": None if args.model != "random_forest" or args.max_depth == 0 else args.max_depth,
        "c_value": args.c_value if args.model == "logistic_regression" else "not_applicable",
    }
    tags = {
        "course": "ceia-ufg-mlops",
        "class": "aula15",
        "tracker": args.tracker,
        "git_commit": git_commit(root),
        "dataset_name": "sklearn-wine",
        "dataset_digest": dataset_digest(dataframe),
        **dvc_info,
    }

    tracking_uri = args.tracking_uri or os.getenv("MLFLOW_TRACKING_URI")
    with create_session(
        args.tracker,
        experiment_name=args.experiment_name,
        run_name=run_name,
        tracking_uri=tracking_uri,
        wandb_project=args.wandb_project,
        wandb_mode=args.wandb_mode,
        wandb_entity=args.wandb_entity,
        params=params,
        tags=tags,
    ) as session:
        session.log_metrics(metrics)
        session.log_dataset(data_path)
        session.log_artifact(model_path, "model")
        session.log_artifact(report_path, "evaluation")
        session.log_artifact(matrix_path, "evaluation")

    result = {
        "run_id": session.run_id,
        "run_name": run_name,
        "tracker": args.tracker,
        "metrics": metrics,
        "params": params,
        "tags": tags,
        "artifact_dir": str(artifact_dir),
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tracker", choices=["mlflow", "wandb"], required=True)
    parser.add_argument("--model", choices=["random_forest", "logistic_regression"], default="random_forest")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--n-estimators", type=int, default=100)
    parser.add_argument("--max-depth", type=int, default=5, help="Use 0 para árvore sem limite")
    parser.add_argument("--c", dest="c_value", type=float, default=1.0)
    parser.add_argument("--run-name")
    parser.add_argument("--data-path", type=Path)
    parser.add_argument("--artifact-dir", type=Path)
    parser.add_argument("--experiment-name", default=os.getenv("MLFLOW_EXPERIMENT_NAME", "aula15_wine_tracking"))
    parser.add_argument("--tracking-uri")
    parser.add_argument("--wandb-project", default=os.getenv("WANDB_PROJECT", "ceia-ufg-aula15"))
    parser.add_argument("--wandb-entity", default=os.getenv("WANDB_ENTITY"))
    parser.add_argument("--wandb-mode", choices=["online", "offline", "disabled"])
    return parser.parse_args()


if __name__ == "__main__":
    run_training(parse_args())
