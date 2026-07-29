"""Teste de carga do serviço de classificação (BentoML).

Dispara N requisições HTTP contra o serviço, controlando o nível de
concorrência, e reporta latência (p50/p95/p99) e throughput (RPS).

A ideia do experimento: cada requisição carrega **um único texto** —
como fariam clientes reais e independentes. O ganho de throughput em
concorrência alta vem do **adaptive batching do servidor**, que funde
as requisições em batches antes de chamar o modelo.

Experimento sugerido (compare os dois)::

    # baseline: 1 requisição por vez (sem chance de formar batch)
    python -m src.load_test --requests 200 --concurrency 1

    # 32 clientes simultâneos (o servidor forma batches de até 32)
    python -m src.load_test --requests 200 --concurrency 32

O que observar: com concorrência 32, o RPS deve subir muito, enquanto a
latência individual (p50) sobe pouco — esse é o trade-off do batching.
"""

from __future__ import annotations

import argparse
import asyncio
import time

import httpx
import numpy as np

# Frases variadas para evitar qualquer cache trivial no caminho.
SAMPLE_TEXTS = [
    "This class about model serving is amazing!",
    "The latency of this API is terrible.",
    "Quantization made my model so much faster.",
    "I hate waiting for cold starts.",
    "Continuous batching is a brilliant idea.",
    "The GPU ran out of memory again...",
    "Deploying with containers keeps things reproducible.",
    "My p99 latency exploded under load.",
]


async def _one_request(client: httpx.AsyncClient, url: str, text: str) -> float:
    """Envia uma requisição e retorna a latência em milissegundos."""
    t0 = time.perf_counter()
    response = await client.post(url, json={"texts": [text]})
    response.raise_for_status()
    return (time.perf_counter() - t0) * 1000.0


async def load_test(url: str, n_requests: int, concurrency: int) -> dict:
    """Executa o teste e retorna as métricas agregadas."""
    semaphore = asyncio.Semaphore(concurrency)

    async with httpx.AsyncClient(timeout=30.0) as client:

        async def bounded(i: int) -> float:
            async with semaphore:
                return await _one_request(client, url, SAMPLE_TEXTS[i % len(SAMPLE_TEXTS)])

        t0 = time.perf_counter()
        latencies = await asyncio.gather(*(bounded(i) for i in range(n_requests)))
        elapsed_s = time.perf_counter() - t0

    return {
        "n_requests": n_requests,
        "concurrency": concurrency,
        "elapsed_s": elapsed_s,
        "rps": n_requests / elapsed_s,
        "p50_ms": float(np.percentile(latencies, 50)),
        "p95_ms": float(np.percentile(latencies, 95)),
        "p99_ms": float(np.percentile(latencies, 99)),
    }


def print_report(metrics: dict) -> None:
    print()
    print(f"requisições : {metrics['n_requests']}")
    print(f"concorrência: {metrics['concurrency']}")
    print(f"tempo total : {metrics['elapsed_s']:.2f} s")
    print(f"throughput  : {metrics['rps']:.1f} req/s")
    print(f"latência    : p50={metrics['p50_ms']:.1f} ms  "
          f"p95={metrics['p95_ms']:.1f} ms  p99={metrics['p99_ms']:.1f} ms")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default="http://localhost:3000/classify")
    parser.add_argument("--requests", type=int, default=200)
    parser.add_argument("--concurrency", type=int, default=1)
    args = parser.parse_args()

    print(f"Disparando {args.requests} requisições contra {args.url} "
          f"(concorrência={args.concurrency})...")
    metrics = asyncio.run(load_test(args.url, args.requests, args.concurrency))
    print_report(metrics)


if __name__ == "__main__":
    main()
