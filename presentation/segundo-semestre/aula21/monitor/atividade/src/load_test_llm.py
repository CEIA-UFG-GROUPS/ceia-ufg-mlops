"""Teste de carga de um servidor de LLM OpenAI-compatible (ex.: vLLM).

Mede as duas métricas que definem a experiência de um LLM servido:

- **TTFT (Time To First Token)** — tempo até o primeiro token chegar.
  Dominado pela fase de *prefill* (processar o prompt) + tempo de fila.
- **TPOT (Time Per Output Token)** — tempo médio entre tokens após o
  primeiro. Dominado pela fase de *decode*, que é memory-bound.

As medições usam **streaming**: sem streaming só dá para medir a
latência total, e TTFT/TPOT ficam invisíveis.

Experimento sugerido (com o serviço `vllm` do docker-compose no ar)::

    # 1 requisição por vez
    python -m src.load_test_llm --requests 8 --concurrency 1

    # 8 simultâneas: o continuous batching processa todas juntas
    python -m src.load_test_llm --requests 8 --concurrency 8

O que observar: com concorrência 8, o tempo total cai drasticamente
(throughput agregado em tokens/s cresce), enquanto o TPOT individual
piora pouco — é o continuous batching preenchendo a GPU.
"""

from __future__ import annotations

import argparse
import asyncio
import time

import numpy as np
from openai import AsyncOpenAI

PROMPTS = [
    "Explique em duas frases o que é latência p99.",
    "Por que a inferência de LLMs é limitada pela memória?",
    "O que é quantização de modelos? Responda brevemente.",
    "Explique o trade-off entre latência e throughput.",
    "O que é KV cache em um transformer?",
    "Para que serve o continuous batching?",
    "Qual a diferença entre prefill e decode?",
    "O que é um SLO de latência? Dê um exemplo.",
]


async def _one_request(client: AsyncOpenAI, model: str, prompt: str, max_tokens: int) -> dict:
    """Faz uma chamada em streaming e cronometra TTFT/TPOT."""
    t0 = time.perf_counter()
    first_token_at: float | None = None
    n_tokens = 0

    stream = await client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7,
        stream=True,
    )
    async for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            if first_token_at is None:
                first_token_at = time.perf_counter()
            n_tokens += 1

    total_s = time.perf_counter() - t0
    ttft_s = (first_token_at - t0) if first_token_at else total_s
    decode_s = total_s - ttft_s
    return {
        "ttft_ms": ttft_s * 1000.0,
        # TPOT: tempo médio entre tokens após o primeiro.
        "tpot_ms": (decode_s / max(n_tokens - 1, 1)) * 1000.0,
        "n_tokens": n_tokens,
        "total_s": total_s,
    }


async def load_test(base_url: str, model: str, n_requests: int,
                    concurrency: int, max_tokens: int) -> None:
    client = AsyncOpenAI(base_url=base_url, api_key="não-usado-pelo-vllm")
    semaphore = asyncio.Semaphore(concurrency)

    async def bounded(i: int) -> dict:
        async with semaphore:
            return await _one_request(client, model, PROMPTS[i % len(PROMPTS)], max_tokens)

    t0 = time.perf_counter()
    results = await asyncio.gather(*(bounded(i) for i in range(n_requests)))
    elapsed_s = time.perf_counter() - t0

    ttfts = [r["ttft_ms"] for r in results]
    tpots = [r["tpot_ms"] for r in results]
    total_tokens = sum(r["n_tokens"] for r in results)

    print()
    print(f"requisições     : {n_requests}  (concorrência={concurrency})")
    print(f"tempo total     : {elapsed_s:.2f} s")
    print(f"tokens gerados  : {total_tokens}")
    print(f"throughput      : {total_tokens / elapsed_s:.1f} tokens/s (agregado)")
    print(f"TTFT            : p50={np.percentile(ttfts, 50):.0f} ms  "
          f"p95={np.percentile(ttfts, 95):.0f} ms")
    print(f"TPOT            : p50={np.percentile(tpots, 50):.1f} ms  "
          f"p95={np.percentile(tpots, 95):.1f} ms")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-url", default="http://localhost:8000/v1")
    parser.add_argument("--model", default="Qwen/Qwen2.5-0.5B-Instruct")
    parser.add_argument("--requests", type=int, default=8)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--max-tokens", type=int, default=128)
    args = parser.parse_args()

    print(f"Disparando {args.requests} requisições contra {args.base_url} "
          f"(modelo={args.model}, concorrência={args.concurrency})...")
    asyncio.run(load_test(args.base_url, args.model, args.requests,
                          args.concurrency, args.max_tokens))


if __name__ == "__main__":
    main()
