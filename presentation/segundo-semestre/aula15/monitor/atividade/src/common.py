import hashlib
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Mapping

import pandas as pd


def activity_root() -> Path:
    return Path(__file__).resolve().parents[1]


def dataset_digest(dataframe: pd.DataFrame) -> str:
    """Calcula um digest determinístico do conteúdo e das colunas do dataset."""

    payload = dataframe.to_csv(index=False, lineterminator="\n").encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def write_dataset_csv(path: Path) -> pd.DataFrame:
    """Materializa o dataset Wine sem depender de download externo."""

    from sklearn.datasets import load_wine

    wine = load_wine(as_frame=True)
    dataframe = wine.frame.copy()
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, index=False)
    return dataframe


def git_commit(path: Path | None = None) -> str:
    """Retorna o commit Git atual ou ``unknown`` fora de um checkout."""

    try:
        output = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(path or activity_root()),
            check=True,
            capture_output=True,
            text=True,
        )
        return output.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def dvc_metadata(data_path: Path) -> dict[str, str]:
    """Lê metadados opcionais de um ponteiro DVC próximo ao dataset.

    O laboratório não inicializa um repositório DVC aninhado. Se o estudante
    executar ``dvc add`` em um workspace isolado e deixar o ponteiro ao lado do
    dataset, o hash será automaticamente associado ao run.
    """

    pointer_path = Path(os.getenv("DVC_POINTER", f"{data_path}.dvc"))
    if not pointer_path.exists():
        return {}

    text = pointer_path.read_text(encoding="utf-8")
    metadata: dict[str, str] = {"dvc_pointer": str(pointer_path)}
    md5_match = re.search(r"\bmd5:\s*([0-9a-fA-F]{32})", text)
    rev_match = re.search(r"\brev:\s*([^\s#]+)", text)
    if md5_match:
        metadata["dvc_md5"] = md5_match.group(1)
    if rev_match:
        metadata["dvc_revision"] = rev_match.group(1)
    return metadata


class TrackingSession:
    """Interface mínima compartilhada por MLflow e W&B."""

    run_id: str = "unknown"

    def __enter__(self) -> "TrackingSession":
        raise NotImplementedError

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        raise NotImplementedError

    def log_params(self, values: Mapping[str, Any]) -> None:
        raise NotImplementedError

    def log_metrics(self, values: Mapping[str, float]) -> None:
        raise NotImplementedError

    def log_tags(self, values: Mapping[str, Any]) -> None:
        raise NotImplementedError

    def log_artifact(self, path: Path, artifact_type: str = "output") -> None:
        raise NotImplementedError

    def log_dataset(self, path: Path) -> None:
        raise NotImplementedError


class MLflowSession(TrackingSession):
    def __init__(
        self,
        experiment_name: str,
        run_name: str,
        tracking_uri: str | None,
        params: Mapping[str, Any],
        tags: Mapping[str, Any],
    ) -> None:
        self.experiment_name = experiment_name
        self.run_name = run_name
        self.tracking_uri = tracking_uri
        self.params = dict(params)
        self.tags = {key: str(value) for key, value in tags.items()}
        self._mlflow: Any = None
        self._run: Any = None

    def __enter__(self) -> "MLflowSession":
        import mlflow

        self._mlflow = mlflow
        tracking_uri = self.tracking_uri
        if not tracking_uri:
            database = activity_root() / ".mlflow" / "mlflow.db"
            database.parent.mkdir(parents=True, exist_ok=True)
            tracking_uri = f"sqlite:///{database.as_posix()}"
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(self.experiment_name)
        self._run = mlflow.start_run(run_name=self.run_name)
        self.run_id = self._run.info.run_id
        self.log_params(self.params)
        self.log_tags(self.tags)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self._mlflow is not None:
            self._mlflow.end_run(status="FAILED" if exc_type else "FINISHED")

    def log_params(self, values: Mapping[str, Any]) -> None:
        cleaned = {key: "None" if value is None else value for key, value in values.items()}
        self._mlflow.log_params(cleaned)

    def log_metrics(self, values: Mapping[str, float]) -> None:
        self._mlflow.log_metrics({key: float(value) for key, value in values.items()})

    def log_tags(self, values: Mapping[str, Any]) -> None:
        self._mlflow.set_tags({key: str(value) for key, value in values.items()})

    def log_artifact(self, path: Path, artifact_type: str = "output") -> None:
        self._mlflow.log_artifact(str(path), artifact_path=artifact_type)

    def log_dataset(self, path: Path) -> None:
        try:
            dataset = self._mlflow.data.from_pandas(
                pd.read_csv(path),
                source=str(path),
                name=path.stem,
                targets="target",
            )
            self._mlflow.log_input(dataset, context="training")
        except (AttributeError, TypeError, ValueError):
            # Mantém compatibilidade com instalações antigas do MLflow.
            self._mlflow.log_artifact(str(path), artifact_path="dataset")


