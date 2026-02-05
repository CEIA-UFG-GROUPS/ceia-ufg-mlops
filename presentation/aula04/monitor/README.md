# Fundamentos de Docker, Compose e Networks

O objetivo deste material é apresentar o contexto histórico que levou ao surgimento do Docker, explicar como ele funciona internamente e demonstrar como utilizá-lo no dia a dia do desenvolvimento e da implantação de software.

## Contexto histórico e motivação

Antes do surgimento de containers, aplicações eram tradicionalmente executadas diretamente em servidores físicos ou virtuais. Em ambientes onde múltiplas aplicações coexistiam em um mesmo servidor, surgiam conflitos de dependências, incompatibilidades entre bibliotecas, divergências de versões de runtime e dificuldades na padronização dos ambientes de desenvolvimento, homologação e produção. Cada aplicação exigia configurações específicas, o que tornava o gerenciamento complexo e sujeito a falhas.

<img width="1040" height="588" alt="image" src="https://github.com/user-attachments/assets/abf0ae9e-7b72-412a-819c-623d6eb2cbcc" />

Para mitigar esses problemas, a virtualização ganhou força. Máquinas virtuais permitiram isolar aplicações em sistemas operacionais independentes, cada uma com seu próprio kernel, sistema de arquivos e conjunto de recursos. Embora eficaz em termos de isolamento, esse modelo apresentava custos elevados de consumo de memória, processamento e armazenamento, além de tempos de inicialização mais longos e maior sobrecarga operacional.

<img width="1046" height="591" alt="image" src="https://github.com/user-attachments/assets/15c2715c-0412-4431-bced-b586ddecaace" />


Com a evolução das tecnologias de kernel e isolamento de processos, surgiu o conceito moderno de containers. Diferente das máquinas virtuais, containers compartilham o kernel do sistema operacional hospedeiro, isolando apenas os processos, dependências e o sistema de arquivos necessários para a aplicação. Isso reduziu drasticamente o consumo de recursos e aumentou a eficiência na execução de workloads.

<img width="1044" height="587" alt="image" src="https://github.com/user-attachments/assets/45d48663-689d-49eb-8885-d1537229a9c4" />

O Docker emergiu como a plataforma que popularizou e padronizou o uso de containers, já que existem outras tecnologias que também trabalham com containers. Ele se consolidou como uma tecnologia open source amplamente adotada, com forte comunidade, integração com provedores de nuvem e um ecossistema robusto para distribuição e execução de aplicações em ambientes isolados .

## Conceito de containers e papel do Docker

Containers podem ser entendidos como unidades leves e portáteis que empacotam uma aplicação junto com todas as suas dependências, bibliotecas e configurações necessárias para execução. Ao compartilhar o kernel do sistema operacional, eles eliminam a necessidade de replicar recursos completos de um sistema operacional, como ocorre em máquinas virtuais, que precisam replicar interface gráfica, ferramentos de entrada e saída, todo o esquema de pastas e gerenciamento de processos próprios.

O Docker atua como uma plataforma para criar, distribuir e executar containers. Ele fornece ferramentas para empacotar aplicações em imagens, instanciar containers a partir dessas imagens e gerenciar o ciclo de vida dessas instâncias. Sua ampla adoção em ambientes de cloud, como Google Cloud Run e AWS Fargate, reforça seu papel como padrão de mercado para empacotamento e implantação de software moderno.

## Instalação do Docker

Você pode instalar o docker seguindo esse tutorial: 

