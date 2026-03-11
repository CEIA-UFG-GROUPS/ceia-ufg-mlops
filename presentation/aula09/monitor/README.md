# Material de Estudo: Introdução à Computação em Nuvem e Instâncias

Este guia foi desenvolvido para fornecer uma base técnica sólida sobre os conceitos fundamentais de Cloud Computing e o processo prático de criação e gerenciamento de servidores virtuais (instâncias). Para profissionais de dados e engenharia, dominar a nuvem é essencial para escalar modelos, processar grandes volumes de dados e garantir alta disponibilidade.

---

## 1. O Paradigma da Computação em Nuvem

Computação em nuvem é a entrega de serviços de computação (servidores, armazenamento, bancos de dados, redes, software) pela internet ("a nuvem"). Você paga apenas pelo que usa (modelo **Pay-As-You-Go**).

### 1.1 Modelos de Serviço (IaaS, PaaS, SaaS)

Entender o que você está alugando é o primeiro passo para arquitetar um sistema.

| Modelo | Descrição | O que você gerencia | Exemplo |
|---|---|---|---|
| **IaaS** (Infraestrutura) | Aluguel de servidores e redes puras | SO, Aplicação, Dados, Runtime | Google Compute Engine (GCE) |
| **PaaS** (Plataforma) | Ambiente pronto para rodar código | Aplicação e Dados | Google App Engine, Heroku |
| **SaaS** (Software) | Software pronto para o usuário final | Apenas seus dados/configurações | Gmail, Google Drive, Salesforce |

> [!TIP]
> Para projetos de MLOps e Engenharia de Dados que exigem controle fino sobre drivers de GPU e dependências de sistema, o modelo **IaaS** é o mais utilizado.

### 1.2 Regiões e Zonas de Disponibilidade (AZs)

A nuvem não é mágica; são data centers físicos espalhados pelo mundo.

| Conceito | Descrição | Impacto Prático |
|---|---|---|
| **Região** | Uma área geográfica (ex: `us-east1` na Carolina do Sul, `southamerica-east1` em SP) | Define a latência para seu usuário e o custo da infraestrutura. |
| **Zona de Disponibilidade** | Um ou mais data centers isolados dentro de uma Região (ex: `us-east1-b`) | Oferece redundância. Se a zona "b" cair, a "c" continua funcionando. |

---

## 2. Máquinas Virtuais (Instâncias) e Armazenamento

Instanciar um servidor significa criar uma Máquina Virtual (VM) no data center do provedor.

### 2.1 Famílias de Instâncias

Os provedores (GCP, AWS, Azure) agrupam os servidores por casos de uso. Escolher a família errada gera gargalos ou custos excessivos.

| Família | Otimização | Caso de Uso em Dados/ML | Exemplo (GCP) |
|---|---|---|---|
| **General Purpose** | Equilíbrio entre CPU, RAM e Rede | Servidores web, orquestradores (Airflow) | `e2`, `n2`, `n2d` |
| **Compute Optimized** | Foco em poder de processamento (CPU) | Treinamento de modelos simples, batch processing | `c2`, `c2d`, `h3` |
| **Memory Optimized** | Alta proporção de RAM por vCPU | Bancos de dados em memória, inferência pesada | `m2`, `m3` |
| **Accelerated (GPU)** | Equipadas com GPUs (NVIDIA) | Treinamento de Deep Learning e LLMs | `a2` (A100), `g2` (L4) |

### 2.2 Tipos de Armazenamento em Nuvem

| Tipo | O que é | Persistência | Uso Ideal |
|---|---|---|---|
| **Persistent Disk** (PD) | Disco rígido/SSD atrelado à instância | Mantém dados se a VM for parada | Sistema Operacional, Banco de Dados |
| **Local SSD** | Disco físico conectado direto no host | Apaga se a VM for parada | Cache temporário, Swap de alta velocidade |
| **Cloud Storage** (GCS) | Armazenamento virtualmente infinito via API HTTP | Altamente durável | Data Lakes, backups de modelos (`.pkl`, `.pt`) |

> [!CAUTION]
> **Impacto Crítico:** Nunca salve dados importantes (como o estado de um treinamento longo) em um Local SSD. Se a máquina for reiniciada pelo provedor, seus dados sumirão para sempre. Use Persistent Disk ou envie checkpoints para o Cloud Storage (GCS).

---

## 3. Redes e Segurança Básica (VPC e Firewall)

Antes de acessar sua instância via SSH (como visto no módulo anterior), ela precisa existir dentro de uma rede segura.

### 3.1 Firewall Rules (Firewalls em Nuvem)

As Firewall Rules do GCP atuam como um firewall virtual dentro da VPC, controlando o tráfego de entrada (**Ingress**) e saída (**Egress**).

| Porta | Protocolo | Uso Comum | Regra de Ouro |
|---|---|---|---|
| `22` | TCP | SSH | Restrinja apenas para o seu IP pessoal ou VPN. |
| `80` | TCP | HTTP | Aberto para o mundo (`0.0.0.0/0`) se for um site público. |
| `443` | TCP | HTTPS | Aberto para tráfego web seguro. |
| `8888` | TCP | Jupyter Notebook | Restringir via IP ou usar tunelamento SSH. |

