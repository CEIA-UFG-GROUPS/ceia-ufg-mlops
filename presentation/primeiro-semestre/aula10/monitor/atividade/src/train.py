import joblib
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# 1. Carregar dados (Exemplo Simples: Iris)
print("📦 Carregando dataset Iris (Banco de dados de flores)...")
iris = load_iris()
X, y = iris.data, iris.target

# 2. Dividir em Treino e Teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. Treinar Modelo
print("🤖 Treinando modelo de Inteligência Artificial (RandomForest)...")
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X_train, y_train)

# 4. Avaliar
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"✅ Modelo treinado! Acurácia: {accuracy:.2f} (Ele acerta {accuracy*100:.0f}% das vezes)")

# 5. Salvar Artefato (Modelo Treinado)
model_filename = "model.pkl"
print(f"💾 Salvando o modelo treinado no arquivo '{model_filename}' para ser usado na API...")
joblib.dump(model, model_filename)
