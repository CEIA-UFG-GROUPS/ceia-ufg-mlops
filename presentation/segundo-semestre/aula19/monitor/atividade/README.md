# 🧪 Atividade Prática — Aula 19: Model Registry (MLOps)

Prática guiada que percorre o ciclo de vida completo de governança e versão de modelos com **Model Registry**: **treinar → registrar → versionar → avaliar (Quality Gate) → atribuir aliases (@champion) → servir dinamicamente**.

---

## 🎯 O que você vai fazer

1. **Treinar e Registrar** — Treinar o modelo baseline `v1` (DecisionTree) e o modelo avançado `v2` (RandomForest), registrando hiperparâmetros, métricas (F1-score) e binários no MLflow Model Registry sob o nome `ModeloClassificacao`.
2. **Atribuir Aliases** — Entender a diferença entre stages fixos e aliases dinâmicos (`@champion` e `@challenger`).
3. **Quality Gate Automatizado** — Executar o script de avaliação que compara as versões registradas e promove a versão vencedora ao alias `@champion`.
4. **Serving Desacoplado** — Subir uma API FastAPI de inferência que consome a URI dinâmica `models:/ModeloClassificacao@champion`, sem caminhos fixos de arquivo.
5. **Simulação de Webhook / Live Reload** — Disparar o recarregamento do modelo em tempo real sem derrubar o servidor ou alterar o código da API.

---

## 📂 Estrutura de Diretórios

```text
atividade/
├── README.md                          # este arquivo
├── requirements.txt                   # ambiente completo (dev local)
├── src/                               # código-fonte documentado
│   ├── train_and_register.py          # Script 1: treina v1 e v2, loga métricas e registra no Registry
│   ├── evaluate_and_promote.py        # Script 2: Quality Gate que avalia e atribui o alias @champion
│   ├── service.py                     # Script 3: API FastAPI servindo dinamicamente a URI @champion
│   └── test_client.py                 # Script 4: cliente HTTP para testar inferências e ver a versão ativa
└── docker/
    ├── Dockerfile                     # Imagem Python para MLflow Server e FastAPI
    └── docker-compose.yml             # Stack com MLflow Registry Server + FastAPI Model Serving API
```

---

## 💡 Como Funciona o MLflow Tracking URI (Importante!)

Os scripts Python em `src/` detectam automaticamente onde salvar e buscar os modelos:

**Com Docker rodando** (`docker compose up`): O servidor do MLflow fica ativo em `http://localhost:5000`. Os scripts detectam essa porta e enviam os experimentos diretamente para a interface web no navegador!

---

## 🛠️ Execução com Docker

### 1. Subindo a Stack com Docker Compose

Suba o servidor central do MLflow Registry e o serviço de inferência FastAPI:

```bash
cd atividade/docker
docker compose up --build -d
```

