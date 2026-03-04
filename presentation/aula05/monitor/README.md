# 📘 Aula 05 — Machine Learning (do Clássico às Redes Neurais) e CRISP-DM
## Material de Estudo Prévio (Monitor)

Este material tem como objetivo **preparar o monitor para a aula de Machine Learning e CRISP-DM**, oferecendo uma base conceitual sólida para acompanhar, complementar e aprofundar a discussão conduzida pelo apresentador.

⚠️ **Este conteúdo não é um guia de instruções para o monitor**, mas sim um **material de estudo prévio**, alinhado ao modelo colaborativo do Grupo de Estudos em MLOps do CEIA/UFG.

Recomenda-se fortmente a leitura dos link e documentações de referencia mais a baixo. Essas documentações explicam muito bem muitos fundamentos e pontos importantes para machine learning. Se for para começar, leia a documentação do Scikit-Learn, ele é muito bom.

---

## 🎯 Objetivo da Aula

Ao final desta aula, espera-se que os participantes compreendam:

- A evolução histórica do Machine Learning e sua importância
- A metodologia **CRISP-DM** e suas 6 fases
- Algoritmos clássicos de ML (supervisionados e não-supervisionados)
- Fundamentos de **redes neurais** e deep learning
- Como escolher entre abordagens clássicas e redes neurais
- A relação entre escolhas de modelo e MLOps

---

## 🧠 Contexto: Evolução do Machine Learning

### Breve História

**Machine Learning Clássico (1950s-2000s):**
- Início com algoritmos estatísticos e de otimização
- Regressão Linear, Árvores de Decisão, SVM
- Foco em problemas bem definidos com dados estruturados
- Interpretabilidade e simplicidade como vantagens

**Redes Neurais (1980s-presente):**
- Perceptron (1957) - primeiro modelo de neurônio artificial
- Backpropagation (1980s) - permitiu treinar redes multicamadas
- Deep Learning (2000s-presente) - redes profundas com múltiplas camadas
- Revolução com grandes volumes de dados e GPUs

**Era Moderna (2010s-presente):**
- Convivência entre abordagens clássicas e deep learning
- Cada abordagem tem seu lugar
- Importância de escolher a ferramenta certa para o problema certo

### Por que Ambas Abordagens Importam?

**ML Clássico:**
- Mais interpretável
- Requer menos dados
- Treinamento mais rápido
- Ainda domina muitos problemas em produção

**Redes Neurais:**
- Excelente para dados não estruturados (imagens, texto, áudio)
- Pode aprender representações complexas
- Requer mais dados e recursos computacionais
- Menos interpretável

> **"Comece simples, escale quando necessário"** - Princípio fundamental em ML

---

## 📋 CRISP-DM: Metodologia Estruturada

### O que é CRISP-DM?

**CRISP-DM** (Cross-Industry Standard Process for Data Mining) é uma metodologia estruturada para projetos de mineração de dados e Machine Learning, desenvolvida em 1996 e ainda amplamente utilizada.

**Por que usar CRISP-DM?**
- Processo estruturado e comprovado
- Reduz retrabalho e erros
- Facilita comunicação entre equipes
- Base para metodologias modernas de MLOps
- Adaptável a diferentes contextos

### As 6 Fases do CRISP-DM

#### 1. Business Understanding (Compreensão do Negócio)

**Objetivo:** Entender os objetivos do negócio e traduzi-los em objetivos técnicos.

**Atividades:**
- Identificar objetivos do negócio
- Avaliar a situação atual
- Definir objetivos de mineração de dados
- Criar plano de projeto

**Perguntas-chave:**
- Qual problema estamos tentando resolver?
- Como o sucesso será medido?
- Quais são as restrições (tempo, recursos, dados)?
- Qual o impacto esperado?

**Exemplo:**
- Objetivo de negócio: Reduzir churn de clientes em 20%
- Objetivo técnico: Prever probabilidade de churn com 80% de precisão
- Métricas: Precision, Recall, F1-Score

#### 2. Data Understanding (Compreensão dos Dados)

**Objetivo:** Coletar e explorar os dados disponíveis.

