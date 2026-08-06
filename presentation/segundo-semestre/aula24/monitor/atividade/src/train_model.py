import argparse
import json
from pathlib import Path

import joblib
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

from .common import (
    build_model,
    bundle_path,
    dataset_digest,
    dataset_path,
    ensure_dirs,
    load_dataset,
    model_path,
    reports_dir,
    save_json,
)


def train(seed: int = 42) -> dict[str, object]:
    ensure_dirs()
    dataframe = load_dataset()
    feature_columns = [
        column for column in dataframe.columns if column not in {"target", "protected_group"}
    ]
    if "protected_group" in feature_columns:
        raise AssertionError("protected_group não pode ser usado como feature")

    X = dataframe[feature_columns]
    y = dataframe["target"]
    sensitive = dataframe["protected_group"]
    X_train, X_test, y_train, y_test, group_train, group_test = train_test_split(
        X,
        y,
        sensitive,
        test_size=0.25,
        random_state=seed,
        stratify=y,
    )

    model = build_model(seed)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1]
    metrics = {
        "accuracy": float(accuracy_score(y_test, predictions)),
        "macro_f1": float(f1_score(y_test, predictions, average="macro")),
        "roc_auc": float(roc_auc_score(y_test, probabilities)),
    }

    joblib.dump(model, model_path())
    joblib.dump(
        {
            "X_train": X_train,
            "X_test": X_test,
            "y_train": y_train,
            "y_test": y_test,
            "group_train": group_train,
            "group_test": group_test,
            "feature_columns": feature_columns,
            "seed": seed,
        },
        bundle_path(),
    )
    (reports_dir() / "predictions.csv").write_text(
        X_test.assign(
            protected_group=group_test.to_numpy(),
            target=y_test.to_numpy(),
            prediction=predictions,
            probability=probabilities,
        ).to_csv(index=False),
        encoding="utf-8",
    )
    save_json(metrics, reports_dir() / "metrics.json")
    save_json({"feature_columns": feature_columns}, reports_dir() / "feature_columns.json")
    save_json(
        {"dataset": str(dataset_path()), "dataset_digest": dataset_digest(dataframe), "seed": seed},
        reports_dir() / "lineage.json",
    )
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    metrics = train(args.seed)
    print(json.dumps(metrics, indent=2))
    print(f"Modelo: {model_path()}")


if __name__ == "__main__":
    main()
