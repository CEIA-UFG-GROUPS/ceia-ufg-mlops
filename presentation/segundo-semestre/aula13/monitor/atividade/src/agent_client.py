"""Cliente MCP mínimo — simula o que um AGENTE faz por baixo dos panos.

Claude Code, Cursor, VS Code/Copilot e afins são clientes MCP: eles (1) abrem
uma sessão, (2) descobrem tools/resources/prompts, (3) chamam o que precisam.
Este script faz exatamente esses três passos, para você VER o loop sem depender
de um cliente pago.

Uso:
    # 1) contra o servidor remoto (Streamable HTTP — Docker):
    python src/agent_client.py

    # 2) contra o servidor local subido como subprocesso (stdio):
    MCP_CLIENT_MODE=stdio python src/agent_client.py

Config:
    MCP_CLIENT_MODE = http | stdio        (padrão: http)
    MCP_URL         = http://localhost:8000/mcp   (modo http)
"""

from __future__ import annotations

import asyncio
import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.streamable_http import streamablehttp_client

# Uma transação suspeita: valor alto, 3h da manhã, conta nova, exterior, longe.
SUSPICIOUS_TX = {
    "amount": 4200.0,
    "hour_of_day": 3,
    "num_tx_last_hour": 6,
    "account_age_days": 9,
    "is_foreign": 1,
    "distance_from_home_km": 830.0,
}


async def drive(session: ClientSession) -> None:
    """Executa o loop que um agente faz: initialize -> discover -> call."""
    await session.initialize()

    # 1) DESCOBERTA — o agente pergunta o que o servidor oferece.
    tools = await session.list_tools()
    print("Tools descobertas:", [t.name for t in tools.tools])

    resources = await session.list_resources()
    print("Resources:", [str(r.uri) for r in resources.resources])

    # 2) CONTEXTO — lê o model card (resource read-only).
    card = await session.read_resource("model://fraud-detector/card")
    print("\n--- Model card (trecho) ---")
    print(card.contents[0].text[:300], "...")

    # 3) AÇÃO — chama a tool `predict` na transação suspeita.
    result = await session.call_tool("predict", SUSPICIOUS_TX)
    print("\n--- Resultado da predição ---")
    # structuredContent traz o dict tipado quando disponível; senão, o texto.
    print(result.structuredContent or result.content[0].text)


async def main() -> None:
    mode = os.getenv("MCP_CLIENT_MODE", "http")

    if mode == "stdio":
        # Sobe o servidor como subprocesso (é o que Claude Desktop/Code fazem localmente).
        params = StdioServerParameters(command="python", args=["src/mcp_server.py"])
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await drive(session)
    else:
        url = os.getenv("MCP_URL", "http://localhost:8000/mcp")
        print(f"Conectando ao servidor remoto em {url}")
        async with streamablehttp_client(url) as (read, write, _):
            async with ClientSession(read, write) as session:
                await drive(session)


if __name__ == "__main__":
    asyncio.run(main())
