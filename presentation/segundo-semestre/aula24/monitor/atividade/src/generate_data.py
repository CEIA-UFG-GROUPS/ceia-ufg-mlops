import argparse

from .common import dataset_digest, make_credit_dataset, save_dataset


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=1200)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    dataframe = make_credit_dataset(args.samples, args.seed)
    path = save_dataset(dataframe)
    print(f"Dataset escrito em: {path}")
    print(f"Linhas: {len(dataframe)} | Digest SHA-256: {dataset_digest(dataframe)}")
    print("Colunas protegidas para auditoria: protected_group")


if __name__ == "__main__":
    main()
