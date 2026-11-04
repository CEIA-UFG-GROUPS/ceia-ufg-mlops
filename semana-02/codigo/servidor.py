"""Servidor HTTP do modelo de sentimento — só com a biblioteca padrão.

Semana 02 do grupo de estudos. Nenhum framework web: `http.server` entrega um
socket TCP já com o parsing da linha de requisição e dos headers feito, e
**tudo o que vem depois é nosso** — rota, método, corpo, status code, headers
de resposta e serialização JSON.

É de propósito. Na Semana 03 o FastAPI faz tudo isso por baixo do pano; quem
escreveu este arquivo sabe o que ele está fazendo por você.

Rodar:

    python servidor.py                 # http://127.0.0.1:8000
    python servidor.py --porta 8080
    python servidor.py --host 0.0.0.0  # aceita conexões de outras máquinas

Contrato:

    GET  /         -> 200  metadados do serviço
    GET  /health   -> 200  liveness: o processo está de pé e o modelo carregado
    POST /prever   -> 200  {"texto": "..."} -> {"sentimento", "score", ...}
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

from modelo import (
    LIMIAR_NEUTRO_PADRAO,
    NOME_MODELO,
    acuracia_treino,
    carregar_modelo,
    classificar,
    modelo_carregado,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("servidor-semana-02")

VERSAO = "1.0.0"

# Teto para o corpo da requisição. Sem isso, qualquer cliente pode anunciar um
# Content-Length gigante e o servidor tenta alocar tudo na memória.
LIMITE_CORPO_BYTES = 64 * 1024  # 64 KB
TAMANHO_MAXIMO_TEXTO = 1000

# Tabela de rotas: caminho -> métodos aceitos. É literalmente o "router" que um
# framework construiria a partir dos decoradores (@app.get, @app.post, ...).
ROTAS: dict[str, set[str]] = {
    "/": {"GET"},
    "/health": {"GET"},
    "/prever": {"POST"},
}


class ManipuladorSentimento(BaseHTTPRequestHandler):
    """Uma instância por requisição. Os métodos `do_<VERBO>` são o ponto de entrada."""

    # HTTP/1.1 habilita keep-alive (a conexão TCP é reaproveitada entre
    # requisições). O preço é rigor: toda resposta precisa de um
    # `Content-Length` correto, senão o cliente fica esperando bytes que não vêm.
    protocol_version = "HTTP/1.1"
    server_version = f"servidor-sentimento/{VERSAO}"
    sys_version = ""  # não vazar a versão do Python no header `Server`

    # ------------------------------------------------------------------
    # Pontos de entrada por método HTTP
    # ------------------------------------------------------------------
    # O `BaseHTTPRequestHandler` procura um método chamado `do_GET`, `do_POST`,
    # etc. Se não existir, ele responde 501 Not Implemented sozinho. Declaramos
    # os verbos que queremos tratar — inclusive os que só vão levar 405, para
    # que a mensagem de erro seja nossa e traga o header `Allow`.

    def do_GET(self) -> None:
        self._tratar("GET")

    def do_POST(self) -> None:
        self._tratar("POST")

    def do_PUT(self) -> None:
        self._tratar("PUT")

    def do_PATCH(self) -> None:
        self._tratar("PATCH")

    def do_DELETE(self) -> None:
        self._tratar("DELETE")

    # ------------------------------------------------------------------
    # Roteamento
    # ------------------------------------------------------------------

    def _tratar(self, metodo: str) -> None:
        """Decide quem responde a esta requisição — e com qual status code."""
        # `self.path` é a request-target crua: "/prever?debug=1#x". A query
        # string e o fragmento não fazem parte da rota.
        caminho = urlparse(self.path).path
        if len(caminho) > 1:
            caminho = caminho.rstrip("/") or "/"

        # Drenar o corpo SEMPRE, antes de qualquer decisão. Com keep-alive, os
        # bytes do corpo que ficassem sem ler seriam interpretados como o início
        # da próxima requisição na mesma conexão — e aí tudo desanda.
        corpo, erro_corpo = self._ler_corpo_bruto()

        try:
            if caminho not in ROTAS:
                # 404 Not Found: o servidor existe, a rota não.
                self._responder_json(
                    HTTPStatus.NOT_FOUND,
                    {
                        "erro": "rota não encontrada",
                        "caminho": caminho,
                        "rotas_disponiveis": sorted(ROTAS),
                    },
                )
                return

            metodos_aceitos = ROTAS[caminho]
            if metodo not in metodos_aceitos:
                # 405 Method Not Allowed: a rota existe, o verbo não serve.
                # A RFC exige o header `Allow` listando o que é aceito.
                self._responder_json(
                    HTTPStatus.METHOD_NOT_ALLOWED,
                    {
                        "erro": "método não permitido nesta rota",
                        "metodo": metodo,
                        "permitidos": sorted(metodos_aceitos),
                    },
                    headers_extra={"Allow": ", ".join(sorted(metodos_aceitos))},
                )
                return

            if erro_corpo is not None:
                status, detalhe = erro_corpo
                self._responder_json(status, detalhe)
                return

            if caminho == "/":
                self._rota_raiz()
            elif caminho == "/health":
                self._rota_health()
            elif caminho == "/prever":
                self._rota_prever(corpo)

        except Exception:  # noqa: BLE001 - a rede não pode derrubar o servidor
            # 500 Internal Server Error: a culpa é nossa, não do cliente.
            # O stack trace vai para o log; o cliente recebe só uma mensagem.
            logger.exception("erro não tratado em %s %s", metodo, caminho)
            self._responder_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                {"erro": "erro interno no servidor"},
            )

    # ------------------------------------------------------------------
    # Rotas
    # ------------------------------------------------------------------

    def _rota_raiz(self) -> None:
        """GET / — 200 OK com o mapa do serviço. Cortesia para quem chega perdido."""
        self._responder_json(
            HTTPStatus.OK,
            {
                "servico": "servidor-sentimento",
                "versao": VERSAO,
                "modelo": NOME_MODELO,
                "rotas": {
                    "GET /": "estes metadados",
                    "GET /health": "status do serviço",
                    "POST /prever": 'corpo {"texto": "..."} -> sentimento e score',
                },
            },
        )

    def _rota_health(self) -> None:
        """GET /health — 200 OK se o processo está de pé e o modelo em memória.

        Rota de healthcheck é contrato com a infraestrutura: o Docker (Semana 04)
        e o Cloud Run (Semana 07) vão bater aqui para decidir se o serviço recebe
        tráfego. Por isso ela precisa ser barata e não depender do modelo acertar.
        """
        self._responder_json(
            HTTPStatus.OK,
            {
                "status": "ok",
                "modelo_carregado": modelo_carregado(),
                "versao": VERSAO,
            },
        )

    def _rota_prever(self, corpo: bytes) -> None:
        """POST /prever — classifica o texto recebido no corpo JSON."""
        # 1) o corpo é JSON válido? Se não, o cliente mandou lixo -> 400.
        try:
            dados = json.loads(corpo.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            # 400 Bad Request: o servidor não conseguiu nem entender a mensagem.
            self._responder_json(
                HTTPStatus.BAD_REQUEST,
                {"erro": "corpo não é um JSON válido", "detalhe": str(exc)},
            )
            return

        # 2) é um objeto JSON (e não uma lista, número ou string solta)?
        if not isinstance(dados, dict):
            self._responder_json(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {"erro": "o corpo deve ser um objeto JSON", "recebido": type(dados).__name__},
            )
            return

        # 3) o JSON é válido, mas o *conteúdo* obedece ao contrato?
        #    Aqui mora a diferença entre 400 e 422: 400 = "não entendi os bytes",
        #    422 = "entendi perfeitamente, mas isso não serve".
        texto = dados.get("texto")
        erro_validacao = _validar_texto(texto)
        if erro_validacao is not None:
            self._responder_json(
                HTTPStatus.UNPROCESSABLE_ENTITY,
                {"erro": erro_validacao, "campo": "texto"},
            )
            return

        inicio = time.perf_counter()
        sentimento, score = classificar(texto, LIMIAR_NEUTRO_PADRAO)
        duracao_ms = (time.perf_counter() - inicio) * 1000

        logger.info(
            "prever | sentimento=%s score=%.4f em %.1f ms", sentimento, score, duracao_ms
        )

        # 200 OK: pedido entendido, processado e respondido.
        self._responder_json(
            HTTPStatus.OK,
            {
                "texto": texto,
                "sentimento": sentimento,
                "score": score,
                "modelo": NOME_MODELO,
            },
        )

    # ------------------------------------------------------------------
    # Leitura do corpo
    # ------------------------------------------------------------------

    def _ler_corpo_bruto(self) -> tuple[bytes, tuple[HTTPStatus, dict] | None]:
        """Lê os bytes do corpo da requisição.

        Devolve `(corpo, erro)`. O erro, quando existe, é um par
        `(status, payload)` pronto para virar resposta — mas só é usado depois
        que a rota e o método forem validados, para que `GET /rota-errada`
        continue devolvendo 404 em vez de reclamar do corpo.

        Em HTTP, quem diz o tamanho do corpo é o header `Content-Length`. Sem
        ele (e sem `Transfer-Encoding: chunked`, que não suportamos aqui), não
        há corpo nenhum — é o caso normal de um GET.
        """
        bruto = self.headers.get("Content-Length")
        if bruto is None:
            return b"", None

        try:
            tamanho = int(bruto)
            if tamanho < 0:
                raise ValueError("Content-Length negativo")
        except ValueError:
            return b"", (
                HTTPStatus.BAD_REQUEST,
                {"erro": "header Content-Length inválido", "valor": bruto},
            )

        if tamanho > LIMITE_CORPO_BYTES:
            # 413 Payload Too Large. Não lemos os bytes: fechamos a conexão.
            self.close_connection = True
            return b"", (
                HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                {"erro": "corpo grande demais", "limite_bytes": LIMITE_CORPO_BYTES},
            )

        corpo = self.rfile.read(tamanho)

        if tamanho == 0:
            return corpo, (
                HTTPStatus.BAD_REQUEST,
                {"erro": "corpo vazio: envie um JSON com o campo 'texto'"},
            )

        # O `Content-Type` é a promessa do cliente sobre o formato do corpo.
        # Recusar o que não sabemos ler é 415 Unsupported Media Type.
        tipo = self.headers.get("Content-Type", "")
        tipo_base = tipo.split(";")[0].strip().lower()
        if tipo_base and tipo_base != "application/json":
            return corpo, (
                HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                {
                    "erro": "Content-Type não suportado",
                    "recebido": tipo_base,
                    "esperado": "application/json",
                },
            )

        return corpo, None

    # ------------------------------------------------------------------
    # Escrita da resposta
    # ------------------------------------------------------------------

    def _responder_json(
        self,
        status: HTTPStatus,
        corpo: dict,
        headers_extra: dict[str, str] | None = None,
    ) -> None:
        """Monta a resposta HTTP inteira: status line, headers e corpo.

        É o que o `return {...}` de um framework esconde. Repare na ordem —
        status line, depois headers, depois linha em branco, depois o corpo.
        Essa ordem é o protocolo; inverter qualquer parte quebra o cliente.
        """
        carga = json.dumps(corpo, ensure_ascii=False).encode("utf-8")

        self.send_response(status)  # "HTTP/1.1 200 OK" + headers Server e Date
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(carga)))
        for nome, valor in (headers_extra or {}).items():
            self.send_header(nome, valor)
        self.end_headers()  # a linha em branco que separa headers do corpo

        self.wfile.write(carga)

    def version_string(self) -> str:
        """Conteúdo do header `Server`. O padrão concatena a versão do Python."""
        return self.server_version

    def log_message(self, formato: str, *args) -> None:
        """Access log no mesmo formato do resto dos logs (o padrão escreve em stderr cru)."""
        logger.info("%s - %s", self.address_string(), formato % args)


def _validar_texto(texto: object) -> str | None:
    """Valida o campo `texto`. Devolve a mensagem de erro, ou `None` se estiver ok.

    É a validação que o Pydantic faz por você na Semana 03 — e que aqui é
    um `if` atrás do outro, escrito à mão.
    """
    if texto is None:
        return "campo obrigatório ausente"
    if not isinstance(texto, str):
        return f"deve ser string, recebido {type(texto).__name__}"
    if not texto.strip():
        return "não pode ser vazio"
    if len(texto) > TAMANHO_MAXIMO_TEXTO:
        return f"excede o máximo de {TAMANHO_MAXIMO_TEXTO} caracteres"
    return None


def principal() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="endereço de bind. 127.0.0.1 = só esta máquina; 0.0.0.0 = toda a rede local",
    )
    parser.add_argument("--porta", type=int, default=8000, help="porta TCP (padrão: 8000)")
    args = parser.parse_args()

    # Treinar ANTES de abrir a porta: enquanto o modelo não está pronto, o
    # serviço não deveria dizer que está saudável.
    inicio = time.perf_counter()
    carregar_modelo()
    duracao_ms = (time.perf_counter() - inicio) * 1000
    logger.info(
        "modelo '%s' treinado em %.0f ms (acurácia no treino: %.2f)",
        NOME_MODELO,
        duracao_ms,
        acuracia_treino(),
    )

    # ThreadingHTTPServer: uma thread por conexão. Com o HTTPServer simples,
    # uma requisição lenta bloqueia todas as outras — dá para demonstrar no lab.
    servidor = ThreadingHTTPServer((args.host, args.porta), ManipuladorSentimento)
    logger.info("servindo em http://%s:%d (Ctrl+C para parar)", args.host, args.porta)

    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        logger.info("encerrando o servidor")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    principal()