**Atividades:**
- Coletar dados iniciais
- Descrever dados (estatísticas descritivas)
- Explorar dados (visualizações, correlações)
- Verificar qualidade dos dados

**Ferramentas:**
- Estatísticas descritivas (média, mediana, desvio padrão)
- Visualizações (histogramas, scatter plots, box plots)
- Análise de correlação
- Detecção de valores faltantes e outliers

**Checklist:**
- Quantos registros temos?
- Quais features estão disponíveis?
- Há dados faltantes?
- Há outliers?
- Os dados estão balanceados?

#### 3. Data Preparation (Preparação dos Dados)

**Objetivo:** Preparar os dados para modelagem.

**Atividades:**
- Seleção de dados (quais usar)
- Limpeza de dados (tratar missing values, outliers)
- Construção de features (feature engineering)
- Integração de dados (combinar fontes)
- Formatação de dados (transformações)

**Técnicas comuns:**
- Tratamento de missing values (imputação, remoção)
- Encoding de variáveis categóricas (one-hot, label encoding)
- Normalização e padronização
- Feature engineering (criar novas features)
- Feature selection (selecionar features relevantes)

**Importância:**
> **"Garbage in, garbage out"** - A qualidade do modelo depende da qualidade dos dados

#### 4. Modeling (Modelagem)

**Objetivo:** Aplicar técnicas de ML para criar modelos.

**Atividades:**
- Selecionar técnica de modelagem
- Gerar design de teste
- Construir modelo
- Avaliar modelo

**Algoritmos comuns:**
- **Supervisionados:** Regressão Linear, Árvores de Decisão, SVM, KNN, Random Forest
- **Não-supervisionados:** K-Means, PCA, DBSCAN
- **Redes Neurais:** Perceptron, MLP, CNNs, RNNs

**Boas práticas:**
- Dividir dados em treino, validação e teste
- Usar validação cruzada
- Comparar múltiplos algoritmos
- Ajustar hiperparâmetros
- Evitar overfitting

#### 5. Evaluation (Avaliação)

**Objetivo:** Avaliar se o modelo atende aos objetivos do negócio.

**Atividades:**
- Avaliar resultados
- Revisar processo
- Determinar próximos passos

**Métricas comuns:**
- **Classificação:** Accuracy, Precision, Recall, F1-Score, ROC-AUC
- **Regressão:** MAE, MSE, RMSE, R²
- **Clustering:** Silhouette Score, Inertia

**Avaliação de negócio:**
- O modelo resolve o problema de negócio?
- As métricas atendem aos critérios definidos?
- Há viés ou problemas éticos?
- O modelo é interpretável o suficiente?

#### 6. Deployment (Deploy)

**Objetivo:** Colocar o modelo em produção.

**Atividades:**
- Planejar deploy
- Planejar monitoramento e manutenção
- Produzir relatório final
- Revisar projeto

**Considerações:**
- Como o modelo será servido? (API, batch, real-time)
- Como será monitorado?
- Como será atualizado?
- Documentação e runbooks
- Versionamento de modelo

**Conexão com MLOps:**
- Esta fase é onde MLOps entra em ação
- Automação de deploy, monitoramento, retreino
- Infraestrutura e pipelines

### Iteratividade do CRISP-DM

**Importante:** CRISP-DM não é linear!

- Fases podem ser repetidas
- É comum voltar a fases anteriores
- Processo iterativo e adaptativo
- Aprendizado contínuo

**Exemplo de iteração:**
1. Data Understanding → descobrimos dados faltantes
2. Data Preparation → tratamos missing values
3. Modeling → modelo tem baixa performance
4. Data Preparation → fazemos feature engineering
5. Modeling → tentamos novamente

---

## 🤖 Machine Learning Clássico

### Algoritmos Supervisionados

#### Regressão Linear

**O que é:**
- Modela relação linear entre features e target contínuo
- Equação: y = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ

**Vantagens:**
- Simples e interpretável
- Rápido de treinar
- Boa baseline
- Não requer muitos dados

**Limitações:**
- Assume relação linear
- Sensível a outliers
- Não captura relações não-lineares

**Casos de uso:**
- Previsão de preços
- Análise de tendências
- Problemas com relação linear clara

