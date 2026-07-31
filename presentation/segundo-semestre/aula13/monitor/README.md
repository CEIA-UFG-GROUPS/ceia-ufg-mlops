# 📘 Aula 13 — Configurando um Servidor MCP (Model Context Protocol)

## Material de Estudo Prévio (Monitor)

Este material tem como objetivo **preparar para a aula de MCP (Model Context
Protocol)**, oferecendo uma base conceitual sólida para acompanhar, complementar e
aprofundar a discussão conduzida pelo apresentador.

⚠️ **Este conteúdo não é um guia de instruções**, mas sim um **material de estudo
prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do CEIA/UFG.

---

## 🎯 Objetivo da Aula

Ao final desta aula, espera-se que os participantes compreendam:

- **Que problema o MCP resolve**: por que integrar cada agente a cada ferramenta "na mão" não escala (o problema **M×N**)
- A **arquitetura cliente-host-servidor** do MCP e por que ela é comparada ao **LSP** (Language Server Protocol) e a uma **"USB-C para IA"**
- As **três primitivas de servidor** — **Tools, Resources, Prompts** — e quem controla cada uma (modelo, aplicação, usuário)
- As **primitivas de cliente** — **Sampling, Roots, Elicitation** — e o fluxo bidirecional
- Os **transportes**: `stdio` (local) e **Streamable HTTP** (remoto), e por que o SSE puro foi depreciado
- Como **construir e depurar** um servidor MCP em Python com **FastMCP** e o **MCP Inspector**
- Onde o MCP se encaixa em **MLOps** e a ponte com *"Preparing for Production"*: expor um modelo/capacidade como serviço **padronizado, descobrível e governado** para agentes
- O **panorama de 2026**: coding agents (Claude Code, Cursor, VS Code/Copilot, Windsurf, Codex) como clientes MCP, registries e os **riscos de segurança** (tool poisoning, prompt injection)

---

## 🧠 Contexto: Por que MCP existe?

### O problema M×N das integrações

Um agente de IA só é útil quando consegue **agir sobre o mundo**: ler um arquivo,
consultar um banco, chamar uma API, rodar um modelo. Antes do MCP, cada dessas
conexões era uma **integração sob medida**: se você tem **M** aplicações de IA
(Claude Desktop, um chatbot interno, um coding agent) e **N** fontes de
dados/ferramentas (GitHub, Postgres, seu model registry), acaba com **M×N**
integrações artesanais para construir e manter.

```text
        SEM MCP (M×N)                         COM MCP (M+N)
  App A ─┬─ GitHub                       App A ─┐        ┌─ GitHub (server)
         ├─ Postgres                     App B ─┼─ MCP ──┼─ Postgres (server)
  App B ─┼─ Registry                     App C ─┘        └─ Registry (server)
         └─ ...                          (cada lado implementa o protocolo UMA vez)
```

O **MCP (Model Context Protocol)** é um **padrão aberto** (lançado pela Anthropic em
**novembro/2024**, doado à **Linux Foundation** no fim de 2025) que resolve isso do
mesmo jeito que o **LSP** resolveu o M×N entre editores e linguagens: define **um
protocolo** para que qualquer cliente converse com qualquer servidor. Você
implementa **M + N**, não **M × N**.

> **A analogia da USB-C**: assim como uma porta única conecta o notebook a
> monitores, teclados e HDs de qualquer fabricante, o MCP é a "porta única" pela
> qual um agente conecta a ferramentas e dados de qualquer origem.

### Por que isso importa para MLOps?

Times de MLOps produzem exatamente o tipo de ativo que agentes querem consumir:
**modelos servindo predições, model registries, feature stores, métricas de
monitoramento, experimentos**. Sem um padrão, cada um vira um plugin proprietário
por cliente. Com MCP, você expõe "o modelo em produção", "os experimentos do
MLflow" ou "as features online" **uma vez**, e todo agente (conversacional ou de
coding) passa a poder perguntar *"qual modelo está em produção e qual o F1 dele?"*,
*"rode uma predição com estes dados"* ou *"este dataset tem drift?"*.

