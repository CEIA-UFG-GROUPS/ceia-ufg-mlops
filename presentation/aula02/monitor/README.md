# Material de Estudo: Sistemas Operacionais, Bash e SSH

Este guia foi desenvolvido para fornecer uma base técnica sólida sobre como os sistemas operacionais funcionam e como interagir com eles via terminal. Este conhecimento é o alicerce para qualquer profissional que trabalhe com dados e modelos em produção.

---

## 1. Arquitetura do Sistema Operacional e Gestão de Recursos

O Sistema Operacional (SO) é o software que gerencia o hardware. Para MLOps, entender essa gestão é a diferença entre um modelo que roda e um sistema que trava por falta de recursos.

### 1.1 Kernel vs. Shell

| Componente | Descrição |
|------------|-----------|
| **Kernel** | O núcleo do SO que gerencia hardware, memória, processos e I/O |
| **Shell** | Interface que interpreta comandos do usuário e os envia ao kernel |

> [!TIP]
> O Bash (Bourne Again Shell) é o shell padrão na maioria das distribuições Linux.

### 1.2 Gerenciamento de Processos

Um **processo** é um programa em execução. Entender como gerenciá-los é essencial para MLOps.

| Modo | Descrição | Exemplo |
|------|-----------|---------|
| **Foreground** | Ocupa o terminal até finalizar | `python train.py` |
| **Background** | Libera o terminal para outros comandos | `python train.py &` |
| **Nohup** | Continua mesmo após fechar o terminal | `nohup python train.py &` |

#### Sinais de Interrupção

| Sinal | Código | Descrição |
|-------|--------|-----------|
| `SIGTERM` | 15 | Pedido educado para fechar (permite salvar dados) |
| `SIGKILL` | 9 | Encerramento forçado (usa com `kill -9 PID`) |
| `SIGINT` | 2 | Interrupção via teclado (`Ctrl+C`) |
| `SIGSTOP` | 19 | Pausa o processo |
| `SIGCONT` | 18 | Continua um processo pausado |

```bash
# Listar processos
ps aux | grep python

# Matar processo específico
kill -9 <PID>

# Matar todos os processos de um programa
pkill -f "python train.py"
```

### 1.3 Memória Virtual e Swap

A **Memória RAM** é rápida mas limitada. Quando a RAM acaba, o SO usa o **Swap** (espaço no disco que simula RAM).

> [!CAUTION]
> **Impacto Crítico:** O disco é 1000x mais lento que a RAM. Se o seu modelo entrar em "Swap", um treinamento de 1 hora pode levar 20 horas.

```bash
# Verificar uso de memória
free -h

# Verificar uso de swap em tempo real
vmstat 1

# Limpar cache de memória (requer root)
sudo sync && sudo sysctl -w vm.drop_caches=3
```

### 1.4 Permissões e Propriedade de Arquivos (rwx)

No Linux, a segurança é baseada em três permissões para três grupos:

| Permissão | Símbolo | Valor |
|-----------|---------|-------|
| **Read** | r | 4 |
| **Write** | w | 2 |
| **Execute** | x | 1 |

| Grupo | Descrição |
|-------|-----------|
| **Dono (u)** | O criador do arquivo |
| **Grupo (g)** | Usuários do mesmo grupo |
| **Outros (o)** | Todos os demais |

```bash
# Formato: chmod [dono][grupo][outros] arquivo
chmod 755 script.sh   # Dono: rwx (7), Grupo: r-x (5), Outros: r-x (5)
chmod 644 config.txt  # Dono: rw- (6), Grupo: r-- (4), Outros: r-- (4)

# Mudar dono do arquivo
chown usuario:grupo arquivo.txt

# Mudar recursivamente
chown -R usuario:grupo diretorio/
```

---

## 2. Comandos Bash Essenciais

O Bash não é apenas para mover arquivos — é uma linguagem de automação poderosa.