#### Árvores de Decisão

**O que é:**
- Modelo que faz decisões baseadas em regras if-else
- Divide dados em subconjuntos baseado em features

**Vantagens:**
- Muito interpretável
- Não requer normalização
- Lida bem com features categóricas
- Captura relações não-lineares

**Limitações:**
- Pode overfit facilmente
- Instável (pequenas mudanças nos dados mudam a árvore)
- Pode não generalizar bem

**Casos de uso:**
- Classificação com regras claras
- Problemas onde interpretabilidade é importante
- Baseline para problemas complexos

#### Random Forest

**O que é:**
- Ensemble de múltiplas árvores de decisão
- Combina predições de várias árvores

**Vantagens:**
- Mais robusto que árvore única
- Menos propenso a overfitting
- Boa performance geral
- Pode medir importância de features

**Limitações:**
- Menos interpretável que árvore única
- Mais lento que árvore única
- Ainda pode overfit com dados muito ruidosos

**Casos de uso:**
- Problemas onde árvores funcionam mas precisamos de mais robustez
- Feature importance
- Baseline sólido

#### SVM (Support Vector Machine)

**O que é:**
- Encontra o hiperplano que melhor separa as classes
- Usa kernel trick para relações não-lineares

**Vantagens:**
- Eficiente em espaços de alta dimensão
- Funciona bem com kernels (não-linear)
- Boa generalização

**Limitações:**
- Não escala bem com muitos dados
- Requer tuning de hiperparâmetros
- Menos interpretável

**Casos de uso:**
- Classificação de texto
- Problemas com muitas features
- Quando precisamos de margem de separação clara

#### K-Nearest Neighbors (KNN)

**O que é:**
- Classifica baseado nos k vizinhos mais próximos
- Algoritmo "lazy" (não aprende, apenas memoriza)

**Vantagens:**
- Simples de entender e implementar
- Não assume distribuição dos dados
- Boa para dados não-lineares

**Limitações:**
- Lento para predição (calcula distâncias)
- Sensível a escala das features
- Requer escolha de k
- Sensível a dados ruidosos

**Casos de uso:**
- Problemas com padrões locais
- Quando dados são bem distribuídos
- Baseline simples

### Algoritmos Não-Supervisionados

#### K-Means Clustering

**O que é:**
- Agrupa dados em k clusters
- Minimiza variância dentro dos clusters

**Vantagens:**
- Simples e rápido
- Escala bem
- Fácil de interpretar

**Limitações:**
- Precisa especificar k
- Assume clusters esféricos
- Sensível a inicialização
- Sensível a outliers

**Casos de uso:**
- Segmentação de clientes
- Análise exploratória
- Redução de dimensionalidade

#### PCA (Principal Component Analysis)

**O que é:**
- Reduz dimensionalidade mantendo variância máxima
- Encontra componentes principais (combinações lineares de features)

**Vantagens:**
- Reduz dimensionalidade
- Remove correlação entre features
- Visualização de dados de alta dimensão

**Limitações:**
- Perde interpretabilidade
- Assume relação linear
- Pode perder informação importante

**Casos de uso:**
- Visualização de dados
- Redução de dimensionalidade antes de modelagem
- Remoção de correlação

---

## 🧠 Redes Neurais: Fundamentos

### Conceitos Básicos

#### Neurônio Artificial

**Estrutura:**
- Recebe múltiplas entradas (x₁, x₂, ..., xₙ)
- Aplica pesos (w₁, w₂, ..., wₙ)
- Calcula soma ponderada: z = Σ(wᵢ × xᵢ) + b
- Aplica função de ativação: a = f(z)
- Produz saída

**Analogia:**
- Similar a neurônio biológico
- Recebe sinais, processa, produz resposta

#### Funções de Ativação

**Sigmoid:**
- f(x) = 1 / (1 + e⁻ˣ)
- Saída entre 0 e 1
- Usada em classificação binária
- Problema: vanishing gradient

**Tanh:**
- f(x) = tanh(x)
- Saída entre -1 e 1
- Similar a sigmoid mas centrada em zero

