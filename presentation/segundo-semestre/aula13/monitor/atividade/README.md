# 🧪 Atividade Prática — Aula 13: Configurando um Servidor MCP

Nesta prática você constrói um **servidor MCP de MLOps**: ele expõe um modelo de
detecção de fraude (e seus metadados) como **tools, resources e prompts** que
**qualquer agente MCP** consegue descobrir e usar — Claude Code, Cursor, VS Code
(Copilot), Windsurf, Claude Desktop ou o cliente Python incluído.

A ideia central da aula em uma frase: **você escreve o servidor uma vez e todos os
agentes passam a "enxergar" seu modelo** — sem integração sob medida por cliente.

O ciclo completo:

**servidor local (stdio) → depurar no MCP Inspector → conectar num coding agent →
levar para remoto (Streamable HTTP + Docker) → dirigir com um cliente-agente**

| Caminho | Para quem | Requisitos | Transporte |
|---|---|---|---|
| **A. Local + Inspector** | Quer entender as primitivas e depurar | Python 3.11+ (e Node, p/ o Inspector) | **stdio** |
| **B. Remoto + Docker** | Quer o fluxo de time (servidor compartilhado) | Docker | **Streamable HTTP** |

> O **servidor é o mesmo** nos dois caminhos: só muda a variável `MCP_TRANSPORT`.

---

## 🎯 O que você vai fazer

1. **Treinar** um modelo didático de fraude (`train_model.py`) → gera `model.pkl` + `model_card.json`.
2. **Expor** esse modelo com um servidor MCP (`mcp_server.py`): tools `predict`, `list_models`, `get_model_card`; resources `model://.../card` e `dataset://schema`; prompt `investigate_alert`.
3. **Depurar** no **MCP Inspector** (`mcp dev`), vendo as tools/resources sem escrever cliente.
4. **Conectar** o servidor a um coding agent (Claude Code / Cursor / VS Code) via config.
5. **Levar para remoto** com Docker (Streamable HTTP) e **dirigir** com `agent_client.py`, que faz o loop de um agente (initialize → discover → call).

O modelo é leve de propósito: o assunto é o **servidor MCP e seu consumo por agentes**, não o modelo.

---

## 📂 Estrutura

```text
atividade/
├── README.md                 # este arquivo
├── requirements.txt          # mcp[cli] (pinado <2) + sklearn
├── src/
│   ├── train_model.py        # treina o modelo e gera o model card
│   ├── mcp_server.py         # o SERVIDOR MCP (tools + resources + prompts)
│   └── agent_client.py       # cliente que simula o loop de um agente
├── models/                   # artefatos gerados (model.pkl, model_card.json)
└── docker/
    ├── Dockerfile            # imagem do servidor (treina no build)
    └── docker-compose.yml    # mcp-server (HTTP) + agent (demo, sob demanda)
```

> ⚠️ **Versão do SDK**: o lab fixa `mcp[cli]>=1.27,<2`. O **v2 estável** saiu em
> **2026-07-27** e **renomeia a classe** do servidor (`from mcp.server import MCPServer`,
> em vez de `from mcp.server.fastmcp import FastMCP`). Pinar mantém o código
> reprodutível — ver o README do monitor para a nota de migração.

---

## 🅰️ Caminho A — Local (stdio) + MCP Inspector

### A.1 — Ambiente e treino

```bash
cd atividade
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/train_model.py                            # gera models/model.pkl e model_card.json
```

### A.2 — Depurar no MCP Inspector

O **Inspector** é a ferramenta oficial para inspecionar um servidor sem precisar
de um cliente: você vê as tools, seus schemas, e pode chamá-las na mão.

```bash
mcp dev src/mcp_server.py        # abre o Inspector no navegador (requer Node/npx)
```

No Inspector: aba **Tools** → chame `predict` com uma transação suspeita
(ex.: `amount=4200, hour_of_day=3, num_tx_last_hour=6, account_age_days=9,
is_foreign=1, distance_from_home_km=830`) e veja a `fraud_probability`.
Aba **Resources** → leia `model://fraud-detector/card`.

### A.3 — O loop de um agente, em Python

Sem Inspector, o `agent_client.py` sobe o servidor como subprocesso (é o que um
cliente local faz) e executa o loop: **initialize → list_tools → read_resource → call_tool**.

```bash
MCP_CLIENT_MODE=stdio python src/agent_client.py
```

Saída esperada (resumida):

```text
Tools descobertas: ['predict', 'list_models', 'get_model_card']
--- Resultado da predição ---
{ "is_fraud": true, "fraud_probability": 0.8357, "model": "fraud-detector:1.0.0" }
```

---