---

## 🏛️ Como Funciona: A Arquitetura

O MCP segue uma arquitetura **cliente-host-servidor**, sobre **JSON-RPC 2.0**, com
sessões que negociam capacidades na inicialização.

```text
┌──────────────────────────── HOST (a aplicação de IA) ────────────────────────────┐
│  Ex.: Claude Code, Cursor, VS Code/Copilot, Claude Desktop, chatbot próprio       │
│  • coordena o LLM  • aplica políticas de segurança/consentimento                   │
│                                                                                    │
│   ┌────────── Client 1 ──────────┐        ┌────────── Client 2 ──────────┐         │
│   │ 1 sessão, 1 conexão isolada  │        │ 1 sessão, 1 conexão isolada  │         │
│   └──────────────┬───────────────┘        └──────────────┬───────────────┘         │
└──────────────────┼────────────────────────────────────────┼───────────────────────┘
                   │ JSON-RPC (stdio / HTTP)                  │
          ┌────────▼─────────┐                       ┌────────▼─────────┐
          │   Server (MCP)   │                       │   Server (MCP)   │
          │ Tools/Resources/ │                       │ Tools/Resources/ │
          │ Prompts          │                       │ Prompts          │
          └──────────────────┘                       └──────────────────┘
```

- **Host**: a aplicação de IA que o usuário usa. Cria e gerencia os clientes,
  controla permissões de conexão, **aplica consentimento** e integra o LLM.
- **Client**: um conector criado pelo host para **um** servidor. Cada cliente mantém
  **uma sessão isolada** — as fronteiras entre servidores são preservadas.