**ReLU (Rectified Linear Unit):**
- f(x) = max(0, x)
- Mais comum em deep learning
- Resolve vanishing gradient
- Problema: dying ReLU (neurônios que nunca ativam)

**Softmax:**
- Usada na última camada para classificação multiclasse
- Produz probabilidades que somam 1

### Perceptron

**O que é:**
- Rede neural mais simples
- Um único neurônio
- Aprende separação linear

**Limitações:**
- Só resolve problemas linearmente separáveis
- Não pode aprender XOR (problema clássico)

**Importância histórica:**
- Base para redes neurais modernas
- Demonstrou que máquinas podem "aprender"

### MLP (Multi-Layer Perceptron)

**O que é:**
- Rede neural com múltiplas camadas
- Camada de entrada → camadas ocultas → camada de saída
- Pode aprender relações não-lineares

**Estrutura:**
- **Camada de entrada:** Recebe features
- **Camadas ocultas:** Processamento intermediário
- **Camada de saída:** Produz predição

**Backpropagation:**
- Algoritmo para treinar MLPs
- Propaga erros de trás para frente
- Ajusta pesos usando gradiente descendente
- Permite treinar redes profundas

**Vantagens:**
- Aprende relações não-lineares complexas
- Universal function approximator (teoricamente)
- Flexível e adaptável

**Limitações:**
- Requer muitos dados
- Pode overfit facilmente
- Requer tuning de hiperparâmetros
- Menos interpretável

### Deep Learning

**O que é:**
- Redes neurais com muitas camadas (profundas)
- Aprende representações hierárquicas

**Por que funciona agora?**
- Grandes volumes de dados disponíveis
- GPUs para treinamento rápido
- Técnicas modernas (dropout, batch normalization)
- Arquiteturas avançadas (CNNs, RNNs, Transformers)

**Tipos:**
- **CNNs:** Para imagens
- **RNNs/LSTMs:** Para sequências (texto, tempo)
- **Transformers:** Para NLP moderno

---

## ⚖️ Comparação: Clássico vs Redes Neurais

### Quando Usar ML Clássico?

**Use quando:**
- Tem poucos dados (< 10k amostras)
- Precisa de interpretabilidade
- Problema é bem definido e estruturado
- Quer uma solução rápida e simples
- Recursos computacionais são limitados
- Features são bem engenheiradas

**Exemplos:**
- Análise de risco de crédito
- Sistemas de recomendação simples
- Classificação de documentos estruturados
- Análise de dados tabulares

### Quando Usar Redes Neurais?

**Use quando:**
- Tem muitos dados (> 100k amostras)
- Dados não estruturados (imagens, texto, áudio)
- Relações complexas e não-lineares
- Performance máxima é crítica
- Recursos computacionais disponíveis
- Problema requer representações aprendidas

**Exemplos:**
- Visão computacional (classificação de imagens)
- Processamento de linguagem natural
- Reconhecimento de voz
- Jogos (AlphaGo, Dota 2)

### Trade-offs

| Aspecto | ML Clássico | Redes Neurais |
|---------|-------------|---------------|
| **Interpretabilidade** | Alta | Baixa |
| **Dados necessários** | Poucos | Muitos |
| **Tempo de treinamento** | Rápido | Lento |
| **Custo computacional** | Baixo | Alto |
| **Complexidade** | Simples | Complexa |
| **Overfitting** | Menos comum | Mais comum |
| **Feature engineering** | Necessário | Menos necessário |

### Princípio: Começar Simples

> **"Start simple, scale when needed"**

1. Comece com ML clássico
2. Estabeleça baseline
3. Se performance não for suficiente, considere redes neurais
4. Avalie trade-offs (custo, complexidade, interpretabilidade)

---

## 🛠️ Frameworks e Ferramentas

### Scikit-learn (ML Clássico)

**O que é:**
- Biblioteca Python para ML clássico
- API consistente e fácil de usar
- Amplamente adotada

**Principais módulos:**
- `sklearn.linear_model`: Regressão Linear, Logistic Regression
- `sklearn.tree`: Árvores de Decisão
- `sklearn.ensemble`: Random Forest, Gradient Boosting
- `sklearn.svm`: Support Vector Machines
- `sklearn.cluster`: K-Means, DBSCAN
- `sklearn.preprocessing`: Normalização, encoding

