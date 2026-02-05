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

```docker
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

## Fluxo conceitual do Docker

O fluxo de trabalho no Docker segue uma sequência lógica que começa com a definição do Dockerfile, passa pela criação da imagem e culmina na execução do container. Esse modelo permite reprodutibilidade, portabilidade e padronização de ambientes, tornando o processo de desenvolvimento e implantação mais previsível e escalável .

## Rede em containers

Containers operam em um modelo de rede isolado, no qual cada instância possui sua própria interface virtual. O Docker permite expor serviços para fora do container por meio do mapeamento de portas, facilitando a comunicação entre aplicações e usuários externos. Esse mecanismo é essencial para executar servidores web, APIs e serviços distribuídos .

## Persistência de dados com volumes

Por padrão, os dados gerados dentro de um container são efêmeros e podem ser perdidos quando ele é removido. Para resolver esse problema, o Docker oferece o conceito de volumes, que permitem mapear diretórios do sistema hospedeiro para dentro do container. Dessa forma, arquivos e dados persistem independentemente do ciclo de vida da instância .

O comando típico para utilização de volumes é:

```bash
docker run -v <out_path>:<in_path> -it <CONTAINER_NAME>
```

Esse recurso é fundamental para bancos de dados, logs, arquivos de configuração e qualquer cenário que exija persistência.

## Introdução ao Docker Compose

Docker Compose é uma ferramenta projetada para definir e executar aplicações compostas por múltiplos containers de forma declarativa, utilizando um único arquivo de configuração em formato YAML. Enquanto o uso tradicional do Docker envolve a execução manual de vários comandos `docker run` para cada serviço, o Compose centraliza toda a definição da arquitetura da aplicação em um único ponto, permitindo que desenvolvedores descrevam serviços, redes, volumes e dependências de maneira estruturada e reproduzível.

O Compose se tornou especialmente relevante em cenários onde uma aplicação depende de múltiplos componentes, como servidores web, bancos de dados, sistemas de cache e filas de mensagens. Em vez de gerenciar cada container individualmente, o Docker Compose permite orquestrar todo o ecossistema com um único comando, garantindo consistência entre ambientes de desenvolvimento, teste e produção.

## Arquitetura conceitual do Docker Compose

Docker Compose opera com base no conceito de infraestrutura como código. O arquivo `compose.yaml` (ou `docker-compose.yml` em versões mais antigas) funciona como uma especificação declarativa da aplicação, descrevendo como cada serviço deve ser construído, configurado e conectado aos demais. Essa abordagem reduz a complexidade operacional, pois toda a configuração fica versionada junto ao código-fonte da aplicação.

Ao executar o comando `docker compose up`, o Compose analisa o arquivo de configuração, cria redes, provisiona volumes, constrói imagens se necessário e inicializa todos os containers na ordem correta, respeitando dependências e parâmetros definidos.

## Estrutura de um arquivo Compose

O arquivo Compose segue a Compose Specification, que unificou versões anteriores do formato e hoje é o padrão oficial suportado pelo Docker CLI moderno. Nele, é possível definir serviços, redes, volumes, segredos e configurações avançadas de execução.

A seção de serviços representa o núcleo do Compose, onde cada container da aplicação é descrito. Cada serviço pode apontar para uma imagem existente ou para um Dockerfile local, definir portas expostas, variáveis de ambiente, volumes persistentes, políticas de reinicialização e limites de recursos. Além disso, o Compose permite configurar redes personalizadas para isolar ou integrar serviços de forma controlada.

## Diferença entre Dockerfile e Compose

Embora Dockerfile e Compose sejam frequentemente utilizados em conjunto, eles possuem propósitos distintos. O Dockerfile descreve como uma imagem deve ser construída, especificando os passos para empacotar uma aplicação em um container. Já o Compose define como múltiplos containers devem ser executados e orquestrados em conjunto, muitas vezes referenciando imagens criadas por Dockerfiles.

Em projetos reais, é comum que cada serviço possua seu próprio Dockerfile, enquanto o Compose atua como o “maestro” responsável por coordenar a execução integrada de todos os componentes.

## Orquestração de múltiplos serviços

Uma das maiores vantagens do Docker Compose é a capacidade de modelar aplicações distribuídas compostas por vários serviços interdependentes. Ele permite definir, por exemplo, um servidor backend, um banco de dados e um serviço de cache como partes de um mesmo sistema, conectados por uma rede interna isolada.

Além de facilitar a inicialização conjunta desses serviços, o Compose simplifica a configuração de variáveis de ambiente compartilhadas, o mapeamento de portas entre containers e a persistência de dados entre reinicializações. Isso reduz significativamente o esforço necessário para reproduzir ambientes completos em diferentes máquinas ou equipes.

## Gerenciamento de redes no Docker Compose

O Docker Compose oferece suporte nativo à criação e ao gerenciamento de redes virtuais. Cada projeto Compose cria, por padrão, uma rede isolada, permitindo que os serviços se comuniquem entre si por meio de seus nomes lógicos, sem a necessidade de configuração manual de endereços IP.

Esse modelo favorece a modularidade e a segurança, pois restringe a exposição de serviços apenas ao que for explicitamente definido. Redes personalizadas podem ser configuradas para simular arquiteturas mais complexas, como separação entre camadas de frontend, backend e banco de dados.

## Persistência de dados com volumes no Compose

Em aplicações reais, muitos serviços dependem de dados persistentes, como bancos de dados, logs e arquivos de configuração. O Docker Compose permite declarar volumes como objetos de alto nível, associando-os a serviços específicos para garantir que os dados sejam preservados mesmo quando containers são recriados.

Essa capacidade torna o Compose adequado para ambientes de desenvolvimento, testes automatizados e até cenários de produção em pequena escala, nos quais a persistência de dados é essencial para a integridade do sistema.

## Automatização de ambientes de desenvolvimento e teste

Docker Compose é amplamente utilizado para padronizar ambientes de desenvolvimento e integração contínua. Ao definir toda a pilha de serviços em um único arquivo, equipes podem clonar um repositório e levantar um ambiente funcional com um único comando, reduzindo o tempo de configuração e evitando discrepâncias entre máquinas.

Essa característica também o torna útil para pipelines de CI/CD, onde ambientes temporários podem ser criados e destruídos automaticamente para execução de testes isolados, garantindo reprodutibilidade e eficiência.

## Evolução do Docker Compose e Compose V2

Originalmente distribuído como uma ferramenta independente chamada `docker-compose`, o Compose evoluiu para ser integrado diretamente ao Docker CLI, passando a ser utilizado como `docker compose`. Essa mudança consolidou o Compose como um plugin oficial, trazendo melhorias de desempenho, compatibilidade e integração com outros recursos do Docker Engine

A versão moderna, conhecida como Compose V2, é implementada em Go e elimina dependências externas, tornando a ferramenta mais leve, rápida e compatível com diferentes sistemas operacionais.

## Casos de uso práticos do Docker Compose

Docker Compose é especialmente indicado para aplicações que exigem múltiplos serviços coordenados, como sistemas web completos, stacks de microserviços, ambientes de testes integrados e protótipos de arquiteturas distribuídas. Ele permite simular ambientes de produção localmente, facilitando o desenvolvimento e a depuração de sistemas complexos.

Além disso, Compose é frequentemente utilizado como ponto de entrada para arquiteturas mais avançadas, servindo como etapa inicial antes da migração para orquestradores mais robustos, como Kubernetes, mantendo uma curva de aprendizado acessível e uma experiência simplificada para desenvolvedores.

Se quiser, posso transformar essas seções em um complemento direto ao README anterior, mantendo coesão com o material principal do workshop.

## Referências

