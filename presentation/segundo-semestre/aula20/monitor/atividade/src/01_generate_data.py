"""
01_generate_data.py

Passo 1: Gera dataset sintético tabular de detecção de fraude em crédito.
Não há download externo — tudo é gerado localmente com NumPy/Pandas.
"""

from __future__ import annotations

import argparse
import os

import numpy as np
import pandas as pd

from src.utils import DATA_DIR, FEATURE_COLUMNS, TARGET_COLUMN, ensure_dirs


def generate_fraud_dataset(n_samples: int = 2500, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    idade = rng.normal(loc=40, scale=12, size=n_samples).clip(18, 80)
    renda = rng.normal(loc=62000, scale=18000, size=n_samples).clip(12000, 200000)
    score = rng.normal(loc=680, scale=75, size=n_samples).clip(300, 850)
    endividamento = rng.uniform(0.05, 0.85, size=n_samples)
    consultas = rng.poisson(lam=2.2, size=n_samples).clip(0, 20).astype(float)

    # Relação funcional: fraude mais provável com score baixo, endividamento alto e muitas consultas
    logit = (
        -0.03 * (idade - 40)
        - 0.00003 * (renda - 62000)
        - 0.018 * (score - 680)
        + 3.5 * endividamento
        + 0.35 * consultas
        - 2.8
    )
    prob = 1.0 / (1.0 + np.exp(-logit))
    fraude = (rng.random(n_samples) < prob).astype(int)

    # Modo de degradação intencional (exercício do gate)
    if os.environ.get("CI_DEGRADE", "0") == "1":
        # Embaralha ~45% dos rótulos → métricas caem e o gate deve falhar
        n_flip = int(0.45 * n_samples)
        idx = rng.choice(n_samples, size=n_flip, replace=False)
        fraude[idx] = 1 - fraude[idx]

    df = pd.DataFrame(
        {
            "idade": np.round(idade, 1),
            "renda_anual": np.round(renda, 2),
            "score_credito": np.round(score, 0),
            "taxa_endividamento": np.round(endividamento, 3),
            "num_consultas_90d": consultas,
            TARGET_COLUMN: fraude,
        }
    )
    assert list(df.columns) == FEATURE_COLUMNS + [TARGET_COLUMN]
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera dados sintéticos de fraude.")
    parser.add_argument("--n-samples", type=int, default=2500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--test-size", type=float, default=0.25)
    args = parser.parse_args()

    ensure_dirs()
    print("🚀 [Passo 1] Gerando dataset sintético de fraude em crédito...")

    df = generate_fraud_dataset(n_samples=args.n_samples, seed=args.seed)
    rng = np.random.default_rng(args.seed)
    mask = rng.random(len(df)) >= args.test_size
    train_df = df.loc[mask].reset_index(drop=True)
    test_df = df.loc[~mask].reset_index(drop=True)

    train_path = DATA_DIR / "train.csv"
    test_path = DATA_DIR / "test.csv"
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)

    rate = df[TARGET_COLUMN].mean()
    print(f"✅ Treino: {train_path} ({len(train_df)} linhas)")
    print(f"✅ Teste : {test_path} ({len(test_df)} linhas)")
    print(f"📊 Taxa de fraude (global): {rate:.3f}")
    if os.environ.get("CI_DEGRADE", "0") == "1":
        print("⚠️  CI_DEGRADE=1 ativo — rótulos corrompidos de propósito para falhar o gate.")
    print("👉 Próximo: python -m src.02_validate_data")


if __name__ == "__main__":
    main()