### 2.1 Navegação e Manipulação de Arquivos

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `pwd` | Diretório atual | `pwd` |
| `ls` | Listar arquivos | `ls -lah` (lista detalhada + ocultos) |
| `cd` | Navegar | `cd ~/projetos` |
| `mkdir` | Criar diretório | `mkdir -p dir/subdir` |
| `cp` | Copiar | `cp -r origem/ destino/` |
| `mv` | Mover/Renomear | `mv arquivo.txt novo_nome.txt` |
| `rm` | Remover | `rm -rf diretorio/`  |
| `touch` | Criar arquivo vazio | `touch arquivo.txt` |
| `find` | Buscar arquivos | `find . -name "*.py"` |
| `locate` | Busca rápida (usa banco de dados) | `locate arquivo.txt` |

### 2.2 Visualização e Edição de Arquivos

| Comando | Descrição | Exemplo |
|---------|-----------|---------|
| `cat` | Mostra conteúdo completo | `cat arquivo.txt` |
| `head` | Primeiras N linhas | `head -n 20 arquivo.txt` |
| `tail` | Últimas N linhas | `tail -f logs.txt` (tempo real) |
| `less` | Navegação interativa | `less arquivo.txt` |
| `grep` | Busca por padrão | `grep -r "erro" logs/` |
| `wc` | Conta linhas/palavras | `wc -l arquivo.txt` |
| `diff` | Compara arquivos | `diff arquivo1 arquivo2` |

### 2.3 Variáveis de Ambiente e PATH

O **PATH** é uma lista de diretórios onde o sistema busca executáveis.

```bash
# Visualizar PATH atual
echo $PATH

# Adicionar ao PATH temporariamente
export PATH=$PATH:/novo/caminho

# Adicionar permanentemente (adicione ao ~/.bashrc ou ~/.zshrc)
echo 'export PATH=$PATH:/novo/caminho' >> ~/.bashrc
source ~/.bashrc

# Variáveis de ambiente comuns
export PYTHONPATH=/caminho/para/modulos
export CUDA_VISIBLE_DEVICES=0,1    # GPUs disponíveis
export TF_CPP_MIN_LOG_LEVEL=2      # Silenciar logs do TensorFlow
```

> [!IMPORTANT]
> Se o terminal diz "command not found" para um programa instalado, provavelmente o PATH está incorreto.

### 2.4 Streams: stdin, stdout e stderr

Todo comando tem três canais de dados:

| Stream | Número | Descrição |
|--------|--------|-----------|
| **stdin** | 0 | Entrada padrão |
| **stdout** | 1 | Saída padrão (resultado) |
| **stderr** | 2 | Saída de erro |

```bash
# Redirecionar saída para arquivo
python script.py > resultado.log

# Redirecionar erros para arquivo separado
python script.py 1> resultado.log 2> erros.log

# Redirecionar ambos para o mesmo arquivo
python script.py &> tudo.log

# Usar Pipe para conectar comandos
cat arquivo.txt | grep "pattern" | wc -l
```

### 2.5 Automação com Loops e Condicionais

```bash
# Loop para processar múltiplos arquivos
for f in *.jpg; do
    mv "$f" "processed_${f}"
done

# Processamento paralelo com xargs
find . -name "*.csv" | xargs -P 4 -I {} python process.py {}

# Condicional em script
if [ -f "modelo.pkl" ]; then
    echo "Modelo encontrado!"
else
    python train.py
fi

# Loop while para monitoramento
while true; do
    nvidia-smi
    sleep 5
done
```

### 2.6 Agendamento de Tarefas (Cron)

```bash
# Editar crontab
crontab -e

# Formato: minuto hora dia_mes mês dia_semana comando
# Exemplos:
# 0 2 * * * /home/user/backup.sh          # Todo dia às 2h
# */15 * * * * /home/user/monitor.sh      # A cada 15 minutos
# 0 0 * * 0 /home/user/cleanup.sh         # Todo domingo à meia-noite
```

---

## 3. SSH e Acesso Remoto

O **SSH (Secure Shell)** é a ferramenta que permite acessar servidores potentes (com GPUs) a partir de um notebook simples.

### 3.1 Conceitos Fundamentais

| Conceito | Descrição |
|----------|-----------|
| **Criptografia Assimétrica** | Par de chaves: pública (servidor) e privada (local) |
| **Porta Padrão** | 22 (pode ser alterada por segurança) |
| **Protocolo** | Comunicação criptografada sobre redes inseguras |

