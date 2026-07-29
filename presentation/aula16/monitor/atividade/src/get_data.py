"""Gera o dataset "bruto" da prática.

Na vida real, esta etapa seria uma extração de banco, uma API, um sensor —
qualquer fonte externa. Aqui geramos dados sintéticos de classificação para
o laboratório ser auto-contido e rápido.

Ponto pedagógico importante: a saída deste script (``data/raw/data.csv``) é
tratada como **dado FONTE** — ela é versionada com ``dvc add``, e NÃO como
estágio do pipeline. A regra de bolso:

- dado **fonte** (chega de fora, é imutável): ``dvc add``
- dado **derivado** (produzido a partir da fonte): ``outs`` de um estágio
  no ``dvc.yaml``, regenerável com ``dvc repro``

Para simular a "chegada de dados novos" (uma nova versão do dataset),
re-execute com outros argumentos::

    python src/get_data.py                       # v1: 2000 amostras
    python src/get_data.py --samples 4000        # v2: "chegou mais dado"
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
from sklearn.datasets import make_classification


def generate(samples: int, seed: int, output: Path) -> None:
    features, target = make_classification(
        n_samples=samples,
        n_features=10,
        n_informative=6,
        n_redundant=2,
        n_classes=2,
        flip_y=0.05,       # um pouco de ruído nos rótulos, como na vida real
        random_state=seed,
    )
    df = pd.DataFrame(features, columns=[f"feature_{i}" for i in range(features.shape[1])])
    df["target"] = target

    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    print(f"Dataset gerado: {output}  ({len(df)} linhas, {output.stat().st_size / 1024:.1f} KB)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--samples", type=int, default=2000, help="Número de amostras")
    parser.add_argument("--seed", type=int, default=42, help="Semente aleatória")
    parser.add_argument("--output", type=Path, default=Path("data/raw/data.csv"))
    args = parser.parse_args()

    generate(args.samples, args.seed, args.output)


if __name__ == "__main__":
    main()
