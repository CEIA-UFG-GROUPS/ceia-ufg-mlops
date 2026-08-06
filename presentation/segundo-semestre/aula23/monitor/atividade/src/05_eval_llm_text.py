"""
05_eval_llm_text.py

Passo 5 (Bônus GenAI): Avaliação de Texto & LLM Drift com Evidently AI.
- Avalia desvio semântico e qualidade de respostas geradas por LLMs em sistemas de atendimento.
- Aplica Descriptors (Sentiment, TextLength, OOV).
- Gera o relatório em HTML (text_eval_report.html).
"""

import os
import pandas as pd
from evidently.report import Report
from evidently.descriptors import Sentiment, TextLength, OOV
from evidently.metric_preset import TextEvals

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

def main():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    
    print("🤖 [Passo 5 - GenAI] Preparando avaliação de desvio semântico em respostas de LLM...")
    
    # Dataset de Referência (Respostas de suporte padrão aprovadas)
    ref_df = pd.DataFrame({
        "resposta_llm": [
            "Olá! Seu pedido foi confirmado e o código de rastreio foi enviado ao seu e-mail cadastrado.",
            "Para alterar a senha da sua conta, acesse o menu Configurações e clique em Segurança.",
            "Agradecemos o seu contato! O estorno será processado em até 2 dias úteis na sua fatura.",
            "Nosso atendimento via chat funciona de segunda a sexta-feira, das 8h às 18h.",
            "Sua solicitação foi concluída com sucesso. Posso te ajudar em algo mais hoje?"
        ]
    })
    
    # Dataset de Produção Recente (Respostas rudes, alucinações ou respostas curtas de falha)
    curr_df = pd.DataFrame({
        "resposta_llm": [
            "Erro interno no sistema de pagamentos. Não sei resolver isso e o suporte tá fora do ar.",
            "Sua conta foi permanentemente bloqueada sem opção de recurso por violação dos termos.",
            "Não entendi absolutamente nada do que você escreveu. Tente escrever de forma clara.",
            "O produto não tem garantia legal e não faremos nenhuma devolução do seu dinheiro.",
            "Sistema indisponível temporariamente. Tente novamente em 48 horas."
        ]
    })
    
    print("🔬 Executando Evidently TextEvals Preset (Sentiment, TextLength, OOV)...")
    text_report = Report(metrics=[
        TextEvals(column_name="resposta_llm", descriptors=[
            Sentiment(),
            TextLength(),
            OOV()
        ])
    ])
    
    text_report.run(reference_data=ref_df, current_data=curr_df)
    
    report_html = os.path.join(REPORTS_DIR, "text_eval_report.html")
    text_report.save_html(report_html)
    
    print(f"📄 Relatório de avaliação de texto em LLM salvo em: {report_html}")
    print("\n💡 Abra http://localhost:8080/text_eval_report.html no seu navegador para explorar o desvio semântico!")

if __name__ == "__main__":
    main()
