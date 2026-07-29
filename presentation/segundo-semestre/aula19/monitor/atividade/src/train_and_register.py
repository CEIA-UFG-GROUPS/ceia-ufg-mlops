"""
Script 1: Treina modelos v1 (baseline) e v2 (melhorado), loga hiperparâmetros/métricas no MLflow
e faz o registro formal das duas versões no Model Registry com o nome 'ModeloClassificacao'.
"""

import sys
import os
import urllib.request
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

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


def log_sklearn_model(model, model_name, registered_name):
    """Auxiliar para logar modelo com compatibilidade entre versões do MLflow."""
    try:
        return mlflow.sklearn.log_model(
            sk_model=model,
            name=model_name,
            registered_model_name=registered_name
        )
    except TypeError:
        return mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path=model_name,
            registered_model_name=registered_name
        )


def main():
    # 1. Configurar URI do MLflow (prioriza http://localhost:5000 se o Docker/Servidor estiver rodando)
    tracking_uri = get_tracking_uri()
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("aula19_model_registry")

    print(f"🔗 Conectado ao MLflow Tracking em: {tracking_uri}")

    # 2. Carregar Dataset (Iris)
    X, y = load_iris(return_X_y=True, as_frame=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    # ==========================================
    # EXPERIMENTO 1: Modelo v1 (Baseline - Tree)
    # ==========================================
    print("\n🚀 Treinando Modelo v1 (Baseline - DecisionTree)...")
    with mlflow.start_run(run_name="v1_baseline_decision_tree") as run_v1:
        model_v1 = DecisionTreeClassifier(max_depth=2, random_state=42)
        model_v1.fit(X_train, y_train)

        preds_v1 = model_v1.predict(X_test)
        acc_v1 = accuracy_score(y_test, preds_v1)
        f1_v1 = f1_score(y_test, preds_v1, average="macro")

        mlflow.log_param("model_type", "DecisionTreeClassifier")
        mlflow.log_param("max_depth", 2)
        mlflow.log_metric("accuracy", acc_v1)
        mlflow.log_metric("f1_score", f1_v1)

        # Log e Registro no Model Registry
        model_info_v1 = log_sklearn_model(model_v1, "model", "ModeloClassificacao")
        print(f"✅ Versão v1 registrada! Run ID: {run_v1.info.run_id} | Acc: {acc_v1:.4f} | F1: {f1_v1:.4f}")

    # ==========================================
    # EXPERIMENTO 2: Modelo v2 (Avançado - Forest)
    # ==========================================
    print("\n🚀 Treinando Modelo v2 (Avançado - RandomForest)...")
    with mlflow.start_run(run_name="v2_advanced_random_forest") as run_v2:
        model_v2 = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
        model_v2.fit(X_train, y_train)

        preds_v2 = model_v2.predict(X_test)
        acc_v2 = accuracy_score(y_test, preds_v2)
        f1_v2 = f1_score(y_test, preds_v2, average="macro")

        mlflow.log_param("model_type", "RandomForestClassifier")
        mlflow.log_param("n_estimators", 100)
        mlflow.log_param("max_depth", 5)
        mlflow.log_metric("accuracy", acc_v2)
        mlflow.log_metric("f1_score", f1_v2)

        # Log e Registro no Model Registry
        model_info_v2 = log_sklearn_model(model_v2, "model", "ModeloClassificacao")
        print(f"✅ Versão v2 registrada! Run ID: {run_v2.info.run_id} | Acc: {acc_v2:.4f} | F1: {f1_v2:.4f}")

    # 3. Atribuir o Alias inicial '@challenger' para a versão 1
    client = mlflow.MlflowClient()
    client.set_registered_model_alias(
        name="ModeloClassificacao",
        alias="challenger",
        version="1"
    )
    print("\n🏷️ Alias '@challenger' atribuído à versão 1 do 'ModeloClassificacao'.")


if __name__ == "__main__":
    main()