Verifique os serviços ativos:
- **MLflow Registry UI**: [http://localhost:5000](http://localhost:5000)
- **FastAPI Serving API**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Treinando e Registrando as Versões no Model Registry

No terminal da sua máquina (na pasta `atividade/`), instale as dependências locais ou use o ambiente virtual (recomendado):

(PowerShell) Criando o ambiente virtual:
```bash
python -m venv .venv
```
(PowerShell) Ativando o ambiente virtual:
```bash
.\.venv\Scripts\Activate.ps1
```
Instalando dependências dentro do ambiente:
```bash
pip install -r requirements.txt
```
Executando treino dos modelos:
```bash
python -m src.train_and_register
```

**Saída esperada no terminal**:
```text
🔗 Conectado ao MLflow Tracking em: http://localhost:5000
🚀 Treinando Modelo v1 (Baseline - DecisionTree)...
Successfully registered model 'ModeloClassificacao'.
Created version '1' of model 'ModeloClassificacao'.
✅ Versão v1 registrada! Run ID: ... | Acc: 0.9778 | F1: 0.9743

🚀 Treinando Modelo v2 (Avançado - RandomForest)...
Registered model 'ModeloClassificacao' already exists. Creating a new version...
Created version '2' of model 'ModeloClassificacao'.
✅ Versão v2 registrada! Run ID: ... | Acc: 1.0000 | F1: 1.0000

🏷️ Alias '@challenger' atribuído à versão 1 do 'ModeloClassificacao'.
```

**Como visualizar no MLflow UI (`http://localhost:5000`)**:
1. Abra [http://localhost:5000](http://localhost:5000) no seu navegador.
2. Na barra lateral esquerda ou no topo da tela, altere o modo para **Model training** (ou clique na aba **Model training** no canto superior esquerdo ao lado do logotipo do MLflow).
3. Clique em **Experiments** na barra lateral para ver o experimento `aula19_model_registry`. Vá em **Model Registry** para visualizar o modelo registrado `ModeloClassificacao` com sua versão (`Version 1`,`Version 2`) e o alias `@challenger` atribuído à versão 1!

### 3. Executando o Quality Gate e Promovendo o Modelo para `@champion`

Execute o script de avaliação automatizada (simulando a etapa do pipeline de CI/CD):

```bash
python -m src.evaluate_and_promote
```

**O que observar**:
- O script lê as métricas cadastradas no Registry, descobre que a `Version 2` (Random Forest) possui maior F1-score e move o alias `@champion` para a `Version 2`.
- Atualize a página no navegador em [http://localhost:5000](http://localhost:5000) (na aba **Model Registry** $\rightarrow$ `ModeloClassificacao`) para visualizar o alias `@champion` na versão 2.

### 4. Testando a API de Inferência e o Live Reload

Com a API rodando no Docker (ou localmente na porta 8000), execute o cliente de testes:

```bash
python -m src.test_client
```

**Saída esperada**:
```text
ℹ️ INFORMAÇÕES DO MODELO ATIVO NO REGISTRY:
   • Modelo: ModeloClassificacao
   • Alias: @champion
   • Versão do Registro: v2
   • Tipo de Algoritmo: RandomForestClassifier
   • F1-Score de Validação: 1.0000

🔮 TESTANDO INFERÊNCIAS:
Amostra #1: Entrada=[5.1, 3.5, 1.4, 0.2] -> Predição='setosa'
   ↳ Modelo Responsável: v2 (RandomForestClassifier) | Latência: 4.12 ms
```

---

## 💬 Perguntas para Discutir no Encontro

1. **Por que conectar a execução do script `train_and_register.py` diretamente à URL `http://localhost:5000` permite que o experimento apareça imediatamente na interface gráfica do MLflow?**
2. **Qual é a diferença entre registrar um modelo no MLflow Tracking (experimento) e registrá-lo no MLflow Model Registry?**
3. **Como o uso do alias dinâmico `@champion` em `models:/ModeloClassificacao@champion` permite atualizar o modelo servido pela API sem alterar nenhuma linha de código da aplicação?**
4. **Em uma interface MLflow 3.x, como você navega entre a visão de experimentos de treinamento (Model Training) e a gestão de Modelos Registrados (Models)?**

---

## ⚠️ Solução de Problemas

| Sintoma | Causa provável / Solução |
|---|---|
| Experimento/Modelo não aparece em `http://localhost:5000` | Você rodou o treino enquanto o servidor Docker estava desligado. Certifique-se de que o container `mlflow-registry-server` está rodando antes de executar `python -m src.train_and_register`. |
| Interface do MLflow mostra tela inicial ("Welcome") | Na barra lateral esquerda ou topo, selecione a aba **Model training** e clique em **Experiments** ou **Models**. |
| `models:/ModeloClassificacao@champion` não encontrado | Certifique-se de ter executado tanto `train_and_register.py` quanto `evaluate_and_promote.py`. |

---

📖 **Material Teórico da Aula**: veja o [README do Monitor](../README.md) para aprofundar os conceitos de linhagem em 5 dimensões, governança, suporte a LLMs e matriz comparativa de registradores.
