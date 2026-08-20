"""Gerador do dataset sintético de crédito, com injeção controlada de defeitos.

Cada defeito foi desenhado para violar UMA expectativa do contrato. Isso deixa
o mapeamento defeito → expectativa visível em aula, em vez de produzir um
relatório vermelho genérico.
"""

from __future__ import annotations

import argparse
from typing import Iterable

import numpy as np
import pandas as pd

from .common import DATA_DIR, RANDOM_SEED

DEFECTS = {
    "nulls": "nulos em renda_anual → expect_column_values_to_not_be_null",
    "ranges": "idades 150 e 7 → expect_column_values_to_be_between",
    "schema": "score_credito renomeada → expect_table_columns_to_match_set",
    "dups": "id_cliente duplicado → expect_column_values_to_be_unique",
    "labels": "rótulo 2 → expect_column_values_to_be_in_set",
    "drift": "renda_anual +60% → expect_column_mean_to_be_between",
}


def generate_clean(n_rows: int = 4000, seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Gera um dataset que satisfaz o contrato `credito_v1`."""
    rng = np.random.default_rng(seed)

    idade = rng.integers(18, 80, size=n_rows)
    renda_anual = np.clip(rng.lognormal(mean=11.0, sigma=0.45, size=n_rows), 5000, 500000)
    score_credito = rng.integers(300, 851, size=n_rows)
    taxa_endividamento = np.clip(rng.beta(2.0, 5.0, size=n_rows), 0.0, 1.0)
    num_consultas_90d = rng.poisson(3.0, size=n_rows).clip(0, 50)

    # Rótulo gerado por um modelo logístico explícito: garante que o sinal de
    # cada feature seja conhecido, o que torna possível escrever testes de
    # expectativa direcional sobre o modelo treinado.
    logito = (
        -1.10
        - 3.20 * (score_credito - 300) / 550
        + 2.60 * taxa_endividamento
        + 0.11 * num_consultas_90d
        - 0.80 * (np.log(renda_anual) - 11.0)
        + 0.010 * (idade - 45)
    )
    prob = 1.0 / (1.0 + np.exp(-logito))
    inadimplente = (rng.random(n_rows) < prob).astype(np.int64)

    return pd.DataFrame(
        {
            "id_cliente": np.arange(1, n_rows + 1, dtype=np.int64),
            "idade": idade.astype(np.int64),
            "renda_anual": renda_anual.astype(np.float64).round(2),
            "score_credito": score_credito.astype(np.int64),
            "taxa_endividamento": taxa_endividamento.astype(np.float64).round(4),
            "num_consultas_90d": num_consultas_90d.astype(np.int64),
            "inadimplente": inadimplente,
        }
    )


def inject(df: pd.DataFrame, defects: Iterable[str], seed: int = RANDOM_SEED) -> pd.DataFrame:
    """Aplica os defeitos pedidos sobre uma cópia do dataset."""
    rng = np.random.default_rng(seed + 1)
    out = df.copy()

    for defect in defects:
        if defect not in DEFECTS:
            raise ValueError(f"Defeito desconhecido: {defect}. Use: {sorted(DEFECTS)}")

        if defect == "nulls":
            idx = rng.choice(out.index, size=max(1, len(out) // 40), replace=False)
            out.loc[idx, "renda_anual"] = np.nan

        elif defect == "ranges":
            out.loc[out.index[:12], "idade"] = 150
            out.loc[out.index[12:24], "idade"] = 7

        elif defect == "schema":
            out = out.rename(columns={"score_credito": "credit_score"})

        elif defect == "dups":
            out.loc[out.index[-20:], "id_cliente"] = out.loc[out.index[0], "id_cliente"]

        elif defect == "labels":
            out.loc[out.index[:30], "inadimplente"] = 2

        elif defect == "drift":
            out["renda_anual"] = (out["renda_anual"] * 1.6).round(2)

    return out


def build_variant(variant: str, defects: list[str] | None, n_rows: int, seed: int) -> pd.DataFrame:
    clean = generate_clean(n_rows=n_rows, seed=seed)
    if variant == "clean":
        return clean
    chosen = defects or sorted(DEFECTS)
    return inject(clean, chosen, seed=seed)


def main() -> None:
    parser = argparse.ArgumentParser(description="Gera dados sintéticos da Aula 14")
    parser.add_argument("--variant", choices=["clean", "corrupted"], default="clean")
    parser.add_argument(
        "--defect",
        action="append",
        choices=sorted(DEFECTS),
        help="Defeito a injetar (repetível). Sem esta flag, 'corrupted' injeta todos.",
    )
    parser.add_argument("--rows", type=int, default=4000)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    args = parser.parse_args()

    df = build_variant(args.variant, args.defect, args.rows, args.seed)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DATA_DIR / f"credito_{args.variant}.csv"
    df.to_csv(path, index=False)

    aplicados = args.defect or (sorted(DEFECTS) if args.variant == "corrupted" else [])
    print(f"✅ {path.relative_to(path.parents[2])} — {len(df)} linhas, {len(df.columns)} colunas")
    if aplicados:
        print("   defeitos injetados:")
        for d in aplicados:
            print(f"   - {d}: {DEFECTS[d]}")
    print("👉 Próximo: python -m src.validate_data --dataset " + args.variant)


if __name__ == "__main__":
    main()
