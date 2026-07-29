# Guia de Execução do Docker Compose

Este documento fornece um passo a passo para executar a aplicação utilizando Docker Compose.

## Pré-requisitos
- Certifique-se de que o Docker e o Docker Compose estão instalados em sua máquina.
- Verifique se o Docker está em execução.

## Estrutura do Projeto
A estrutura do projeto é a seguinte:
```
.
├── docker-compose.yml
├── server/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
└── web/
    ├── app.py
    ├── Dockerfile
    └── requirements.txt
```

## Passo a Passo para Executar o Docker Compose
1. **Navegue até o diretório do projeto**:
   ```bash
   cd <...>/docker-compose
   ```
   Substitua `<...>` pelo caminho correto até o diretório `docker-compose`.

2. **Construa e inicie os containers**:
   ```bash
   docker-compose up --build
   ```
   Este comando irá construir as imagens e iniciar os containers definidos no arquivo `docker-compose.yml`.

3. **Acesse a aplicação**:
   - Após a execução do comando acima, você poderá acessar a aplicação através do navegador em `http://localhost:<PORTA>`, onde `<PORTA>` é a porta configurada no `docker-compose.yml`.

4. **Parar os containers**:
   - Para parar os containers em execução, pressione `CTRL + C` no terminal onde o Docker Compose está rodando ou execute:
   ```bash
   docker-compose down
   ```

## Considerações Finais
- Certifique-se de que todas as dependências estão corretamente listadas nos arquivos `requirements.txt`.
- Para mais informações sobre o Docker Compose, consulte a [documentação oficial](https://docs.docker.com/compose/).