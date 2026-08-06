"""
app.py

Serviço de Inferência em Produção (FastAPI).
- Fornece o endpoint POST /predict para inferência em tempo real.
- Salva assincronamente os dados de entrada e predição em data/production_logs/inference_logs.csv.
- Suporta Live Reload via POST /reload para carregar modelos re-treinados sem derrubar o container.
"""

import os
import joblib
import numpy as np
import pandas as pd
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sklearn.ensemble import RandomForestClassifier

app = FastAPI(title="Credit Scoring Inference API - MLOps Aula 23", version="1.0")

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")
from src.utils import get_latest_file_path, get_latest_version

# Paths base
MODEL_PREFIX = "credit_model"
REF_PREFIX = "reference"
LOG_PREFIX = "inference_logs"
LOG_DIR = os.path.join(DATA_DIR, "production_logs")

# Estado global
model = None
current_version = 0

class PredictionInput(BaseModel):
    idade: float
    renda_anual: float
    score_credito: float
    taxa_endividamento: float

class BatchInput(BaseModel):
    samples: List[PredictionInput]

def auto_train_baseline():
    """Gera o dataset baseline de referência e treina o modelo inicial automaticamente caso não existam."""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    
    print("⚙️ [Auto-Setup] Gerando baseline de referência e treinando modelo inicial...")
    np.random.seed(42)
    n_samples = 2000
    
    age = np.random.normal(loc=38, scale=10, size=n_samples).clip(18, 75)
    income = np.random.normal(loc=55000, scale=15000, size=n_samples).clip(15000, 150000)
    credit_score = np.random.normal(loc=650, scale=80, size=n_samples).clip(300, 850)
    debt_ratio = np.random.uniform(low=0.1, high=0.6, size=n_samples)
    
    prob_default = 1 / (1 + np.exp(-( -0.05*(age-38) - 0.00004*(income-55000) - 0.015*(credit_score-650) + 3.2*debt_ratio )))
    target = (prob_default > 0.45).astype(int)
    
    df = pd.DataFrame({
        "idade": np.round(age, 1),
        "renda_anual": np.round(income, 2),
        "score_credito": np.round(credit_score, 0),
        "taxa_endividamento": np.round(debt_ratio, 3),
        "target": target
    })
    
    X = df.drop(columns=["target"])
    y = df["target"]
    
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    rf_model.fit(X, y)
    
    ref_path = os.path.join(DATA_DIR, f"{REF_PREFIX}_v1.csv")
    model_path = os.path.join(MODEL_DIR, f"{MODEL_PREFIX}_v1.joblib")
    
    df["prediction"] = rf_model.predict(X)
    df.to_csv(ref_path, index=False)
    joblib.dump(rf_model, model_path)
    print(f"✅ Baseline e modelo inicial (v1) criados com sucesso!")
    
    global current_version
    current_version = 1
    return rf_model

def load_model():
    global model, current_version
    
    latest_model_path = get_latest_file_path(MODEL_DIR, MODEL_PREFIX, ".joblib")
    
    if latest_model_path and os.path.exists(latest_model_path):
        try:
            model = joblib.load(latest_model_path)
            current_version = get_latest_version(MODEL_DIR, MODEL_PREFIX, ".joblib")
            print(f"✅ Modelo carregado com sucesso de: {latest_model_path} (Versão {current_version})")
        except Exception as e:
            print(f"⚠️ Erro ao carregar arquivo de modelo: {e}. Re-treinando...")
            model = auto_train_baseline()
    else:
        print("⚠️ Nenhum modelo encontrado. Executando treinamento automático da baseline (v1)...")
        model = auto_train_baseline()

@app.on_event("startup")
def startup_event():
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)
    load_model()

@app.get("/")
def read_root():
    return {
        "service": "Credit Scoring Inference API",
        "status": "online",
        "model_loaded": model is not None
    }

@app.post("/predict")
def predict(input_data: PredictionInput):
    global model
    if model is None:
        load_model()
        if model is None:
            raise HTTPException(status_code=500, detail="Erro interno: Não foi possível carregar ou inicializar o modelo de inferência.")

    try:
        # Garantir ordem exata dos atributos exigida pelo scikit-learn
        feature_cols = ["idade", "renda_anual", "score_credito", "taxa_endividamento"]
        data_dict = input_data.dict()
        df = pd.DataFrame([[data_dict[col] for col in feature_cols]], columns=feature_cols)
        
        # Realizar predição
        pred = int(model.predict(df)[0])
        prob = float(model.predict_proba(df)[0][1])
        
        # Logar requisição assincronamente no CSV correspondente à versão atual do modelo
        log_path = os.path.join(LOG_DIR, f"{LOG_PREFIX}_v{current_version}.csv")
        
        log_row = data_dict.copy()
        log_row["timestamp"] = datetime.now().isoformat()
        log_row["prediction"] = pred
        log_row["pred_probability"] = round(prob, 4)
        
        log_df = pd.DataFrame([log_row])
        os.makedirs(LOG_DIR, exist_ok=True)
        file_exists = os.path.exists(log_path)
        log_df.to_csv(log_path, mode='a', header=not file_exists, index=False)
        
        return {
            "prediction": pred,
            "probability": prob,
            "status": "logged"
        }
    except Exception as e:
        print(f"❌ Erro ao processar predição: {e}")
        raise HTTPException(status_code=500, detail=f"Erro no processamento da inferência: {str(e)}")

@app.post("/reload")
def reload_model_endpoint():
    load_model()
    return {"status": "reloaded", "model_loaded": model is not None}
