#!/usr/bin/env python3
"""Hello world da Semana 00 — prova de que o Python está vivo.

Imprime a versão do Python, o sistema operacional e se existe uma GPU NVIDIA
visível. Só usa a biblioteca padrão: nada para instalar, roda igual no Windows,
no WSL, no macOS e na máquina 4090 do laboratório.

Uso:
    python hello_world.py
"""

from __future__ import annotations

import platform
import shutil
import subprocess
import sys

# O console do Windows nem sempre aceita emoji; não deixamos isso virar crash.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except (AttributeError, ValueError):  # pragma: no cover - ambientes exóticos
    pass


def detectar_gpu() -> str:
    """Devolve o nome da GPU NVIDIA, ou uma mensagem explicando por que não achou."""
    nvidia_smi = shutil.which("nvidia-smi")
    if nvidia_smi is None:
        return "nenhuma GPU NVIDIA detectada (nvidia-smi não encontrado)"

    try:
        resultado = subprocess.run(
            [nvidia_smi, "--query-gpu=name,driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as erro:
        return f"nvidia-smi encontrado, mas falhou ao executar ({erro})"

    if resultado.returncode != 0:
        detalhe = (resultado.stderr or resultado.stdout).strip().splitlines()
        motivo = detalhe[0] if detalhe else f"exit code {resultado.returncode}"
        return f"nvidia-smi falhou: {motivo}"

    linhas = [linha.strip() for linha in resultado.stdout.splitlines() if linha.strip()]
    if not linhas:
        return "nvidia-smi respondeu, mas nenhuma GPU foi listada"
    return " | ".join(linhas)


def main() -> int:
    print("✅ Hello, MLOps! O ambiente Python está funcionando.")
    print()
    print(f"Python     : {platform.python_version()} ({sys.executable})")
    print(f"Sistema    : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"GPU        : {detectar_gpu()}")
    print()
    print("Se você está lendo isso sem nenhum traceback acima, o passo 1 do")
    print("desafio da Semana 00 está cumprido. Cole esta saída no README do")
    print("seu repositório pessoal.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
