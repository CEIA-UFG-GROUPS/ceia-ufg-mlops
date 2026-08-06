"""
03_evaluate_drift.py

Passo 3: Construção e Execução do Monitor Evidently AI.
- Compara o conjunto de referência (reference.csv) com os logs de produção recentes (inference_logs.csv).
- Configura o ColumnMapping e os testes estatísticos.
- Gera relatórios visuais (data_drift_report.html) e executa a TestSuite de automação MLOps.
"""

import os
import pandas as pd
from evidently import ColumnMapping
from evidently.report import Report
from evidently.metric_preset import DataDriftPreset, DataQualityPreset
from evidently.test_suite import TestSuite
from evidently.tests import TestNumberOfColumns, TestShareOfDriftedColumns, TestColumnDrift

from src.utils import get_latest_file_path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_DIR = os.path.join(DATA_DIR, "production_logs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

def main():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    print("📊 [Passo 3] Carregando dados para avaliação no Evidently AI...")
    
    ref_path = get_latest_file_path(DATA_DIR, "reference", ".csv")
    log_path = get_latest_file_path(LOG_DIR, "inference_logs", ".csv")
    
    if not ref_path or not os.path.exists(ref_path):
        print("❌ Dataset de referência não encontrado! Execute 'python -m src.01_train_baseline' primeiro.")
        return
        
    if not log_path or not os.path.exists(log_path):
        print("❌ Logs de inferência de produção não encontrados! Execute 'python -m src.02_simulate_traffic' primeiro.")
        return
        
    ref_df = pd.read_csv(ref_path)
    curr_df = pd.read_csv(log_path)
    
    print(f"✅ Baseline de Referência: {len(ref_df)} registros")
    print(f"✅ Logs de Produção:       {len(curr_df)} registros")
    
    # Selecionar e alinhar exclusivamente as colunas presentes em ambos os DataFrames para avaliação de Data Drift
    eval_cols = ["idade", "renda_anual", "score_credito", "taxa_endividamento", "prediction"]
    ref_eval = ref_df[[c for c in eval_cols if c in ref_df.columns]].copy()
    curr_eval = curr_df[[c for c in eval_cols if c in curr_df.columns]].copy()
    
    # 1. Configurar o ColumnMapping explicitando target como None (pois a produção ainda não tem ground truth)
    column_mapping = ColumnMapping()
    column_mapping.target = None
    column_mapping.prediction = "prediction"
    column_mapping.numerical_features = ["idade", "renda_anual", "score_credito", "taxa_endividamento"]
    
    # 2. Executar Report Visual (Data Drift & Data Quality)
    print("\n🔬 Gerando Evidently Report visual...")
    drift_report = Report(metrics=[
        DataDriftPreset(),
        DataQualityPreset()
    ])
    drift_report.run(reference_data=ref_eval, current_data=curr_eval, column_mapping=column_mapping)
    
    report_html = os.path.join(REPORTS_DIR, "data_drift_report.html")
    drift_report.save_html(report_html)
    print(f"📄 Relatório visual salvo em: {report_html}")
    
    # 3. Executar TestSuite determinística para MLOps
    print("🧪 Executando TestSuite de validação de Drift...")
    drift_suite = TestSuite(tests=[
        TestNumberOfColumns(),
        TestShareOfDriftedColumns(lt=0.25), # Alerta se mais de 25% das features apresentarem drift
        TestColumnDrift(column_name="renda_anual", stattest="ks", stattest_threshold=0.05),
    ])
    drift_suite.run(reference_data=ref_eval, current_data=curr_eval, column_mapping=column_mapping)
    
    suite_html = os.path.join(REPORTS_DIR, "test_suite_report.html")
    drift_suite.save_html(suite_html)
    print(f"📄 Suíte de testes salva em: {suite_html}")
    
    # 4. Analisar resultados
    suite_dict = drift_suite.as_dict()
    all_passed = suite_dict["summary"]["all_passed"]
    failed_tests = suite_dict["summary"]["failed_tests"]
    
    print("\n" + "="*65)
    print("📌 RESULTADO DA AVALIAÇÃO DE DRIFT (EVIDENTLY AI)")
    print("="*65)
    print(f"Status Geral: {'🟢 PASS (Sem Drift Severo)' if all_passed else '🚨 FAIL (Drift Severo Detectado!)'}")
    print(f"Testes Com Falha: {failed_tests}")
    print("="*65)
    
    if not all_passed:
        print("\n⚠️ ALERTA DE DRIFT CRÍTICO: As distribuições de produções recentes divergiram do baseline!")
        print("💡 Abra http://localhost:8080/data_drift_report.html no navegador para inspecionar os gráficos.")
        print("\n👉 Próximo Passo: Execute 'python -m src.04_remediation_ct' para acionar o pipeline de Re-treinamento (CT)!")
    else:
        print("\n✅ As distribuições de dados continuam estáveis dentro dos limiares aceitáveis.")

if __name__ == "__main__":
    main()