**Vantagens:**
- Fácil de usar
- Bem documentada
- Grande comunidade
- Integração com NumPy/Pandas

**Exemplo básico:**
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Dividir dados
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Treinar modelo
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Predizer
predictions = model.predict(X_test)
```

### TensorFlow/Keras (Redes Neurais)

**O que é:**
- TensorFlow: Framework de baixo nível
- Keras: API de alto nível (agora parte do TensorFlow)
- Desenvolvido pelo Google

**Vantagens:**
- Produção-ready
- Suporte a GPU/TPU
- Ecossistema completo (TensorFlow Serving, TensorBoard)
- Amplamente usado na indústria

**Exemplo básico:**
```python
from tensorflow import keras
from tensorflow.keras import layers

# Criar modelo
model = keras.Sequential([
    layers.Dense(64, activation='relu', input_shape=(784,)),
    layers.Dense(32, activation='relu'),
    layers.Dense(10, activation='softmax')
])

# Compilar
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Treinar
model.fit(X_train, y_train, epochs=10, validation_split=0.2)
```

### PyTorch (Redes Neurais)

**O que é:**
- Framework desenvolvido pelo Facebook
- Mais Pythonic que TensorFlow
- Popular em pesquisa

**Vantagens:**
- Mais flexível para pesquisa
- Debugging mais fácil
- Computação dinâmica
- Boa para prototipagem

**Exemplo básico:**
```python
import torch
import torch.nn as nn

# Definir modelo
class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(
            nn.Linear(784, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 10)
        )
    
    def forward(self, x):
        return self.layers(x)

