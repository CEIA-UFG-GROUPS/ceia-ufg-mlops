# 🧪 Atividade Prática — Aula 24

Esta atividade combina três perspectivas de um sistema confiável:

1. **Explainability:** explicar decisões tabulares com SHAP e LIME;
2. **Fairness:** medir desempenho e impacto por grupo com Fairlearn;
3. **LLMs:** recuperar contexto local para um pipeline RAG sem API key ou GPU.

O dataset de crédito é sintético e possui `protected_group` para auditoria e
`area_proxy` para demonstrar como remover o atributo protegido não elimina
necessariamente sinais correlacionados.

## 📂 Estrutura

```text
atividade/
├── README.md
├── requirements.txt
├── data/
│   └── knowledge_base.jsonl
├── notebooks/
│   └── aula24_pratica_colab.ipynb
├── src/
│   ├── common.py
│   ├── generate_data.py
│   ├── train_model.py
│   ├── explain.py
│   ├── fairness.py
│   └── rag_retrieve.py
├── tests/
│   └── test_aula24.py
└── docker/
    ├── Dockerfile
    └── docker-compose.yml
```

Execute os comandos a partir da pasta `atividade/`.

## 🛠️ Execução local

```bash
python -m venv .venv
# PowerShell
.\.venv\Scripts\Activate.ps1
# Linux/macOS
# source .venv/bin/activate
pip install -r requirements.txt
```

### 1. Gerar os dados e treinar

```bash
python -m src.generate_data
python -m src.train_model
```

O treinamento salva o modelo em `models/` e os relatórios iniciais em
`reports/`. `protected_group` é explicitamente excluído das features.

### 2. Explainability com SHAP

```bash
python -m src.explain --method shap --row-index 0
```

Arquivos principais:

- `reports/explainability/shap_global_importance.csv`;
- `reports/explainability/shap_global_summary.png`;
- `reports/explainability/shap_local_row_0.png`;
- `reports/explainability/shap_local_row_0.json`.

### 3. Explainability com LIME

```bash
python -m src.explain --method lime --row-index 0
```

Abra `reports/explainability/lime_local_row_0.html` e compare a explicação
local com o resultado do SHAP para a mesma instância.

### 4. Fairness

```bash
python -m src.fairness
```

O comando gera:

- `reports/fairness_by_group.csv`;
- `reports/fairness_metrics.json`.

Observe selection rate, accuracy, TPR, FPR, demographic parity e equalized
odds. Não trate um valor isolado como prova de que o modelo é justo ou injusto;
discuta a métrica adequada ao caso de uso.

### 5. Retrieval RAG local

```bash
python -m src.rag_retrieve --query "quando usar RAG em vez de fine-tuning?"
```

O resultado contém:

- documentos recuperados;
- score de similaridade;
- identificador e fonte;
- prompt montado com o contexto.

Não há geração de texto nesta atividade. O objetivo é tornar visível a etapa de
retrieval e a trilha de fontes antes de conectar um modelo generativo.

## 🐳 Execução com Docker

```bash
docker compose -f docker/docker-compose.yml build
docker compose -f docker/docker-compose.yml run --rm lab python -m src.generate_data
docker compose -f docker/docker-compose.yml run --rm lab python -m src.train_model
docker compose -f docker/docker-compose.yml run --rm lab python -m src.explain --method shap
docker compose -f docker/docker-compose.yml run --rm lab python -m src.fairness
docker compose -f docker/docker-compose.yml run --rm lab python -m src.rag_retrieve --query "o que é RAG?"
```

O serviço é CPU-only e monta o diretório da atividade para que os relatórios
sejam visíveis no host.

## 🔍 Interpretação correta

- SHAP/LIME explicam o comportamento do modelo, não uma causa social.
- Importância global não explica automaticamente uma instância individual.
- `protected_group` fora das features não impede o uso de proxies.
- Demographic parity e equalized odds não são equivalentes.
- RAG recuperando uma fonte correta não garante resposta correta.
- Fine-tuning é uma decisão de adaptação; não é mecanismo geral de atualização
  de conhecimento.

## ✅ Validação

```bash
python -m unittest discover -s tests -v
```

Os testes verificam geração determinística, exclusão do atributo protegido,
treino, artefatos SHAP/LIME, métricas Fairlearn e retrieval determinístico.

## 💬 Perguntas para discutir

1. O que a variável `area_proxy` revela sobre fairness?
2. SHAP e LIME concordam para a mesma decisão? Se não, o que investigar?
3. Qual métrica de fairness seria relevante para crédito e por quê?
4. Quando atualizar a base RAG é melhor que fazer fine-tuning?
5. Que informações você registraria para auditar uma resposta de LLM?

## ⚠️ Solução de problemas

| Sintoma | Causa provável / solução |
|---|---|
| `No module named src` | Execute a partir de `monitor/atividade/`. |
| SHAP falha antes do treino | Rode `python -m src.train_model`. |
| LIME não encontra o modelo | Instale `lime` pelo `requirements.txt`. |
| Fairlearn não importa | Reinstale as dependências no ambiente virtual. |
| Docker não mostra relatórios | Confira o volume e execute os comandos na pasta da atividade. |
