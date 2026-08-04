import argparse
import json
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .common import load_bundle, model_path, reports_dir, save_json


def _positive_class_values(values: Any) -> np.ndarray:
    array = np.asarray(values)
    if array.ndim == 3:
        return array[:, :, 1]
    if array.ndim == 2:
        return array
    raise ValueError(f"Formato de valores de explicação não suportado: {array.shape}")


def explain_shap(row_index: int = 0) -> dict[str, str]:
    import shap

    bundle = load_bundle()
    X_train = bundle["X_train"]
    X_test = bundle["X_test"].reset_index(drop=True)
    row_index = min(max(row_index, 0), len(X_test) - 1)
    model = __import__("joblib").load(model_path())
    output_dir = reports_dir() / "explainability"
    output_dir.mkdir(parents=True, exist_ok=True)

    explainer = shap.TreeExplainer(model)
    global_explanation = explainer(X_test)
    global_values = _positive_class_values(global_explanation.values)
    importance = pd.DataFrame(
        {
            "feature": X_test.columns,
            "mean_abs_shap": np.abs(global_values).mean(axis=0),
        }
    ).sort_values("mean_abs_shap", ascending=False)
    importance_path = output_dir / "shap_global_importance.csv"
    importance.to_csv(importance_path, index=False)

    plt.figure(figsize=(8, 5))
    shap.summary_plot(global_values, X_test, show=False, plot_size=None)
    plt.tight_layout()
    global_plot = output_dir / "shap_global_summary.png"
    plt.savefig(global_plot, dpi=140, bbox_inches="tight")
    plt.close()

    local_explanation = explainer(X_test.iloc[[row_index]])
    local_values = _positive_class_values(local_explanation.values)[0]
    local = pd.DataFrame(
        {"feature": X_test.columns, "shap_value": local_values}
    ).sort_values("shap_value", key=np.abs, ascending=False)
    local_json = output_dir / f"shap_local_row_{row_index}.json"
    save_json(
        {
            "row_index": row_index,
            "prediction_probability": float(model.predict_proba(X_test.iloc[[row_index]])[0, 1]),
            "contributions": local.to_dict(orient="records"),
        },
        local_json,
    )
    plt.figure(figsize=(8, 5))
    ordered = local.sort_values("shap_value")
    colors = ["#d95f02" if value > 0 else "#1b9e77" for value in ordered["shap_value"]]
    plt.barh(ordered["feature"], ordered["shap_value"], color=colors)
    plt.axvline(0, color="black", linewidth=0.8)
    plt.title(f"SHAP local — linha {row_index}")
    plt.xlabel("Contribuição para a classe aprovada")
    plt.tight_layout()
    local_plot = output_dir / f"shap_local_row_{row_index}.png"
    plt.savefig(local_plot, dpi=140)
    plt.close()
    return {"global_plot": str(global_plot), "local_plot": str(local_plot), "local_json": str(local_json)}


def explain_lime(row_index: int = 0) -> dict[str, str]:
    import joblib
    from lime.lime_tabular import LimeTabularExplainer

    bundle = load_bundle()
    X_train = bundle["X_train"]
    X_test = bundle["X_test"].reset_index(drop=True)
    row_index = min(max(row_index, 0), len(X_test) - 1)
    model = joblib.load(model_path())
    output_dir = reports_dir() / "explainability"
    output_dir.mkdir(parents=True, exist_ok=True)
    explainer = LimeTabularExplainer(
        X_train.to_numpy(),
        feature_names=list(X_train.columns),
        class_names=["rejected", "approved"],
        mode="classification",
        discretize_continuous=True,
        random_state=int(bundle["seed"]),
    )
    explanation = explainer.explain_instance(
        X_test.iloc[row_index].to_numpy(),
        model.predict_proba,
        num_features=len(X_train.columns),
        num_samples=1200,
    )
    html_path = output_dir / f"lime_local_row_{row_index}.html"
    explanation.save_to_file(str(html_path))
    records = [{"feature": feature, "weight": float(weight)} for feature, weight in explanation.as_list(label=1)]
    json_path = output_dir / f"lime_local_row_{row_index}.json"
    save_json(
        {
            "row_index": row_index,
            "prediction_probability": float(model.predict_proba(X_test.iloc[[row_index]])[0, 1]),
            "contributions": records,
        },
        json_path,
    )
    return {"html": str(html_path), "json": str(json_path)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", choices=["shap", "lime"], required=True)
    parser.add_argument("--row-index", type=int, default=0)
    args = parser.parse_args()
    result = explain_shap(args.row_index) if args.method == "shap" else explain_lime(args.row_index)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
