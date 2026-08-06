"""
02_simulate_traffic.py

Passo 2: Simulação de Tráfego de Produção & Ingestão de Logs.
- Conecta à API FastAPI (http://localhost:8000/predict) ou grava diretamente nos logs de produção.
- Envia 3 lotes distintos de requisições:
  • Lote A: Tráfego Normal (mesma distribuição da referência)
  • Lote B: Tráfego com Data Drift (alteração na renda e taxa de endividamento)
  • Lote C: Tráfego com Concept Drift severo
"""

import os
import time
import requests
import numpy as np
import pandas as pd

from src.utils import get_latest_file_path

API_URL = "http://localhost:8000/predict"
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOG_DIR = os.path.join(BASE_DIR, "data", "production_logs")

def generate_sample(batch_type: str, seed: int):
    np.random.seed(seed)
    
    if batch_type == "normal":
        # Lote A: Distribuição idêntica ao treino
        age = np.random.normal(loc=38, scale=10)
        income = np.random.normal(loc=55000, scale=15000)
        credit_score = np.random.normal(loc=650, scale=80)
        debt_ratio = np.random.uniform(low=0.1, high=0.6)
    elif batch_type == "data_drift":
        # Lote B: Covariate Shift (Data Drift na renda e taxa de endividamento)
        age = np.random.normal(loc=28, scale=7)         # Mais jovens
        income = np.random.normal(loc=82000, scale=25000) # Renda maior
        credit_score = np.random.normal(loc=610, scale=90)
        debt_ratio = np.random.uniform(low=0.4, high=0.85) # Taxa de endividamento alta
    else:
        # Lote C: Concept Drift severo (alta inflação / crise econômica)
        age = np.random.normal(loc=31, scale=9)
        income = np.random.normal(loc=95000, scale=30000)
        credit_score = np.random.normal(loc=580, scale=100)
        debt_ratio = np.random.uniform(low=0.5, high=0.95)

    return {
        "idade": round(float(np.clip(age, 18, 75)), 1),
        "renda_anual": round(float(np.clip(income, 15000, 180000)), 2),
        "score_credito": round(float(np.clip(credit_score, 300, 850)), 0),
        "taxa_endividamento": round(float(np.clip(debt_ratio, 0.05, 0.99)), 3)
    }

def main():
    print("🌐 [Passo 2] Simulando tráfego de inferência em produção...")
    
    # Obter o caminho do log da versão atual para fins de exibição/limpeza local
    current_log = get_latest_file_path(LOG_DIR, "inference_logs", ".csv")
    if current_log and os.path.exists(current_log):
        os.remove(current_log)
        print(f"🧹 Logs anteriores limpos em: {current_log}")
        
    api_online = False
    try:
        res = requests.get("http://localhost:8000/")
        if res.status_code == 200:
            api_online = True
            print("✅ Conectado com sucesso à API FastAPI (http://localhost:8000)")
            # Solicitar recarregamento inicial de segurança
            requests.post("http://localhost:8000/reload")
    except Exception:
        print("⚠️ API FastAPI não detectada em http://localhost:8000. Certifique-se de ter executado 'docker compose up -d'!")
        print("💡 Alternativa: Ingestando diretamente nos logs de produção...")

    batches = [
        ("normal", 80, "Lote A (Tráfego Normal - 80 requisições)"),
        ("data_drift", 120, "Lote B (Data Drift em Renda e Endividamento - 120 requisições)"),
        ("concept_drift", 150, "Lote C (Concept Drift Severo - 150 requisições)")
    ]
    
    total_sent = 0
    error_logged = False
    
    for batch_type, count, label in batches:
        print(f"\n📡 Enviando {label}...")
        for i in range(count):
            sample = generate_sample(batch_type, seed=total_sent + i)
            
            if api_online:
                try:
                    r = requests.post(API_URL, json=sample)
                    if r.status_code != 200 and not error_logged:
                        print(f"❌ Erro na requisição (HTTP {r.status_code}): {r.text}")
                        error_logged = True
                except Exception as e:
                    if not error_logged:
                        print(f"❌ Falha de rede: {e}")
                        error_logged = True
            else:
                # Simular log direto caso API offline
                from src.app import predict, PredictionInput
                predict(PredictionInput(**sample))
                
            total_sent += 1
            if total_sent % 50 == 0:
                print(f"   ↳ {total_sent} requisições processadas...")
                
    final_log = get_latest_file_path(LOG_DIR, "inference_logs", ".csv")
    print(f"\n✅ Total de {total_sent} inferências registradas no log: {final_log}")
    print("\n👉 Próximo Passo: Execute 'python -m src.03_evaluate_drift' para analisar os logs no Evidently AI!")

if __name__ == "__main__":
    main()
