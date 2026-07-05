<div align="center">

# ⚡ NAP — Nexus AI Platform

**Plataforma de Engenharia de Software de Alta Performance Potencializada por Inteligência Artificial Multiagente**

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0052CC?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=nextdotjs&logoColor=white)](https://nextjs.org)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-AI-10B981?style=for-the-badge&logo=openai&logoColor=white)](https://openrouter.ai)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

*Orquestração de agentes autônomos para arquitetura, codificação, documentação e revisão em um fluxo contínuo.*

[🚀 Começar](#-instalação-rápida) •
[📖 Documentação](#-documentação-da-api) •
[🏗️ Arquitetura](#-arquitetura) •
[🤝 Contribuir](#-contribuição)

</div>

---

## 🎯 Visão Rápida

```mermaid
graph LR
    A[👤 Seu Requisito] --> B[🧠 Orquestrador AI]
    B --> C[📐 Architect Agent]
    B --> D[💻 Backend Agent]
    B --> E[🎨 Frontend Agent]
    B --> F[🔍 Reviewer Agent]
    B --> G[📝 Docs Agent]
    C & D & E & F & G --> H[✅ Projeto Completo]
    
    style A fill:#3b82f6,color:#fff
    style B fill:#8b5cf6,color:#fff
    style C fill:#10b981,color:#fff
    style D fill:#10b981,color:#fff
    style E fill:#10b981,color:#fff
    style F fill:#f59e0b,color:#fff
    style G fill:#f59e0b,color:#fff
    style H fill:#ef4444,color:#fff
```

---

## 📋 Índice

- [🎯 Visão Rápida](#-visão-rápida)
- [🌟 Sobre o Projeto](#-sobre-o-projeto)
- [🏗️ Arquitetura](#-arquitetura)
- [🤖 Ecossistema Multiagente](#-ecossistema-multiagente)
- [🛠️ Stack Tecnológica](#-stack-tecnológica)
- [⚙️ Instalação Rápida](#-instalação-rápida)
- [💻 CLI / TUI Hacker](#-cli--tui-hacker)
- [🚀 Documentação da API](#-documentação-da-api)
- [🛡️ Segurança](#-segurança)
- [🤝 Contribuição](#-contribuição)
- [🗺️ Roadmap](#-roadmap)

---

## 🌟 Sobre o Projeto

A **NAP (Nexus AI Platform)** é um ecossistema de engenharia de software autônomo projetado para atuar como uma equipe inteira de desenvolvimento. 

### 🎯 O Problema
Engenheiros gastam 60%+ do tempo em tarefas acessórias: context switching, documentação repetitiva, configuração de ambientes, correção de regressões. Ferramentas como Copilot auxiliam em autocompletar linhas, mas falham em compreender a **visão macro** de arquitetura.

### ✨ A Solução
A NAP implementa um **Orquestrador Central (Architect)** baseado em grafos de tarefas (DAG). O desenvolvedor insere um requisito em linguagem natural e o Orquestrador:
- Analisa a demanda
- Gera documentos de decisão arquitetural (ADRs)
- Divide o épico em tarefas atômicas
- Distribui tarefas para agentes de IA hiper-especializados
- Executa trabalho de forma paralela e segura

---

## 🏗️ Arquitetura

### 📊 Diagramas de Arquitetura

> 📁 **Diagramas detalhados disponíveis em:** [`docs/arquitetura/`](docs/arquitetura/)

#### Arquitetura Geral do Sistema
```mermaid
graph TD
    %% Estilos Modernos
    style User fill:#0f172a,stroke:#3b82f6,stroke-width:3px,color:#fff
    style Frontend fill:#1e293b,stroke:#8b5cf6,stroke-width:2px,color:#fff
    style Backend fill:#1e293b,stroke:#10b981,stroke-width:2px,color:#fff
    style Orchestrator fill:#0f172a,stroke:#f59e0b,stroke-width:3px,color:#fff
    style AIAgents fill:#1e293b,stroke:#ef4444,stroke-width:2px,color:#fff
    style Data fill:#1e293b,stroke:#06b6d4,stroke-width:2px,color:#fff
    style External fill:#374151,stroke:#6b7280,stroke-width:2px,color:#fff

    User[👤 Usuário/Engenheiro]
    
    subgraph UI_LAYER["🎨 Camada de Interface"]
        Frontend[⚡ Frontend - Next.js 14<br/>TypeScript + Tailwind<br/>Porta :3000]
        CLI[⌨️ CLI/TUI Hacker<br/>Rich + prompt-toolkit]
    end
    
    subgraph API_LAYER["🚀 Camada de API"]
        Backend[⚙️ Backend - FastAPI<br/>Python 3.10+<br/>Porta :8000]
        WebSocket[🔌 WebSocket Gateway<br/>Streaming em Tempo Real]
    end
    
    subgraph ORCHESTRATION["🧠 Camada de Orquestração"]
        Orchestrator[🎯 Orquestrador Central<br/>Graph-based DAG<br/>Task Decomposition]
        MCP[🛠️ MCP Tools SDK<br/>FileSystem + Git + Docker]
    end
    
    subgraph AI_LAYER["🤖 Camada de Inteligência Artificial"]
        Architect[📐 Architect Agent<br/>Planning & ADRs]
        BackendAgent[💻 Backend Agent<br/>Python/FastAPI]
        FrontendAgent[🎨 Frontend Agent<br/>Next.js/React]
        Reviewer[🔍 Reviewer Agent<br/>QA & Security]
        Docs[📝 Docs Agent<br/>Documentation]
    end
    
    subgraph DATA_LAYER["💾 Camada de Dados"]
        PostgreSQL[(🗄️ PostgreSQL 16<br/>Dados Estruturados)]
        Redis[(⚡ Redis 7<br/>Cache & Filas)]
        Qdrant[(📐 Qdrant Vector DB<br/>RAG & Memória)]
        FileSystem[💾 Workspace<br/>Código Gerado]
    end
    
    subgraph EXTERNAL["🌐 Serviços Externos"]
        OpenRouter[🔌 OpenRouter API<br/>LLM Gateway]
    end
    
    %% Fluxos
    User -->|HTTP/HTTPS| Frontend
    User -->|Terminal| CLI
    Frontend <-->|REST API| Backend
    CLI <-->|REST API| Backend
    Backend -->|Task Submission| Orchestrator
    Orchestrator -->|Task Distribution| Architect
    Orchestrator -->|Task Distribution| BackendAgent
    Orchestrator -->|Task Distribution| FrontendAgent
    Orchestrator -->|Task Distribution| Reviewer
    Orchestrator -->|Task Distribution| Docs
    Architect <-->|LLM Calls| OpenRouter
    BackendAgent <-->|LLM Calls| OpenRouter
    FrontendAgent <-->|LLM Calls| OpenRouter
    Reviewer <-->|LLM Calls| OpenRouter
    Docs <-->|LLM Calls| OpenRouter
    BackendAgent -->|Code Generation| FileSystem
    FrontendAgent -->|Code Generation| FileSystem
    Reviewer -->|Code Audit| FileSystem
    Docs -->|Doc Generation| FileSystem
    Backend <-->|Queries| PostgreSQL
    Backend <-->|Session Cache| Redis
    Orchestrator <-->|Semantic Search| Qdrant
```

#### Outros Diagramas

| Diagrama | Descrição | Arquivo |
|----------|-----------|---------|
| **Fluxo de Agentes** | Sequência detalhada de interação | [`02-fluxo-agentes.mmd`](docs/arquitetura/02-fluxo-agentes.mmd) |
| **Modelo de Dados** | Diagrama ER do banco de dados | [`03-modelo-dados.mmd`](docs/arquitetura/03-modelo-dados.mmd) |
| **Fluxo de Dados** | Pipeline de processamento | [`04-fluxo-dados.mmd`](docs/arquitetura/04-fluxo-dados.mmd) |
| **Deploy & Infra** | Arquitetura de produção | [`05-deploy-infra.mmd`](docs/arquitetura/05-deploy-infra.mmd) |

---

## 🤖 Ecossistema Multiagente

### 🎯 Matrix de Especialistas

| Agente | Função | Capacidades |
|--------|--------|-------------|
| **📐 Architect** | Orquestrador & Planejamento | ADRs, padrões de design, DAG de tarefas |
| **💻 Backend** | Desenvolvedor Server-side | Python/FastAPI, async/await, Pydantic v2, SQLAlchemy |
| **🎨 Frontend** | UI/UX Developer | Next.js App Router, TypeScript, TailwindCSS |
| **🔍 Reviewer** | QA & Security Auditor | OWASP Top 10, SQL Injection, PEP 8/ESLint |
| **📝 Docs** | Engenheiro de Conhecimento | Documentação técnica, Markdown, diagramas |

### 🔄 Fluxo de Trabalho

```mermaid
graph LR
    A[📋 Requisito] --> B[📐 Architect]
    B --> C[🧠 Planejamento]
    C --> D[💻 Backend]
    C --> E[🎨 Frontend]
    D --> F[🔍 Reviewer]
    E --> F
    F --> G{Aprovado?}
    G -->|Sim| H[📝 Docs]
    G -->|Não| D
    H --> I[✅ Projeto Completo]
    
    style A fill:#3b82f6,color:#fff
    style B fill:#8b5cf6,color:#fff
    style C fill:#8b5cf6,color:#fff
    style D fill:#10b981,color:#fff
    style E fill:#10b981,color:#fff
    style F fill:#f59e0b,color:#fff
    style G fill:#ef4444,color:#fff
    style H fill:#f59e0b,color:#fff
    style I fill:#22c55e,color:#fff
```

---

## 🛠️ Stack Tecnológica

### 🎨 Frontend
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Next.js** | 14+ | Framework React com App Router |
| **TypeScript** | 5+ | Tipagem estática |
| **TailwindCSS** | 3+ | Estilização utility-first |
| **React** | 18+ | Biblioteca UI |

### ⚙️ Backend
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **Python** | 3.10+ | Linguagem principal |
| **FastAPI** | Latest | Framework API async |
| **Pydantic** | v2 | Validação de dados |
| **SQLAlchemy** | 2.0+ | ORM |
| **Alembic** | Latest | Migrações |

### 💾 Dados & Infra
| Tecnologia | Versão | Uso |
|------------|--------|-----|
| **PostgreSQL** | 16+ | Banco transacional |
| **Redis** | 7+ | Cache e filas |
| **Qdrant** | Latest | Vector DB para RAG |
| **Docker** | 24+ | Containerização |

### 🤖 Inteligência Artificial
| Tecnologia | Uso |
|------------|-----|
| **OpenRouter** | Gateway para múltiplos LLMs |
| **MCP Protocol** | Model Context Protocol |
| **Vector Embeddings** | Indexação semântica |

---

## ⚙️ Instalação Rápida

### 📋 Pré-requisitos

| Ferramenta | Versão Mínima | Verificação |
|------------|---------------|-------------|
| **Docker** | 24.0.0+ | `docker --version` |
| **Docker Compose** | v2.20.0+ | `docker compose version` |
| **Git** | 2.34.0+ | `git --version` |
| **Python** | 3.10.0+ | `python3 --version` |
| **Node.js** | 18.0.0+ | `node --version` |

### 🚀 Docker Compose (Recomendado)

```bash
# 1. Clone o repositório
git clone https://github.com/seu-organizacao/nap-platform.git
cd nap-platform

# 2. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env e adicione sua chave OpenRouter

# 3. Suba os containers
docker compose up -d --build

# 4. Verifique os serviços
docker compose ps
```

### 🔗 Serviços Disponíveis

| Serviço | URL | Descrição |
|---------|-----|-----------|
| **Frontend** | http://localhost:3000 | Interface web Next.js |
| **API** | http://localhost:8000 | Backend FastAPI |
| **Swagger** | http://localhost:8000/docs | Documentação interativa |
| **ReDoc** | http://localhost:8000/redoc | Especificação OpenAPI |
| **Qdrant** | http://localhost:6333/dashboard | Painel Vector DB |

### 💻 Desenvolvimento Local

#### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

### 🔧 Configuração do .env

```env
# Geral
ENVIRONMENT=development
SECRET_KEY=sua_chave_secreta_aqui

# OpenRouter
OPENROUTER_API_KEY=sk-or-v1-***
DEFAULT_MODEL_ARCHITECT=deepseek/deepseek-chat
DEFAULT_MODEL_DEVELOPER=qwen/qwen-2.5-coder-32b-instruct

# Banco de Dados
POSTGRES_USER=nap_admin
POSTGRES_PASSWORD=nap_secure_pass
POSTGRES_DB=nap_core
DATABASE_URL=postgresql+asyncpg://nap_admin:nap_secure_pass@postgres:5432/nap_core

# Redis & Qdrant
REDIS_URL=redis://redis:6379/0
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

---

## 💻 CLI / TUI Hacker

Para desenvolvedores que preferem a velocidade do terminal, a NAP disponibiliza uma **Terminal User Interface (TUI)** imersiva construída sobre `Rich` e `prompt-toolkit`.

### 🚀 Execução

```bash
# Via pacote Debian
nap-tui

# Via código fonte
python -m cli.v2.main
```

### 🎨 Layout da Interface

1. **Painel Esquerdo:** Prompt & Logs do Orquestrador
2. **Painel Superior Direito:** Acompanhamento em Tempo Real (progress bars)
3. **Painel Inferior Direito:** Terminal de Aprovação (governança)

### ⌨️ Atalhos

| Atalho | Ação |
|--------|------|
| `Ctrl + C` | Cancela processamento e reverte alterações |
| `Tab` | Alterna foco entre painéis |
| `Ctrl + L` | Limpa tela de logs |
| `↑ / ↓` | Navega histórico de comandos |

---

## 🚀 Documentação da API

### Endpoints REST

| Método | Rota | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/tasks/submit` | Envia requisito para orquestrador |
| `GET` | `/api/v1/tasks/{task_id}` | Consulta estado de tarefa |
| `GET` | `/api/v1/agents/status` | Status dos agentes |
| `POST` | `/api/v1/workspace/clean` | Limpa workspace |

### WebSocket

- **Rota:** `WS://localhost:8000/api/v1/stream/tasks/{session_id}`
- **Descrição:** Streaming em tempo real de tokens e progresso

---

## 🛡️ Segurança

### 🔒 Human-in-the-Loop (HITL)

Comandos prejudiciais (`rm -rf`, `docker compose down`, etc.) são suspensos aguardando aprovação explícita do operador.

### 🛡️ Sandboxing

Tarefas de compilação e execução acontecem em containers efêmeros e isolados.

### 📋 Auditoria Git

Toda alteração cria uma *feature branch* temporária. Nada é mergeado na `main` sem validação do Reviewer e aprovação humana.

---

## 🤝 Contribuição

O ecossistema NAP é modular. Para adicionar um novo agente (ex: DevOps Agent):

1. **Criar Prompt de Sistema:** `backend/app/agents/prompts/devops.json`
2. **Herdar Classe Base:** `backend/app/agents/devops_agent.py` (herda de `BaseAgent`)
3. **Mapear Ferramentas MCP:** Declarar tools disponíveis no config
4. **Registrar no Orquestrador:** Adicionar nó em `backend/app/orchestrator/graph.py`

---

## 🗺️ Roadmap

- [ ] ✅ Arquitetura base com orquestrador
- [ ] ✅ 5 agentes especializados iniciais
- [ ] 🔄 Interface TUI hacker melhorada
- [ ] 📋 Suporte a mais modelos LLM
- [ ] 🔄 Integração com CI/CD
- [ ] 📋 Marketplace de agentes customizados
- [ ] 🔄 Dashboard de métricas avançado
- [ ] 📋 Multi-tenancy

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

<div align="center">

**⚡ Feito com ❤️ pela equipe NAP**

[🔝 Voltar ao topo](#-nap--nexus-ai-platform)

</div>