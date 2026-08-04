import hashlib
import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier


def activity_root() -> Path:
    return Path(__file__).resolve().parents[1]


def data_dir() -> Path:
    return activity_root() / "data"


def reports_dir() -> Path:
    return activity_root() / "reports"


def models_dir() -> Path:
    return activity_root() / "models"


def ensure_dirs() -> None:
    for directory in (data_dir(), reports_dir(), models_dir()):
        directory.mkdir(parents=True, exist_ok=True)


def dataset_path() -> Path:
    return data_dir() / "credit.csv"


def model_path() -> Path:
    return models_dir() / "credit_model.joblib"


def bundle_path() -> Path:
    return models_dir() / "test_bundle.joblib"


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(values, -30, 30)))


def make_credit_dataset(n_samples: int = 1200, seed: int = 42) -> pd.DataFrame:
    """Gera dados sintéticos determinísticos com uma variável proxy controlada."""

    rng = np.random.default_rng(seed)
    protected_group = rng.integers(0, 2, size=n_samples)
    income = np.clip(rng.normal(6800 - 750 * protected_group, 1500, n_samples), 1800, None)
    debt_to_income = np.clip(rng.beta(2.2, 5.0, n_samples) + 0.06 * protected_group, 0.02, 0.95)
    employment_years = np.clip(rng.normal(7.0 - 1.0 * protected_group, 3.0, n_samples), 0, 30)
    prior_defaults = rng.poisson(0.45 + 0.35 * protected_group, n_samples)
    requested_amount = np.clip(rng.normal(8500 + 700 * protected_group, 3200, n_samples), 1000, None)
    area_proxy = np.clip(protected_group + rng.normal(0, 0.16, n_samples), -0.5, 1.5)

    historical_score = (
        1.15
        + 0.00018 * income
        - 2.7 * debt_to_income
        + 0.10 * employment_years
        - 0.65 * prior_defaults
        - 0.000035 * requested_amount
        - 0.65 * area_proxy
    )
    probability = sigmoid(historical_score)
    approved = rng.binomial(1, probability)

    return pd.DataFrame(
        {
            "income": income.round(2),
            "debt_to_income": debt_to_income.round(4),
            "employment_years": employment_years.round(2),
            "prior_defaults": prior_defaults,
            "requested_amount": requested_amount.round(2),
            "area_proxy": area_proxy.round(4),
            "protected_group": protected_group,
            "target": approved,
        }
    )


def save_dataset(dataframe: pd.DataFrame, path: Path | None = None) -> Path:
    ensure_dirs()
    output = path or dataset_path()
    output.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(output, index=False)
    return output


def load_dataset(path: Path | None = None) -> pd.DataFrame:
    source = path or dataset_path()
    if not source.exists():
        save_dataset(make_credit_dataset(), source)
    return pd.read_csv(source)


def dataset_digest(dataframe: pd.DataFrame) -> str:
    payload = dataframe.to_csv(index=False, lineterminator="\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_model(seed: int = 42) -> RandomForestClassifier:
    return RandomForestClassifier(
        n_estimators=160,
        max_depth=6,
        min_samples_leaf=4,
        random_state=seed,
        n_jobs=1,
    )


def save_json(payload: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_bundle() -> dict[str, Any]:
    if not model_path().exists() or not bundle_path().exists():
        raise FileNotFoundError("Execute primeiro: python -m src.train_model")
    return joblib.load(bundle_path())