- **Server**: um processo que expõe capacidades **focadas** (ex.: "acesso ao model
  registry"). Pode ser **local** (subprocesso) ou **remoto** (serviço de rede).

### Negociação de capacidades

Na inicialização, cliente e servidor **declaram o que suportam**. O servidor anuncia
se oferece `tools`, `resources` (com `subscribe`/`listChanged`), `prompts`; o cliente
anuncia se suporta `sampling`, `roots`, `elicitation`. Cada lado só usa o que o outro
declarou — é o que torna o protocolo **extensível** e **descobrível**.

---

## 🧩 As Três Primitivas de Servidor

O coração da aula. Um servidor MCP oferece capacidades por meio de **três blocos**, e
o que diferencia cada um é **quem tem o controle**:

| Primitiva | O que é | Quem controla | Efeito colateral | Analogia REST |
|---|---|---|---|---|
| **Tools** | Funções que o modelo pode **executar** | **Modelo** (o LLM decide chamar) | Sim (potencial) | `POST` |
| **Resources** | Dados **read-only** para contexto | **Aplicação** (o host decide injetar) | Não | `GET` |
| **Prompts** | Templates de interação reutilizáveis | **Usuário** (invoca explicitamente) | Não | — |

### 1. Tools (controladas pelo modelo)

São operações com **schema de entrada/saída tipado** (JSON Schema, gerado a partir
dos type hints em Python). O modelo **descobre** as tools via `tools/list` e as
**executa** via `tools/call`. Como podem ter efeitos colaterais (escrever num banco,
disparar uma API), **tipicamente exigem consentimento do usuário**.

> Exemplos MLOps: `predict(features)`, `retrain(model, dataset)`, `promote_model(name, stage)`.

### 2. Resources (controlados pela aplicação)

Fontes de dados **somente leitura**, identificadas por **URI** (ex.:
`model://fraud-detector/card`, `file:///path`, `dataset://schema`). Servem para
**injetar contexto** no modelo — sem lógica pesada, análogos a um `GET`. Suportam
**templates** com parâmetros (`travel://activities/{city}`) e, opcionalmente,
**subscriptions** para notificar mudanças.

> Exemplos MLOps: o **model card**, o **schema do dataset**, a **documentação** de uma API.

### 3. Prompts (controlados pelo usuário)

**Templates parametrizados** que estruturam um fluxo de trabalho — normalmente
expostos como **slash commands** ou itens de menu no host. Guiam o modelo a combinar
resources e tools de forma consistente.

> Exemplo MLOps: `investigate_alert(transacao)` → "leia o model card, chame `predict`, explique a decisão".

### Primitivas de cliente (o caminho de volta)

O fluxo é **bidirecional** — o servidor também pode pedir coisas ao cliente:

- **Sampling**: o servidor pede ao cliente que **rode uma inferência no LLM** dele — mantém o servidor **agnóstico de modelo** (com aprovação humana).
- **Roots**: o cliente informa ao servidor **as fronteiras de filesystem/URI** onde ele pode operar.
- **Elicitation**: o servidor **pede informações adicionais ao usuário** via um schema estruturado (ex.: confirmar uma ação).

---

## 🔌 Transportes

Como as mensagens JSON-RPC viajam entre cliente e servidor:

| Transporte | Como roda | Endpoint | Quando usar |
|---|---|---|---|
| **stdio** (padrão) | Cliente sobe o servidor como **subprocesso**; fala por stdin/stdout | — | Servidor **local**, mesma máquina do cliente. Simples, sem rede, sem auth. |
| **Streamable HTTP** | Servidor HTTP; um **único endpoint** `/mcp` (POST + SSE opcional) | `http://host:porta/mcp` | Servidor **remoto/compartilhado**, múltiplos clientes, deploy em rede. |
| **SSE (legado)** | Dois endpoints (POST + SSE de longa duração) | — | **Depreciado** (2025-03-26). Só clientes antigos. |

Dois pontos que a aula enfatiza:

1. **stdio: NUNCA escreva em stdout** (um `print()`) — isso **corrompe o JSON-RPC** e
   quebra o servidor. Logue em **stderr**.
2. **Streamable HTTP** (introduzido em 2025-03-26) colapsou tudo em **um endpoint**,
   o que o torna amigável a **load balancers** e **serverless** — a base de qualquer
   servidor MCP **remoto** de produção. Em produção, esse endpoint deve ficar atrás de
   **OAuth 2.1**, com validação de token a cada request.

---

## 🐍 Construindo com FastMCP + MCP Inspector

O **SDK oficial em Python** (`pip install "mcp[cli]"`) traz o **FastMCP**, uma API de
alto nível que gera o schema das tools automaticamente a partir de **type hints** e
**docstrings**:

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mlops-fraud")

@mcp.tool()
def predict(amount: float, hour_of_day: int) -> dict:
    """Avalia o risco de fraude de uma transação."""   # vira a descrição da tool
    ...
    return {"is_fraud": True, "fraud_probability": 0.83}

@mcp.resource("model://{name}/card")
def model_card(name: str) -> str:
    """Retorna o model card (contexto read-only)."""
    ...

@mcp.prompt()
def investigate_alert(amount: float) -> str:
    """Template que guia o agente a investigar um alerta."""
    ...

if __name__ == "__main__":
    mcp.run()                              # stdio (padrão)
    # mcp.run(transport="streamable-http") # remoto
```

- **`@mcp.tool()`** lê nome, type hints e docstring → schema JSON da tool.
- **Depuração**: `mcp dev src/mcp_server.py` abre o **MCP Inspector**, onde você vê e
  chama tools/resources sem escrever cliente. É a forma mais rápida de iterar.
- **Nomes e descrições importam**: o modelo escolhe qual tool chamar **lendo a
  descrição**. Descrições ruins = tool errada. Trate a descrição como parte da API.

> ⚠️ **Nota de versão (jul/2026)**: o SDK teve o **v2 estável** lançado em **2026-07-27**,
> que **renomeia** a classe (`from mcp.server import MCPServer`) e ajusta a API. Para
> manter o lab reprodutível, fixamos `mcp[cli]>=1.27,<2` e usamos `FastMCP`. Ao
> começar um projeto novo hoje, **pine a versão** e leia o guia de migração.

---

## 🏭 A Ponte com "Preparing for Production" (Introducing MLOps, Cap. 5)

O capítulo indicado no cronograma trata de **preparar modelos e artefatos para
produção**: ambientes de runtime, empacotamento de artefatos, testes e QA,
reprodutibilidade e governança. O MCP **não** está no livro (que é de 2020), mas a
conexão é direta — e é o fio condutor desta aula:

> **Um servidor MCP é uma forma moderna de "preparar uma capacidade para produção":**
> em vez de entregar um modelo apenas como um endpoint REST para outros sistemas,
> você o empacota como um serviço **padronizado, descobrível, versionado e governado**
> para ser consumido por **agentes de IA**.

| Tema do Cap. 5 | Como aparece num servidor MCP |
|---|---|
| **Ambiente de runtime** | O servidor roda num container (Docker), com deps pinadas |
| **Artefatos para produção** | O model card e o schema viram **resources**; o modelo, uma **tool** `predict` |
| **QA / testes** | O **MCP Inspector** e um cliente de teste validam tools/schemas antes do deploy |
| **Reprodutibilidade** | Versão do modelo no card + versão do SDK pinada |
| **Governança** | Consentimento por ação, menor privilégio, OAuth no remoto, logs de auditoria |

---

## 🌐 Panorama 2026: MCP e os Agentes

MCP deixou de ser curiosidade e virou o **contrato padrão** que todo agente que usa
ferramentas assume. Números e fatos (meados de 2026):

- **Adoção massiva**: ~**97M+** downloads mensais dos SDKs; o pacote `mcp` (PyPI)
  sozinho na casa das centenas de milhões/mês. Milhares de servidores publicados
  (a contagem varia por registry: ~6,6k curados na Smithery, ~20k+ em trackers amplos).
- **Seis "host surfaces" canônicas** (clientes MCP maduros): **Claude Desktop,
  Claude Code, Cursor, Codex CLI, Windsurf** e **VS Code com GitHub Copilot** (agent mode, GA jul/2025).
- **Coding agents puxaram a fila**: o cluster que mais cresceu foi o de ferramentas de
  dev (git, build, test, DB, observabilidade) — exatamente onde MLOps mora.
- **Portabilidade real**: um servidor bem escrito **roda sem mudança** nos seis
  clientes. Se o seu código tem ramos "por cliente", é *code smell* — o schema
  provavelmente divergiu da forma canônica do SDK.
- **Só muda o invólucro da config**: Claude Code usa `.mcp.json`/`claude mcp add`;
  Cursor usa `.cursor/mcp.json`; VS Code usa `.vscode/mcp.json` (chave `servers`);
  **Codex usa TOML**; Claude Desktop é **stdio-only** (remoto via Connectors/OAuth).
- **Governança chegou**: OAuth 2.1 em servidores remotos, escopos, auditoria e
  **registries** com sinais de confiança viraram *table-stakes* — porque **listar
  não é verificar** (auditorias apontam que boa parte dos servidores listados está
  morta ou insegura).

---

## 🔐 Segurança: A Superfície de Ataque dos Agentes

Dar a um agente a capacidade de **agir** cria riscos novos. A aula trata os
principais (referências no fim):

- **Prompt Injection (indireta)**: instruções maliciosas escondidas em conteúdo
  externo (um ticket, um arquivo) que o modelo processa e obedece como se fossem do usuário.
- **Tool Poisoning**: instruções maliciosas embutidas na **descrição** de uma tool —
  invisíveis ao usuário, lidas pelo modelo. O **"rug pull"** é a variante em que a tool
  muda **depois** de já ter sido aprovada.
- **Respostas de tools como vetor**: o conteúdo retornado por uma tool entra no
  contexto do modelo **sem validação**. Uma resposta pode conter instruções — por isso
  prefira **saída estruturada** (JSON com schema) e trate respostas como **não confiáveis**.
- **Confused deputy / session hijacking / OAuth**: em servidores remotos, valide
  **todo** request, use **session IDs não determinísticos** ligados ao usuário, e
  **nunca** trate posse de sessão como autenticação.
- **Incidentes reais**: casos como o **CVE-2025-6514** (comprometimento de centenas de
  milhares de ambientes de dev via pacote MCP malicioso) mostram que **vetar a origem**
  dos servidores é essencial.

**Mitigações-chave**: consentimento humano em ações sensíveis; **menor privilégio**
(separar read/write, escopos estreitos); **allowlist** de servidores confiáveis;
**pinar versões** e alertar sobre mudanças; validar entradas e schemas; **logar** toda
invocação (quem, qual tool, com quais args, resultado).

---

## 💡 Boas Práticas ao Escrever um Servidor

1. **Uma tool = uma operação clara**, com nome e descrição que o modelo entenda — a descrição É a API.
2. **Tipos e docstrings sempre**: o schema (e a qualidade da escolha do modelo) depende deles.
3. **Read por padrão, write com cuidado**: exponha o mínimo; separe leitura de escrita; peça confirmação em ações com efeito colateral.
4. **stdio → logue em stderr**, nunca em stdout.
5. **Comece stdio, evolua para HTTP** só quando precisar compartilhar; aí adicione **OAuth 2.1** e trate como API pública.
6. **Prefira saída estruturada** a texto livre — reduz a superfície de injeção e facilita o consumo pelo agente.
7. **Depure no Inspector** antes de plugar num cliente — itera muito mais rápido.
8. **Pine o SDK** (`mcp<2` hoje) e documente a versão do protocolo suportada.

---

## 📊 Casos de Uso Práticos (em MLOps)

### Caso 1: Coding agent com acesso ao model registry
- **Cenário**: um dev no Cursor pergunta *"qual modelo de fraude está em produção e qual o F1?"*
- **Com MCP**: um servidor expõe `list_models`/`get_model_card` como tools + o model card como resource. O agente responde sem sair do editor.

### Caso 2: Agente conversantional de suporte antifraude
- **Cenário**: um analista descreve uma transação suspeita a um chatbot.
- **Com MCP**: o prompt `investigate_alert` guia o agente a ler o card e chamar `predict`, explicando a probabilidade e as **limitações** do modelo.

### Caso 3: Servidor MCP interno compartilhado pelo time
- **Cenário**: vários agentes (Claude Code, VS Code) precisam consultar as métricas de monitoramento.
- **Com MCP**: um servidor **remoto** (Streamable HTTP + OAuth) exposto uma vez; cada agente só adiciona a URL. Governança e auditoria centralizadas.

### Caso 4: Da REST ao MCP
- **Cenário**: já existe uma API REST do model service.
- **Com MCP**: se as tools apenas espelham os endpoints, um bridge OpenAPI→MCP resolve 90%. **Construa** um servidor sob medida quando o agente precisa de primitivas que a API humana não tem (ex.: "espere o evento chegar e explique o que deu errado").

---

## 🧪 Atividade Prática

A pasta [`atividade/`](./atividade/) traz um laboratório que percorre o ciclo
completo: **treinar um modelo → expô-lo num servidor MCP → depurar no Inspector →
conectar num coding agent → levar para remoto com Docker → dirigir com um
cliente-agente**.

- **`src/mcp_server.py`**: o servidor MCP (tools `predict`/`list_models`/`get_model_card`, resources `model://.../card` e `dataset://schema`, prompt `investigate_alert`).
- **`src/agent_client.py`**: um cliente que faz o loop de um agente (initialize → discover → call), por **stdio** ou **Streamable HTTP**.
- **`docker/`**: o servidor como serviço remoto (Streamable HTTP) + o cliente-agente sob demanda.
- **Configs prontas** para Claude Code, Cursor e VS Code/Copilot.

Instruções completas no [`atividade/README.md`](./atividade/README.md).

---

## 💬 Pontos para Reflexão Pré-Aula

1. **O que muda** entre expor seu modelo como uma **API REST** e como um **servidor MCP**? Quem é o "consumidor" em cada caso?
2. Por que a distinção **Tools (modelo) / Resources (aplicação) / Prompts (usuário)** existe? O que daria errado se tudo fosse "tool"?
3. Quando faz sentido **stdio** e quando **Streamable HTTP**? O que o remoto **obriga** você a resolver (que o local não obriga)?
4. **Tool poisoning**: por que a resposta de uma tool é um vetor de ataque tão perigoso? Como saída estruturada ajuda?
5. No seu contexto de MLOps, **quais 3 capacidades** você exporia primeiro para um agente (e quais você jamais exporia sem confirmação)?
6. "Listar não é verificar": com milhares de servidores públicos, como você **decidiria** em qual confiar?
7. Qual a relação entre um servidor MCP e o tema **"Preparing for Production"** — o que significa "preparar uma capacidade para ser consumida por agentes"?

---

## 📚 Referências

### Material Indicado no Cronograma do Grupo

1. **Treveil, M. et al. (2020).** *Introducing MLOps*. O'Reilly. — Cap. 5 "Preparing for Production", pp. 85-104. (Âncora teórica; a ponte com MCP é feita nesta aula.)

### Documentação Oficial do MCP

2. **Model Context Protocol — site oficial** — [https://modelcontextprotocol.io/](https://modelcontextprotocol.io/)
3. **MCP — Especificação** — [https://modelcontextprotocol.io/specification](https://modelcontextprotocol.io/specification)
4. **MCP — Understanding MCP servers (Tools/Resources/Prompts)** — [https://modelcontextprotocol.io/docs/learn/server-concepts](https://modelcontextprotocol.io/docs/learn/server-concepts)
5. **MCP — Build an MCP server (tutorial)** — [https://modelcontextprotocol.io/docs/develop/build-server](https://modelcontextprotocol.io/docs/develop/build-server)
6. **MCP Python SDK (GitHub)** — [https://github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk)
7. **MCP Inspector** — [https://github.com/modelcontextprotocol/inspector](https://github.com/modelcontextprotocol/inspector)

### Segurança

8. **MCP — Security Best Practices** — [https://modelcontextprotocol.io/specification/draft/basic/security_best_practices](https://modelcontextprotocol.io/specification/draft/basic/security_best_practices)
9. **OWASP — MCP Tool Poisoning** — [https://github.com/OWASP/www-community/blob/master/pages/attacks/MCP_Tool_Poisoning.md](https://github.com/OWASP/www-community/blob/master/pages/attacks/MCP_Tool_Poisoning.md)
10. **Microsoft — Protecting against indirect prompt injection in MCP** — [https://developer.microsoft.com/blog/protecting-against-indirect-injection-attacks-mcp](https://developer.microsoft.com/blog/protecting-against-indirect-injection-attacks-mcp)

### Ecossistema e Guias (2026)

11. **Hugging Face — MCP Course** — [https://huggingface.co/learn/mcp-course](https://huggingface.co/learn/mcp-course)
12. **Registry oficial de servidores MCP** — [https://registry.modelcontextprotocol.io/](https://registry.modelcontextprotocol.io/)
13. **Aviraj — MCP Explained for MLOps Engineers** — [https://aviraj.info/mlops/mcp-explained.html](https://aviraj.info/mlops/mcp-explained.html)

---

## 🔗 Conexões com Outras Aulas

- **Serverless e Aplicações com Agentes (1º sem.)**: MCP é a "cola" padronizada entre agentes e ferramentas.
- **Bancos Vetoriais / Embeddings**: um servidor MCP pode expor um vector store para RAG dentro de um agente.
- **Aula 19 (Model Registry)** e **Feature Stores**: candidatos naturais a virarem servidores MCP — expor modelos/features a agentes.
- **CI/CD e Containers (Docker)**: o servidor remoto é empacotado e versionado como qualquer serviço.
- **Monitoramento e Drift**: métricas de produção expostas como resources/tools para um agente investigar incidentes.

---

🚀 **Leitura concluída? Venha para a aula pronto para discutir: se todo agente hoje
"fala MCP", qual capacidade do seu sistema de ML você exporia primeiro — e como faria
isso com segurança?**
