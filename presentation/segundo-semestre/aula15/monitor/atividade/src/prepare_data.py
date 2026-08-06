import argparse
from pathlib import Path

from .common import activity_root, dataset_digest, write_dataset_csv


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=activity_root() / "data" / "wine.csv")
    args = parser.parse_args()
    dataframe = write_dataset_csv(args.output)
    print(f"Dataset escrito em: {args.output}")
    print(f"Linhas: {len(dataframe)} | Colunas: {len(dataframe.columns)}")
    print(f"Digest SHA-256: {dataset_digest(dataframe)}")


if __name__ == "__main__":
    main()
