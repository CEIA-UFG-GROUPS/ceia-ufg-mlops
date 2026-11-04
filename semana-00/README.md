# Semana 00 — Onboarding (ao vivo)

> **Encontro 1 de 12** · Primeiro semestre — Fundamentos + DevOps
> **Host:** `TODO: nome de quem conduz` · **Data:** `TODO: dd/mm`

Encontro de abertura: todo mundo sai com o ambiente pronto para os 11 labs seguintes — contas, acessos, ferramentas e canal de comunicação funcionando.

---

## Objetivos de aprendizagem

Ao final do encontro, cada participante deve ser capaz de:

- Criar e configurar a conta GCP com os créditos educacionais ativos e um alerta de orçamento ligado
- Ter um ambiente local funcional (WSL2 + Docker) ou saber usar a alternativa do lab
- Acessar por SSH as máquinas com GPU 4090 do laboratório
- Ter Git e GitHub configurados (chave SSH, nome, e-mail, repositório pessoal criado)
- Rodar o `verificar-ambiente` e entender o que cada item checa
- Estar no servidor do Discord, no canal certo e com o nome identificável

---

## Pré-requisitos

Esta é a única semana sem pré-requisito técnico — ela **é** o pré-requisito das outras onze.
O que precisa estar resolvido antes de sentar:

- Notebook/desktop próprio, com **permissão de administrador** para instalar software
- Pelo menos **15 GB livres** em disco (WSL + Docker + imagens ocupam espaço)
- Conta Google criada (a mesma que vai receber os créditos do GCP)
- Conta GitHub criada, com o e-mail já verificado
- Carregador na tomada e paciência com download: parte do tempo é a rede do lab

> **Nada instalado ainda? Sem problema.** O encontro começa do zero. Mas se der para
> baixar os instaladores antes (Docker Desktop e Git), você ganha uns 20 minutos.

---

## Agenda

| Bloco | Duração | O que acontece |
| --- | --- | --- |
| ⏱️ Conceito | ~10 min | Como o grupo funciona e por que cada ferramenta está na lista |
| 💻 Mão na massa | ~70 min | Setup guiado, todo mundo no mesmo ritmo, com checkpoints |
| 🎯 Desafio | ~10 min | Apresentação do [`desafio.md`](./desafio.md) e combinados de entrega |

> Esta semana foge um pouco do formato padrão: não há "código do lab" para escrever.
> A sessão é **guiada passo a passo**, com paradas frequentes para ninguém ficar para trás.

### ⏱️ Conceito (~10 min)

- Como o grupo funciona: labs independentes, rodízio de hosts, entrega por pull request
- O domínio recorrente do semestre: análise de sentimento (NLP) como fio condutor
- Por que cada ferramenta está na lista: Git (histórico), Docker (reprodutibilidade), GCP (produção), 4090 (GPU)
- Visão geral da infraestrutura: GCP (créditos) + máquinas 4090 do lab, e quando usar cada uma
- Regras de custo: o que pode ficar ligado e o que precisa ser desligado ao fim do lab

### 💻 Mão na massa (~70 min)

- Instalar WSL2 + Docker Desktop (Windows) ou Docker Engine (Linux/macOS)
- Configurar Git, gerar chave SSH e cadastrar no GitHub
- Criar o projeto no GCP e ativar os créditos educacionais
- Primeiro acesso SSH às máquinas 4090 do lab (`nvidia-smi` para confirmar a GPU)
- Rodar o `verificar-ambiente` e fechar os ❌ que sobrarem
- Entrar no Discord, se apresentar e escolher a semana que vai hostear

### 🎯 Desafio (~10 min)

Criar o repositório pessoal do projeto do semestre, rodar o verificador e o hello world,
e abrir o primeiro pull request.

Enunciado completo em [`desafio.md`](./desafio.md).

---

## Passo a passo

Ao longo dos comandos abaixo, substitua os placeholders:

| Placeholder | O que é | Onde conseguir |
| --- | --- | --- |
| `<seu-usuario>` | Seu usuário do GitHub | <https://github.com/settings/profile> |
| `<seu-email>` | O e-mail da conta GitHub | o mesmo da conta |
| `<HOST_LAB>` | Endereço da máquina 4090 (ex.: `gpu01.lab.ufg.br`) | canal `#semana-00` no Discord |
| `<USUARIO_LAB>` | Seu login nas máquinas do laboratório | o host entrega no encontro |

