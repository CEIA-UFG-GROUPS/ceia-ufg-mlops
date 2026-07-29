"""
Script 3: Servidor de Inferência FastAPI desacoplado.
Carrega a versão ativa do modelo diretamente do MLflow Model Registry através da URI
dinâmica 'models:/ModeloClassificacao@champion', sem caminhos locais fixos!
"""

import sys
import os
import urllib.request
import mlflow
import mlflow.pyfunc
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

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


TRACKING_URI = get_tracking_uri()
MODEL_NAME = "ModeloClassificacao"
MODEL_ALIAS = "champion"
MODEL_URI = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"

# Variáveis globais para armazenar o modelo carregado e metadados
loaded_model = None
model_version_info = {}


def reload_model_from_registry():
    """Carrega ou recarrega a versão ativa do modelo a partir do Model Registry."""
    global loaded_model, model_version_info, TRACKING_URI
    TRACKING_URI = get_tracking_uri()
    mlflow.set_tracking_uri(TRACKING_URI)
    client = mlflow.MlflowClient()

    try:
        # Obter detalhes da versão apontada pelo alias @champion
        mv = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
        run_data = client.get_run(mv.run_id)

        # Carregar modelo usando a URI do Registry
        loaded_model = mlflow.pyfunc.load_model(MODEL_URI)

        model_version_info = {
            "model_name": MODEL_NAME,
            "alias": MODEL_ALIAS,
            "version": mv.version,
            "run_id": mv.run_id,
            "model_type": run_data.data.params.get("model_type", "Desconhecido"),
            "f1_score": run_data.data.metrics.get("f1_score", 0.0),
            "model_uri": MODEL_URI,
            "tracking_uri": TRACKING_URI
        }
        print(f"✅ Modelo carregado com sucesso! Versão: {mv.version} | Algoritmo: {model_version_info['model_type']} | Tracking: {TRACKING_URI}")
        return True
    except Exception as e:
        print(f"⚠️ Erro ao carregar modelo do Registry ({MODEL_URI}): {e}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Executar recarregamento na inicialização
    reload_model_from_registry()
    yield


# Inicializar aplicação FastAPI com contexto de lifespan
app = FastAPI(
    title="Serviço de Inferência com Model Registry (MLOps)",
    description="Serviço REST que carrega dinamicamente a versão @champion do MLflow Registry",
    version="1.0.0",
    lifespan=lifespan
)


class InferenceInput(BaseModel):
    features: list[float] = Field(
        ...,
        json_schema_extra={"example": [5.1, 3.5, 1.4, 0.2]},
        description="Lista com 4 atributos numéricos [sepal length, sepal width, petal length, petal width]"
    )


CLASSES_MAP = {0: "setosa", 1: "versicolor", 2: "virginica"}


@app.get("/")
def read_root():
    if loaded_model is None:
        reload_model_from_registry()
    return {
        "status": "online",
        "service": "Model Registry FastAPI Service",
        "active_model_uri": MODEL_URI,
        "loaded_version": model_version_info.get("version", "Nenhuma"),
        "tracking_uri": TRACKING_URI
    }


@app.get("/model-info")
def get_model_info():
    """Retorna detalhes sobre a versão do modelo atualmente carregada na memória."""
    if loaded_model is None or not model_version_info:
        reloaded = reload_model_from_registry()
        if not reloaded or not model_version_info:
            raise HTTPException(
                status_code=503,
                detail="Modelo não encontrado ou alias '@champion' não atribuído no Registry. Execute 'train_and_register.py' e 'evaluate_and_promote.py' antes."
            )
    return model_version_info


@app.post("/reload")
def trigger_reload():
    """Simula o efeito de um Webhook: força o serviço a recarregar o alias @champion do Registry."""
    success = reload_model_from_registry()
    if not success:
        raise HTTPException(
            status_code=500,
            detail="Falha ao recarregar o modelo do Registry. Verifique se o alias '@champion' existe."
        )
    return {
        "message": "Modelo recarregado com sucesso a partir do Model Registry!",
        "current_version_info": model_version_info
    }


@app.post("/predict")
def predict(input_data: InferenceInput):
    """Executa a predição utilizando a versão ativa carregada do Registry."""
    if loaded_model is None:
        reloaded = reload_model_from_registry()
        if not reloaded or loaded_model is None:
            raise HTTPException(
                status_code=503,
                detail="Modelo não carregado. Certifique-se de ter atribuído o alias '@champion' no Registry."
            )

    if len(input_data.features) != 4:
        raise HTTPException(status_code=400, detail="É necessário fornecer exatamente 4 atributos.")

    try:
        prediction = loaded_model.predict([input_data.features])
        class_id = int(prediction[0])
        class_name = CLASSES_MAP.get(class_id, "desconhecida")

        return {
            "prediction_class_id": class_id,
            "prediction_class_name": class_name,
            "model_metadata": {
                "version": model_version_info.get("version"),
                "model_type": model_version_info.get("model_type"),
                "alias_used": MODEL_ALIAS
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno na inferência: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
