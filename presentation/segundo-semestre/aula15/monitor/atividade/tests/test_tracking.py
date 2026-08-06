from __future__ import annotations

import os
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

from src.common import dataset_digest, write_dataset_csv
from src.train import run_training


class TrackingActivityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory(ignore_cleanup_errors=True)
        self.root = Path(self.tempdir.name)
        self.data_path = self.root / "data" / "wine.csv"
        self.artifact_dir = self.root / "artifacts"
        self.old_env = dict(os.environ)

    def tearDown(self) -> None:
        os.environ.clear()
        os.environ.update(self.old_env)
        self.tempdir.cleanup()

    def args(self, tracker: str, **overrides: object) -> Namespace:
        values: dict[str, object] = {
            "tracker": tracker,
            "model": "random_forest",
            "seed": 42,
            "test_size": 0.2,
            "n_estimators": 20,
            "max_depth": 4,
            "c_value": 1.0,
            "run_name": "test-run",
            "data_path": self.data_path,
            "artifact_dir": self.artifact_dir,
            "experiment_name": "aula15_test_tracking",
            "tracking_uri": f"sqlite:///{(self.root / 'mlflow.db').as_posix()}",
            "wandb_project": "aula15-test",
            "wandb_entity": None,
            "wandb_mode": "offline",
        }
        values.update(overrides)
        return Namespace(**values)

    def test_dataset_digest_is_deterministic(self) -> None:
        first = write_dataset_csv(self.data_path)
        second = first.copy()
        self.assertEqual(dataset_digest(first), dataset_digest(second))

    def test_mlflow_run_has_expected_data(self) -> None:
        result = run_training(self.args("mlflow"))

        import mlflow
        from mlflow.tracking import MlflowClient

        mlflow.set_tracking_uri(f"sqlite:///{(self.root / 'mlflow.db').as_posix()}")
        client = MlflowClient()
        run = client.get_run(result["run_id"])
        self.assertEqual(run.data.params["model"], "random_forest")
        self.assertIn("macro_f1", run.data.metrics)
        self.assertIn("dataset_digest", run.data.tags)
        model_artifacts = client.list_artifacts(result["run_id"], "model")
        evaluation_artifacts = client.list_artifacts(result["run_id"], "evaluation")
        self.assertTrue(model_artifacts)
        self.assertGreaterEqual(len(evaluation_artifacts), 2)

    def test_wandb_offline_run_completes(self) -> None:
        os.environ["WANDB_MODE"] = "offline"
        os.environ["WANDB_DIR"] = str(self.root / "wandb")
        os.environ["WANDB_DATA_DIR"] = str(self.root / "wandb-data")
        result = run_training(self.args("wandb", run_name="offline-test"))
        self.assertEqual(result["tracker"], "wandb")
        self.assertTrue(result["run_id"])
        self.assertTrue(Path(result["artifact_dir"]).exists())


if __name__ == "__main__":
    unittest.main()
