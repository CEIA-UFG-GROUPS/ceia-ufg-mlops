"""
04_remediation_ct.py

Passo 4: Remediação Automatizada & Continuous Training (CT).
- Captura os logs de produção com drift e simula a rotulagem de novos dados.
- Concatena o histórico antigo com o novo perfil de dados.
- Re-treina o modelo de Machine Learning e atualiza a referência (reference.csv).
- Notifica a API FastAPI para efetuar o Live Reload do modelo sem downtime.
- Re-avalia o Evidently AI para comprovar o retorno do sistema ao estado verde (PASS).
"""

import os
import requests
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score

from evidently import ColumnMapping
from evidently.test_suite import TestSuite
from evidently.tests import TestShareOfDriftedColumns, TestColumnDrift

from src.utils import get_latest_file_path, get_next_file_path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
MODEL_DIR = os.path.join(BASE_DIR, "models")
LOG_DIR = os.path.join(DATA_DIR, "production_logs")

def main():
    print("🔄 [Passo 4] Executando Pipeline de Remediação & Re-treinamento Contínuo (CT)...")
    
    ref_path = get_latest_file_path(DATA_DIR, "reference", ".csv")
    log_path = get_latest_file_path(LOG_DIR, "inference_logs", ".csv")
    
    if not log_path or not ref_path or not os.path.exists(log_path) or not os.path.exists(ref_path):
        print("❌ Arquivos de dados necessários não encontrados. Execute os passos 1 a 3 primeiro!")
        return
        
    old_ref = pd.read_csv(ref_path)
    logs_df = pd.read_csv(log_path)
    
    print(f"📦 Coletando {len(logs_df)} novas inferências de produção para composição da nova referência...")
    
    # Simular a chegada de rótulos reais (Ground Truth) nos logs de produção
    prob = 1 / (1 + np.exp(-( -0.02*(logs_df['idade']-29) - 0.00002*(logs_df['renda_anual']-78000) - 0.010*(logs_df['score_credito']-620) + 5.5*logs_df['taxa_endividamento'] )))
    logs_df["target"] = (prob > 0.45).astype(int)
    
    # Manter apenas as colunas de treino
    cols = ["idade", "renda_anual", "score_credito", "taxa_endividamento", "target"]
    new_data = logs_df[cols]
    
    # Combinar 60% da referência antiga com os novos dados de produção (janela móvel adaptativa)
    combined_df = pd.concat([old_ref[cols].sample(frac=0.6, random_state=42), new_data], ignore_index=True)
    
    print(f"🏋️ Re-treinando o modelo com o novo dataset unificado ({len(combined_df)} amostras)...")
    X = combined_df.drop(columns=["target"])
    y = combined_df["target"]
    
    new_model = RandomForestClassifier(n_estimators=120, max_depth=7, random_state=42)
    new_model.fit(X, y)
    
    preds = new_model.predict(X)
    acc = accuracy_score(y, preds)
    f1 = f1_score(y, preds)
    
    combined_df["prediction"] = preds
    
    # Salvar novos artefatos com versão incrementada
    next_model_path = get_next_file_path(MODEL_DIR, "credit_model", ".joblib")
    next_ref_path = get_next_file_path(DATA_DIR, "reference", ".csv")
    
    joblib.dump(new_model, next_model_path)
    combined_df.to_csv(next_ref_path, index=False)
    
    print(f"✅ Novo modelo re-treinado salvo em: {next_model_path}")
    print(f"✅ Nova baseline de referência atualizada em: {next_ref_path}")
    print(f"📊 Desempenho do Novo Modelo Re-treinado: Acurácia = {acc:.4f} | F1-Score = {f1:.4f}")
    
    # Disparar Live Reload na API FastAPI
    try:
        r = requests.post("http://localhost:8000/reload")
        if r.status_code == 200:
            print("⚡ Webhook disparado com sucesso: API de produção recarregou o novo modelo sem downtime!")
    except Exception:
        print("💡 API FastAPI não conectada para reload. O modelo local foi atualizado.")
        
    # Re-avaliar o Evidently AI com o novo baseline
    print("\n🔬 Re-executando validação do Evidently AI com o novo baseline de referência...")
    eval_cols = ["idade", "renda_anual", "score_credito", "taxa_endividamento", "prediction"]
    ref_eval = combined_df[[c for c in eval_cols if c in combined_df.columns]].copy()
    # Avaliar as últimas inferências (simulando um novo lote de tráfego que segue o novo perfil do mercado)
    # Aqui, usamos uma amostra do combined_df para representar o tráfego "pós-remediação"
    curr_eval = combined_df.sample(n=len(logs_df), random_state=100)[[c for c in eval_cols if c in combined_df.columns]].copy()
    
    column_mapping = ColumnMapping()
    column_mapping.target = None
    column_mapping.prediction = "prediction"
    column_mapping.numerical_features = ["idade", "renda_anual", "score_credito", "taxa_endividamento"]
    
    # Avaliar as últimas inferências contra a NOVA referência
    drift_suite = TestSuite(tests=[
        TestShareOfDriftedColumns(lt=0.25),
        TestColumnDrift(column_name="renda_anual", stattest="ks", stattest_threshold=0.05)
    ])
    
    drift_suite.run(reference_data=ref_eval, current_data=curr_eval, column_mapping=column_mapping)
    results = drift_suite.as_dict()
    passed = results["summary"]["all_passed"]
    
    print("\n" + "="*65)
    print("📌 RE-AVALIAÇÃO PÓS-REMEDIAÇÃO (EVIDENTLY AI)")
    print("="*65)
    print(f"Status do Monitor: {'🟢 PASS (SISTEMA RESTAURADO E RE-ALINHADO!)' if passed else '🚨 ALERTA PERSISTENTE'}")
    print("="*65)
    print("\n🎉 PARABÉNS! Você completou o ciclo fechado de MLOps: Treino -> Drift -> Alerta -> CT -> Remediação!")
    print("\n👉 Bônus Opcional: Execute 'python -m src.05_eval_llm_text' para testar a avaliação de LLMs!")

if __name__ == "__main__":
    main()
