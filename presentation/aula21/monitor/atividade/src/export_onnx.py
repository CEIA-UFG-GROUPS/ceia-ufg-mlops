"""Exporta o modelo para ONNX e gera uma versão quantizada em INT8.

Este script materializa a etapa de **aceleração de inferência** da aula:

1. **Exportação para ONNX** — converte o modelo PyTorch (Hugging Face)
   para um grafo estático no formato ONNX. O grafo pode então ser
   executado pelo ONNX Runtime, que aplica otimizações (fusão de
   operadores, eliminação de nós) e roda em CPU/GPU sem depender do
   PyTorch em produção.

2. **Quantização dinâmica INT8** — os pesos são armazenados em INT8
   (1 byte em vez de 4 do FP32) e as ativações são quantizadas em tempo
   de execução. Reduz o tamanho do modelo em ~4x e acelera a inferência
   em CPU, com perda de qualidade geralmente pequena (mas que DEVE ser
   validada no seu conjunto de avaliação!).

Estrutura de saída::

    <output-dir>/
    ├── onnx/          # modelo FP32 exportado + tokenizer
    │   └── model.onnx
    └── onnx-int8/     # modelo quantizado + tokenizer
        └── model.onnx

Uso::

    python -m src.export_onnx --output-dir models
    python -m src.export_onnx --output-dir models --model-id <outro-modelo-hf>
"""

from __future__ import annotations

import argparse
from pathlib import Path

from onnxruntime.quantization import QuantType, quantize_dynamic
from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer

# Modelo de análise de sentimento (~67M parâmetros): pequeno o bastante
# para baixar rápido, grande o bastante para os efeitos de batching e
# quantização aparecerem nas medições.
DEFAULT_MODEL_ID = "distilbert-base-uncased-finetuned-sst-2-english"


def export_and_quantize(model_id: str, output_dir: Path) -> tuple[Path, Path]:
    """Exporta ``model_id`` para ONNX FP32 e gera a variante INT8."""
    fp32_dir = output_dir / "onnx"
    int8_dir = output_dir / "onnx-int8"
    fp32_dir.mkdir(parents=True, exist_ok=True)
    int8_dir.mkdir(parents=True, exist_ok=True)

    print(f"[1/3] Exportando '{model_id}' para ONNX (FP32)...")
    # export=True dispara a conversão PyTorch -> ONNX via optimum.
    model = ORTModelForSequenceClassification.from_pretrained(model_id, export=True)
    model.save_pretrained(fp32_dir)

    # O tokenizer é salvo junto de cada variante para que o serviço de
    # inferência seja auto-contido (não precisa baixar nada em runtime).
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    tokenizer.save_pretrained(fp32_dir)
    tokenizer.save_pretrained(int8_dir)

    print("[2/3] Quantizando pesos para INT8 (quantização dinâmica)...")
    quantize_dynamic(
        model_input=fp32_dir / "model.onnx",
        model_output=int8_dir / "model.onnx",
        weight_type=QuantType.QInt8,
    )

    # O config.json carrega o mapeamento id2label usado pelo serviço.
    config_src = fp32_dir / "config.json"
    if config_src.exists():
        (int8_dir / "config.json").write_bytes(config_src.read_bytes())

    print("[3/3] Comparando tamanhos em disco:")
    for label, path in [("FP32", fp32_dir / "model.onnx"), ("INT8", int8_dir / "model.onnx")]:
        size_mb = path.stat().st_size / 1024**2
        print(f"       {label}: {size_mb:8.1f} MB  ({path})")

    return fp32_dir, int8_dir


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--model-id", default=DEFAULT_MODEL_ID, help="Modelo no Hugging Face Hub")
    parser.add_argument("--output-dir", default="models", type=Path, help="Diretório de saída")
    args = parser.parse_args()

    export_and_quantize(args.model_id, args.output_dir)
    print("\nPronto! Sirva com: bentoml serve src.service:SentimentService")


if __name__ == "__main__":
    main()
