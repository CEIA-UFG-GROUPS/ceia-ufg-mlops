# Configurando um Servidor MCP (Model Context Protocol)

## README do Apresentador

Este documento organiza a apresentação da aula e serve como **guia conceitual** para
o expositor. A estrutura abaixo é uma sugestão para garantir clareza, progressão
lógica e alinhamento com o grupo.

> 💡 **Fio condutor sugerido**: partir de uma dor concreta — *"eu quero que o Claude
> Code / Cursor consulte o modelo em produção do nosso time"* — e mostrar que, sem um
> padrão, isso é uma integração sob medida por cliente (o problema **M×N**). O MCP é o
> **LSP dos agentes**: um protocolo, e qualquer agente passa a "enxergar" suas
> ferramentas. Termine construindo, ao vivo, um servidor que expõe um modelo e
> plugando-o num coding agent. Reaproveite o que a turma já sabe de **APIs, Docker e
> deploy** — MCP é "só" um contrato bem desenhado por cima disso.

---

## 1️⃣ Motivação

### 1.1 A dor: integrar agentes a ferramentas não escala

- Cada agente (Claude Code, Cursor, VS Code/Copilot, chatbot interno) × cada
  ferramenta (GitHub, Postgres, model registry) = uma integração artesanal. **M×N**.
- Pergunte à turma: *"como o seu editor de IA consultaria hoje o modelo de fraude em produção do time?"* — provavelmente ninguém tem resposta padronizada.

### 1.2 A ideia: um protocolo, como o LSP fez com editores

- Antes do LSP: N editores × M linguagens. Depois: cada um implementa o protocolo uma vez.
- MCP faz o mesmo para **agentes × ferramentas/dados**: implementa-se **M + N**.
- Analogia da **USB-C para IA**: uma porta, muitos periféricos.

### 1.3 Por que MLOps deveria se importar

- Modelos, registries, feature stores, métricas de drift — tudo isso é o que agentes querem consumir.
- Expor "o modelo em produção" **uma vez** como servidor MCP → todo agente passa a usá-lo.
- Ponte com o Cap. 5 ("Preparing for Production"): **servidor MCP = preparar uma capacidade para ser consumida por agentes**, de forma padronizada, versionada e governada.

---

## 2️⃣ Como Funciona

### 2.1 Arquitetura cliente-host-servidor (conceito central)

- **Host** (a app de IA) coordena o LLM e aplica **consentimento**; cria **clients**; cada client tem **uma sessão isolada** com **um server**.
- **Server** expõe capacidades focadas; pode ser **local** (subprocesso) ou **remoto** (rede).
- Base: **JSON-RPC 2.0** + **negociação de capacidades** na inicialização.
- Desenhar no quadro o diagrama Host → Clients → Servers.

### 2.2 As três primitivas (o coração da aula)

- **Tools** — o **modelo** decide chamar; ações com efeito colateral; schema tipado; pedem consentimento. (`POST`)
- **Resources** — a **aplicação** injeta como contexto; **read-only**; por URI, com templates. (`GET`)
- **Prompts** — o **usuário** invoca (slash command); orquestram tools + resources.
- Enfatizar **quem controla cada uma** — é o insight que organiza tudo.
- Mencionar o caminho de volta (cliente): **Sampling, Roots, Elicitation** (rápido).

### 2.3 Transportes

- **stdio**: local, cliente sobe o servidor como subprocesso. **Regra de ouro: não escreva em stdout** (quebra o JSON-RPC) → logue em stderr.
- **Streamable HTTP**: remoto, **um endpoint `/mcp`**; base do servidor de produção; em produção, atrás de **OAuth 2.1**.
- **SSE puro**: legado/depreciado — citar e seguir.

### 2.4 Construir e depurar (FastMCP + Inspector)

- `FastMCP` gera o schema a partir de **type hints + docstring**: `@mcp.tool()`, `@mcp.resource("uri://{x}")`, `@mcp.prompt()`.
- **Descrição da tool É a API** — o modelo escolhe a tool lendo a descrição.
- **MCP Inspector** (`mcp dev server.py`): ver/chamar tools sem cliente. É onde se itera.
- **Nota de versão (jul/2026)**: v2 estável saiu 27/jul (renomeia a classe `MCPServer`). Pinar `mcp<2` para reprodutibilidade.

