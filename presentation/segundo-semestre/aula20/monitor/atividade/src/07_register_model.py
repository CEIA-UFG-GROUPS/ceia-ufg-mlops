"""
07_register_model.py

Passo 7: Registra o candidato em um registry JSON local com aliases
`challenger` / `champion` (espelha semanticamente a Aula 19 — Model Registry).
Executado apenas no caminho feliz de push em `main` (ou MODE=main local).
"""

from __future__ import annotations

import hashlib
import shutil
import sys
from datetime import datetime, timezone

from src.utils import MODEL_DIR, REGISTRY_DIR, REPORT_DIR, ensure_dirs, load_json, save_json

MODEL_NAME = "fraude_credito"


def sha256_file(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_registry() -> dict:
    path = REGISTRY_DIR / "models.json"
    if path.exists():
        return load_json(path)
    return {"models": {}}


def main() -> None:
    ensure_dirs()
    print("🚀 [Passo 7] Registrando candidato no registry local (aliases Aula 19)...")

    artifact = MODEL_DIR / "candidate.joblib"
    metrics_path = REPORT_DIR / "metrics.json"
    gate_path = REPORT_DIR / "gate_result.json"
    security_path = REPORT_DIR / "security_report.json"

    for required in (artifact, metrics_path, gate_path):
        if not required.exists():
            print(f"❌ Arquivo obrigatório ausente: {required}")
            sys.exit(1)

    gate = load_json(gate_path)
    if not gate.get("passed"):
        print("❌ Recusando registro: quality gate não passou.")
        sys.exit(1)

    metrics = load_json(metrics_path)
    security = load_json(security_path) if security_path.exists() else {}
    digest = security.get("sha256") or sha256_file(artifact)

    registry = load_registry()
    model_entry = registry["models"].setdefault(
        MODEL_NAME,
        {"versions": [], "aliases": {}},
    )
    next_version = 1 + max((int(v["version"]) for v in model_entry["versions"]), default=0)

    versioned_name = f"{MODEL_NAME}_v{next_version}.joblib"
    dest = MODEL_DIR / versioned_name
    shutil.copy2(artifact, dest)

    record = {
        "version": next_version,
        "artifact": versioned_name,
        "sha256": digest,
        "metrics": {
            k: metrics[k]
            for k in ("accuracy", "precision", "recall", "f1", "roc_auc")
            if k in metrics
        },
        "created_at": datetime.now(timezone.utc).isoformat(),
        "signing": security.get("signing", {}),
    }
    model_entry["versions"].append(record)

    # Semântica: novo aprovado vira @challenger; se não há @champion, promove também
    model_entry["aliases"]["challenger"] = next_version
    if "champion" not in model_entry["aliases"]:
        model_entry["aliases"]["champion"] = next_version
        print(f"🏆 Primeiro modelo: aliases @champion e @challenger → v{next_version}")
    else:
        print(f"🥊 Registrado como @challenger → v{next_version} (promova @champion na Aula 19/22)")

    save_json(REGISTRY_DIR / "models.json", registry)
    print(f"✅ Registry atualizado: {REGISTRY_DIR / 'models.json'}")
    print(f"✅ Artefato versionado: {dest}")
    print(f"🔑 SHA-256: {digest}")


if __name__ == "__main__":
    main()
