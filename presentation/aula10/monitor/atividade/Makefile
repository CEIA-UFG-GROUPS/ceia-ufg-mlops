install:
	pip install -r requirements.txt

test:
	pytest tests/

build-docker:
	docker build -t ml-app-ufg:latest .

# Roda tudo em sequência (Fluxo Completo)
all: install test build-docker