### 2.5 Panorama 2026 (para dar mapa mental)

- Seis clientes canônicos: **Claude Desktop, Claude Code, Cursor, Codex CLI, Windsurf, VS Code/Copilot**.
- Um servidor bem escrito roda **sem mudança** nos seis; muda só a **config** (Codex é TOML; VS Code usa `servers`; Claude Desktop é stdio-only).
- Adoção enorme (SDKs com dezenas/centenas de M de downloads/mês); milhares de servidores; **"listar ≠ verificar"**.

### 2.6 Segurança (não pular)

- **Tool poisoning / prompt injection**; **rug pull**; respostas de tools como vetor.
- Mitigações: **consentimento**, **menor privilégio**, **allowlist**, **pinar versões**, **saída estruturada**, **logs**.
- Citar incidente real (CVE-2025-6514) para materializar o risco.

---

## 3️⃣ Quickstart & Demos

> 💡 **Material pronto**: a pasta `../monitor/atividade/` traz o servidor, o
> cliente-agente e o Docker. As demos abaixo saem direto dela. Já tenha o venv criado
> e `python src/train_model.py` rodado **antes** da aula.

### 3.1 Demo 1 — O servidor e o Inspector (o essencial)

- Abrir `src/mcp_server.py` e mostrar as **três primitivas** decoradas (tool/resource/prompt).
- `mcp dev src/mcp_server.py` → no Inspector, aba **Tools** → chamar `predict` com uma transação suspeita (`amount=4200, hour_of_day=3, ... is_foreign=1, distance=830`) → `fraud_probability ≈ 0.84`.
- Aba **Resources** → ler `model://fraud-detector/card`. **Momento "aha"**: o agente descobre e usa tudo sozinho, via um protocolo.

### 3.2 Demo 2 — O loop de um agente, em Python

- `MCP_CLIENT_MODE=stdio python src/agent_client.py`
- Narrar o loop: **initialize → list_tools → read_resource → call_tool**. É literalmente o que Claude Code/Cursor fazem por baixo.

### 3.3 Demo 3 — Plugar num coding agent de verdade

- `claude mcp add mlops -- python /CAMINHO/ABSOLUTO/src/mcp_server.py`
- Dentro do Claude Code: `/mcp` para ver as tools; pedir *"avalie o risco desta transação: R$4200, 3h, exterior, 830km de casa"* e ver o agente chamar `predict`.
- Mostrar o **mesmo servidor** numa config do Cursor/VS Code (só muda o invólucro).

### 3.4 Demo 4 — Levar para remoto (Docker + Streamable HTTP)

- `cd docker && docker compose up -d --build` → servidor em `http://localhost:8000/mcp`.
- `docker compose run --rm agent` → o cliente conecta pela rede. Mesmo código, transporte diferente.
- Discutir: agora é uma **API pública** → precisa de **OAuth 2.1** e validação de token (não incluído de propósito no lab).

### 3.5 Para fechar

- Recap das 3 primitivas + quem controla cada uma.
- A frase-síntese: *"você escreve o servidor uma vez; todos os agentes passam a enxergar seu modelo."*
- Amarrar em "Preparing for Production" e nas próximas aulas (Registry, Feature Stores como candidatos a servidores MCP).

---

## 4️⃣ Quando Usar (e Quando NÃO Usar)

### Usar ✅
- Você quer que **agentes** (conversacionais ou de coding) consumam ativos de ML de forma padronizada.
- Precisa expor a mesma capacidade para **vários clientes** sem integração por cliente.
- O agente precisa de **primitivas** que uma API humana não tem (fluxos agentivos).

### Não usar / cuidado ❌
- Se as tools só **espelham** endpoints REST existentes → um bridge OpenAPI→MCP resolve 90% com 5% do esforço.
- Servidor remoto **sem OAuth/validação** exposto na internet — é uma API pública com efeitos colaterais.
- Conectar agentes a **servidores não verificados** — "listar não é verificar".

> **Regra prática**: se mais de um agente precisa da mesma capacidade e você quer
> governança central, construa um servidor MCP. Se é um wrapper 1:1 de REST, avalie um
> bridge antes.
