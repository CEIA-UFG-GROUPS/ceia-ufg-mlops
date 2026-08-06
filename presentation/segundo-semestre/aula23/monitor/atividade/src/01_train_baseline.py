"""
01_train_baseline.py

Passo 1: Treinar o modelo baseline de concessão de crédito e estabelecer o conjunto de referência.
- Gera os dados de treino de referência (reference.csv).
- Treina o modelo RandomForest.
- Salva o artefato do modelo em models/credit_model.joblib.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

from src.utils import get_next_file_path

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")

def generate_reference_dataset(n_samples: int = 2000, seed: int = 42):
    np.random.seed(seed)
    
    age = np.random.normal(loc=38, scale=10, size=n_samples).clip(18, 75)
    income = np.random.normal(loc=55000, scale=15000, size=n_samples).clip(15000, 150000)
    credit_score = np.random.normal(loc=650, scale=80, size=n_samples).clip(300, 850)
    debt_ratio = np.random.uniform(low=0.1, high=0.6, size=n_samples)
    
    # Relação funcional real (Target = 1 se inadimplente)
    prob_default = 1 / (1 + np.exp(-( -0.05*(age-38) - 0.00004*(income-55000) - 0.015*(credit_score-650) + 3.2*debt_ratio )))
    target = (prob_default > 0.45).astype(int)
    
    df = pd.DataFrame({
        "idade": np.round(age, 1),
        "renda_anual": np.round(income, 2),
        "score_credito": np.round(credit_score, 0),
        "taxa_endividamento": np.round(debt_ratio, 3),
        "target": target
    })
    return df

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    print("🚀 [Passo 1] Gerando conjunto de dados de referência e treinando modelo baseline...")
    
    ref_df = generate_reference_dataset(n_samples=2000, seed=42)
    ref_path = get_next_file_path(DATA_DIR, "reference", ".csv")
    ref_df.to_csv(ref_path, index=False)
    print(f"✅ Baseline salva em: {ref_path} ({len(ref_df)} registros)")
    
    # Treinar modelo
    X_ref = ref_df.drop(columns=["target"])
    y_ref = ref_df["target"]
    
    model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
    model.fit(X_ref, y_ref)
    
    # Avaliar no dataset de referência
    preds = model.predict(X_ref)
    acc = accuracy_score(y_ref, preds)
    f1 = f1_score(y_ref, preds)
    
    ref_df["prediction"] = preds
    ref_df.to_csv(ref_path, index=False)
    
    model_path = get_next_file_path(MODEL_DIR, "credit_model", ".joblib")
    joblib.dump(model, model_path)
    
    print(f"✅ Modelo salvo em: {model_path}")
    print(f"📊 Desempenho do Modelo Baseline (Treino/Validação): Acurácia = {acc:.4f} | F1-Score = {f1:.4f}")
    print("\n👉 Próximo Passo: Execute 'python -m src.02_simulate_traffic' para enviar requisições de produção!")

if __name__ == "__main__":
    main()
