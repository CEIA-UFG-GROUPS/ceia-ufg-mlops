# Semana 02 — Como a web funciona I (Redes)

> **Encontro 3 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

O que acontece entre digitar uma URL e receber uma resposta — e por que isso importa para quem vai colocar um modelo no ar.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Explicar o caminho de uma requisição: DNS, TCP, TLS e HTTP
- Ler e interpretar headers e métodos HTTP
- Entender portas, `localhost`, `0.0.0.0` e por que o container parece não responder
- Diferenciar cliente e servidor na prática, com ferramentas de linha de comando
- Subir um servidor HTTP simples e acessá-lo de outra máquina

---

## Pré-requisitos

- Semana 01 concluída (terminal e Git confortáveis)
- Python 3 instalado no ambiente local

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~15 min | Contexto mínimo para o lab fazer sentido |
| 💻 Mão na massa | ~60 min | Todo mundo codando junto, no mesmo ritmo |
| 🎯 Desafio | ~15 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

### ⏱️ Conceito (~15 min)

- Modelo cliente-servidor e o ciclo request/response
- DNS: do nome ao IP, cache e por que a mudança demora a propagar
- TCP vs UDP, portas e sockets — o mínimo necessário
- HTTP vs HTTPS: o que o TLS protege e o que ele não protege
- Anatomia de uma requisição: método, path, headers, body e status

### 💻 Mão na massa (~60 min)

- Inspecionar requisições reais com `curl -v`, `dig`, `ping` e `ss`/`netstat`
- Servir um diretório com `python -m http.server` e acessar de outro dispositivo da rede
- Entender bind em `127.0.0.1` vs `0.0.0.0` na prática (quebrar e consertar)
- Escrever um servidor HTTP mínimo que carrega o modelo de sentimento e responde em texto
- Testar o servidor com `curl` e com o navegador, lendo os headers de resposta

### 🎯 Desafio (~15 min)

Subir um servidor HTTP simples que serve o modelo de análise de sentimento e responde a requisições vindas de outra máquina.

Enunciado completo em [`desafio.md`](./desafio.md).

---

## Passo a passo

> **TODO (host):** detalhar aqui o passo a passo do lab, na ordem em que ele será conduzido.
> Sugestão de formato: um passo numerado por ação, com o comando exato e o resultado esperado.
>
> 1. `> TODO` — passo 1
> 2. `> TODO` — passo 2
> 3. `> TODO` — passo 3
>
> Marque os pontos de checkpoint (`checkpoint: todo mundo chegou até aqui?`) a cada 15-20 minutos.

---

## Código

O código de apoio desta semana vive em [`codigo/`](./codigo/).

> **TODO (host):** incluir ali os arquivos de apoio (scripts, configs, exemplos) usados no lab,
> junto de um `README.md` curto dentro de `codigo/` explicando como executá-los.

---

## Recursos e links

- [MDN — Visão geral do HTTP](https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Overview)
- [High Performance Browser Networking (livro gratuito)](https://hpbn.co/)
- [How DNS works (quadrinho)](https://howdns.works/)
- [curl — manual oficial](https://curl.se/docs/manual.html)

> **TODO (host):** acrescentar os links específicos que você usar na condução.

---

## Notas para o host

- Use um modelo bem simples (regra ou scikit-learn treinado na Semana 01) — o foco aqui é rede, não ML
- Tenha um plano B se a rede do lab bloquear portas: usar duas máquinas via SSH ou um túnel
- Demonstre um erro de porta fechada de propósito; o aprendizado vem do debug
- Evite entrar em FastAPI aqui — isso é assunto da Semana 03

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [ ] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
