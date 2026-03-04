import joblib
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
import numpy as np

# Definir estrutura de entrada e saída
class InputData(BaseModel):
    comprimento_sepala: float = Field(..., description="Comprimento da sépala em cm (ex: 5.1)")
    largura_sepala: float = Field(..., description="Largura da sépala em cm (ex: 3.5)")
    comprimento_petala: float = Field(..., description="Comprimento da pétala em cm (ex: 1.4)")
    largura_petala: float = Field(..., description="Largura da pétala em cm (ex: 0.2)")

class Prediction(BaseModel):
    id_classe: int = Field(..., description="ID numérico da classe predita (0, 1 ou 2)")
    nome_classe: str = Field(..., description="Nome da espécie da flor (setosa, versicolor ou virginica)")

# 1. Inicializar API
app = FastAPI(title="Minha API de Machine Learning (Iris Dataset)", description="API para classificar flores do tipo Iris com base em suas medidas.", version="1.0.0")

# 2. Carregar Modelo
try:
    model = joblib.load("model.pkl")
    print("✅ Modelo carregado com sucesso!")
except FileNotFoundError:
    model = None
    print("❌ ALERTA: Modelo 'model.pkl' não encontrado. Execute 'python src/train.py' primeiro para treinar o modelo.")

# 3. Mapeamento de Classes (Iris Dataset)
CLASS_NAMES = {0: "setosa", 1: "versicolor", 2: "virginica"}

@app.get("/", summary="Verificar status da API")
def home():
    return {"mensagem": "API de Machine Learning está online!", "modelo_carregado": model is not None}

@app.post("/predict", response_model=Prediction, summary="Fazer uma predição")
def predict(data: InputData):
    """
    Envia as medidas da flor e retorna a espécie prevista pelo modelo.
    """
    if model is None:
        return {"erro": "Modelo não disponível. Treine o modelo primeiro executando 'src/train.py'."}
    
    # Converter entrada para array numpy
    input_features = np.array([[
        data.comprimento_sepala, 
        data.largura_sepala, 
        data.comprimento_petala, 
        data.largura_petala
    ]])
    
    # Fazer predição
    prediction_id = int(model.predict(input_features)[0])
    prediction_name = CLASS_NAMES.get(prediction_id, "Desconhecido")
    
    return {"id_classe": prediction_id, "nome_classe": prediction_name}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