model = MLP()
```

### Outras Ferramentas

**XGBoost/LightGBM:**
- Gradient Boosting avançado
- Excelente para dados tabulares
- Muito usado em competições (Kaggle)

**Pandas/NumPy:**
- Manipulação e análise de dados
- Essenciais para qualquer projeto de ML

**Matplotlib/Seaborn:**
- Visualização de dados
- Importante para exploração e apresentação

---

## 💡 Boas Práticas

### Seguir Metodologias Estruturadas

- Use CRISP-DM ou metodologias similares
- Documente cada fase
- Mantenha rastreabilidade
- Facilita reprodução e manutenção

### Validação e Avaliação

**Dividir dados corretamente:**
- Treino: ~70%
- Validação: ~15%
- Teste: ~15%

**Validação cruzada:**
- K-fold cross-validation
- Mais robusto que split único
- Especialmente importante com poucos dados

**Métricas apropriadas:**
- Escolha métricas relevantes para o problema
- Não use apenas accuracy (pode ser enganoso)
- Considere métricas de negócio

### Evitar Overfitting

**Sinais de overfitting:**
- Performance alta no treino, baixa no teste
- Modelo muito complexo para os dados disponíveis

**Soluções:**
- Regularização (L1, L2)
- Dropout (redes neurais)
- Early stopping
- Mais dados
- Modelo mais simples

### Feature Engineering

**Importante para ML clássico:**
- Criar features relevantes
- Remover features irrelevantes
- Normalizar/padronizar quando necessário

**Menos crítico para deep learning:**
- Redes neurais podem aprender features
- Ainda importante, mas menos crítico

### Interpretabilidade

**Quando é importante:**
- Regulamentações (ex: crédito, saúde)
- Debugging de modelos
- Ganhar confiança de stakeholders
- Entender o que o modelo aprendeu

**Técnicas:**
- Feature importance (árvores)
- SHAP values
- LIME
- Visualizações

### Conexão com MLOps

**Escolhas de modelo impactam MLOps:**
- Modelos simples são mais fáceis de deploy
- Modelos complexos podem precisar de infraestrutura especial
- Interpretabilidade facilita monitoramento
- Performance vs complexidade trade-off

---

## 💬 Pontos para Reflexão Pré-Aula

Como monitor, reflita sobre:

1. **Por que começar com ML clássico antes de deep learning?**
   - Quais são as vantagens de começar simples?
   - Quando faz sentido escalar para redes neurais?

2. **Como CRISP-DM se relaciona com MLOps?**
   - Quais fases do CRISP-DM são mais críticas para produção?
   - Como metodologias estruturadas facilitam MLOps?

3. **Quando escolher ML clássico vs redes neurais?**
   - Quais critérios são mais importantes?
   - Como balancear performance, interpretabilidade e complexidade?

4. **Qual o papel da interpretabilidade em produção?**
   - Quando interpretabilidade é crítica?
   - Como isso impacta monitoramento e debugging?

5. **Como feature engineering difere entre abordagens?**
   - Por que é mais importante para ML clássico?
   - Como deep learning muda isso?

6. **Quais são os trade-offs reais em produção?**
   - Custo computacional vs performance
   - Complexidade vs manutenibilidade
   - Interpretabilidade vs acurácia

Esses pontos são fundamentais para enriquecer a discussão durante o encontro.

---

## 📚 Referências

### Livros e Artigos

1. **Huyen, C. (2022).** *Designing Machine Learning Systems: An Iterative Process for Production-Ready Applications*. O'Reilly Media.
   - Repositório: [https://github.com/chiphuyen/dmls-book](https://github.com/chiphuyen/dmls-book)
   - Capítulos sobre escolha de modelos, feature engineering, e avaliação
   - Visão holística de sistemas de ML em produção
   - Pedro Saraiva tem uma versão fisica desse livro, se quiserem, podem pedir emprestado.

2. **Géron, A. (2019).** *Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow*. O'Reilly Media.
   - Guia prático de ML clássico e deep learning
   - Exemplos práticos e código

3. **Goodfellow, I., Bengio, Y., & Courville, A. (2016).** *Deep Learning*. MIT Press.
   - Referência fundamental sobre deep learning
   - Teoria e fundamentos matemáticos

### Documentação e Recursos Online

4. **Scikit-learn Documentation**
   - [https://scikit-learn.org/stable/](https://scikit-learn.org/stable/)
   - Guia completo de ML clássico
   - Tutoriais e exemplos

5. **TensorFlow Documentation**
   - [https://www.tensorflow.org/](https://www.tensorflow.org/)
   - Guia de redes neurais e deep learning
   - Tutoriais práticos

6. **PyTorch Documentation**
   - [https://pytorch.org/docs/stable/index.html](https://pytorch.org/docs/stable/index.html)
   - Documentação completa do PyTorch
   - Tutoriais e exemplos

7. **CRISP-DM Guide**
   - [https://www.ibm.com/docs/en/spss-modeler/saas?topic=dm-crisp-help-overview](https://www.ibm.com/docs/en/spss-modeler/saas?topic=dm-crisp-help-overview)
   - Guia oficial da metodologia CRISP-DM
   - Detalhamento das 6 fases

### Artigos e Blog Posts

8. **"No Free Lunch Theorem"**
   - Não existe algoritmo que funcione melhor para todos os problemas
   - Importância de escolher a abordagem certa

9. **"The Unreasonable Effectiveness of Data"**
   - Por que dados são tão importantes
   - Relação entre dados e performance

10. **"Why Deep Learning Works"**
    - Explicações sobre por que deep learning funciona
    - Teoria e prática

### Exemplos Práticos e Repositórios

11. **PyTorch Sentiment Analysis Tutorials**
    - [https://github.com/bentrevett/pytorch-sentiment-analysis](https://github.com/bentrevett/pytorch-sentiment-analysis)
    - Tutoriais completos de análise de sentimento com PyTorch
    - Evolução de modelos: Neural Bag of Words → RNN/LSTM → CNN → Transformers
    - Prática recomendada para a aula: executar, entender, modificar e fazer deploy de API

12. **Scikit-learn Examples**
    - [https://scikit-learn.org/stable/auto_examples/index.html](https://scikit-learn.org/stable/auto_examples/index.html)
    - Exemplos práticos de todos os algoritmos

13. **TensorFlow Tutorials**
    - [https://www.tensorflow.org/tutorials](https://www.tensorflow.org/tutorials)
    - Tutoriais passo a passo

14. **Kaggle Learn**
    - [https://www.kaggle.com/learn](https://www.kaggle.com/learn)
    - Cursos práticos de ML
    - Competições para prática