### 3.2 Geração e Configuração de Chaves

```bash
# Gerar par de chaves (RSA 4096-bit recomendado)
ssh-keygen -t rsa -b 4096 -C "seu_email@exemplo.com"

# Gerar chave Ed25519 (mais moderna e segura)
ssh-keygen -t ed25519 -C "seu_email@exemplo.com"

# Copiar chave pública para o servidor
ssh-copy-id usuario@servidor

# Manualmente (se ssh-copy-id não disponível)
cat ~/.ssh/id_rsa.pub | ssh usuario@servidor 'cat >> ~/.ssh/authorized_keys'
```

### 3.3 Configuração Avançada (~/.ssh/config)

```bash
# Arquivo: ~/.ssh/config
# Simplifica conexões e habilita recursos avançados

Host gpu-server
    HostName 192.168.1.100
    User mlops
    IdentityFile ~/.ssh/id_rsa
    Port 22
    
Host aws-training
    HostName ec2-xx-xx-xxx-xxx.compute-1.amazonaws.com
    User ubuntu
    IdentityFile ~/.ssh/aws-key.pem

Host bastion
    HostName bastion.empresa.com
    User admin
    
Host internal-server
    HostName 10.0.0.50
    User deploy
    ProxyJump bastion  # Conecta através do bastion (jump host)

# Configuração global para multiplexing (conexões mais rápidas)
Host *
    ControlMaster auto
    ControlPath ~/.ssh/sockets/%r@%h-%p
    ControlPersist 600
```

```bash
# Uso simplificado após configuração
ssh gpu-server
scp modelo.pkl gpu-server:/home/mlops/models/
```

### 3.4 Tunelamento SSH (Port Forwarding)

O tunelamento cria "pontes" seguras para acessar serviços remotos.

#### Local Port Forwarding

Acessa um serviço remoto como se fosse local:

```bash
# Acessar Jupyter Notebook remoto no navegador local
ssh -L 8888:localhost:8888 usuario@servidor
# Agora acesse: http://localhost:8888

# Acessar TensorBoard remoto
ssh -L 6006:localhost:6006 usuario@servidor

# Acessar banco de dados remoto
ssh -L 5432:localhost:5432 usuario@servidor
```

#### Remote Port Forwarding

Expõe um serviço local para o servidor remoto:

```bash
# Permitir que o servidor acesse algo na sua máquina
ssh -R 9000:localhost:3000 usuario@servidor
```

#### Dynamic Port Forwarding (Proxy SOCKS)

Cria um proxy para todo o tráfego:

```bash
# Criar proxy SOCKS na porta 1080
ssh -D 1080 usuario@servidor
# Configure seu navegador para usar localhost:1080 como proxy SOCKS
```

### 3.5 Transferência de Arquivos

| Ferramenta | Uso | Comando |
|------------|-----|---------|
| **scp** | Cópia simples | `scp arquivo.txt usuario@servidor:/destino/` |
| **rsync** | Sincronização eficiente | `rsync -avz --progress local/ servidor:/remoto/` |
| **sftp** | FTP seguro interativo | `sftp usuario@servidor` |

```bash
# scp - Copiar arquivo para servidor
scp modelo.pkl usuario@servidor:/home/user/models/

# scp - Copiar diretório recursivamente
scp -r dataset/ usuario@servidor:/data/

# rsync - Sincronizar (só transfere diferenças)
rsync -avz --progress \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    ./projeto/ usuario@servidor:/projetos/

# rsync - Retomar transferência interrompida
rsync -avz --partial --progress grande_arquivo.tar.gz servidor:/destino/
```

### 3.6 Persistência de Sessão: Tmux e Screen

> [!WARNING]
> Se sua internet cair durante um treinamento SSH, **o processo é interrompido**! Use `tmux` ou `screen` para evitar isso.

#### Tmux (Recomendado)

```bash
# Criar nova sessão
tmux new -s treino

# Listar sessões
tmux ls

# Anexar a sessão existente
tmux attach -t treino

# Desanexar (dentro do tmux): Ctrl+B, depois D

# Comandos dentro do tmux:
# Ctrl+B, C       → Nova janela
# Ctrl+B, N       → Próxima janela
# Ctrl+B, P       → Janela anterior
# Ctrl+B, %       → Dividir verticalmente
# Ctrl+B, "       → Dividir horizontalmente
```

