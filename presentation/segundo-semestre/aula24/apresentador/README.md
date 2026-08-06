# Explainability, Fairness e LLMs

## README do Apresentador

Esta aula conecta duas perguntas de confiança em sistemas de ML:

1. **Por que este modelo tomou esta decisão?**
2. **A decisão afeta grupos diferentes de forma diferente?**

Depois, a discussão sobe de nível para LLMs: como escolher entre um Foundation
Model, fine-tuning e RAG quando o sistema precisa ser útil, rastreável e
governável?

> **Fio condutor sugerido:** começar com uma aprovação de crédito que o modelo
> não consegue explicar, revelar um proxy de grupo protegido e mostrar que uma
> explicação plausível não prova fairness. Fechar com a analogia para LLMs:
> explicabilidade exige rastrear entradas, contexto recuperado, versão do modelo
> e critérios de avaliação — não apenas exibir uma resposta convincente.

## 1️⃣ Motivação

### 1.1 O modelo acertou, mas podemos confiar nele?

- Métricas agregadas escondem decisões individuais e diferenças entre grupos.
- Uma feature pode ser importante para o modelo sem ser uma causa legítima.
- Um atributo protegido pode ser removido e continuar presente por meio de
  proxies.
- Explicabilidade é evidência para investigação; não é prova de causalidade ou
  de ausência de discriminação.

### 1.2 O que a turma deve sair sabendo fazer

- Explicar uma predição tabular com SHAP e LIME.
- Interpretar importância global versus explicação local.
- Calcular métricas de fairness por grupo.
- Identificar o trade-off entre desempenho e critérios de fairness.
- Diferenciar Foundation Model, fine-tuning e RAG.
- Rastrear as fontes usadas por um pipeline de retrieval.

## 2️⃣ Como Funciona

### 2.1 SHAP: contribuição aditiva

- SHAP atribui contribuições às features em relação a um valor de referência.
- A soma das contribuições aproxima a saída explicada do modelo.
- Para o Random Forest da atividade, usamos `TreeExplainer`.
- **Global:** média do valor absoluto das contribuições em várias amostras.
- **Local:** contribuições das features para uma decisão específica.

Mensagem importante: “feature importante” significa importante para o modelo e
para a distribuição analisada; não significa que seja causal, justa ou estável
fora daquela distribuição.

### 2.2 LIME: modelo local aproximador

- LIME perturba uma instância, consulta o modelo e ajusta um modelo simples ao
  redor daquele ponto.
- É agnóstico ao modelo e útil para uma explicação local rápida.
- A explicação depende da amostragem, da representação e do raio local.
- Uma explicação LIME instável deve ser tratada como sinal de investigação, não
  como verdade definitiva.

### 2.3 Fairness: medir antes de concluir

Avaliar o modelo por grupo protegido:

- selection rate;
- accuracy;
- true-positive rate;
- false-positive rate;
- demographic parity difference/ratio;
- equalized odds difference/ratio.

Apresente a distinção:

| Critério | Pergunta |
|---|---|
| Demographic parity | Os grupos recebem decisões positivas em proporções semelhantes? |
| Equalized odds | TPR e FPR são semelhantes entre os grupos? |
| Performance por grupo | O modelo erra de forma semelhante? |

Não há uma métrica universal. A escolha depende do domínio, do significado do
rótulo, dos custos dos erros e das obrigações legais/organizacionais.

### 2.4 O caso da atividade

- `protected_group` é mantido para auditoria e não entra nas features.
- `area_proxy` é uma variável correlacionada ao grupo e entra no modelo.
- O dataset é sintético para tornar a origem do efeito controlável e não expor
  dados pessoais reais.
- O objetivo não é declarar que um grupo é “problemático”; é revelar como uma
  feature proxy pode produzir diferenças de decisão.

### 2.5 Foundation Models

- São modelos pré-treinados em grandes corpora e reutilizados em diferentes
  tarefas.
- O pré-treinamento produz capacidades gerais; a adaptação conecta o modelo ao
  domínio, tarefa, estilo e políticas do produto.
- A decisão enterprise inclui custo, latência, privacidade, licença,
  segurança, qualidade e dependência do fornecedor.
- Um modelo maior não é automaticamente melhor para uma aplicação específica.

### 2.6 Fine-tuning e LoRA

- **Full fine-tuning:** atualiza muitos ou todos os pesos; é caro e produz uma
  cópia especializada.
