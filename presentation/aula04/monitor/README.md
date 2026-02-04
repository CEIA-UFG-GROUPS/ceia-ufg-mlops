# Fundamentos de Docker — Material para Workshop

Este repositório contém um material introdutório e aprofundado sobre Docker, desenvolvido para servir como base teórica e prática em um workshop sobre containers, virtualização e empacotamento de aplicações. O objetivo é apresentar o contexto histórico que levou ao surgimento do Docker, explicar como ele funciona internamente e demonstrar como utilizá-lo no dia a dia do desenvolvimento e da implantação de software.

## Contexto histórico e motivação

Antes do surgimento de containers, aplicações eram tradicionalmente executadas diretamente em servidores físicos ou virtuais. Em ambientes onde múltiplas aplicações coexistiam em um mesmo servidor, surgiam conflitos de dependências, incompatibilidades entre bibliotecas, divergências de versões de runtime e dificuldades na padronização dos ambientes de desenvolvimento, homologação e produção. Cada aplicação exigia configurações específicas, o que tornava o gerenciamento complexo e sujeito a falhas .

Para mitigar esses problemas, a virtualização ganhou força. Máquinas virtuais permitiram isolar aplicações em sistemas operacionais independentes, cada uma com seu próprio kernel, sistema de arquivos e conjunto de recursos. Embora eficaz em termos de isolamento, esse modelo apresentava custos elevados de consumo de memória, processamento e armazenamento, além de tempos de inicialização mais longos e maior sobrecarga operacional .

Com a evolução das tecnologias de kernel e isolamento de processos, surgiu o conceito moderno de containers. Diferentemente das máquinas virtuais, containers compartilham o kernel do sistema operacional hospedeiro, isolando apenas os processos, dependências e o sistema de arquivos necessários para a aplicação. Isso reduziu drasticamente o consumo de recursos e aumentou a eficiência na execução de workloads .

O Docker emergiu como a plataforma que popularizou e padronizou o uso de containers. Ele se consolidou como uma tecnologia open source amplamente adotada, com forte comunidade, integração com provedores de nuvem e um ecossistema robusto para distribuição e execução de aplicações em ambientes isolados .

## Conceito de containers e papel do Docker

Containers podem ser entendidos como unidades leves e portáteis que empacotam uma aplicação junto com todas as suas dependências, bibliotecas e configurações necessárias para execução. Ao compartilhar o kernel do sistema operacional, eles eliminam a necessidade de replicar recursos completos de um sistema operacional, como ocorre em máquinas virtuais .

O Docker atua como uma plataforma para criar, distribuir e executar containers. Ele fornece ferramentas para empacotar aplicações em imagens, instanciar containers a partir dessas imagens e gerenciar o ciclo de vida dessas instâncias. Sua ampla adoção em ambientes de cloud, como Google Cloud Run e AWS Fargate, reforça seu papel como padrão de mercado para empacotamento e implantação de software moderno .

## Imagens Docker e containers

Um container Docker sempre é criado a partir de uma imagem. A imagem funciona como um modelo imutável que descreve tudo o que é necessário para executar uma aplicação, incluindo sistema de arquivos, dependências, variáveis de ambiente e comandos de inicialização. É importante compreender que uma imagem não é um container em execução; ela representa apenas a definição estática do ambiente .

As imagens podem ser listadas localmente utilizando o comando:

```bash
docker images
```

Elas podem ser obtidas a partir de repositórios públicos ou privados, como o Docker Hub, ou construídas localmente a partir de um arquivo de configuração chamado Dockerfile.

## Dockerfile e processo de build

O Dockerfile é um arquivo declarativo que descreve passo a passo como uma imagem deve ser construída. Ele define a imagem base, copia arquivos da aplicação, instala dependências, configura variáveis de ambiente e especifica o comando que será executado quando o container for iniciado .

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

## Objetivo do workshop

Este material foi elaborado para auxiliar participantes a compreenderem não apenas os comandos básicos do Docker, mas também os fundamentos conceituais que justificam sua existência e sua ampla adoção. A proposta do workshop é capacitar os participantes a utilizarem Docker de forma consciente, entendendo as diferenças entre virtualização tradicional e containers, dominando o fluxo de criação de imagens e aplicando boas práticas para execução de aplicações em ambientes isolados.

## Referências

