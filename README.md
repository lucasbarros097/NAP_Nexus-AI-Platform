<div align="center">

# ⚡ NAP — Nexus AI Platform

**Plataforma de Engenharia de Software de Alta Performance Potencializada por Inteligência Artificial Multiagente**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0052CC?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=nextdotjs)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker)](https://docker.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-AI-10B981?style=for-the-badge)](https://openrouter.ai)

*Orquestração de agentes autônomos para arquitetura, codificação, documentação e revisão em um fluxo contínuo.*

</div>

---

## 📋 Índice
1. [Visão Geral e Filosofia do Projeto](#-visão-geral-e-filosofia-do-projeto)
2. [Arquitetura de Sistemas Detalhada](#-arquitetura-de-sistemas-detalhada)
3. [Ecossistema Multiagente (Especializações)](#-ecossistema-multiagente-especializações)
4. [Stack Tecnológica e Justificativas](#-stack-tecnológica-e-justificativas)
5. [Guia de Instalação e Configuração Completo](#-guia-de-instalação-e-configuração-completo)
   - [Pré-requisitos e Verificação](#pré-requisitos-e-verificação)
   - [Configuração de Variáveis de Ambiente (.env)](#configuração-de-variáveis-de-ambiente-env)
   - [Deploy com Docker Compose](#deploy-com-docker-compose)
   - [Configuração para Desenvolvimento Local (Bare-Metal)](#configuração-para-desenvolvimento-local-bare-metal)
6. [Manual de Uso da CLI / TUI Hacker](#-manual-de-uso-da-cli--tui-hacker)
7. [Documentação da API e Endpoints Principais](#-documentação-da-api-e-endpoints-principais)
8. [Segurança, Governança e Human-in-the-Loop](#-segurança-governança-e-human-in-the-loop)
9. [Guia de Contribuição e Engenharia de Agentes](#-guia-de-contribuição-e-engenharia-de-agentes)
10. [Roadmap e Visão de Futuro](#-roadmap-e-visão-de-futuro)

---

## 🌟 Visão Geral e Filosofia do Projeto

A **NAP (Nexus AI Platform)** não é apenas mais um gerador de código isolado ou um assistente de chat simples. Ela foi concebida como um **ecossistema de engenharia de software autônomo e semi-autônomo**, projetado para atuar como uma equipe inteira de desenvolvimento de software dentro de uma única esteira de produção.

### O Problema Atual
No desenvolvimento tradicional, engenheiros gastam mais de 60% do seu tempo em tarefas acessórias: alternar contextos, escrever documentações repetitivas, configurar ambientes Docker, corrigir regressões de testes ou revisar sintaxes de código. Ferramentas como Copilot auxiliam em autocompletar linhas, mas falham em compreender a **visão macro** de uma arquitetura de microsserviços ou o impacto de uma alteração no banco de dados sobre o front-end.

### A Solução NAP
A NAP resolve o problema de contexto macro ao implementar um **Orquestrador Central (Architect)** baseado em grafos de tarefas (DAG). O desenvolvedor insere um requisito de alto nível em linguagem natural (ex: *"Preciso de um sistema de autenticação JWT com controle de acesso RBAC, persistido no Postgres e com tela de login responsiva no Next.js"*). O Orquestrador analisa a demanda, gera documentos de decisão arquitetural (ADRs), divide o épico em tarefas atômicas e distribui essas tarefas para agentes de IA hiper-especializados que executam o trabalho de forma paralela e segura.

---

## 🏗️ Arquitetura de Sistemas Detalhada

A topologia da plataforma é distribuída de forma a isolar completamente a interface do usuário da lógica complexa de processamento de contexto de IA. Abaixo está a representação estrutural de comunicação síncrona e assíncrona do sistema:

```mermaid
graph TD
    %% Estilos Globais
    style User fill:#2d3748,stroke:#4a5568,stroke-width:2px,color:#fff
    style API fill:#1a365d,stroke:#2b6cb0,stroke-width:2px,color:#fff
    style Orchestrator fill:#2c5282,stroke:#4299e1,stroke-width:2px,color:#fff
    style OpenRouter fill:#234e52,stroke:#319795,stroke-width:2px,color:#fff

    User((👤 Operador / Engenheiro))
    
    subgraph Camada de Apresentação (UI/UX)
        Browser[🖥️ Painel Web - Next.js 14<br>Porta :3000 / SSR / Tailwind]
        Terminal[⌨️ CLI / TUI Hacker<br>Rich / prompt-toolkit]
    end

    User -->|Interage via Web| Browser
    User -->|Interage via Terminal| Terminal

    subgraph Núcleo de Processamento (Core API)
        API[🚀 Backend FastAPI<br>Porta :8000 / Asyncio / Router]
        Browser <-->|HTTP REST / WebSockets| API
        Terminal <-->|Chamadas REST nativas| API
    end

    subgraph Inteligência e Orquestração (AI Core)
        Orchestrator[🧠 Orquestrador Central<br>Decomposição em DAG / Graph Theory]
        MCP[🛠️ Ferramentas MCP / SDK<br>Acesso ao FileSystem, Git e Docker]
        
        API -->|Instancia Sessão| Orchestrator
        Orchestrator <-->|Executa Comandos| MCP
    end

    subgraph Gateway de Inferência de Modelos
        OpenRouter{🔌 OpenRouter Gateway}
        Orchestrator <-->|Chamadas com Streaming| OpenRouter
    end

    subgraph Matriz de Agentes Especialistas
        AgentBack[💻 Agente Backend<br>Python / FastAPI / SQLA]
        AgentFront[🎨 Agente Frontend<br>TypeScript / Next / Tailwind]
        AgentReview[🔍 Agente Reviewer<br>Segurança / Testes / Sonar]
        AgentDocs[📝 Agente Docs<br>ADRs / Markdown / MkDocs]
    end

    OpenRouter -->|Assina contexto| AgentBack
    OpenRouter -->|Assina contexto| AgentFront
    OpenRouter -->|Assina contexto| AgentReview
    OpenRouter -->|Assina contexto| AgentDocs

    subgraph Infraestrutura e Persistência de Dados
        DB[(🗄️ PostgreSQL 16<br>Dados Estruturados & Estados)]
        Cache[(⚡ Redis 7<br>Fila de Tarefas & PubSub)]
        VectorDB[(📐 Qdrant Vector DB<br>Memória de Longo Prazo / RAG)]
        FS[💾 FileSystem Local / Workspace<br>Código Fonte Gerado]
    end

    AgentBack & AgentFront -->|Persiste Código| FS
    AgentReview -->|Audita Arquivos| FS
    AgentDocs -->|Gera Documentação| FS
    API <-->|Cache de Sessões| Cache
    Orchestrator <-->|Busca Semântica Contextual| VectorDB
    AgentBack & API -->|Leitura/Escrita| DB
```

---

## 🤖 Ecossistema Multiagente (Especializações)

Diferente de abordagens lineares, a NAP cria uma mesa de debates de engenharia de software antes de colocar a primeira linha de código no arquivo. Cada agente opera sob um *prompt de sistema* extremamente rigoroso e focado em sua disciplina:

### 1. 📐 Architect Agent (O Orquestrador)
* **Função:** Atua como o CTO/Principal Architect do projeto. Ele recebe a especificação bruta do usuário e a converte em um plano técnico viável.
* **Capacidades:** Gera documentos ADR (Architecture Decision Records), define padrões de design (Clean Architecture, DDD ou MVC) e constrói a árvore de dependência das tarefas para evitar conflitos de merge entre os outros agentes.

### 2. 💻 Backend Agent (O Desenvolvedor Core)
* **Função:** Codificação puramente lógica do lado do servidor.
* **Capacidades:** Domínio profundo de Python, FastAPI, tratamento assíncrono, estruturação de schemas com Pydantic v2, escrita de queries eficientes no SQLAlchemy e mapeamento de migrações estruturais via Alembic.

### 3. 🎨 Frontend Agent (O UI/UX Coder)
* **Função:** Transformar especificações de rotas e dados de API em interfaces ricas, performáticas e responsivas.
* **Capacidades:** Geração de componentes limpos em Next.js (App Router), aplicação rigorosa de padrões TailwindCSS, controle de estados globais ou locais e tratamento correto de renderização no lado do servidor (SSR) e no cliente (CSR).

### 4. 🔍 Reviewer Agent (O Auditor de Qualidade)
* **Função:** Atuar como a barreira de segurança e garantia de qualidade (QA). Ele é acionado automaticamente a cada alteração efetuada pelos agentes de Backend e Frontend.
* **Capacidades:** Varredura em busca de vulnerabilidades (OWASP Top 10, SQL Injection, vazamento de memória), checagem de conformidade com PEP 8/ESLint, verificação de cobertura de testes unitários e bloqueio de código defeituoso.

### 5. 📝 Docs Agent (O Engenheiro de Conhecimento)
* **Função:** Garantir que o projeto seja documentado em tempo real, eliminando o "débito de documentação".
* **Capacidades:** Geração automática de documentação técnica interna, arquivos Markdown autoexplicativos, diagramas de arquitetura atualizados e docstrings padronizadas no código fonte.

---

## 🛠️ Stack Tecnológica e Justificativas

A escolha de ferramentas para a NAP priorizou performance, tipagem estática para estabilidade do código gerado por IA e flexibilidade de armazenamento de contexto:

<details>
<summary><strong>Python 3.10+ & FastAPI</strong></summary>
Escolhidos pela velocidade de execução bruta devido ao suporte nativo a operações assíncronas (`async/await`) e documentação imediata via Swagger, crucial para os agentes entenderem o que os outros estão expondo.
</details>

<details>
<summary><strong>Next.js 14 & TypeScript</strong></summary>
O uso de TypeScript garante que o Agente de Front-end siga interfaces estritas expostas pelo Back-end. O Next.js com App Router provê a otimização de performance necessária para dashboards em tempo real.
</details>

<details>
<summary><strong>PostgreSQL 16 & Redis 7</strong></summary>
PostgreSQL atua como banco transacional robusto para armazenar logs de auditoria e históricos. O Redis atua como barramento de comunicação assíncrona rápida (Pub/Sub) e gerenciador de filas para que os agentes processem tarefas pesadas em background.
</details>

<details>
<summary><strong>Qdrant Vector DB & OpenRouter</strong></summary>
Qdrant é o motor de RAG que permite indexar semanticamente toda a base de código do usuário. O OpenRouter é a abstração que permite trocar dinamicamente o modelo LLM subjacente (DeepSeek, Qwen, Llama) sem alterar o código.
</details>

---

## ⚙️ Guia de Instalação e Configuração Completo

### Pré-requisitos e Verificação

Antes de iniciar a instalação, certifique-se de que sua máquina possui as versões adequadas das ferramentas abaixo executando os comandos em seu terminal:

| Ferramenta | Versão Mínima | Comando de Verificação |
| :--- | :--- | :--- |
| **Docker** | 24.0.0+ | `docker --version` |
| **Docker Compose** | v2.20.0+ | `docker compose version` |
| **Git** | 2.34.0+ | `git --version` |
| **Python** | 3.10.0+ | `python3 --version` |
| **Node.js** | 18.0.0+ | `node --version` |

---

### Configuração de Variáveis de Ambiente (.env)

Crie um arquivo chamado `.env` na raiz do diretório clonado utilizando como base o exemplo abaixo. Configure suas chaves adequadamente:

```env
# ==============================================================================
# CONFIGURAÇÕES GERAIS DA PLATAFORMA NAP
# ==============================================================================
ENVIRONMENT=development
PROJECT_NAME="NAP - Nexus AI Platform"
SECRET_KEY=suachave_secreta_jwt_super_segura_aqui

# ==============================================================================
# PROVEDORES DE INTELIGÊNCIA ARTIFICIAL (IA)
# ==============================================================================
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEFAULT_MODEL_ARCHITECT=deepseek/deepseek-chat
DEFAULT_MODEL_DEVELOPER=qwen/qwen-2.5-coder-32b-instruct
DEFAULT_MODEL_REVIEWER=google/gemini-flash-1.5

# ==============================================================================
# BANCOS DE DADOS E PERSISTÊNCIA
# ==============================================================================
POSTGRES_USER=nap_admin
POSTGRES_PASSWORD=nap_secure_pass_99
POSTGRES_DB=nap_core
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}/0

QDRANT_HOST=qdrant
QDRANT_PORT=6333

# ==============================================================================
# DIRETÓRIOS E WORKSPACE DOS AGENTES
# ==============================================================================
WORKSPACE_DIR=/app/workspace
MAX_CONCURRENT_TASKS=4
```

---

### Deploy com Docker Compose

Esta é a abordagem recomendada para ambientes de homologação ou uso corporativo local rápido, pois inicializa todas as dependências de rede e persistência isoladamente.

```bash
# 1. Realize o clone do repositório oficial
git clone [https://github.com/seu-organizacao/nap-platform.git](https://github.com/seu-organizacao/nap-platform.git)
cd nap-platform

# 2. Inicialize o arquivo de variáveis de ambiente
cp .env.example .env
# [!] Lembre-se de abrir o .env com seu editor (nano, vim, vscode) e inserir sua chave OpenRouter.

# 3. Execute o build e inicialização dos containers em segundo plano (detached mode)
docker compose up -d --build

# 4. Monitore a saúde da inicialização dos microsserviços
docker compose ps

# 5. Acompanhe a transmissão de logs do core backend se necessário
docker compose logs -f backend
```

#### Verificação de Portas e Serviços Ativos:
Após a execução com sucesso, valide o acesso aos seguintes endpoints mapeados no seu `localhost`:
* **Interface Gráfica (Frontend Next.js):** [http://localhost:3000](http://localhost:3000)
* **Documentação Interativa da API (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Especificação Técnica Completa (ReDoc):** [http://localhost:8000/redoc](http://localhost:8000/redoc)
* **Painel Administrativo do Banco Vetorial Qdrant:** [http://localhost:6333/dashboard](http://localhost:6333/dashboard)

---

### Configuração para Desenvolvimento Local (Bare-Metal)

Se você deseja modificar o código fonte da NAP, criar novos agentes ou debugar endpoints diretamente na sua máquina física, siga os passos abaixo de forma isolada para o Backend e o Frontend:

#### Configuração do Ambiente Backend (FastAPI):
```bash
# Navegue até a pasta do backend
cd backend

# Crie um ambiente virtual Python isolado
python3 -m venv venv

# Ative o ambiente virtual
# No Linux/macOS:
source venv/bin/activate
# No Windows (PowerShell):
# .\venv\Scripts\Activate.ps1

# Atualize o gerenciador de pacotes pip e instale as dependências
pip install --upgrade pip
pip install -r requirements.txt

# Execute as migrações iniciais do banco de dados via Alembic
alembic upgrade head

# Inicie o servidor em modo de desenvolvimento com hot-reload ativo
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Configuração do Ambiente Frontend (Next.js):
```bash
# Abra uma nova aba no terminal e acesse a pasta do frontend
cd frontend

# Instale os pacotes e dependências listadas no package.json
npm install

# Inicialize o servidor de desenvolvimento local node
npm run dev
```
O painel de desenvolvimento front-end estará disponível em `http://localhost:3000`.

---

## 💻 Manual de Uso da CLI / TUI Hacker

Para desenvolvedores veteranos que preferem a velocidade do teclado à navegação por cliques no mouse, a NAP disponibiliza uma Terminal User Interface (TUI) imersiva construída sobre as bibliotecas `Rich` e `prompt-toolkit`.

### Formas de Execução
* **Se instalado via pacote Debian:** Execute diretamente o atalho global `nap-tui`.
* **Se executando manualmente via código fonte:** No diretório raiz, execute `python -m cli.v2.main`.

### Layout da Interface do Terminal
Ao ser instanciado, o terminal se divide em 3 painéis principais responsivos:
1.  **Painel Esquerdo (Prompt & Logs do Orquestrador):** Local onde você digita seus comandos e visualiza o agente Architect fatiando os épicos em micro-tarefas.
2.  **Painel Superior Direito (Acompanhamento em Tempo Real):** Exibe barras de progresso animadas para cada agente ativo, mostrando qual arquivo está sendo lido, editado ou auditado naquele exato segundo.
3.  **Painel Inferior Direito (Terminal de Aprovação):** Canal crítico de governança onde a IA interrompe o fluxo para solicitar autorizações do usuário.

### Atalhos Críticos de Controle na TUI:
* `Ctrl + C`: Cancela imediatamente o processamento do agente atual e reverte as alterações parciais não salvas no Git.
* `Tab`: Alterna o foco de digitação e navegação entre o painel de histórico de comandos e o painel de aprovações.
* `Ctrl + L`: Limpa a tela de logs sem perder o estado de processamento em background da sessão de IA.
* `Seta Cima / Seta Baixo`: Navega pelo histórico de comandos executados anteriormente na sessão.

---

## 🚀 Documentação da API e Endpoints Principais

A API do backend atua como um barramento REST HTTP e via canais bidirecionais contínuos de WebSockets. Abaixo estão os endpoints mais importantes para integrações de sistemas de terceiros ou automações em pipelines de CI/CD:

### Endpoints REST HTTP

| Método | Rota | Descrição Técnica | Corpo da Requisição / Parâmetros |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Verificação de integridade operacional (Liveness/Readiness probe). | Nenhum. Retorna status `200 OK`. |
| `POST` | `/api/v1/tasks/submit` | Envia um requisito para o Orquestrador iniciar a criação da DAG. | `{"prompt": "string", "context_id": "string"}` |
| `GET` | `/api/v1/tasks/{task_id}` | Consulta o estado atualizado de uma tarefa específica e logs. | `task_id` (parâmetro de rota). |
| `GET` | `/api/v1/agents/status` | Retorna a matriz de agentes do ecossistema informando ocupação. | Nenhum. |
| `POST` | `/api/v1/workspace/clean` | Limpa arquivos temporários gerados por agentes com falha. | `{"workspace_id": "string"}` |

### Canal de Comunicação em Tempo Real (WebSockets)
* **Rota:** `WS://localhost:8000/api/v1/stream/tasks/{session_id}`
* **Descrição:** O cliente se conecta a este canal para receber transmissões de dados em tempo real (*streaming de tokens*) à medida que as LLMs respondem, além de capturar imediatamente mudanças de progresso nas barras da TUI.

---

## 🛡️ Segurança, Governança e Human-in-the-Loop

Deixar agentes de Inteligência Artificial manipularem arquivos de código fonte e comandos de terminal sem supervisão pode resultar em desastres estruturais. A NAP implementa camadas rígidas de controle operacional:

1.  **Princípio "Human-in-the-Loop" (HITL):** Por padrão, qualquer comando gerado por um agente classificado como prejudicial ou destrutivo (ex: `rm -rf`, `docker compose down`, modificações estruturais em bancos SQL) é colocado em estado de suspensão. O sistema aguarda um sinal explícito `Y` (Sim) do operador.
2.  **Isolamento em Ambientes Seguros (Sandboxing):** As tarefas de compilação, checagem e execução de códigos acontecem dentro de containers efêmeros e isolados.
3.  **Auditoria Automatizada via Git:** Toda alteração de código abre automaticamente uma *feature branch* temporária. Nenhuma escrita acontece diretamente na branch `main` sem que o Agente Reviewer valide a integridade e o humano realize o merge via Pull Request.

---

## 🤝 Guia de Contribuição e Engenharia de Agentes

O ecossistema NAP é modular, permitindo a adição de novos agentes especialistas facilmente. Se você deseja contribuir criando, por exemplo, um *Agente de Engenharia de Infraestrutura e Terraform (DevOps Agent)*, siga o padrão de engenharia:

1.  **Criação do Prompt de Sistema:** Adicione a definição comportamental rigorosa do novo agente em `backend/app/agents/prompts/devops.json`.
2.  **Herdar a Classe Base de Agentes:** Crie o arquivo em `backend/app/agents/devops_agent.py`, herdando de `BaseAgent` e implementando o método assíncrono `execute_task`.
3.  **Mapear as Ferramentas MCP:** Declare no arquivo de configuração a quais ferramentas do Model Context Protocol o agente terá acesso.
4.  **Registrar no Orquestrador:** Abra `backend/app/orchestrator/graph.py` e adicione o nó do novo agente nas possibilidades de roteamento de tarefas da DAG manipulada pelo *Architect Agent*.

---

## 🗺️ Roadmap e Visão de Futuro

- [ ] **RAG Arquitetural Avançado:** Indexação de livros de referência de design de código no Qdrant para forçar agentes a seguirem padrões de nível sênior.
- [ ] **Autenticação Corporativa:** Controle de acesso via chaves JWT integradas a provedores OAuth2 (Azure AD, Okta, Keycloak).
- [ ] **Execução Concorrente de Agentes:** Permitir que o Backend Agent e o Frontend Agent desenvolvam a mesma funcionalidade em paralelo, utilizando o Architect Agent para arbitrar conflitos de interface.
- [ ] **Módulo Auto-Healing Inteligente:** Capacidade de o sistema ler logs de erro de produção reais e propor patches corretivos sem intervenção humana prévia.

---

<div align="center">
    <strong>Nexus AI Platform (NAP)</strong><br>
    <em>Construído por Engenheiros de Software, Escalado por Inteligência Artificial.</em>
</div>