#### Screen (Alternativa)

```bash
# Criar sessão
screen -S treino

# Listar sessões
screen -ls

# Reconectar
screen -r treino

# Desanexar: Ctrl+A, depois D
```

---

## 4. Diagnóstico e Monitoramento de Performance

Aprender a identificar problemas silenciosos evita desperdício de dinheiro e tempo em cloud.

### 4.1 Comandos de Monitoramento

| Comando | Finalidade | Exemplo |
|---------|------------|---------|
| `top` / `htop` | Processos e CPU em tempo real | `htop` |
| `nvidia-smi` | Status das GPUs NVIDIA | `watch -n 1 nvidia-smi` |
| `free -h` | Uso de memória RAM | `free -h` |
| `df -h` | Espaço em disco | `df -h` |
| `du -sh *` | Tamanho de diretórios | `du -sh /data/*` |
| `iotop` | I/O de disco por processo | `sudo iotop` |
| `nethogs` | Uso de rede por processo | `sudo nethogs` |
| `dmesg` | Logs do kernel | `dmesg | tail -50` |
| `journalctl` | Logs do sistema | `journalctl -f` |

### 4.2 Gargalos Comuns em ML

| Problema | Sintoma | Diagnóstico | Solução |
|----------|---------|-------------|---------|
| **I/O Wait** | CPU/GPU ociosas | `%wa` alto no `top` | SSDs, otimizar DataLoader |
| **Thrashing (Swap)** | Lentidão extrema | `free -h` mostra swap alto | Reduzir batch size, mais RAM |
| **OOM Killer** | Processo morto | `dmesg \| grep -i oom` | Limitar memória, usar gradient checkpointing |
| **GPU Underutilization** | GPU < 90% | `nvidia-smi` | Aumentar batch size, prefetch |

### 4.3 Processos Zombie

São processos que terminaram mas ainda ocupam espaço na tabela de processos.

```bash
# Encontrar processos zombie
ps aux | grep 'Z'

# Matar processo pai (libera os zombies)
kill -9 <PPID>
```

### 4.4 OOM Killer (Out of Memory Killer)

Quando a RAM acaba totalmente, o Kernel escolhe um processo para "matar".

```bash
# Verificar se houve OOM
dmesg | grep -i "out of memory"
dmesg | grep -i "killed process"

# Ver quem foi morto
journalctl -k | grep -i oom
```

---

## 5. Boas Práticas para MLOps

### 5.1 Segurança

-  Use **autenticação por chave SSH** (nunca senha)
-  **Desabilite login root** via SSH
-  Mantenha o sistema **sempre atualizado**
-  Configure **firewall** (`ufw`, `iptables`)
-  Use **chaves 4096-bit RSA** ou **Ed25519**
-  Implemente **2FA** quando possível

### 5.2 Automação

-  Scripts devem ser **idempotentes** (podem rodar várias vezes sem erro)
-  Use **variáveis de ambiente** para configuração
-  Nomes de arquivos **sem espaços** e caracteres especiais
-  Versionamento com **Git** para tudo

### 5.3 Monitoramento

-  Sempre use **tmux/screen** para treinos longos
-  Configure **alertas** para uso de recursos
-  Mantenha **logs estruturados** para debugging

---

## 6. Referências e Recursos

### Documentação Oficial
- [GNU Bash Manual](https://www.gnu.org/software/bash/manual/)
- [OpenSSH Documentation](https://www.openssh.com/manual.html)
- [Linux man pages](https://man7.org/linux/man-pages/)

### Ferramentas Úteis
- [tmux cheatsheet](https://tmuxcheatsheet.com/)
- [explainshell.com](https://explainshell.com/) - Explica comandos Bash
- [ShellCheck](https://www.shellcheck.net/) - Linter para scripts Bash

### Livros Recomendados
- *The Linux Command Line* - William Shotts
- *SSH Mastery* - Michael W. Lucas
- *Bash Pocket Reference* - Arnold Robbins