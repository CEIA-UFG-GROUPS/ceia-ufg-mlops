"""Utilitários de benchmark de inferência.

Mede latência (p50/p95/p99) e throughput de uma função de inferência
qualquer. É a base de toda a prática: antes de otimizar, meça.

Conceitos importantes implementados aqui:

- **Warmup**: as primeiras execuções são descartadas — elas incluem custos
  que não se repetem em produção (compilação de kernels, alocação de
  memória, caches frios) e distorceriam a medição.
- **Percentis, não média**: a média esconde a cauda. SLOs de latência são
  definidos em p95/p99, porque é isso que os usuários "azarados" sentem.
- **perf_counter**: relógio monotônico de alta resolução, apropriado para
  medir intervalos curtos (time.time() tem resolução pior e pode "voltar").
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable

import numpy as np


@dataclass
class BenchmarkResult:
    """Resultado agregado de um benchmark de latência."""

    name: str
    n_iters: int
    latencies_ms: list[float]

    @property
    def p50(self) -> float:
        return float(np.percentile(self.latencies_ms, 50))

    @property
    def p95(self) -> float:
        return float(np.percentile(self.latencies_ms, 95))

    @property
    def p99(self) -> float:
        return float(np.percentile(self.latencies_ms, 99))

    @property
    def mean(self) -> float:
        return float(np.mean(self.latencies_ms))

    @property
    def throughput_per_s(self) -> float:
        """Itens processados por segundo (assumindo 1 item por chamada)."""
        total_s = sum(self.latencies_ms) / 1000.0
        return self.n_iters / total_s if total_s > 0 else float("inf")

    def row(self) -> str:
        return (
            f"{self.name:<28} p50={self.p50:8.2f}ms  p95={self.p95:8.2f}ms  "
            f"p99={self.p99:8.2f}ms  média={self.mean:8.2f}ms"
        )


def benchmark(
    fn: Callable[[], object],
    name: str = "inference",
    n_iters: int = 50,
    warmup: int = 5,
) -> BenchmarkResult:
    """Executa ``fn`` repetidamente e coleta as latências individuais.

    Args:
        fn: função sem argumentos que executa UMA inferência. Se estiver
            medindo GPU, a função deve sincronizar internamente
            (ex.: ``torch.cuda.synchronize()``) — chamadas CUDA são
            assíncronas e, sem sincronizar, você mede só o tempo de
            enfileirar o kernel, não de executá-lo.
        name: rótulo para exibição.
        n_iters: número de medições após o warmup.
        warmup: execuções descartadas no início.
    """
    for _ in range(warmup):
        fn()

    latencies: list[float] = []
    for _ in range(n_iters):
        t0 = time.perf_counter()
        fn()
        latencies.append((time.perf_counter() - t0) * 1000.0)

    return BenchmarkResult(name=name, n_iters=n_iters, latencies_ms=latencies)


def compare(results: list[BenchmarkResult], baseline: str | None = None) -> None:
    """Imprime uma tabela comparativa, com speedup relativo ao baseline."""
    base = None
    if baseline is not None:
        base = next((r for r in results if r.name == baseline), None)

    print(f"{'variante':<28} {'p50 (ms)':>10} {'p95 (ms)':>10} {'p99 (ms)':>10} {'speedup':>9}")
    print("-" * 72)
    for r in results:
        speedup = f"{base.p50 / r.p50:8.2f}x" if base else "     -"
        print(f"{r.name:<28} {r.p50:>10.2f} {r.p95:>10.2f} {r.p99:>10.2f} {speedup:>9}")
