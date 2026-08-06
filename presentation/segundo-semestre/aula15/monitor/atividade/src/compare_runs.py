import argparse
import os


def main() -> None:
    import mlflow
    from mlflow.tracking import MlflowClient

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", default=os.getenv("MLFLOW_EXPERIMENT_NAME", "aula15_wine_tracking"))
    parser.add_argument("--metric", default="macro_f1")
    parser.add_argument("--tracking-uri", default=os.getenv("MLFLOW_TRACKING_URI"))
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    if args.tracking_uri:
        mlflow.set_tracking_uri(args.tracking_uri)
    client = MlflowClient()
    experiment = client.get_experiment_by_name(args.experiment)
    if experiment is None:
        raise SystemExit(f"Experimento não encontrado: {args.experiment}")
    runs = client.search_runs(
        [experiment.experiment_id],
        order_by=[f"metrics.{args.metric} DESC"],
        max_results=args.limit,
    )
    print(f"Runs ordenados por {args.metric}:")
    for run in runs:
        print(
            f"{run.info.run_id} | {run.data.tags.get('mlflow.runName', '')} | "
            f"{args.metric}={run.data.metrics.get(args.metric, 'n/a')} | "
            f"model={run.data.params.get('model', 'n/a')}"
        )


if __name__ == "__main__":
    main()
