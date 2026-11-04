# Código — Semana 00 (Onboarding)

Ferramentas de verificação do ambiente. Não há aplicação nesta semana: o
"código" do lab é justamente o que prova que a sua máquina está pronta para as
11 semanas seguintes.

```
codigo/
├── verificar-ambiente.ps1   # verificador para Windows / PowerShell
├── verificar-ambiente.sh    # verificador para Linux, WSL e macOS
└── hello_world.py           # hello world mínimo (só stdlib)
```

Os dois verificadores são **somente leitura**: eles não instalam nada, não
alteram configuração e não escrevem arquivo nenhum. Para cada item imprimem
✅ (ok), ❌ (falta algo obrigatório) ou ⚠️ (aviso não bloqueante), com a dica
de como resolver.

---

## Rodar no Windows (PowerShell)

A partir desta pasta (`semana-00/codigo/`):

```powershell
.\verificar-ambiente.ps1
```

Se o PowerShell recusar por política de execução, libere **só para esta sessão**:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\verificar-ambiente.ps1
```

Opções:

| Opção | Para que serve |
| --- | --- |
| `-HostLab usuario@servidor` | Também testa o SSH na máquina 4090 do laboratório |
| `-PularRede` | Pula tudo que depende de rede (GitHub e lab) |

---

## Rodar no Linux, WSL ou macOS

```bash
chmod +x verificar-ambiente.sh      # só na primeira vez
./verificar-ambiente.sh
```

Opções: `--host-lab usuario@servidor`, `--pular-rede`, `--help`.

> Rodou o `.ps1` no Windows e o `.sh` dentro do WSL? **Ótimo** — são ambientes
> diferentes, com PATH, Python e chaves SSH próprios. Para o lab, o que vale é
> o ambiente onde você vai trabalhar.

---

## O que é checado

| Item | Como é verificado | Obrigatório |
| --- | --- | --- |
| `git` | `git --version` | sim |
| Identidade do Git | `git config --global user.name` / `user.email` | sim |
| Chave SSH | existe algum `~/.ssh/*.pub` | sim |
| GitHub por SSH | `ssh -T git@github.com` responde *successfully authenticated* | sim |
| `python` + `pip` + `venv` | `--version` e `-m venv --help` | sim |
| `docker` | `docker --version` e `docker info` (daemon de pé) | sim |
| `docker compose` | `docker compose version` | aviso |
| WSL2 | `wsl -e uname -sr` responde Linux (ou você já está dentro do WSL) | sim no Windows |
| `gcloud` | `gcloud --version`, conta e projeto ativos | aviso (vira obrigatório na Semana 06) |
| Máquina 4090 | `ssh <host> nvidia-smi` | só com `-HostLab` / `--host-lab` |

Código de saída: **0** se tudo passou, **1** se algum item obrigatório falhou —
o que também serve para usar o script dentro de um CI mais pra frente.

---

## Hello world

```bash
python hello_world.py          # Linux / WSL / macOS: python3 hello_world.py
```

Saída esperada (os valores mudam conforme a máquina):

```text
✅ Hello, MLOps! O ambiente Python está funcionando.

Python     : 3.12.3 (/usr/bin/python3)
Sistema    : Linux 6.6.87.2-microsoft-standard-WSL2 (x86_64)
GPU        : nenhuma GPU NVIDIA detectada (nvidia-smi não encontrado)
```

Na máquina 4090 do laboratório, a linha `GPU` deve trazer o modelo da placa e a
versão do driver — é essa saída que vai como evidência no desafio.

---

## Deu ❌ em algo?

A dica logo abaixo do item é o primeiro caminho. Os erros mais comuns (BIOS sem
virtualização, Docker sem backend WSL, `Permission denied (publickey)`) estão
resolvidos passo a passo na seção **Troubleshooting** do
[`README.md`](../README.md) da semana.
