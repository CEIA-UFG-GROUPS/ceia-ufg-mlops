# Desafio — Semana 00: Repositório pessoal + hello world

> Entrega até o encontro seguinte · Vale como participação técnica da semana

## Objetivo

Sair da Semana 00 com o que todas as outras onze assumem como dado: um
**repositório pessoal** no GitHub, um **ambiente verificado** e o fluxo
`branch → commit → push → pull request` rodando pela primeira vez.

O entregável não é código complexo — é a **prova de que a máquina está pronta**.

---

## O que entregar

### 1. O repositório pessoal

Crie no GitHub um repositório chamado **`meu-mlops`** (ou faça um fork do
repositório do grupo, se preferir trabalhar em cima dele). Público, ou privado
com acesso para o grupo.

Clone por **SSH**, não por HTTPS:

```bash
git clone git@github.com:<seu-usuario>/meu-mlops.git
cd meu-mlops
```

### 2. Os arquivos

Dentro de uma pasta `semana-00/` do seu repositório:

| Arquivo | Requisito |
| --- | --- |
| `README.md` | Nome, ambiente usado (Windows+WSL / Linux / macOS) e a **saída colada** do verificador |
| `hello_world.py` | Seu hello world: imprime a versão do Python e se há GPU disponível |
| `saida-lab.txt` | A saída do `hello_world.py` **rodando na máquina 4090** (ou print equivalente) |

Pode partir do [`codigo/hello_world.py`](./codigo/hello_world.py) do lab, mas
**leia o que você está copiando** e ajuste: acrescente seu nome, a data, ou o que
achar que falta.

### 3. A saída do verificador no README

Rode o verificador da sua plataforma e cole a saída **inteira** no `README.md`,
dentro de um bloco de código:

```bash
./verificar-ambiente.sh                 # Linux / WSL / macOS
```

```powershell
.\verificar-ambiente.ps1                # Windows
```

É normal sobrar ⚠️ (gcloud ainda não é obrigatório, por exemplo). Se sobrar ❌,
escreva no README **qual item falhou e o que você já tentou** — ambiente
quebrado documentado vale mais do que ambiente quebrado escondido, e é assim que
o plantão consegue te ajudar.

---

## Critérios de aceite

Marque cada item depois de verificar com o comando indicado.

**Acesso e identidade**

- [ ] `ssh -T git@github.com` responde `Hi <seu-usuario>! You've successfully authenticated`
- [ ] `git config --global user.name` e `user.email` devolvem os seus dados reais
- [ ] `git remote -v` mostra a URL em **SSH** (`git@github.com:...`), não em HTTPS

**Ambiente local**

- [ ] `python --version` (ou `python3`) responde 3.10 ou superior
- [ ] `docker run --rm hello-world` imprime `Hello from Docker!`
- [ ] No Windows: `wsl --list --verbose` mostra uma distro com `VERSION 2`
- [ ] O verificador termina com `✅ Ambiente pronto!` — ou o README explica cada ❌ restante

**Cloud e laboratório**

- [ ] Projeto criado no GCP, com os créditos educacionais visíveis em *Faturamento*
- [ ] Alerta de orçamento configurado (50% / 90% / 100%) com o seu e-mail
- [ ] `ssh <USUARIO_LAB>@<HOST_LAB> nvidia-smi` lista uma **RTX 4090**
- [ ] `hello_world.py` rodou na máquina do lab e a saída está em `saida-lab.txt`

**Entrega**

- [ ] O repositório existe e o link do PR foi postado no Discord
- [ ] O pull request foi aberto a partir de uma branch (não direto na `main`)
- [ ] O `README.md` traz a saída do verificador colada, não um print ilegível
- [ ] Nenhuma chave privada no repositório (`id_ed25519` **sem** `.pub` nunca é commitado)

**Bônus (não obrigatório)**

- [ ] `gcloud projects list` funcionando a partir do seu terminal
- [ ] Um `~/.ssh/config` com o atalho `lab4090` (passo 21 do lab), documentado no README
- [ ] Um `.gitignore` já preparado para Python (`.venv/`, `__pycache__/`, `.env`)
- [ ] Você se inscreveu para hostear uma das semanas

---

## Evidências para o PR

Cole na descrição do pull request:

1. A saída completa do `verificar-ambiente` (local)
2. A saída do `hello_world.py` rodando **na 4090**, com a linha da GPU visível
3. Um print da tela de *Crédito promocional* do GCP (pode borrar os valores)
4. Qual semana você escolheu para hostear

---

## Como entregar

1. Trabalhe no **seu repositório pessoal** do projeto (criado nesta semana) ou em um fork do repositório do grupo.
2. Crie uma branch descritiva: `git checkout -b semana-00/<seu-usuario>`.
3. Faça commits pequenos e com mensagem clara, em PT-BR.
4. Abra um **pull request** para a `main` do seu repositório, com:
   - título no formato `Semana 00 — <resumo em poucas palavras>`;
   - descrição do que foi feito, como rodar e o que ficou pendente;
   - evidências (prints, saída de terminal, links do serviço).
5. Poste o link do pull request no canal da semana no **Discord**.

> **Primeira vez abrindo um PR?** A sequência completa é:
>
> ```bash
> git checkout -b semana-00/<seu-usuario>
> git add semana-00/
> git commit -m "Semana 00: ambiente verificado e hello world"
> git push -u origin semana-00/<seu-usuario>
> ```
>
> O `git push` imprime um link pronto para abrir o pull request. Clique nele.

---

## Peer review

- Revise o pull request de **pelo menos 1 colega** antes do próximo encontro.
- Comente de forma específica: aponte o trecho, explique o porquê e sugira uma alternativa.
- Procure por: critérios de aceite atendidos, clareza do README, segredos vazados e reprodutibilidade.
- Nesta semana, o review é literal: **confira o ambiente do colega**. Abra a saída do verificador que
  ele colou e pergunte sobre cada ⚠️ e cada ❌ — se ele não souber o que aquele item significa, o
  ambiente não está pronto, só silencioso.
- Olhe com atenção especial se escapou alguma **chave privada** ou credencial do GCP no diff. Achou?
  Comente **e avise no Discord na hora** — chave vazada se revoga, não se discute em thread.
- Aprove apenas se você conseguiria rodar o projeto seguindo o README.
- Receber review também faz parte da entrega: responda aos comentários antes do encontro seguinte.
