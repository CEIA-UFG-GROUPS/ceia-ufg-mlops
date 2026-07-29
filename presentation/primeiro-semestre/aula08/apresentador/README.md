ga# Introdução à Computação em Nuvem e Instâncias — Guia do Apresentador

Este documento organiza a progressão da aula. O objetivo é levar o aluno do entendimento conceitual do que é a nuvem até a capacidade prática de instanciar, configurar e gerenciar financeiramente servidores remotos para projetos de engenharia de dados e MLOps.

---

## 1. Motivação (~5 min)

### 1.1 A Nuvem como Habilitadora de Escala

Modelos de Machine Learning e grandes volumes de dados exigem hardware que um notebook pessoal não consegue fornecer.

- **Vantagem principal:** O modelo **Pay-As-You-Go** (pague pelo que usar) transforma despesa de capital (comprar servidores) em despesa operacional (alugar por hora).

> 💬 **Pergunta para a turma:** Alguém aqui já tentou treinar um modelo pesado e o computador congelou ou ficou inutilizável por horas?

### 1.2 Por que não apenas usar interfaces gráficas (Console)?

- Interfaces web mudam constantemente.
- Clicar em botões não é escalável nem reprodutível.
- **Contexto MLOps:** A infraestrutura deve ser tratada como código (CLI, Terraform) para garantir padronização e automação.

---

## 2. O Paradigma da Computação em Nuvem (~15 min)

### 2.1 Modelos de Serviço (IaaS, PaaS, SaaS)

Explicar a diferença: **O nível de controle vs. o nível de gerenciamento exigido.**

- **IaaS (Infraestrutura):** Você gerencia o SO e os dados. Essencial para controle fino de drivers de GPU em ML.
- **PaaS (Plataforma):** Foco apenas no código (ex: Google App Engine, Heroku).
- **SaaS (Software):** Produto final (ex: Gmail).

### 2.2 Regiões e Zonas de Disponibilidade

**Conceitos a cobrir:**

- **Região:** Área geográfica isolada (impacta latência e custo).
- **Zona:** Data centers físicos separados dentro da mesma região (impacta tolerância a falhas).

**Exemplo prático:**

> Se a zona `us-east1-b` ficar indisponível, seu banco de dados na `us-east1-c` continua operando.

---

## 3. Máquinas Virtuais e Armazenamento (~15 min)

### 3.1 Famílias de Instâncias

Explicar que os provedores agrupam hardware por caso de uso.

**Comparação rápida:**

- **Compute Optimized** (Foco em CPU) → Processamento em lote. (`c2`, `c2d`, `h3`)
- **Memory Optimized** (Foco em RAM) → Bancos em memória. (`m2`, `m3`)
- **Accelerated** (Foco em GPU) → Treinamento de Deep Learning. (`a2` com A100, `g2` com L4)

### 3.2 Tipos de Armazenamento em Nuvem

>  **Ponto crítico:** Armazenamento errado causa perda de dados!

| Tipo | Característica | Caso de Uso |
|---|---|---|
| **Persistent Disk** (PD) | Persistente, atrelado à VM | SO, Bancos de Dados |
| **Local SSD** | Volátil (apaga ao desligar) | Cache, Swap |
| **Cloud Storage** (GCS) | Virtualmente infinito, via API HTTP | Data Lakes, Checkpoints |

>  **Atenção para a turma:** Nunca salvem o resultado de um treino de 5 dias em um Local SSD.

---

## 4. Redes e Segurança Básica (~15 min)

### 4.1 Firewall Rules (Firewalls em Nuvem)

**Conceito-chave:** O servidor nasce bloqueado para o mundo. Você deve abrir portas específicas via Firewall Rules na VPC.

**Demonstrar lógica de regras:**

| Porta | Uso Comum | Regra Segura |
|---|---|---|
| `22` (SSH) | Acesso ao terminal | Apenas seu IP ou VPN |
| `80` / `443` | Tráfego Web | Aberto (`0.0.0.0/0`) |
| `8888` | Jupyter Notebook | Apenas seu IP via tunelamento |

>  **Ponto importante:** Explicar o perigo de abrir a porta 22 para `0.0.0.0/0` (ataques de bots nos primeiros minutos).

---

## 5. Gestão de Custos e Ciclo de Vida (~10 min)

### 5.1 Estados da Instância

**Explicar o faturamento:**

- **Running:** Paga CPU + RAM + Disco.
- **Stopped:** Paga apenas o Disco (Persistent Disk). A CPU para de ser cobrada.
- **Deleted (Terminated):** Destruição total. Verifique se o disco está marcado para ser deletado junto.

### 5.2 Modelos de Compra

- **On-Demand:** Preço fixo, máquina sua enquanto pagar.
- **Spot VMs:** Leilão de capacidade ociosa (até **60-91%** mais barato).

>  **Aviso importante:** Spot VMs no GCP podem ser interrompidas com aviso de apenas **30 segundos**. Salvem checkpoints do modelo frequentemente!

---

## 6. Prática: Interagindo via CLI (~20 min)

### 6.1 gcloud CLI Essencial

**Demonstração prática (Terminal):**

```bash
# Autenticação e configuração do projeto
gcloud auth login
gcloud config set project MEU_PROJETO_ID

# Listar VMs do Compute Engine rodando
gcloud compute instances list \
    --format="table(name, networkInterfaces[0].accessConfigs[0].natIP, status)"

# Parar uma máquina para não gerar custo no fim de semana
gcloud compute instances stop minha-instancia --zone=us-east1-b
```

### 6.2 Automação com Startup Script

Explicar que não precisamos entrar via SSH toda vez para instalar o Python. O SO pode fazer isso no primeiro boot via **Startup Script**.

**Demonstração do Script:**

```bash
#!/bin/bash
apt-get update -y
apt-get install -y python3-pip htop
pip3 install torch pandas
```

**Como associar ao criar a VM:**

```bash
gcloud compute instances create minha-vm \
    --zone=us-east1-b \
    --machine-type=e2-medium \
    --metadata-from-file startup-script=startup.sh
```

---

## 7. Boas Práticas (~10 min)

### 7.1 Governança e Segurança

- **Service Accounts:** Nunca coloque chaves JSON do GCP de texto puro dentro do código Python. Atribua uma Service Account diretamente à VM para que ela tenha permissão nativa de acessar GCS, BigQuery, etc.
- **Labels:** Marque os servidores com `projeto` e `dono` para saber quem gastou no fim do mês via Billing Reports.

### 7.2 Prevenção de Prejuízos

- Configurar **Budget Alerts** (Alertas de Orçamento) no [Cloud Billing](https://cloud.google.com/billing/docs/how-to/budgets) na casa dos $10 para evitar surpresas no cartão de crédito.
- Criar rotinas automáticas de desligamento com [Cloud Scheduler](https://cloud.google.com/scheduler) + Cloud Functions (ex: máquinas de Dev desligam às 20h).

---

## 8. Exercícios Sugeridos

1. **Configurar Credenciais:** Instalar e autenticar a `gcloud` CLI no terminal local (`gcloud auth login`).
2. **Subir uma Instância via CLI:** Criar uma VM básica da família `e2` usando um Startup Script para instalar dependências.
3. **Configurar Firewall:** Criar uma Firewall Rule que libere a porta 22 exclusivamente para o IP da sua casa.
4. **Validar Armazenamento:** Parar (Stop) a máquina, iniciá-la novamente (Start) e confirmar que o IP externo mudou, mas os dados no Persistent Disk continuam lá.
5. **Destruir tudo:** Deletar a instância para garantir que nenhum custo continuará rodando (`gcloud compute instances delete`).

