"""
Script 2: Simula o Quality Gate automatizado (CI/CD).
Busca as versões registradas do 'ModeloClassificacao', compara as métricas de validação
e promove programaticamente a versão mais recente com maior F1-score ao alias '@champion'.
"""

import sys
import os
import urllib.request
import mlflow

# Prevenir UnicodeEncodeError em terminais Windows (cp1252)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


def get_tracking_uri():
    """Detecta automaticamente se o servidor MLflow está rodando na porta 5000 ou usa SQLite local."""
    if "MLFLOW_TRACKING_URI" in os.environ:
        return os.environ["MLFLOW_TRACKING_URI"]
    try:
        urllib.request.urlopen("http://localhost:5000/", timeout=1)
        return "http://localhost:5000"
    except Exception:
        return "sqlite:///mlflow.db"


def main():
    # 1. Configurar URI do MLflow
    tracking_uri = get_tracking_uri()
    mlflow.set_tracking_uri(tracking_uri)
    client = mlflow.MlflowClient()

    model_name = "ModeloClassificacao"
    print(f"🔎 Avaliando versões do modelo '{model_name}' em: {tracking_uri}...")

    # 2. Obter informações de todas as versões registradas
    try:
        versions = client.search_model_versions(f"name='{model_name}'")
    except Exception as e:
        print(f"❌ Erro ao buscar versões no Registry: {e}")
        return

    if not versions:
        print(f"❌ Nenhuma versão encontrada para '{model_name}'. Execute antes 'train_and_register.py'.")
        return

    best_version = None
    best_f1 = -1.0

    print("\n📊 Métricas das versões encontradas:")
    print("-" * 55)
    print(f"{'Versão':<10} | {'Run ID':<32} | {'F1-Score':<10}")
    print("-" * 55)

    # Ordenar por número da versão crescente para garantir que em caso de empate a mais recente vença
    sorted_versions = sorted(versions, key=lambda x: int(x.version))

    for mv in sorted_versions:
        run_data = client.get_run(mv.run_id)
        f1 = run_data.data.metrics.get("f1_score", 0.0)
        print(f"{mv.version:<10} | {mv.run_id:<32} | {f1:<10.4f}")

        # f1 >= best_f1 garante que a versão mais recente com maior ou igual F1 seja escolhida
        if f1 >= best_f1:
            best_f1 = f1
            best_version = mv.version

    print("-" * 55)
    print(f"\n🏆 Versão Vencedora no Quality Gate: Versão {best_version} (F1: {best_f1:.4f})")

    # 3. Atualizar Aliases no Registry
    client.set_registered_model_alias(
        name=model_name,
        alias="champion",
        version=str(best_version)
    )

    for mv in versions:
        if str(mv.version) != str(best_version):
            client.set_registered_model_alias(
                name=model_name,
                alias="previous",
                version=str(mv.version)
            )

    print(f"\n✅ PROMOÇÃO CONCLUÍDA:")
    print(f"   • Versão {best_version} -> Alias '@champion' (Ativo para inferência em Produção)")
    print(f"   • Demais versões -> Alias '@previous'")


if __name__ == "__main__":
    main()
