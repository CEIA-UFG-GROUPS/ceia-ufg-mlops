# 📘 Aula 24 — Explainability, Fairness e LLMs

## Material de Estudo Prévio

Esta aula trata de confiança em sistemas de ML sob dois ângulos: entender as
decisões do modelo e verificar se seus efeitos diferem entre grupos. Depois,
aplica o mesmo raciocínio de rastreabilidade a aplicações com LLMs.

## 🎯 Objetivos da aula

Ao final, você deverá conseguir:

- explicar uma predição tabular com SHAP e LIME;
- diferenciar explicação global e local;
- calcular métricas de desempenho e fairness por grupo;
- explicar por que um proxy pode manter um viés mesmo sem o atributo protegido;
- comparar Foundation Model, fine-tuning e RAG;
- descrever as etapas de um pipeline RAG;
- identificar quais artefatos precisam ser auditados em uma aplicação com LLM.

## 🧠 Explainability não é causalidade

Uma explicação descreve como o modelo relaciona entradas e saída segundo uma
determinada técnica. Ela não demonstra que uma feature causou o resultado no
mundo real.

### SHAP

SHAP distribui a diferença entre a previsão e um valor de referência entre as
features. No laboratório:

- `TreeExplainer` explica o Random Forest;
- a visão global calcula a média das contribuições absolutas;
- a visão local explica uma linha específica.

### LIME

LIME cria perturbações ao redor de uma instância, consulta o modelo e ajusta um
modelo interpretável local. Ele pode ser útil para investigação, mas depende da
amostragem e da definição de proximidade.

| Pergunta | SHAP global | SHAP/LIME local |
|---|---|---|
| Quais features mais influenciam o conjunto? | Sim | Não necessariamente |
| Por que esta decisão ocorreu? | Indiretamente | Sim |
| É explicação causal? | Não | Não |
| Pode variar com a amostra? | Sim | Sim, especialmente LIME |

## ⚖️ Fairness

O atributo protegido deve ser preservado para auditoria, mesmo quando não é
usado pelo modelo. Avaliamos o impacto por grupo:

- **Selection rate:** proporção de decisões positivas;
- **Accuracy:** proporção de decisões corretas;
- **TPR:** proporção de positivos reais aprovados;
- **FPR:** proporção de negativos reais aprovados;
- **Demographic parity:** compara decisões positivas entre grupos;
- **Equalized odds:** compara TPR e FPR entre grupos.

Não existe uma definição única adequada para todos os problemas. Além disso,
uma métrica pode melhorar enquanto outra piora. O resultado deve ser interpretado
com contexto jurídico, social, operacional e de negócio.

O exemplo sintético de crédito contém `protected_group` e uma variável proxy.
O grupo não entra no treinamento, mas a proxy pode carregar informação sobre ele.
Isso representa um risco de engenharia e governança, não uma conclusão sobre
qualquer população real.

## 🤖 Foundation Models, fine-tuning e RAG

### Foundation Models

Modelos pré-treinados em grandes volumes de dados podem ser adaptados para várias
tarefas. A escolha empresarial considera qualidade, custo, latência, privacidade,
licença, segurança e lock-in.

### Fine-tuning

Fine-tuning altera os pesos para especializar comportamento ou formato. Full
fine-tuning pode ser caro; PEFT/LoRA treina adaptadores menores. Fine-tuning não
é a melhor ferramenta para toda informação nova: dados instáveis frequentemente
pedem retrieval.

### RAG

RAG recupera trechos relevantes e os adiciona ao contexto do modelo:

```text
fonte → chunks → índice → consulta → top-k documentos → contexto → geração
```

O laboratório executa as primeiras etapas com TF-IDF e monta um prompt com
fontes. Não há modelo generativo obrigatório. A Aula 18 aprofunda vector stores
e a Aula 21 cobre serving de LLMs.

## 🔍 Auditabilidade em aplicações com LLM

Para investigar uma resposta, registre pelo menos:

- versão do modelo e parâmetros de geração;
- prompt e instruções do sistema;
- documentos recuperados e seus scores;
- fontes e versão da base documental;
- resposta final e avaliações;
- custo, latência e falhas de retrieval.

SHAP/LIME para modelos tabulares não explicam sozinhos a “intenção” de um LLM.
Em RAG, a trilha de fontes e contexto é parte essencial da investigação.

## 🧪 Atividade prática

Na pasta [`atividade/`](./atividade/):

```bash
pip install -r requirements.txt
python -m src.generate_data
python -m src.train_model
python -m src.explain --method shap
python -m src.explain --method lime
python -m src.fairness
python -m src.rag_retrieve --query "quando usar RAG em vez de fine-tuning?"
```

## 💬 Pontos para reflexão

1. Uma explicação fiel ao modelo pode ainda ser inadequada para uma decisão
   regulada? Por quê?
2. Como uma feature proxy aparece no relatório de SHAP?
3. Qual diferença entre igualdade de seleção e igualdade de TPR/FPR?
4. O que muda quando o conhecimento da aplicação muda toda semana?
5. Que tipo de mudança exige fine-tuning e qual exige apenas atualização do
   índice RAG?
6. O retrieval correto garante uma resposta correta?

## 📚 Referências

- Haviv, A.; Gift, N. *Implementing MLOps in the Enterprise*. Cap. 8,
  “Building Scalable Deep Learning and Large Language Model Projects”, seção
  “LLMs”, pp. 526–541.
- [SHAP TreeExplainer](https://shap.readthedocs.io/en/latest/generated/shap.TreeExplainer.html)
- [LIME](https://lime-ml.readthedocs.io/en/stable/)
- [Fairlearn](https://fairlearn.org/v0.11/user_guide/assessment/common_fairness_metrics.html)
- [Hugging Face PEFT](https://github.com/huggingface/peft)

## 🔗 Conexões com outras aulas

- **Aula 18:** retrieval, embeddings e vector stores.
- **Aula 19:** governança e registro de modelos/LLMs.
- **Aula 21:** serving e observabilidade de LLMs.
- **Aula 11:** monitoramento de qualidade após o deploy.

> **Pergunta para levar ao encontro:** uma resposta de LLM pode ser útil sem ser
> auditável? O que precisaria estar registrado para investigar seu comportamento?