## 🔌 Conectar a um coding agent (contexto 2026)

Todo coding agent sério é um **cliente MCP**. O servidor é o mesmo; muda só **onde
fica a config e o formato**. Com o servidor rodando localmente por stdio:

### Claude Code (CLI)

```bash
claude mcp add mlops -- python /CAMINHO/ABSOLUTO/atividade/src/mcp_server.py
# depois, dentro do Claude Code: /mcp   para ver as tools; peça "avalie esta transação..."
```

### Cursor — `.cursor/mcp.json` (projeto) ou `~/.cursor/mcp.json` (global)

```json
{
  "mcpServers": {
    "mlops": {
      "command": "python",
      "args": ["/CAMINHO/ABSOLUTO/atividade/src/mcp_server.py"]
    }
  }
}
```

### VS Code (GitHub Copilot, agent mode) — `.vscode/mcp.json`

```json
{
  "servers": {
    "mlops": {
      "command": "python",
      "args": ["/CAMINHO/ABSOLUTO/atividade/src/mcp_server.py"]
    }
  }
}
```

> **Pegadinhas comuns**: VS Code usa a chave `servers` (os outros usam `mcpServers`);
> Windsurf usa `serverUrl` em vez de `url`; **Codex CLI usa TOML** (`~/.codex/config.toml`),
> não JSON. O servidor não muda — só o "invólucro" da config.

### Servidor remoto (HTTP) num agente

Depois do Caminho B, aponte o agente para a URL em vez de um comando:

```bash
claude mcp add --transport http mlops http://localhost:8000/mcp
```

---

## 🅱️ Caminho B — Remoto (Streamable HTTP) com Docker

Um servidor **stdio** serve um usuário (um subprocesso por cliente). Para
compartilhar entre um time, você o expõe como serviço de rede via **Streamable
HTTP** — um único endpoint `/mcp` que vários agentes acessam.

### B.1 — Subir o servidor

```bash
cd atividade/docker
docker compose up -d --build      # treina o modelo no build e sobe o servidor em :8000
docker compose ps                 # mcp-server deve estar (healthy)
```

O endpoint fica em **http://localhost:8000/mcp** (o sufixo `/mcp` é obrigatório).

### B.2 — Dirigir com o cliente-agente

```bash
docker compose run --rm agent     # roda agent_client.py contra o servidor (rede interna)
```

Ou do host (com o venv do Caminho A ativo):

```bash
MCP_CLIENT_MODE=http MCP_URL=http://localhost:8000/mcp python ../src/agent_client.py
```

### B.3 — Encerrar

```bash
docker compose down
```

---

## 🔐 Segurança (discuta, não pule)

Um servidor MCP dá a um agente **capacidade de agir**. Pontos que a aula levanta:

- **Tools são model-controlled**: o LLM decide chamá-las. Ações com efeito colateral exigem **confirmação humana**.
- **Tool poisoning / prompt injection**: descrições de tools e **respostas** de tools entram no contexto do modelo. Uma resposta maliciosa pode conter instruções. Prefira **saída estruturada** e valide entradas.
- **Menor privilégio**: separe read de write; uma tool que só lê não deve poder apagar. Aqui todas as tools são read-only de propósito.
- **stdio**: nunca escreva em stdout (corrompe o JSON-RPC) — logue em stderr. O servidor já faz isso.
- **Remoto = API pública**: em produção, um servidor HTTP precisa de **OAuth 2.1** e validação de token a cada request. Este lab **não** tem auth (é local/didático) — não exponha na internet assim.

---

## ⚠️ Solução de problemas

| Sintoma | Causa provável / solução |
|---|---|
| `Modelo não carregado` nas tools | Rode `python src/train_model.py` antes de subir o servidor |
| Servidor "não responde" no stdio | Você usou `print()` para stdout? Isso quebra o JSON-RPC — use `logging`/stderr |
| Agente conecta mas não lista tools | No stdio, confirme o **caminho absoluto** do `mcp_server.py` na config |
| `404` ao conectar no HTTP | Faltou o sufixo `/mcp` na URL (`http://localhost:8000/mcp`) |
| `mcp dev` falha | O Inspector precisa de **Node/npx** instalado |
| Cursor não acha o servidor | Chave é `mcpServers`; no VS Code é `servers` — não misture |
| `docker compose` sem `agent` subindo | É de propósito: `agent` está no profile `demo` (`docker compose run --rm agent`) |

---

📖 **Material teórico**: veja o [README do monitor](../README.md) — arquitetura
cliente-host-servidor, as primitivas (tools/resources/prompts), transportes,
a ponte com "Preparing for Production" e o panorama de agentes de 2026.