- **Instruction tuning:** ajusta o comportamento para seguir instruções.
- **PEFT/LoRA:** treina adaptadores pequenos enquanto preserva o modelo base.
- Fine-tuning é adequado quando o comportamento/estilo/formato precisa mudar de
  forma persistente e há dados de qualidade.
- Riscos: overfitting, esquecimento catastrófico, vazamento de dados e custo de
  manutenção de múltiplos adaptadores.

### 2.7 RAG

```text
documentos → chunking → representação vetorial → retrieval → contexto → resposta
```

- RAG injeta conhecimento externo no contexto sem alterar os pesos do modelo.
- É adequado quando o conhecimento muda, precisa de fonte/citação ou não deve
  ser incorporado permanentemente ao modelo.
- A qualidade depende de chunking, indexação, recuperação e geração.
- O laboratório para no retrieval e monta o prompt; a geração é discutida sem
  exigir API ou GPU.

### 2.8 Explicabilidade em LLMs não é SHAP para texto

- SHAP/LIME tabular explicam decisões de um classificador específico.
- Em LLMs, a investigação precisa incluir prompt, modelo, parâmetros de
  geração, documentos recuperados, fontes, filtros e resposta.
- Uma resposta com citação não é automaticamente verdadeira.
- Traces e avaliações de RAG complementam, mas não substituem, explicações
  causais ou auditorias de fairness.

## 3️⃣ Quickstart & Demos

### 3.1 Demo 1 — Treinar o classificador

Na pasta `monitor/atividade/`:

```bash
pip install -r requirements.txt
python -m src.generate_data
python -m src.train_model
```

Mostre que `protected_group` não está em `reports/feature_columns.json`.

### 3.2 Demo 2 — SHAP e LIME para a mesma decisão

```bash
python -m src.explain --method shap --row-index 0
python -m src.explain --method lime --row-index 0
```

Abra o gráfico global, o gráfico local e o HTML do LIME. Pergunte:

- as duas explicações concordam?
- a feature proxy aparece?
- isso prova que o modelo é injusto?

### 3.3 Demo 3 — Métricas de fairness

```bash
python -m src.fairness
```

Compare as taxas por grupo e peça que a turma escolha qual critério seria mais
relevante em um caso de crédito real. Não transforme o resultado sintético em
conclusão sobre pessoas ou grupos reais.

### 3.4 Demo 4 — Retrieval RAG local

```bash
python -m src.rag_retrieve --query "quando usar RAG em vez de fine-tuning?"
```

Mostre os documentos, scores, fontes e o prompt montado. Relacione com a Aula
18, que aprofunda Feature Stores e vector search, e com a Aula 21, que trata do
serving de LLMs.

### 3.5 Para fechar

Peça uma decisão de arquitetura:

> “Para um chatbot interno com documentos que mudam semanalmente, privacidade
> alta e necessidade de citar fontes, você escolheria Foundation Model + RAG,
> fine-tuning ou ambos? Quais evidências e controles exigiria?”

## 4️⃣ Perguntas para discussão

1. Por que remover `protected_group` não elimina necessariamente o viés?
2. SHAP global e LIME local respondem à mesma pergunta?
3. O que significa uma explicação ser fiel ao modelo, mas não causal?
4. É possível satisfazer demographic parity e equalized odds ao mesmo tempo?
5. Quando fine-tuning é uma solução ruim para conhecimento que muda rapidamente?
6. Como você auditaria um RAG que recupera documentos corretos, mas gera uma
   resposta incorreta?

## 5️⃣ Conexões com outras aulas

- **Aula 11:** monitoramento de qualidade, drift e métricas de produção.
- **Aula 13:** agentes e capacidades LLM governadas.
- **Aula 18:** Feature Stores, embeddings e vector search/RAG.
- **Aula 19:** registro, governança e avaliação de modelos/LLMs.
- **Aula 21:** serving, custo e latência de LLMs.

## Referências

- Haviv, A.; Gift, N. *Implementing MLOps in the Enterprise*. Cap. 8,
  “Building Scalable Deep Learning and Large Language Model Projects”, seção
  “LLMs”, pp. 526–541.
- [SHAP TreeExplainer](https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html)
- [LIME Tabular Explainer](https://lime-ml.readthedocs.io/en/stable/)
- [Fairlearn — métricas comuns](https://fairlearn.org/v0.11/user_guide/assessment/common_fairness_metrics.html)
- [Hugging Face PEFT/LoRA](https://github.com/huggingface/peft)
