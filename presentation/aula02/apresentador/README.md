# Sistemas Operacionais, Bash, SSH e Acesso Remoto

**Guia do Apresentador**

Este documento organiza a progressão da aula. O objetivo é levar o aluno do entendimento do hardware e SO até a capacidade de gerenciar servidores remotos para MLOps.

---

## 1. Motivação (~5 min)

### 1.1 O SO como alicerce de MLOps

- O Sistema Operacional gerencia os recursos críticos: **CPU**, **RAM** e **GPU**.
- Falhas em modelos muitas vezes não são do código Python, mas de gestão de recursos do SO (falta de memória, permissões ou disco).
- **Pergunta para a turma:** Alguém já teve um treino de ML que travou ou foi morto sem explicação?

### 1.2 Por que Linux e Bash?

- **Domínio de mercado:** A infraestrutura de nuvem (AWS, GCP, Azure) é majoritariamente Linux.
- **Automação:** O terminal permite criar fluxos que interfaces gráficas não alcançam.
- **Contexto MLOps:** Servidores com GPUs, pipelines de dados, containers — tudo roda em Linux.

---

## 2. Arquitetura do SO e Gestão de Recursos (~15 min)

### 2.1 Kernel vs. Shell

- **Explicar a diferença:** Kernel = núcleo (hardware), Shell = interface (usuário).
- **Demonstrar:** Mostrar que `bash` é um processo como qualquer outro com `ps aux | grep bash`.

### 2.2 Gerenciamento de Processos

**Conceitos a cobrir:**
- Foreground vs. Background (`&`, `nohup`)
- Sinais: `SIGTERM` (15), `SIGKILL` (9), `SIGINT` (Ctrl+C)

**Demonstração prática:**
```bash
# Rodar algo em background
sleep 100 &

# Listar e matar
ps aux | grep sleep
kill -9 <PID>
```

### 2.3 Memória Virtual e Swap

- Explicar o conceito de **Swap** e seu impacto em ML.
- **Ponto crítico:** Disco é 1000x mais lento que RAM — treino em swap é desastroso.

**Demonstração:**
```bash
free -h
```

### 2.4 Permissões (rwx)

- Explicar a lógica binária: `r=4`, `w=2`, `x=1`.
- **Exemplo prático:** `chmod 755` vs `chmod 644`.

**Demonstração:**
```bash
ls -la
chmod 755 script.sh
chown usuario:grupo arquivo.txt
```

---

## 3. Comandos Bash Essenciais (~20 min)

### 3.1 Navegação e Manipulação

**Comandos para demonstrar:**
- `pwd`, `ls -lah`, `cd`, `mkdir -p`
- `cp -r`, `mv`, `rm -rf` (⚠️ cuidado!)
- `find . -name "*.py"`

### 3.2 Visualização e Edição

**Comandos para demonstrar:**
- `cat`, `head -n 20`, `tail -f` (logs em tempo real!)
- `grep -r "pattern" .`
- `wc -l` (contar linhas)

### 3.3 Variáveis de Ambiente e PATH

**Ponto importante:** Explicar por que "command not found" acontece.

**Demonstração:**
```bash
echo $PATH
export MINHA_VAR="valor"
echo $MINHA_VAR
```

**Variáveis úteis para ML:**
- `PYTHONPATH`
- `CUDA_VISIBLE_DEVICES`

### 3.4 Streams: stdin, stdout, stderr

**Conceito-chave:** Todo comando tem 3 canais (0, 1, 2).

**Demonstração:**
```bash
# Separar saída normal de erros
python script.py 1> resultado.log 2> erros.log

# Pipes
cat arquivo.txt | grep "pattern" | wc -l
```

### 3.5 Automação com Loops

**Demonstração prática:**
```bash
for f in *.jpg; do
    echo "Processando $f"
done
```

### 3.6 Cron (Agendamento)