[Instalando Docker](https://docs.docker.com/desktop/?_gl=1*x9vebn*_gcl_au*MTM5MTcxMjgzLjE3Njg4MzgzNDQ.*_ga*MjkzNTgzNjAzLjE3NjM2ODI3MjI.*_ga_XJWPQMJYHQ*czE3NzAzMjI2MzMkbzEwJGcxJHQxNzcwMzIyNjUxJGo0MiRsMCRoMA..)

## Imagens Docker e containers

Um container Docker sempre é criado a partir de uma **imagem**. A imagem funciona como um modelo imutável que descreve tudo o que é necessário para executar uma aplicação, incluindo sistema de arquivos, dependências, variáveis de ambiente e comandos de inicialização. É importante compreender que uma imagem não é um container em execução; ela representa apenas a definição estática do ambiente. Podemos pensar nela como um instalador do ambiente no qual é possível rodar a aplicação que ela propõe. 

As imagens podem ser listadas localmente utilizando o comando:

```bash
docker images
```

Elas podem ser obtidas a partir de repositórios públicos ou privados, como o [Docker Hub](https://hub.docker.com/), ou construídas localmente a partir de um arquivo de configuração chamado **Dockerfile**.

## Dockerfile e processo de build

O Dockerfile é um arquivo declarativo que descreve passo a passo como uma imagem deve ser construída. Podemos pensar nele como uma "receita" que diz como a imagem deve ser constrída. Ele define a imagem base, copia arquivos da aplicação, instala dependências, configura variáveis de ambiente e especifica o comando que será executado quando o container for iniciado .

Exemplo de Dockerfile:
```dockerfile
# Define uma imagem base para iniciar o build
FROM python:3.12.4 

# Define uma variável de ambiente
ENV PYTHONDONTWRITEBYTECODE=1

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

O processo de criação de uma imagem a partir de um Dockerfile é realizado com o comando:

```bash
docker build -f <DOCKERFILE> -t <CONTAINER_NAME> .
```

Esse comando instrui o Docker a ler o Dockerfile, executar cada instrução em sequência e gerar uma imagem final nomeada conforme especificado.

## Execução de containers

Após a criação da imagem, o próximo passo é instanciar um container em execução. Esse processo transforma a definição estática da imagem em um processo ativo no sistema operacional. O comando `docker run` permite iniciar containers com parâmetros específicos, como mapeamento de portas, volumes e modo interativo .

Um exemplo comum de execução é:

```bash
docker run -p <OUT_PORT>:<IN_PORT> -it <CONTAINER_NAME>
```

Esse comando associa uma porta externa da máquina hospedeira a uma porta interna do container, permitindo o acesso à aplicação a partir do ambiente externo.

Containers operam em um modelo de rede isolado, no qual cada instância possui sua própria interface virtual. O Docker permite expor serviços para fora do container por meio do mapeamento de portas, facilitando a comunicação entre aplicações e usuários externos. Esse mecanismo é essencial para executar servidores web, APIs e serviços distribuídos. Por esse motivo precisamos,muitas vezes, expor uma porta com a flag "-p" que mapeia qual porta externa <OUT_PORT> será linkada à porta interna do conteiner <IN_PORT>.

## Fluxo conceitual do Docker

O fluxo de trabalho no Docker segue uma sequência lógica que começa com a definição do Dockerfile, passa pela criação da imagem e culmina na execução do container. Esse modelo permite reprodutibilidade, portabilidade e padronização de ambientes, tornando o processo de desenvolvimento e implantação mais previsível e escalável .

<img width="1048" height="583" alt="image" src="https://github.com/user-attachments/assets/18ced274-c7a5-4535-96dd-a05aff681706" />

## Persistência de dados com volumes

Por padrão, os dados gerados dentro de um container são efêmeros e podem ser perdidos quando ele é removido. Para resolver esse problema, o Docker oferece o conceito de volumes, que permitem mapear diretórios do sistema hospedeiro para dentro do container. Dessa forma, arquivos e dados persistem independentemente do ciclo de vida da instância.

O comando típico para utilização de volumes é:

```bash
docker run -v <out_path>:<in_path> -it <CONTAINER_NAME>
```

Esse recurso é fundamental para bancos de dados, logs, arquivos de configuração e qualquer cenário que exija persistência.

Podemos pensar em um volume como uma pasta compartilhada entre o computador hospedeiro e o contaier. Alterações nessa pasta feitas no hospedeiro vão afetar a pasta interna do container e o contrário também ocorre. Por isso a existência da flag "-v" que define um uma pasta externa no sistema <out_path> que será linkada auma pasta interna do container <in_path>.

## Introdução ao Docker Compose

Docker Compose é uma ferramenta projetada para definir e executar aplicações compostas por múltiplos containers de forma declarativa, utilizando um único arquivo de configuração em formato YAML. Enquanto o uso tradicional do Docker envolve a execução manual de vários comandos `docker run` para cada serviço, o Compose centraliza toda a definição da arquitetura da aplicação em um único ponto, permitindo que desenvolvedores descrevam serviços, redes, volumes e dependências de maneira estruturada e reproduzível.

O Compose se tornou especialmente relevante em cenários onde uma aplicação depende de múltiplos componentes, como servidores web, bancos de dados, sistemas de cache e filas de mensagens. Em vez de gerenciar cada container individualmente, o Docker Compose permite orquestrar todo o ecossistema com um único comando, garantindo consistência entre ambientes de desenvolvimento, teste e produção.

Exemplo de um arquivo docker-compose.yaml
```yaml
services:
  # Serviço do frontend (aplicação web)
  front:
    # Configuração de build da imagem Docker
    build:
      # Diretório base onde está o Dockerfile do front-end
      context: web
      # Nome do Dockerfile usado para build
      dockerfile: Dockerfile
      # Argumentos passados para o Dockerfile durante o build
      # Podem ser acessados via ARG no Dockerfile
      args:
        - PROJECT_NAME=${PROJECT_NAME}
        - VITE_CHAT_URL=${VITE_CHAT_URL}
        - VITE_APP_MODE=${VITE_APP_MODE}
    # Nome fixo do container gerado
    container_name: ${PROJECT_NAME}-front
    # Arquivo contendo variáveis de ambiente globais
    env_file: .env
    # Mapeamento de portas entre host e container
    ports:
      - ${FRONT_PORT}:4173
    # Rede Docker compartilhada entre os serviços
    networks:
      - tron-network


  # Serviço do backend (API / servidor)
  backend:
    # Configuração de build da imagem Docker
    build:
      # Diretório base do backend
      context: server
      # Dockerfile usado para construir o backend
      dockerfile: Dockerfile
    # Nome fixo do container backend
    container_name: ${PROJECT_NAME}-extension-backend

    # Variáveis de ambiente injetadas dentro do container
    environment:
      - DATABASE_URL=postgresql://secret:password@${PROJECT_NAME}-postgres:5432/tron_db
    # Volumes persistentes e sincronização de código
    volumes:
      - ./server/app/cache:/cache/
      - ./server/app:/app/
      - ./logs:/logs/
    # Porta externa → porta interna do backend
    ports:
      - ${SERVER_PORT}:8000
    # Rede compartilhada
    networks:
      - tron-network
    # Define dependências para garantir ordem de inicialização
    depends_on:
      - postgres


  # Serviço do banco PostgreSQL
  postgres:
    # Imagem oficial do PostgreSQL (versão Alpine, mais leve)
    image: postgres:14-alpine
    # Define plataforma para compatibilidade multi-arch
    platform: ${PLATFORM}
    # Nome fixo do container PostgreSQL
    container_name: ${PROJECT_NAME}-postgres
    # Variáveis de ambiente internas do banco
    environment:
      - POSTGRES_PASSWORD=password
      - POSTGRES_USER=user
      - POSTGRES_DB=db_name
      - PGDATA=/var/lib/postgresql/data/pgdata
      - PG_PORT_5432=${PG_PORT_5432}
    # Volume persistente para dados do banco
    volumes:
      - postgres_data:/var/lib/postgresql/data
    # Porta externa → porta interna padrão do PostgreSQL
    ports:
      - ${PG_PORT_5432}:5432
    # Rede compartilhada
    networks:
      - tron-network

# Definição dos volumes persistentes
volumes:
  postgres_data:

# Definição da rede compartilhada entre os containers
networks:
  tron-network:
    driver: bridge
    # Nome customizado da rede baseado no projeto
    name: ${PROJECT_NAME}-tron-network
```

Uma das grandes vantagens do uso do compose é que, além dapossibilidade de levantar vários containers de uma vez, é possível definir parâmetros para rodar containers sem a necessidade de colocá-los sempre em flags do `docker run`. 

## Arquitetura conceitual do Docker Compose

Docker Compose opera com base no conceito de infraestrutura como código. O arquivo `compose.yaml` (ou `docker-compose.yml` em versões mais antigas) funciona como uma especificação declarativa da aplicação, descrevendo como cada serviço deve ser construído, configurado e conectado aos demais. Essa abordagem reduz a complexidade operacional, pois toda a configuração fica versionada junto ao código-fonte da aplicação.

Ao executar o comando `docker compose up`, o Compose analisa o arquivo de configuração, cria redes, provisiona volumes, constrói imagens se necessário e inicializa todos os containers na ordem correta, respeitando dependências e parâmetros definidos.

Esse comando deve inicializar os serviços,quando executado na mesma pasta com o arquivo docker-compose.yaml, executando todos os serviços
```bash
docker compose up --build
```

## Diferença entre Dockerfile e Compose

Embora Dockerfile e Compose sejam frequentemente utilizados em conjunto, eles possuem propósitos distintos. O Dockerfile descreve como uma imagem deve ser construída, especificando os passos para empacotar uma aplicação em um container. Já o Compose define como múltiplos containers devem ser executados e orquestrados em conjunto, muitas vezes referenciando imagens criadas por Dockerfiles.

Em projetos reais, é comum que cada serviço possua seu próprio Dockerfile, enquanto o Compose atua como o “maestro” responsável por coordenar a execução integrada de todos os componentes.

## Gerenciamento de redes no Docker Compose

O Docker Compose oferece suporte nativo à criação e ao gerenciamento de redes virtuais. Cada projeto Compose cria, por padrão, uma rede isolada, permitindo que os serviços se comuniquem entre si por meio de seus nomes lógicos, sem a necessidade de configuração manual de endereços IP.

Esse modelo favorece a modularidade e a segurança, pois restringe a exposição de serviços apenas ao que for explicitamente definido. Redes personalizadas podem ser configuradas para simular arquiteturas mais complexas, como separação entre camadas de frontend, backend e banco de dados.

## Evolução do Docker Compose e Compose V2

Originalmente distribuído como uma ferramenta independente chamada `docker-compose`, o Compose evoluiu para ser integrado diretamente ao Docker CLI, passando a ser utilizado como `docker compose`. Essa mudança consolidou o Compose como um plugin oficial, trazendo melhorias de desempenho, compatibilidade e integração com outros recursos do Docker Engine

A versão moderna, conhecida como Compose V2, é implementada em Go e elimina dependências externas, tornando a ferramenta mais leve, rápida e compatível com diferentes sistemas operacionais.

## Referências

