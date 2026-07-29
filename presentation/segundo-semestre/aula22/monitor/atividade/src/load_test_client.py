"""
Script 3: cliente de carga simples. Dispara N requisições contra o Gateway e
tabula a distribuição de respostas entre champion/canary, além de reportar a
taxa de divergência acumulada quando a estratégia ativa é "shadow".

Uso:
    python -m src.load_test_client
    N_REQUESTS=500 python -m src.load_test_client
"""

import collections
import os

import httpx

GATEWAY_URL = os.environ.get("GATEWAY_URL", "http://localhost:8000")
N_REQUESTS = int(os.environ.get("N_REQUESTS", "200"))


def main():
    contagem = collections.Counter()

    with httpx.Client(timeout=5.0) as client:
        strategy = client.get(f"{GATEWAY_URL}/health").json().get("strategy")

        for i in range(N_REQUESTS):
            payload = {"features": [i % 5 - 2, (i * 3) % 7 - 3]}
            resp = client.post(f"{GATEWAY_URL}/predict", json=payload)
            body = resp.json()
            versao = body.get("version", "desconhecida")
            contagem[versao] += 1

        stats = client.get(f"{GATEWAY_URL}/shadow/stats").json()

    print(f"\nEstratégia ativa no gateway: {strategy}")
    print(f"Resultado após {N_REQUESTS} requisições ao Gateway ({GATEWAY_URL}):")
    for versao, total in contagem.items():
        pct = 100 * total / N_REQUESTS
        print(f"  {versao}: {total} respostas ({pct:.1f}%)")

    if stats.get("total_comparacoes"):
        print(f"\n[Shadow] Comparações realizadas: {stats['total_comparacoes']}")
        print(f"[Shadow] Taxa de divergência champion vs. shadow: {stats['taxa_divergencia'] * 100:.2f}%")


if __name__ == "__main__":
    main()