- Explicar o formato: `minuto hora dia_mes mês dia_semana`.
- **Exemplo:** Backup diário às 2h → `0 2 * * * /home/user/backup.sh`.

---

## 4. SSH e Acesso Remoto (~20 min)

### 4.1 Conceitos Fundamentais

- **Criptografia assimétrica:** Chave pública vs. privada.
- **Por que não usar senha:** Segurança e automação.

### 4.2 Geração de Chaves

**Demonstração:**
```bash
ssh-keygen -t ed25519 -C "email@exemplo.com"
ssh-copy-id usuario@servidor
```

### 4.3 Configuração Avançada (~/.ssh/config)

**Mostrar exemplo de config:**
```bash
Host gpu-server
    HostName 192.168.1.100
    User mlops
    IdentityFile ~/.ssh/id_rsa
```

**Benefício:** `ssh gpu-server` em vez de `ssh mlops@192.168.1.100 -i ~/.ssh/id_rsa`.

### 4.4 Tunelamento SSH (Port Forwarding)

**Caso de uso principal:** Acessar Jupyter/TensorBoard remoto.

**Demonstração:**
```bash
# Jupyter remoto na porta local
ssh -L 8888:localhost:8888 usuario@servidor
```

**Explicar os 3 tipos:**
- Local Forwarding (`-L`)
- Remote Forwarding (`-R`)
- Dynamic/SOCKS (`-D`)

### 4.5 Transferência de Arquivos

**Comparar ferramentas:**
- `scp` → Simples, cópia direta
- `rsync` → Eficiente (só diferenças), retoma interrupções

**Demonstração:**
```bash
scp modelo.pkl usuario@servidor:/destino/
rsync -avz --progress ./dados/ servidor:/data/
```

### 4.6 Persistência: Tmux/Screen

**Ponto crítico:** Se a internet cair, o processo SSH morre!

**Demonstração tmux:**
```bash
tmux new -s treino
# Ctrl+B, D para desanexar
tmux attach -t treino
```

---

## 5. Diagnóstico e Troubleshooting (~10 min)

### 5.1 Comandos de Monitoramento

**Demonstrar:**
- `htop` ou `top`
- `nvidia-smi` (se GPU disponível)
- `free -h`, `df -h`
- `watch -n 1 nvidia-smi`

### 5.2 Gargalos Comuns em ML

**Explicar cada um:**
| Problema | Diagnóstico | Solução |
|----------|-------------|---------|
| **I/O Wait** | `%wa` alto no `top` | SSDs, otimizar DataLoader |
| **Swap/Thrashing** | `free -h` | Reduzir batch size |
| **OOM Killer** | `dmesg \| grep oom` | Limitar memória |

### 5.3 Logs do Sistema

**Demonstração:**
```bash
dmesg | tail -50
journalctl -f
```

---

## 6. Boas Práticas (~5 min)

### 6.1 Segurança

- Autenticação por chave SSH (nunca senha)
- Desabilitar login root via SSH
- Usar chaves Ed25519 ou RSA 4096-bit

### 6.2 Automação

- Scripts idempotentes
- Variáveis de ambiente para configuração
- Git para versionamento

### 6.3 Monitoramento

- Sempre usar tmux/screen para treinos longos
- Logs estruturados

---

## 7. Exercícios Sugeridos

1. **Criar par de chaves SSH** e conectar a uma VM local (ou WSL).
2. **Configurar `~/.ssh/config`** com pelo menos um host.
3. **Criar túnel SSH** para acessar um serviço remoto.
4. **Escrever um script Bash** que processa múltiplos arquivos com loop.
5. **Monitorar recursos** durante um processo intensivo usando `htop` e `watch`.

---

## Recursos para Compartilhar com a Turma

- [explainshell.com](https://explainshell.com/) — Explica comandos Bash
- [tmuxcheatsheet.com](https://tmuxcheatsheet.com/) — Atalhos do Tmux
- [ShellCheck](https://www.shellcheck.net/) — Linter para scripts Bash