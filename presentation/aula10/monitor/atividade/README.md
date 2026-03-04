# 🛠️ Atividade Prática: MLOps "Hands-on"

Bem-vindo ao desafio prático de CI/CD para Machine Learning!
Nesta atividade, você não vai apenas ler sobre automação; você vai construir um pipeline real que treina, testa e empacota um modelo de Inteligência Artificial automaticamente.

## 🎯 O Cenário

Você é o Engenheiro de MLOps de uma startup. A equipe de Ciência de Dados criou um modelo incrível para classificar flores (clássico Iris Dataset), mas o código está solto e o processo de deploy é manual.
**Sua missão:** Profissionalizar este projeto criando uma esteira de Integração e Entrega Contínua (CI/CD).

---

## 📂 Estrutura do Projeto

**Para o CI/CD funcionar, renomeie a pasta "#.github" para ".github" (retire o "#")**

O projeto já está organizado da seguinte forma:

```bash
atividade/
├── .github/workflows/ci.yml  # O "Cérebro" da automação (GitHub Actions)
├── src/
│   ├── app.py                # API que serve o modelo (FastAPI)
│   └── train.py              # Script que cria e treina o modelo
├── tests/
│   └── test_app.py           # Testes automáticos para garantir qualidade
├── Dockerfile                # Receita para criar o container da aplicação
├── Makefile                  # Atalhos para comandos longos
└── requirements.txt          # Lista de bibliotecas necessárias
```

---

## 🚀 Passo a Passo da Atividade

### Passo 1: Preparando o Terreno (Setup Local)

Antes de automatizar, precisamos garantir que tudo funciona na sua máquina. Para isso, é uma **boa prática** utilizarmos um ambiente virtual (`venv`) para isolar as dependências do projeto.

1. **Crie e ative o ambiente virtual:**

    ```bash
    # Windows (PowerShell)
    python -m venv venv
    .\venv\Scripts\Activate
    # ⚠️ Se der erro de permissão no PowerShell, execute:
    # Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

    # Linux / Mac (Bash)
    python3 -m venv venv
    source venv/bin/activate
    ```

2. **Instale as dependências:**

    Agora, instale as bibliotecas dentro do ambiente virtual:

    ```bash
    pip install -r requirements.txt
    ```

3. **Treine o Modelo Localmente:**
    O código da API precisa de um modelo treinado (`model.pkl`). Vamos criá-lo:

    ```bash
    python src/train.py
    ```

    *Deverá aparecer na tela: "Acurácia do modelo: 1.00" (ou valor próximo) e o arquivo `model.pkl` será criado.*

4. **Teste a API:**
    Levante o servidor localmente para ver se está tudo certo:

    ```bash
    uvicorn src.app:app --reload
    ```

    Acesse no seu navegador: `http://localhost:8000`. Você deve ver a mensagem de boas-vindas.
    Acesse a documentação interativa: `http://localhost:8000/docs` e teste o endpoint `/predict`.

    *Para parar o servidor, pressione `CTRL+C` no terminal.*

### Passo 2: Garantindo a Qualidade (Testes)

MLOps exige confiança. Se o código quebrar, não podemos fazer deploy.
Execute os testes unitários que criamos para validar a API (**certifique-se de que o venv ainda está ativo**):

```bash
pytest tests/
```

*Se todos os testes passarem (ficarem verdes), seu código está robusto!*

### Passo 3: O Pipeline de Automação (CI/CD)

Agora vamos ver a mágica acontecer. O arquivo `.github/workflows/ci.yml` contém as instruções para o GitHub fazer tudo isso que você fez manualmente (instalar, treinar, testar) toda vez que você enviar código novo.

**O que você deve fazer:**

1. **Crie um Repositório no GitHub:** Crie um repositório vazio na sua conta pessoal.
2. **Envie o Código:**

    ```bash
    git init
    git add .
    git commit -m "Configurando pipeline MLOps inicial"
    git branch -M main
    git remote add origin <LINK_DO_SEU_REPOSITORIO>
    git push -u origin main
    ```

3. **Acompanhe a Action:**
    Vá até a aba **Actions** no seu repositório do GitHub. Você verá um fluxo de trabalho rodando. Clique nele para ver os detalhes.

    **O que o GitHub Actions fará por você:**
    * ✅ Baixar seu código.
    * ✅ Instalar Python e dependências.
    * ✅ Verificar se o código está bonito (Linting).
    * ✅ **Treinar o modelo do zero.**
    * ✅ **Rodar os testes automatizados.**
    * ✅ **Buildar a Imagem Docker.**

---

## 🐛 Experimente Quebrar o Pipeline

A melhor forma de aprender é vendo o CI te proteger de erros.

1. Abra o arquivo `src/app.py`.
2. Introduza um erro de sintaxe proposital (apague um parêntese, por exemplo) ou mude a lógica para que o teste falhe.
3. Faça o commit e push:

    ```bash
    git add .
    git commit -m "Introduzindo erro proposital"
    git push
    ```

4. Volte na aba **Actions** do GitHub. O pipeline vai falhar (ficar vermelho) ❌.
5. Corrija o erro e faça push novamente. O pipeline ficará verde ✅.

---

## 🐳 Passo Bônus: Rodando com Docker

Se você tem Docker instalado, pode rodar a aplicação exatamente como ela rodará no servidor de produção:

1. **Construir a Imagem:**

    ```bash
    docker build -t ml-app-ufg .
    ```

2. **Rodar o Container:**

    ```bash
    docker run -p 8000:8000 ml-app-ufg
    ```

    Acesse `http://localhost:8000` novamente. Agora sua IA está isolada em um container!

---

**Parabéns!** Você acabou de criar um ciclo completo de Engenharia de Machine Learning. 🚀
