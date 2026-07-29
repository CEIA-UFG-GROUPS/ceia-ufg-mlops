"""
Script 4: Cliente de teste para interagir com o serviço de inferência FastAPI.
Dispara requisições de predição e consulta as informações da versão do modelo em execução.
"""

import sys
import time
import httpx

# Prevenir UnicodeEncodeError em terminais Windows (cp1252)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

BASE_URL = "http://localhost:8000"


def main():
    print(f"📡 Conectando ao serviço de inferência em {BASE_URL}...")

    # 1. Consultar informações do modelo ativo (tenta recarregar se der 503)
    try:
        resp_info = httpx.get(f"{BASE_URL}/model-info", timeout=5.0)
        if resp_info.status_code == 503:
            print("🔄 Modelo não estava carregado na memória. Disparando /reload no Registry...")
            httpx.post(f"{BASE_URL}/reload", timeout=5.0)
            resp_info = httpx.get(f"{BASE_URL}/model-info", timeout=5.0)

        if resp_info.status_code == 200:
            info = resp_info.json()
            print("\nℹ️ INFORMAÇÕES DO MODELO ATIVO NO REGISTRY:")
            print(f"   • Modelo: {info.get('model_name')}")
            print(f"   • Alias: @{info.get('alias')}")
            print(f"   • Versão do Registro: v{info.get('version')}")
            print(f"   • Tipo de Algoritmo: {info.get('model_type')}")
            print(f"   • F1-Score de Validação: {info.get('f1_score'):.4f}")
        else:
            print(f"⚠️ Não foi possível obter informações do modelo. Status: {resp_info.status_code}")
            print(f"   Mensagem: {resp_info.text}")
            print("💡 Certifique-se de executar 'python -m src.evaluate_and_promote' antes de testar!")
            return
    except Exception as e:
        print(f"❌ Falha ao conectar com o serviço: {e}")
        print("💡 Certifique-se de que o servidor 'service.py' (ou o container model-api) está rodando na porta 8000.")
        return

    # 2. Testar requisições de inferência
    test_samples = [
        {"features": [5.1, 3.5, 1.4, 0.2], "label_esperado": "setosa"},
        {"features": [6.0, 2.9, 4.5, 1.5], "label_esperado": "versicolor"},
        {"features": [6.9, 3.1, 5.4, 2.1], "label_esperado": "virginica"}
    ]

    print("\n🔮 TESTANDO INFERÊNCIAS:")
    print("-" * 65)

    for i, sample in enumerate(test_samples, 1):
        payload = {"features": sample["features"]}
        start_time = time.time()
        res = httpx.post(f"{BASE_URL}/predict", json=payload, timeout=5.0)
        elapsed_ms = (time.time() - start_time) * 1000

        if res.status_code == 200:
            data = res.json()
            classe = data["prediction_class_name"]
            versao = data["model_metadata"]["version"]
            algo = data["model_metadata"]["model_type"]
            print(f"Amostra #{i}: Entrada={sample['features']} -> Predição='{classe}' (Esperado='{sample['label_esperado']}')")
            print(f"   ↳ Modelo Responsável: v{versao} ({algo}) | Latência: {elapsed_ms:.2f} ms\n")
        else:
            print(f"Amostra #{i}: Erro na inferência. Status: {res.status_code}")
            print(f"   Detalhes: {res.text}")

    print("-" * 65)
    print("✨ Teste concluído com sucesso!")


if __name__ == "__main__":
    main()
