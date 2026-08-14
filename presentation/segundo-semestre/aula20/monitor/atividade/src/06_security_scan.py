"""
06_security_scan.py

Passo 6: Supply-chain básico do artefato do modelo.
- Prefere joblib (não pickle solto de fontes não confiáveis).
- Calcula SHA-256 do artefato.
- Tenta assinar com `model-signing` se instalado; degrada com aviso se ausente.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from datetime import datetime, timezone

from src.utils import MODEL_DIR, REPORT_DIR, ensure_dirs, save_json


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def try_model_signing(artifact_path) -> dict:
    """Assinatura opcional via OpenSSF model-signing (se instalado)."""
    # Pacote PyPI `model-signing` — API pode variar; tentamos via sys.executable.
    try:
        import importlib.util

        if importlib.util.find_spec("model_signing") is None:
            return {
                "attempted": True,
                "signed": False,
                "reason": "pacote model-signing não instalado (opcional)",
            }
    except Exception as exc:  # noqa: BLE001
        return {"attempted": True, "signed": False, "reason": str(exc)}

    sig_path = REPORT_DIR / "candidate.sig"
    # Tentativa best-effort: algumas versões expõem `python -m model_signing`
    cmd = [
        sys.executable,
        "-m",
        "model_signing",
        "sign",
        str(artifact_path),
        "--signature",
        str(sig_path),
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=60)
        if proc.returncode == 0 and sig_path.exists():
            return {
                "attempted": True,
                "signed": True,
                "signature_path": str(sig_path),
                "stdout": proc.stdout[-500:],
            }
        return {
            "attempted": True,
            "signed": False,
            "reason": "CLI model_signing não concluiu (degradação graciosa)",
            "stderr": (proc.stderr or proc.stdout)[-500:],
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "attempted": True,
            "signed": False,
            "reason": f"exceção ao assinar (ignorada): {exc}",
        }


def main() -> None:
    ensure_dirs()
    print("🚀 [Passo 6] Security / supply-chain do artefato...")

    artifact = MODEL_DIR / "candidate.joblib"
    if not artifact.exists():
        print("❌ Artefato ausente. Execute: python -m src.03_train_model")
        sys.exit(1)

    digest = sha256_file(artifact)
    signing = try_model_signing(artifact)

    payload = {
        "artifact": str(artifact.name),
        "format": "joblib",
        "note": (
            "Preferimos joblib/safetensors a pickle arbitrário de fontes não confiáveis. "
            "Ver Hugging Face Hub security-pickle e OpenSSF Model Signing."
        ),
        "sha256": digest,
        "bytes": artifact.stat().st_size,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "signing": signing,
    }
    out = REPORT_DIR / "security_report.json"
    save_json(out, payload)

    print(f"✅ SHA-256: {digest}")
    print(f"✅ Relatório: {out}")
    if signing.get("signed"):
        print("✅ Assinatura model-signing gerada.")
    else:
        print(
            f"ℹ️  Assinatura opcional não aplicada: {signing.get('reason', 'n/d')} "
            "(pipeline continua — degradação graciosa)."
        )
    print("👉 Próximo (só em main / MODE=main): python -m src.07_register_model")


if __name__ == "__main__":
    main()
