import argparse
import json

import joblib
import pandas as pd
from fairlearn.metrics import (
    MetricFrame,
    demographic_parity_difference,
    demographic_parity_ratio,
    equalized_odds_difference,
    equalized_odds_ratio,
    false_positive_rate,
    selection_rate,
    true_positive_rate,
)
from sklearn.metrics import accuracy_score

from .common import bundle_path, load_bundle, model_path, reports_dir, save_json


def assess() -> dict[str, object]:
    bundle = load_bundle()
    model = joblib.load(model_path())
    feature_columns = list(bundle["feature_columns"])
    if "protected_group" in feature_columns:
        raise AssertionError("Atributo protegido entrou indevidamente no treinamento")
    X_test = bundle["X_test"]
    y_test = bundle["y_test"]
    groups = bundle["group_test"]
    predictions = model.predict(X_test)

    frame = MetricFrame(
        metrics={
            "accuracy": accuracy_score,
            "selection_rate": selection_rate,
            "true_positive_rate": true_positive_rate,
            "false_positive_rate": false_positive_rate,
        },
        y_true=y_test,
        y_pred=predictions,
        sensitive_features=groups,
    )
    by_group = frame.by_group.reset_index().rename(columns={"index": "protected_group"})
    reports_dir().mkdir(parents=True, exist_ok=True)
    by_group.to_csv(reports_dir() / "fairness_by_group.csv", index=False)
    metrics = {
        "overall": {key: float(value) for key, value in frame.overall.items()},
        "demographic_parity_difference": float(
            demographic_parity_difference(y_test, predictions, sensitive_features=groups)
        ),
        "demographic_parity_ratio": float(
            demographic_parity_ratio(y_test, predictions, sensitive_features=groups)
        ),
        "equalized_odds_difference": float(
            equalized_odds_difference(y_test, predictions, sensitive_features=groups)
        ),
        "equalized_odds_ratio": float(
            equalized_odds_ratio(y_test, predictions, sensitive_features=groups)
        ),
        "protected_group_column_used_as_feature": False,
        "model_artifact": str(model_path()),
        "bundle_artifact": str(bundle_path()),
    }
    save_json(metrics, reports_dir() / "fairness_metrics.json")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    print(json.dumps(assess(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
