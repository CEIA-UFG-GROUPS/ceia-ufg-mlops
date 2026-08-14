"""
02_validate_data.py

Passo 2: Quality gate de dados — schema, nulos e faixas válidas (pandas asserts).
Exit code != 0 se a validação falhar (bloqueia o restante do pipeline).
"""

from __future__ import annotations

import sys

import pandas as pd

from src.utils import DATA_DIR, FEATURE_COLUMNS, REQUIRED_COLUMNS, TARGET_COLUMN


def validate_frame(df: pd.DataFrame, name: str) -> None:
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise AssertionError(f"[{name}] Colunas ausentes: {missing}")

    extra = [c for c in df.columns if c not in REQUIRED_COLUMNS]
    if extra:
        raise AssertionError(f"[{name}] Colunas inesperadas: {extra}")

    if len(df) < 100:
        raise AssertionError(f"[{name}] Poucas linhas ({len(df)}); mínimo esperado: 100")

    nulls = df[REQUIRED_COLUMNS].isna().sum()
    if nulls.any():
        raise AssertionError(f"[{name}] Nulos detectados:\n{nulls[nulls > 0]}")

    if not ((df["idade"] >= 18) & (df["idade"] <= 100)).all():
        raise AssertionError(f"[{name}] idade fora de [18, 100]")
    if not ((df["renda_anual"] >= 5000) & (df["renda_anual"] <= 500000)).all():
        raise AssertionError(f"[{name}] renda_anual fora de [5000, 500000]")
    if not ((df["score_credito"] >= 300) & (df["score_credito"] <= 850)).all():
        raise AssertionError(f"[{name}] score_credito fora de [300, 850]")
    if not ((df["taxa_endividamento"] >= 0) & (df["taxa_endividamento"] <= 1)).all():
        raise AssertionError(f"[{name}] taxa_endividamento fora de [0, 1]")
    if not ((df["num_consultas_90d"] >= 0) & (df["num_consultas_90d"] <= 50)).all():
        raise AssertionError(f"[{name}] num_consultas_90d fora de [0, 50]")
    if not df[TARGET_COLUMN].isin([0, 1]).all():
        raise AssertionError(f"[{name}] {TARGET_COLUMN} deve ser binário {{0,1}}")

    # Features numéricas
    for col in FEATURE_COLUMNS:
        if not pd.api.types.is_numeric_dtype(df[col]):
            raise AssertionError(f"[{name}] Coluna {col} não é numérica")


def main() -> None:
    print("🚀 [Passo 2] Validando schema, nulos e faixas dos dados...")
    train_path = DATA_DIR / "train.csv"
    test_path = DATA_DIR / "test.csv"

    if not train_path.exists() or not test_path.exists():
        print("❌ Arquivos de dados ausentes. Execute antes: python -m src.01_generate_data")
        sys.exit(1)

    train_df = pd.read_csv(train_path)
    test_df = pd.read_csv(test_path)

    try:
        validate_frame(train_df, "train")
        validate_frame(test_df, "test")
    except AssertionError as exc:
        print(f"❌ Gate de dados FALHOU: {exc}")
        sys.exit(1)

    print("✅ Gate de dados OK (schema + ranges + nulls)")
    print("👉 Próximo: python -m src.03_train_model")


if __name__ == "__main__":
    main()