class WandbSession(TrackingSession):
    def __init__(
        self,
        project: str,
        run_name: str,
        mode: str | None,
        params: Mapping[str, Any],
        tags: Mapping[str, Any],
        entity: str | None = None,
    ) -> None:
        self.project = project
        self.run_name = run_name
        self.mode = mode
        self.params = dict(params)
        self.tags_map = dict(tags)
        self.tags = [f"{key}:{str(value)[:48]}"[:64] for key, value in tags.items()]
        self.entity = entity
        self._wandb: Any = None
        self._run: Any = None

    def __enter__(self) -> "WandbSession":
        import wandb

        self._wandb = wandb
        effective_mode = self.mode or os.getenv("WANDB_MODE")
        if effective_mode is None and not os.getenv("WANDB_API_KEY"):
            effective_mode = "offline"
        run_dir = Path(os.getenv("WANDB_DIR", activity_root() / "wandb")).resolve()
        run_dir.mkdir(parents=True, exist_ok=True)
        data_dir = Path(os.getenv("WANDB_DATA_DIR", run_dir / "data")).resolve()
        data_dir.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("WANDB_DATA_DIR", str(data_dir))
        for variable, directory in {
            "WANDB_CONFIG_DIR": run_dir / "config",
            "WANDB_CACHE_DIR": run_dir / "cache",
            "WANDB_ARTIFACT_DIR": run_dir / "artifacts",
        }.items():
            Path(directory).mkdir(parents=True, exist_ok=True)
            os.environ.setdefault(variable, str(directory))
        self._run = wandb.init(
            project=self.project,
            name=self.run_name,
            entity=self.entity or os.getenv("WANDB_ENTITY"),
            dir=str(run_dir),
            config={key: "None" if value is None else value for key, value in self.params.items()},
            tags=self.tags,
            mode=effective_mode,
        )
        self.run_id = getattr(self._run, "id", "offline")
        self.log_tags(self.tags_map)
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        if self._run is not None:
            self._run.finish(exit_code=1 if exc_type else 0)

    def log_params(self, values: Mapping[str, Any]) -> None:
        self._run.config.update(dict(values), allow_val_change=True)

    def log_metrics(self, values: Mapping[str, float]) -> None:
        self._run.log({key: float(value) for key, value in values.items()})

    def log_tags(self, values: Mapping[str, Any]) -> None:
        self._run.config.update({f"tag_{key}": str(value) for key, value in values.items()}, allow_val_change=True)

    def log_artifact(self, path: Path, artifact_type: str = "output") -> None:
        artifact = self._wandb.Artifact(
            name=f"{self.run_name}-{artifact_type}",
            type=artifact_type,
        )
        artifact.add_file(str(path), name=path.name)
        self._run.log_artifact(artifact)

    def log_dataset(self, path: Path) -> None:
        self.log_artifact(path, artifact_type="dataset")


def create_session(
    tracker: str,
    *,
    experiment_name: str,
    run_name: str,
    tracking_uri: str | None,
    wandb_project: str,
    wandb_mode: str | None,
    wandb_entity: str | None,
    params: Mapping[str, Any],
    tags: Mapping[str, Any],
) -> TrackingSession:
    if tracker == "mlflow":
        return MLflowSession(experiment_name, run_name, tracking_uri, params, tags)
    if tracker == "wandb":
        return WandbSession(wandb_project, run_name, wandb_mode, params, tags, wandb_entity)
    raise ValueError(f"Tracker desconhecido: {tracker}")