> **Dois sistemas, duas colunas.** Quem está no Windows faz a versão PowerShell;
> quem está no Linux/macOS (ou já dentro do WSL) faz a versão Bash. A partir do
> bloco 2, **quem instalou o WSL roda tudo dentro do Ubuntu**, não no PowerShell —
> é lá que o semestre inteiro vai acontecer.

### Bloco 1 — terminal de verdade: WSL2 (~15 min)

*(Linux e macOS já têm terminal POSIX: pule para o passo 4.)*

1. **Conferir se a virtualização está ligada.** Abra o Gerenciador de Tarefas
   (`Ctrl+Shift+Esc`) → aba *Desempenho* → *CPU*. Procure a linha
   **Virtualização**.

   *Esperado:* `Virtualização: Habilitado`. Se estiver **Desabilitado**, pare
   aqui e vá para o item 1 do [Troubleshooting](#troubleshooting) — nada do WSL
   vai funcionar antes disso.

2. **Instalar o WSL2 com Ubuntu.** Abra o **PowerShell como administrador**
   (botão direito no menu Iniciar → *Terminal (Admin)*) e rode:

   ```powershell
   wsl --install -d Ubuntu
   ```

   *Esperado:* download da plataforma de máquina virtual, do kernel e do Ubuntu,
   terminando com um pedido de **reiniciar**. Reinicie de verdade — não adianta
   seguir sem isso.

   Já tinha WSL instalado? Confirme a versão:

   ```powershell
   wsl --list --verbose
   ```

   A coluna `VERSION` precisa ser **2**. Se vier `1`, veja o item 2 do Troubleshooting.

3. **Criar o usuário do Linux.** Depois de reiniciar, abra o app **Ubuntu** pelo
   menu Iniciar. Na primeira execução ele pede um usuário e uma senha — **não
   precisam ser iguais aos do Windows**, e a senha não aparece enquanto você
   digita (é normal). Guarde essa senha: é ela que o `sudo` vai pedir.

   ```bash
   whoami
   uname -sr
   ```

   *Esperado:* o usuário que você acabou de criar e algo como
   `Linux 6.6.87.2-microsoft-standard-WSL2`.

4. **Atualizar os pacotes e instalar o básico.** Dentro do Ubuntu (ou no seu
   Linux nativo):

   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y git curl python3 python3-pip python3-venv
   ```

   *Esperado:* termina sem erro. Confirme:

   ```bash
   git --version && python3 --version
   ```

   > **macOS:** instale as ferramentas de linha de comando com
   > `xcode-select --install` e, se usar Homebrew, `brew install git python`.

> ✅ **checkpoint 1 — todo mundo chegou até aqui?**
> Todo mundo com um terminal Linux aberto, respondendo `git --version` e `python3 --version`.
> Quem travou na virtualização fica com o plano B (ver *Notas para o host*) e segue junto.

### Bloco 2 — Git e GitHub por SSH (~15 min)

5. **Dizer ao Git quem é você.** Esse nome e e-mail vão em **todo commit** do
   semestre, então capriche:

   ```bash
   git config --global user.name "Seu Nome Completo"
   git config --global user.email "<seu-email>"
   git config --global init.defaultBranch main
   git config --global pull.rebase false
   ```

   *Esperado:* nenhum output (o Git é silencioso quando dá certo). Confira com:

   ```bash
   git config --global --list
   ```

6. **Gerar a chave SSH.** Uma única chave, formato `ed25519`:

   ```bash
   ssh-keygen -t ed25519 -C "<seu-email>"
   ```

   *Esperado:* três perguntas. Aceite o caminho padrão (`Enter`), e defina uma
   passphrase — ou deixe vazia com `Enter` se preferir comodidade. No fim,
   aparece o *randomart* e dois arquivos novos:

   ```bash
   ls -l ~/.ssh/id_ed25519*
   ```

   `id_ed25519` é a chave **privada** (nunca sai da sua máquina, nunca vai para
   um repositório) e `id_ed25519.pub` é a **pública** (essa sim é para distribuir).

7. **Ligar o ssh-agent e carregar a chave:**

   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

   *Esperado:* `Agent pid ...` e `Identity added: ...`.

   > **PowerShell nativo (sem WSL):** o agente é um serviço do Windows. Em um
   > terminal **como administrador**, rode uma vez:
   >
   > ```powershell
   > Get-Service ssh-agent | Set-Service -StartupType Automatic
   > Start-Service ssh-agent
   > ssh-add $HOME\.ssh\id_ed25519
   > ```

8. **Copiar a chave pública e cadastrar no GitHub.**

   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

   ```powershell
   # PowerShell: copia direto para a área de transferência
   Get-Content $HOME\.ssh\id_ed25519.pub | Set-Clipboard
   ```

   Selecione a linha inteira (começa com `ssh-ed25519` e termina no seu e-mail),
   copie e cole em <https://github.com/settings/ssh/new>:
   *Title* = algo como `notebook-ufg`, *Key type* = **Authentication Key**, e
   **Add SSH key**.

   > ⚠️ Copiou o arquivo **sem** o `.pub`? Essa é a chave privada — apague a
   > chave do GitHub, gere outra com `ssh-keygen` e recomece o passo 6.

9. **Testar a conexão:**

   ```bash
   ssh -T git@github.com
   ```

   *Esperado:* na primeira vez ele pergunta sobre a autenticidade do host —
   responda `yes`. Depois:

   ```text
   Hi <seu-usuario>! You've successfully authenticated, but GitHub does not provide shell access.
   ```

   Essa mensagem **é o sucesso**, mesmo parecendo um aviso. Se vier
   `Permission denied (publickey)`, veja o item 5 do Troubleshooting.

> ✅ **checkpoint 2 — todo mundo chegou até aqui?**
> Todo mundo vendo o `Hi <usuario>!` do GitHub. Esse é o item que mais trava a turma —
> não siga com ninguém pendurado aqui.

### Bloco 3 — Docker (~15 min)

10. **Instalar o Docker.**

    - **Windows:** baixe o **Docker Desktop** em
      <https://docs.docker.com/desktop/install/windows-install/> e instale
      mantendo marcada a opção *Use WSL 2 instead of Hyper-V*. Depois de abrir,
      vá em **Settings → Resources → WSL Integration** e **ative o toggle da sua
      distro Ubuntu**. Sem isso, o `docker` não existe dentro do WSL.
    - **macOS:** Docker Desktop for Mac (escolha Apple Silicon ou Intel).
    - **Linux:**

      ```bash
      curl -fsSL https://get.docker.com | sh
      sudo usermod -aG docker $USER
      newgrp docker
      ```

11. **Confirmar que o daemon responde.** No terminal onde você vai trabalhar
    (dentro do Ubuntu, se for Windows):

    ```bash
    docker --version
    docker info --format '{{.ServerVersion}}'
    ```

    *Esperado:* a versão do cliente **e** a do servidor. Se o segundo comando
    reclamar de `Cannot connect to the Docker daemon`, o Docker Desktop não está
    aberto ou a integração com o WSL não foi ligada (item 3 do Troubleshooting).

12. **O hello world oficial do Docker:**

    ```bash
    docker run --rm hello-world
    ```

    *Esperado:* o Docker não acha a imagem localmente, baixa do Docker Hub e
    imprime `Hello from Docker!` seguido da explicação dos quatro passos que
    acabaram de acontecer. Leia esses quatro passos — eles são, em resumo, a
    Semana 04 inteira.

13. **Um container com terminal, só para sentir o isolamento:**

    ```bash
    docker run --rm -it python:3.12-slim python -c "import sys; print(sys.version)"
    ```

    *Esperado:* uma versão do Python **diferente** da que está na sua máquina,
    vinda de dentro do container. Esse é o ponto: o container traz o ambiente
    junto.

> ✅ **checkpoint 3 — todo mundo chegou até aqui?**
> `docker run --rm hello-world` funcionando no terminal de trabalho de cada um.

### Bloco 4 — GCP e créditos educacionais (~15 min)

14. **Entrar no console e aceitar os termos.** Acesse
    <https://console.cloud.google.com> com a **conta Google que vai usar o
    semestre inteiro** (de preferência a institucional) e aceite os termos de uso.

15. **Criar o projeto do semestre.** No seletor de projetos (barra superior) →
    **Novo projeto**:

    - *Nome do projeto:* `mlops-ceia-<seu-usuario>`
    - Anote o **Project ID** gerado — ele é único no mundo e vai aparecer em
      todos os comandos a partir da Semana 06.

    *Esperado:* o projeto aparece selecionado na barra superior.

16. **Ativar os créditos educacionais.** O host vai distribuir o código do
    programa educacional no Discord. Com ele em mãos:

    - Acesse <https://console.cloud.google.com/education>
    - Cole o código e confirme a instituição (UFG)
    - Verifique em **Faturamento → Crédito promocional** que o valor e a data de
      validade aparecem

    *Esperado:* a conta de faturamento criada e **vinculada ao projeto do passo 15**
    (Faturamento → *Vincular conta de faturamento*). Sem o vínculo, o projeto
    existe mas não habilita serviço nenhum.

    > 💳 Os créditos educacionais **não pedem cartão de crédito**. Se a tela
    > estiver pedindo cartão, você caiu no fluxo de trial comum — volte e use o
    > link `/education`.

17. **Ligar um alerta de orçamento agora** (sim, agora — é mais fácil do que
    explicar o estouro depois). Em **Faturamento → Orçamentos e alertas →
    Criar orçamento**:

    - Escopo: o projeto do passo 15
    - Valor: o combinado da turma (o host informa)
    - Alertas em **50%, 90% e 100%**, por e-mail

    *Esperado:* o orçamento listado com o seu e-mail como destinatário.

18. **(Opcional) Instalar a `gcloud`.** A CLI só vira obrigatória na Semana 06,
    mas se quiser já deixar pronto:

    ```bash
    # Linux / WSL
    curl -sSL https://sdk.cloud.google.com | bash
    exec -l $SHELL
    gcloud init
    ```

    ```powershell
    # Windows: instalador gráfico
    # https://cloud.google.com/sdk/docs/install#windows
    ```

    Depois:

    ```bash
    gcloud auth login
    gcloud config set project <SEU_PROJECT_ID>
    gcloud projects list
    ```

    *Esperado:* o seu projeto na lista. Esse é todo o uso de `gcloud` desta semana.

> ✅ **checkpoint 4 — todo mundo chegou até aqui?**
> Projeto criado, créditos visíveis na tela de faturamento e alerta de orçamento configurado.

### Bloco 5 — máquinas 4090, Discord e rodízio (~15 min)

19. **Mandar a sua chave pública para a máquina do lab.** O host distribui
    `<USUARIO_LAB>` e `<HOST_LAB>` no Discord.

    ```bash
    ssh-copy-id -i ~/.ssh/id_ed25519.pub <USUARIO_LAB>@<HOST_LAB>
    ```

    *Esperado:* ele pede a senha provisória uma única vez e responde
    `Number of key(s) added: 1`.

    > Sem `ssh-copy-id` (PowerShell nativo ou macOS antigo), faça na mão:
    >
    > ```powershell
    > type $HOME\.ssh\id_ed25519.pub | ssh <USUARIO_LAB>@<HOST_LAB> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
    > ```

20. **Entrar e confirmar que a GPU está lá:**

    ```bash
    ssh <USUARIO_LAB>@<HOST_LAB>
    nvidia-smi
    ```

    *Esperado:* na primeira conexão, a pergunta sobre o fingerprint do host
    (responda `yes` — e confira com o host se o fingerprint bate). Depois, a
    tabela do `nvidia-smi` com **NVIDIA GeForce RTX 4090**, a versão do driver e
    o consumo de memória. **Tire um print dessa tela**: ela vale como evidência
    no desafio.

21. **Guardar um atalho** para não digitar o endereço inteiro toda vez. Ainda na
    sua máquina (`exit` para sair do lab), edite `~/.ssh/config`:

    ```text
    Host lab4090
        HostName <HOST_LAB>
        User <USUARIO_LAB>
        IdentityFile ~/.ssh/id_ed25519
        ServerAliveInterval 60
    ```

    ```bash
    ssh lab4090 nvidia-smi --query-gpu=name --format=csv,noheader
    ```

    *Esperado:* o nome da GPU, sem precisar entrar na máquina.

22. **Discord: entrar, se identificar e escolher a semana.**

    - Entre pelo convite do servidor (link no e-mail da turma)
    - Ajuste o **apelido no servidor** para `Nome Sobrenome (@usuario-github)` —
      é assim que a gente liga PR a pessoa
    - Dê um alô no canal geral e entre no `#semana-00`
    - Escolha **uma semana para hostear** na thread de rodízio. Quem nunca
      apresentou tem prioridade, e dupla é bem-vinda

23. **Fechar o ciclo: rodar o verificador.** Clone este repositório e rode o
    script da sua plataforma:

    ```bash
    git clone git@github.com:<org-ou-usuario>/ceia-ufg-mlops.git
    cd ceia-ufg-mlops/semana-00/codigo
    ./verificar-ambiente.sh --host-lab <USUARIO_LAB>@<HOST_LAB>
    python3 hello_world.py
    ```

    ```powershell
    cd ceia-ufg-mlops\semana-00\codigo
    .\verificar-ambiente.ps1 -HostLab <USUARIO_LAB>@<HOST_LAB>
    python hello_world.py
    ```

    *Esperado:* a linha final `✅ Ambiente pronto!` e o hello world imprimindo a
    versão do Python. Qualquer ❌ vem com a dica de correção logo abaixo — resolva
    e rode de novo. **Guarde essa saída**: ela é a entrega do desafio.

> ✅ **checkpoint 5 — fechamento**
> Todo mundo com `✅ Ambiente pronto!` (ou com os pendentes anotados e um plantão
> designado), no Discord, e inscrito em uma semana do rodízio.

---

## Troubleshooting

Os erros abaixo cobrem a esmagadora maioria dos travamentos desta semana.
Achou um que não está aqui? Poste no `#semana-00` **com a mensagem de erro
completa** — e depois mande um PR acrescentando a solução nesta seção.

### 1. `wsl --install` falha, ou a virtualização está desabilitada

**Sintoma:** `Erro: 0x80370102 ... A máquina virtual não pôde ser iniciada
porque um recurso necessário não está instalado`, ou o Gerenciador de Tarefas
mostrando `Virtualização: Desabilitado`.

**Causa:** VT-x (Intel) / SVM Mode (AMD) desligado na BIOS/UEFI, ou os recursos
opcionais do Windows faltando.

**Solução:**

1. Reinicie e entre na BIOS/UEFI (`Del`, `F2`, `F10` ou `F12`, conforme o
   fabricante). Procure por *Intel Virtualization Technology*, *VT-x*, *SVM Mode*
   ou *AMD-V* e deixe **Enabled**. Salve e saia.
2. De volta no Windows, em um PowerShell **como administrador**:

   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```

3. Reinicie e repita o passo 2 do lab.

> Em notebooks corporativos, a BIOS pode estar bloqueada por política de TI.
> Nesse caso, use o plano B do host (máquina do lab via SSH ou Codespaces) e
> siga o semestre por lá — **nada do curso depende de Docker local**.

### 2. WSL instalado, mas na versão 1

**Sintoma:** `wsl --list --verbose` mostra `VERSION 1`. Docker Desktop recusa a
integração.

**Solução:**

```powershell
wsl --set-default-version 2
wsl --set-version Ubuntu 2      # a conversão leva alguns minutos
wsl --list --verbose            # confirme: VERSION 2
```

### 3. `docker: command not found` dentro do WSL (ou daemon não responde)

**Sintoma:** o Docker Desktop está aberto no Windows, mas no Ubuntu o comando
não existe — ou existe e devolve
`Cannot connect to the Docker daemon at unix:///var/run/docker.sock`.

**Causa:** a integração WSL ↔ Docker Desktop está desligada.

**Solução:** Docker Desktop → **Settings** → **Resources** → **WSL Integration**
→ ligue *Enable integration with my default WSL distro* **e** o toggle da sua
distro Ubuntu → **Apply & restart**. Feche e reabra o terminal do Ubuntu:

```bash
docker info --format '{{.ServerVersion}}'
```

Confira também, em **Settings → General**, se *Use the WSL 2 based engine* está
marcado.

### 4. `permission denied while trying to connect to the Docker daemon socket`

**Sintoma:** Linux nativo, `docker ps` reclamando de permissão.

**Causa:** seu usuário não está no grupo `docker`.

**Solução:**

```bash
sudo usermod -aG docker $USER
newgrp docker          # ou simplesmente deslogue e logue de novo
docker run --rm hello-world
```

Nunca resolva isso com `sudo docker` para sempre: é o caminho curto para
arquivos `root` espalhados pelo projeto.

### 5. `Permission denied (publickey)` no GitHub ou no lab

**Sintoma:** `ssh -T git@github.com` ou `ssh <USUARIO_LAB>@<HOST_LAB>` devolvendo
`Permission denied (publickey)`.

**Diagnóstico — rode com `-v` e leia as linhas `Offering public key`:**

```bash
ssh -vT git@github.com 2>&1 | grep -E "Offering|Authentications|identity file"
```

**Causas mais comuns, em ordem de frequência:**

1. **A chave não foi cadastrada** — confira em <https://github.com/settings/keys>
   se a chave listada é igual à saída de `cat ~/.ssh/id_ed25519.pub`.
2. **Você gerou a chave no Windows e está testando no WSL** (ou vice-versa). São
   `~/.ssh` diferentes! Gere uma chave no ambiente onde vai trabalhar, ou copie:
   `cp /mnt/c/Users/<voce>/.ssh/id_ed25519* ~/.ssh/ && chmod 600 ~/.ssh/id_ed25519`.
3. **Permissões largas demais** — o OpenSSH ignora chaves que o grupo/mundo
   possa ler:

   ```bash
   chmod 700 ~/.ssh && chmod 600 ~/.ssh/id_ed25519 && chmod 644 ~/.ssh/id_ed25519.pub
   ```

4. **O agente não está rodando** nesta sessão: `eval "$(ssh-agent -s)" && ssh-add ~/.ssh/id_ed25519`.
5. **Chave cadastrada na conta GitHub errada** (pessoal vs. institucional).

### 6. `git push` pedindo usuário e senha

**Sintoma:** o GitHub pede `Username for 'https://github.com'` e recusa a senha
da conta.

**Causa:** o remote está em HTTPS, não em SSH (e o GitHub não aceita senha desde
2021).

**Solução:**

```bash
git remote -v
git remote set-url origin git@github.com:<seu-usuario>/<repo>.git
git remote -v          # agora deve começar com git@github.com:
```

### 7. `Host key verification failed` ao conectar no 4090

**Sintoma:** aviso em caixa alta sobre
`REMOTE HOST IDENTIFICATION HAS CHANGED`.

**Causa:** a máquina do lab foi reinstalada e a chave antiga ficou no seu
`known_hosts`.

**Solução:** confirme com o host que a reinstalação aconteceu (nunca ignore o
aviso às cegas) e remova só a entrada antiga:

```bash
ssh-keygen -R <HOST_LAB>
ssh <USUARIO_LAB>@<HOST_LAB>
```

### 8. Os créditos do GCP não aparecem / a tela pede cartão

**Sintoma:** você resgatou o código mas *Crédito promocional* está vazio, ou o
console insiste em pedir cartão de crédito.

**Solução:**

1. Confirme que você está logado com a **conta que recebeu o código** (olhe o
   avatar no canto superior direito — contas Google misturadas são a causa número um).
2. Use o fluxo <https://console.cloud.google.com/education>, não o de trial comum.
3. Depois de resgatar, **vincule a conta de faturamento ao projeto**:
   Faturamento → *Vincular conta de faturamento* → selecione o projeto.
4. Continua sem aparecer? Poste no `#semana-00` — o host tem o canal de suporte
   do programa educacional.

### 9. O verificador imprime `?` no lugar dos ✅/❌

**Sintoma:** Windows PowerShell mostrando caixinhas ou interrogações.

**Causa:** console em codepage legada.

**Solução:** o script já tenta ajustar sozinho; se não resolver, force antes de
rodar:

```powershell
chcp 65001
.\verificar-ambiente.ps1
```

É cosmético: o resultado da checagem continua correto de qualquer jeito.

### 10. `.\verificar-ambiente.ps1` recusado pela política de execução

**Sintoma:** `não pode ser carregado porque a execução de scripts foi
desabilitada neste sistema`.

**Solução (vale só para a janela atual, não mexe na máquina):**

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\verificar-ambiente.ps1
```

---

## Código

O código de apoio desta semana vive em [`codigo/`](./codigo/) — veja
[`codigo/README.md`](./codigo/README.md) para as opções de cada script.

| Arquivo | O que é |
| --- | --- |
| [`codigo/verificar-ambiente.ps1`](./codigo/verificar-ambiente.ps1) | Verificador de ambiente para Windows/PowerShell (git, SSH, python, docker, wsl, gcloud, lab) |
| [`codigo/verificar-ambiente.sh`](./codigo/verificar-ambiente.sh) | O mesmo verificador para Linux, WSL e macOS |
| [`codigo/hello_world.py`](./codigo/hello_world.py) | Hello world mínimo: versão do Python, sistema e GPU detectada |

Os verificadores são somente leitura — não instalam nem alteram nada — e saem com
código **0** (tudo ok) ou **1** (algo obrigatório faltando).

---

## Recursos e links

- [Google Cloud for Education](https://cloud.google.com/edu)
- [Google Cloud — Free tier e créditos iniciais](https://cloud.google.com/free)
- [Cloud Billing — criar orçamentos e alertas](https://cloud.google.com/billing/docs/how-to/budgets)
- [Instalação do WSL2](https://learn.microsoft.com/windows/wsl/install)
- [WSL — boas práticas de setup (Microsoft Learn)](https://learn.microsoft.com/windows/wsl/setup/environment)
- [Docker Desktop — instalação](https://docs.docker.com/desktop/)
- [Docker Desktop — integração com WSL2](https://docs.docker.com/desktop/features/wsl/)
- [Gerando uma chave SSH para o GitHub](https://docs.github.com/authentication/connecting-to-github-with-ssh)
- [GitHub Docs — Quickstart (criar conta, repo e primeiro commit)](https://docs.github.com/en/get-started/quickstart)
- [Git — primeiros passos e configuração (Pro Git, em português)](https://git-scm.com/book/pt-br/v2/Primeiros-passos-Configura%C3%A7%C3%A3o-Inicial-do-Git)
- [Discord — Guia para iniciantes](https://support.discord.com/hc/en-us/articles/360045138571-Beginner-s-Guide-to-Discord)

---

## Notas para o host

- Esta é a única sessão majoritariamente de setup — proteja o tempo, nada de teoria longa
- Tenha um checklist compartilhado (planilha ou thread no Discord) para marcar quem concluiu cada item
- Separe duas pessoas como plantão de setup, para resolver problemas individuais sem travar a turma
- Peça para quem terminar cedo ajudar quem travou — é o primeiro exercício de peer review
- **O gargalo real é download**, não conceito: peça com antecedência no Discord que todo mundo já baixe
  o instalador do Docker Desktop e rode `wsl --install` em casa. Quem chegar com isso pronto economiza
  metade do bloco 1
- **O checkpoint 2 (SSH no GitHub) é onde a turma mais trava.** Reserve folga ali e tenha o item 5 do
  Troubleshooting aberto em uma aba
- Tenha em mãos, antes do encontro: o código dos créditos educacionais, o `<HOST_LAB>`, os logins
  provisórios do laboratório e o fingerprint da máquina 4090 (para ninguém aceitar às cegas)
- Combine o valor do alerta de orçamento com o grupo **antes** do passo 17, para não debater em aula
- Deixe a inscrição do rodízio de hosts para o fim, com a tabela de semanas já projetada na tela
- Plano B para quem não conseguir virtualização: conta no lab via SSH (tudo roda lá) ou GitHub Codespaces

**Checklist de preparação:**

- [ ] Rodar o lab inteiro do zero antes do encontro, cronometrando
- [x] Preencher a seção *Passo a passo* e subir o conteúdo de `codigo/`
- [ ] Postar os pré-requisitos no Discord com pelo menos 3 dias de antecedência
- [ ] Conseguir e testar o código dos créditos educacionais do GCP
- [ ] Criar os logins provisórios nas máquinas 4090 e anotar o fingerprint SSH
- [ ] Preparar um plano B para quem travar no setup (ambiente pronto, repositório de referência)
- [ ] Revisar o `desafio.md` e os critérios de aceite
