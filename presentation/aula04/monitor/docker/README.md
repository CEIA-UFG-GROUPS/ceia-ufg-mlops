# Prática em Docker

## 📝 Dockerfile

Um Dockerfile é um arquivo de texto que descreve como uma imagem Docker será construída. Ele é geralmente montado com referência a uma pasta local que contém os arquivos da aplicação.

Dockerfile:

```dockerfile
# Define uma imagem base para iniciar o build
FROM python:3.12.4 

# Define uma pasta interna na imagem na qual vamos trabalhar a partir dessa linha
WORKDIR /app

# Copia o arquivo requirements.txt para dentro da pasta /app (onde estamos trabalhando) 
COPY requirements.txt . 

# Instala dependências do sistema
RUN pip install --no-cache-dir -r requirements.txt 

# Copia todo o restante dos arquivos da aplicação para a pasta /app
COPY . . 

# Define comando que será executado quando o container for iniciado
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"] 
```

## ⚙️ Construindo uma Imagem (Build)

Após criar seu Dockerfile, você pode construir a imagem Docker usando o comando `docker build`:

```bash
docker build -f <DOCKERFILE_PATH> -t <CONTAINER_NAME> .
```

  * `<DOCKERFILE_PATH>`: Caminho para o seu Dockerfile (ex: `Dockerfile`).
  * `<CONTAINER_NAME>`: Um nome para a sua imagem (ex: `minha-app-docker`). Opcionalmente, pode-se adicionar uma tag, como `minha-app-docker:v1.0`.
  * `.`: Indica o contexto de build, geralmente o diretório atual onde o Dockerfile está localizado.

Se você estiver no mesmo diretório do Dockerfile, o comando pode ser simplificado para:

```bash
docker build -t fastapi-app .
```

Assim você acaba de criar uma imagem Docker chamada `fastapi-app` baseada nas instruções do seu Dockerfile presente em [`presentation/aula04/monitor/docker`](./Dockerfile).

## 🚀 Executando um Container (Run)

Uma vez que a imagem é construída, o container pode ser executado com base nela. O comando `docker run` permite iniciar um container e pode incluir parâmetros específicos que diferenciam containers criados a partir da mesma imagem.

Para executar um container e mapear portas, utilize:

```bash
docker run -p <OUT_PORT>:<IN_PORT> -it <CONTAINER_NAME>
```


  * `<OUT_PORT>`: A porta no seu host (máquina local) que você deseja expor.
  * `<IN_PORT>`: A porta interna no container onde sua aplicação está rodando.
  * `-it`: Combinação de `-i` (modo interativo) e `-t` (aloca um pseudo-TTY), que permite interagir com o container.
  * `<CONTAINER_NAME>`: O nome da imagem que você construiu.


Se sua aplicação no container roda na porta 8000, e você quer acessá-la pela porta 8000 do seu host:

```bash
docker run -p 8000:8000 -it fastapi-app
```

A aplicação FastAPI estará acessível em `http://localhost:8000`.

### Resumindo Etapas:

1.  **Crie um diretório para o seu projeto:**

    ```bash
    mkdir docker-hello-world
    cd docker-hello-world
    ```

2.  **Crie um arquivo Python com fastapi (`app.py`):**

    ```python
    from fastapi import FastAPI
    import logging
    import os
    from logging.handlers import RotatingFileHandler
    from fastapi.responses import JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from datetime import datetime
    import uvicorn

    app = FastAPI()

    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    log_file_path = os.path.join(log_directory, "app.log")

    logger = logging.getLogger("uvicorn.access")

    handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=2)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/", response_class=JSONResponse)
    async def read_root():
        logger.info("Rota raiz '/' acessada")
        return {"message": "Hello, FastAPI!"}

    if __name__ == "__main__":
        uvicorn.run(app, host="0.0.0.0", port=8000)
    ```

3.  **Crie um Dockerfile no mesmo diretório:**

    ```dockerfile
    FROM python:3.12.4 

    WORKDIR /app

    COPY requirements.txt . 

    RUN pip install --no-cache-dir -r requirements.txt 

    COPY . . 

    CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"] 
    ```

      * `FROM python:3.12.4 `: Define a imagem base.
      * `WORKDIR /app`: Define o diretório de trabalho dentro do container.
      * `COPY requirements.txt .`: Copia o arquivo `requirements.txt` para o diretório de trabalho.
      * `RUN pip install --no-cache-dir -r requirements.txt `: Instala as dependências listadas em `requirements.txt`.
      * `COPY . .`: Copia o arquivos do seu host para o diretório `/app` no container.
      * `CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]`: Define o comando que será executado quando o container iniciar.

4.  **Construa a imagem Docker:**
    No terminal, dentro do diretório `docker-hello-world`:

    ```bash
    docker build -t fastapi-app .
    ```

    Este comando construirá uma imagem chamada `fastapi-app`.

5.  **Execute o container:**

    ```bash
    docker run fastapi-app
    ```

    Você deverá ver a saída: `Hello, FastAPI!` quando acessar `http://localhost:8000` no seu navegador.

**Parabéns\!** Você acabou de executar sua primeira aplicação Dockerizada\!

-----

## 📚 Referências

  * [Docker Guides](https://docs.docker.com/guides/)
  * [Developer Roadmap (Docker)](https://roadmap.sh/docker)
  * [Um breve histórico sobre virtualização](https://www2.decom.ufop.br/terralab/um-breve-historico-sobre-virtualizacao/)
  * [Dive into the decades-long history of container technology](https://www.techtarget.com/searchitoperations/feature/Dive-into-the-decades-long-history-of-container-technology)
  * [Análise de desempenho entre máquinas virtuais e containers utilizando o Docker](https://www.grupounibra.com/repositorio/REDES/2022/analise-de-desempenho-entre-maquinas-virtuais-e-containers-utilizando-o-docker3.pdf?)
  * [Containers e virtualização](https://www.targetso.com/artigos/containers-e-virtualizacao/)

-----