> [!IMPORTANT]
> A regra de origem `0.0.0.0/0` significa "qualquer lugar da internet". Deixar a porta 22 aberta para `0.0.0.0/0` atrai milhares de bots de força bruta nos primeiros minutos de vida do seu servidor.

---

## 4. O Ciclo de Vida e Gestão de Custos

O maior risco da nuvem não é técnico, é financeiro. Entender o ciclo de vida da instância evita surpresas no cartão de crédito.

### 4.1 Estados da Instância

| Estado | CPU/RAM sendo cobrada? | Disco sendo cobrado? | Ação |
|---|---|---|---|
| **Running** | Sim | Sim | A máquina está ligada e processando. |
| **Stopped** | Não | Sim | Máquina desligada. Você paga apenas pelo espaço ocupado no disco. |
| **Terminated** | Não | Não | Instância destruída. (Cuidado: certifique-se de que o disco esteja configurado para ser deletado junto). |

### 4.2 Modelos de Cobrança (On-Demand vs Spot VMs)

```bash
# Custos aproximados para uma GPU (Exemplo)
On-Demand (Preço Fixo):                ~$3.00 / hora
Spot VM (Leilão de capacidade ociosa): ~$0.90 / hora (Até 60-91% de desconto)
```

> [!WARNING]
> **Spot VMs** no GCP podem ser interrompidas pelo provedor com um aviso de apenas **30 segundos**. Use apenas para cargas de trabalho tolerantes a falhas, scripts stateless ou treinamentos de ML que salvam checkpoints (pesos) frequentemente.

---

## 5. Prática: Interagindo com a Nuvem via CLI

A interface web (Console) é boa para aprendizado, mas na prática, engenheiros usam o terminal (CLI) ou ferramentas de Infraestrutura como Código (Terraform).

### 5.1 gcloud CLI Essencial

```bash
# Autenticar e configurar o projeto padrão
gcloud auth login
gcloud config set project MEU_PROJETO_ID

# Listar instâncias do Compute Engine ativas e extrair seus IPs externos
gcloud compute instances list \
    --format="table(name, networkInterfaces[0].accessConfigs[0].natIP, status)"

# Parar e Iniciar instâncias rapidamente
gcloud compute instances stop minha-instancia --zone=us-east1-b
gcloud compute instances start minha-instancia --zone=us-east1-b
```

### 5.2 Automação de Inicialização (Startup Script)

Você pode passar um **Startup Script** para a VM rodar automaticamente assim que ela ligar pela primeira vez. Isso evita ter que instalar dependências manualmente via SSH.

```bash
#!/bin/bash
# Exemplo de Startup Script para instanciar um ambiente ML
apt-get update -y
apt-get install -y python3-pip git htop
pip3 install torch torchvision pandas scikit-learn

# Baixar o repositório do projeto
git clone https://github.com/sua-empresa/modelo.git /home/ubuntu/projeto
chown -R ubuntu:ubuntu /home/ubuntu/projeto
```

> Para associar o script ao criar a VM via CLI:
> ```bash
> gcloud compute instances create minha-vm \
>     --metadata-from-file startup-script=startup.sh
> ```

---

## 6. Boas Práticas para Instâncias em Produção

### 6.1 Segurança e Governança

- **Use Service Accounts:** Em vez de colocar chaves JSON do GCP dentro do código `.py` no servidor, anexe uma Service Account à VM. Assim ela tem permissão nativa para acessar o Cloud Storage (GCS), BigQuery, etc.
- **Labels são obrigatórias:** Sempre adicione labels como `projeto: previsao-vendas` e `ambiente: dev`. Isso ajuda a descobrir de onde está vindo o custo no fim do mês via Billing Reports.

### 6.2 Monitoramento e Custo

- **Crie Alertas de Orçamento (Budget Alerts):** No [Cloud Billing](https://cloud.google.com/billing/docs/how-to/budgets), configure para receber um email se sua conta passar de $50 no mês.
- **Desligamento Automático:** Para ambientes de desenvolvimento, crie rotinas com [Cloud Scheduler](https://cloud.google.com/scheduler) + Cloud Functions que desligam as instâncias todos os dias às 20h.

---

## 7. Referências e Recursos

### Documentação Oficial

- [Google Compute Engine (GCE)](https://cloud.google.com/compute/docs) — Documentação principal das VMs no GCP.
- [Visão geral do Google Cloud](https://cloud.google.com/docs/overview) — Introdução geral à plataforma GCP.
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference) — Referência completa dos comandos da CLI.

### Ferramentas Úteis

- [Vantage](https://www.vantage.sh/) — Plataforma de gerenciamento e visibilidade de custos em nuvem (multi-cloud).
- [Google Cloud Monitoring](https://cloud.google.com/monitoring/docs) — Monitoramento de métricas, logs e configuração de alertas no GCP.
- [GCP Pricing Calculator](https://cloud.google.com/products/calculator) — Estimativa de custos antes de provisionar recursos.
- [Terraform Registry](https://registry.terraform.io/) — Para avançar de CLI para Infraestrutura como Código.