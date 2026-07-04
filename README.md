# 🧠 NAP — Nexus AI Platform

**Plataforma de Engenharia de Software baseada em Inteligência Artificial**

NAP orquestra agentes de IA especializados para auxiliar desenvolvedores humanos em todo o ciclo de vida do software: arquitetura, geração de código backend/frontend, documentação e revisão.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Stack Tecnológica](#-stack-tecnológica)
- [Arquitetura](#-arquitetura)
- [Pré-requisitos](#-pré-requisitos)
- [Instalação e Execução](#-instalação-e-execução)
- [Como Usar](#-como-usar)
  - [Via Frontend](#via-frontend)
  - [Via API (Swagger)](#via-api-swagger)
  - [Via curl](#via-curl)
- [Agentes](#-agentes)
- [MCP Tools](#-mcp-tools)
- [API Endpoints](#-api-endpoints)
- [Exemplos Práticos](#-exemplos-práticos)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Testes](#-testes)
- [Solução de Problemas](#-solução-de-problemas)
- [Roadmap](#-roadmap)
- [Arquitetura de Decisões (ADRs)](#-arquitetura-de-decisões-adrs)

---

## 🎯 Visão Geral

A NAP é uma plataforma que conecta **modelos de IA** (via OpenRouter) a **agentes especializados** que geram código de software sob demanda. O fluxo é:

```
Usuário → Frontend (Next.js) → API (FastAPI) → Orchestrator → 
OpenRouter → Agentes (Backend, Frontend, Docs, Reviewer) → 
MCP Tools → Resultado → Frontend → Usuário
```

### O que a NAP **faz**:
- ✅ Interpreta requisitos de software em linguagem natural
- ✅ Decompõe problemas complexos em tarefas menores
- ✅ Gera código backend (Python/FastAPI) e frontend (React/Next.js)
- ✅ Gera documentação técnica e ADRs
- ✅ Revisa código gerado por outros agentes
- ✅ Executa comandos Git, Docker, Bash, Python e PostgreSQL via MCP Tools

### O que a NAP **NÃO faz**:
- ❌ Não é um LLM — orquestra modelos existentes
- ❌ Não substitui o desenvolvedor — atua como equipe de apoio
- ❌ Não faz fine-tuning de modelos

---

## 🚀 Stack Tecnológica

| Camada | Tecnologia | Versão |
|--------|-----------|--------|
| **Backend** | Python + FastAPI + SQLAlchemy + Pydantic | 3.13 / 0.115 / 2.0 / 2.9 |
| **Frontend** | React + Next.js + TypeScript + TailwindCSS | 18 / 14 / 5.5 / 3.4 |
| **Banco Relacional** | PostgreSQL | 16 Alpine |
| **Cache** | Redis | 7 Alpine |
| **Banco Vetorial** | Qdrant | latest |
| **Infraestrutura** | Docker Compose | v2+ |
| **Modelos IA** | OpenRouter (Free Tier) | DeepSeek, Qwen, Mistral, Llama |
| **ORM** | SQLAlchemy + Alembic | Async |
| **Validação** | Pydantic v2 | — |

---

## 🏗️ Arquitetura

### Diagrama de Componentes

```
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│   Usuário   │────▶│   Frontend   │────▶│    Backend      │
│  (Browser)  │     │  Next.js 14  │     │   FastAPI       │
└─────────────┘     └──────────────┘     └────────┬────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │   Orchestrator   │
                                          │  (Architect IA)  │
                                          └────────┬────────┘
                                                   │
                          ┌────────────────────────┼────────────────────────┐
                          │                        │                        │
                          ▼                        ▼                        ▼
                  ┌──────────────┐        ┌──────────────┐        ┌──────────────┐
                  │ Backend      │        │ Frontend     │        │ Reviewer     │
                  │ Agent        │        │ Agent        │        │ Agent        │
                  └──────┬───────┘        └──────┬───────┘        └──────┬───────┘
                         │                       │                       │
                         ▼                       ▼                       ▼
                  ┌──────────────────────────────────────────────────────────┐
                  │                    OpenRouter API                        │
                  │     (DeepSeek, Qwen, Mistral, Llama — Free Tier)        │
                  └──────────────────────────────────────────────────────────┘
                         │                       │                       │
                         ▼                       ▼                       ▼
                  ┌──────────────────────────────────────────────────────────┐
                  │                    MCP Tools                             │
                  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────────┐     │
                  │  │ Git  │ │Docker│ │Python│ │ Bash │ │PostgreSQL│     │
                  │  └──────┘ └──────┘ └──────┘ └──────┘ └──────────┘     │
                  └──────────────────────────────────────────────────────────┘
```

### Infraestrutura (Docker)

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose                            │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │PostgreSQL│  │  Redis   │  │  Qdrant  │  │ Backend  │   │
│  │  :5432   │  │  :6379   │  │ :6333-34 │  │  :8000   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                              │
│  ┌──────────┐                                               │
│  │ Frontend │                                               │
│  │  :3000   │                                               │
│  └──────────┘                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Pré-requisitos

| Ferramenta | Versão Mínima | Como Verificar |
|-----------|--------------|----------------|
| **Docker** | 24+ | `docker --version` |
| **Docker Compose** | v2+ | `docker compose version` |
| **Git** | 2.x | `git --version` |
| **OpenRouter API Key** | — | [Criar conta gratuita](https://openrouter.ai/keys) |

> 💡 **OpenRouter é gratuito!** Os modelos Free Tier (DeepSeek, Qwen, Mistral) não exigem cartão de crédito.

---

## ⚡ Instalação e Execução

### Passo 1: Clone e configure

```bash
# Entre no diretório do projeto
cd "/home/ghost/Documents/Projetos/0 - NAP_Nexus AI Platform"

# Crie o arquivo de ambiente
cp .env.example .env
```

### Passo 2: Configure a chave da API

Edite o arquivo `.env` e adicione sua chave do OpenRouter:

```env
# .env
POSTGRES_USER=nap_user
POSTGRES_PASSWORD=nap_pass
POSTGRES_DB=nap_nexus
REDIS_URL=redis://redis:6379/0
QDRANT_URL=http://qdrant:6333
OPENROUTER_API_KEY=sk-or-v1-SUA_CHAVE_AQUI
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=deepseek/deepseek-chat:free
LOG_LEVEL=INFO
```

> 🔑 **Onde conseguir a chave:** https://openrouter.ai/keys → "Create Key" → Copie a chave que começa com `sk-or-v1-`

### Passo 3: Inicie a plataforma

```bash
# Comando único para subir tudo
docker compose up -d --build
```

### Passo 4: Acesse

| Serviço | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **API (FastAPI)** | http://localhost:8000 |
| **Swagger UI (docs)** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **Qdrant Dashboard** | http://localhost:6333/dashboard |

### Passo 5: Verifique se está tudo funcionando

```bash
# Verificar containers
docker ps

# Testar health check da API
curl http://localhost:8000/health

# Testar frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
```

**Saída esperada:**
```
NAMES          STATUS
nap-frontend   Up
nap-backend    Up
nap-postgres   Up (healthy)
nap-redis      Up (healthy)
nap-qdrant     Up (healthy)

{"status":"healthy","service":"NAP - Nexus AI Platform","version":"0.1.0"}
200
```

### Comandos Úteis

```bash
# Parar tudo
docker compose down

# Ver logs de um serviço
docker compose logs backend
docker compose logs frontend

# Reiniciar um serviço específico
docker compose restart backend

# Reconstruir e subir
docker compose up -d --build

# Executar comando dentro do container
docker compose exec backend bash
docker compose exec backend pytest tests/ -v
```

---

## 📖 Como Usar

### Via Frontend

Acesse http://localhost:3000 para ver a tela inicial da NAP com:
- Cards informativos sobre Agentes, Infraestrutura e MCP Tools
- Botão "Verificar Status" para testar a conexão com a API

> ⚠️ **Nota:** O frontend atual é uma interface de monitoramento. Para executar agentes, use a API.

### Via API (Swagger)

Acesse http://localhost:8000/docs para uma interface interativa onde você pode:

1. Expandir o endpoint desejado
2. Clicar em "Try it out"
3. Preencher os parâmetros
4. Clicar em "Execute"

### Via curl

#### Executar um agente específico

```bash
curl -X POST http://localhost:8000/api/v1/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "backend",
    "task": "Crie uma API REST com FastAPI para gerenciar tarefas (CRUD) com SQLAlchemy e PostgreSQL"
  }'
```

**Parâmetros:**
| Campo | Tipo | Descrição |
|-------|------|-----------|
| `agent_type` | string | `backend`, `frontend`, `documentation`, `reviewer` |
| `task` | string | Descrição da tarefa em linguagem natural |
| `context` | object | (opcional) Contexto adicional |

#### Executar workflow completo

```bash
curl -X POST http://localhost:8000/api/v1/agents/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Crie um sistema de blog com backend FastAPI e frontend React. O backend deve ter CRUD de posts e o frontend uma listagem simples."
  }'
```

#### Gerenciar projetos

```bash
# Listar projetos
curl http://localhost:8000/api/v1/projects/

# Criar projeto
curl -X POST http://localhost:8000/api/v1/projects/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Meu Projeto", "description": "API de tarefas"}'

# Buscar projeto por ID
curl http://localhost:8000/api/v1/projects/1
```

---

## 🤖 Agentes

### Orchestrator (Arquiteto)

O **Orchestrator** é o cérebro da NAP. Ele:
1. Recebe o requisito do usuário em linguagem natural
2. Analisa a complexidade e tipo do projeto
3. Decompõe em tarefas atômicas
4. Atribui cada tarefa ao agente especializado correto
5. Define dependências e ordem de execução
6. Consolida os resultados

### Agentes Especializados

| Agente | agent_type | Especialidade | Gera |
|--------|-----------|---------------|------|
| **🧠 Orchestrator** | `architect` | Arquitetura de software, decomposição de tarefas | Planos de implementação |
| **⚙️ Backend Agent** | `backend` | Python, FastAPI, SQLAlchemy, Pydantic | Código backend completo |
| **🎨 Frontend Agent** | `frontend` | React, Next.js, TypeScript, TailwindCSS | Componentes e páginas |
| **📝 Documentation Agent** | `documentation` | Documentação técnica | READMEs, ADRs, docstrings |
| **🔍 Reviewer Agent** | `reviewer` | Qualidade de código, segurança | Relatórios de revisão |

### Como os Agentes Funcionam

Cada agente usa o **OpenRouter** para acessar modelos de IA. O fluxo interno é:

```
Agente recebe tarefa
    │
    ▼
Monta system prompt especializado (ex: "Você é um expert em FastAPI...")
    │
    ▼
Envia para OpenRouter (modelo configurado em OPENROUTER_MODEL)
    │
    ▼
Recebe resposta do modelo
    │
    ▼
Retorna código/documentação gerados
```

---

## 🔌 MCP Tools

As MCP Tools (Model Context Protocol) são ferramentas que os agentes podem usar para interagir com o sistema:

| Tool | Arquivo | Funções |
|------|---------|---------|
| **Git** | `mcp/git/tool.py` | `init`, `clone`, `add`, `commit`, `status`, `diff`, `log`, `push`, `pull`, `branch` |
| **Docker** | `mcp/docker/tool.py` | `ps`, `images`, `build`, `pull`, `compose_up`, `compose_down`, `logs`, `exec` |
| **Python** | `mcp/python/tool.py` | `check_syntax`, `run_code`, `run_file`, `install_package`, `lint`, `format` |
| **Bash** | `mcp/bash/tool.py` | `execute`, `read_file`, `write_file`, `list_directory`, `make_directory` |
| **PostgreSQL** | `mcp/postgresql/tool.py` | `query`, `list_tables`, `describe_table`, `run_migrations` |

---

## 📚 API Endpoints

### Health & System

| Método | Path | Descrição |
|--------|------|-----------|
| `GET` | `/health` | Health check básico |
| `GET` | `/api/v1/system` | Informações do sistema (versão, modelo) |
| `GET` | `/api/v1/db` | Status da conexão com PostgreSQL |

### Agentes

| Método | Path | Descrição |
|--------|------|-----------|
| `POST` | `/api/v1/agents/execute` | Executa um agente específico |
| `POST` | `/api/v1/agents/workflow` | Executa workflow completo com múltiplos agentes |

**Request `/agents/execute`:**
```json
{
  "agent_type": "backend",
  "task": "Crie uma API de usuários com CRUD",
  "context": {}
}
```

**Response:**
```json
{
  "agent_type": "backend",
  "status": "completed",
  "result": {
    "generated_code": "código gerado...",
    "length": 1234
  },
  "artifacts": []
}
```

**Request `/agents/workflow`:**
```json
{
  "task": "Crie um sistema de blog completo",
  "context": {}
}
```

**Response:**
```json
{
  "status": "completed",
  "total_tasks": 3,
  "results": {
    "task-1": {
      "agent_type": "backend",
      "task_id": "task-1",
      "status": "completed",
      "result": { "generated_code": "..." }
    }
  }
}
```

### Projetos

| Método | Path | Descrição |
|--------|------|-----------|
| `GET` | `/api/v1/projects/` | Lista todos os projetos |
| `POST` | `/api/v1/projects/` | Cria um novo projeto |
| `GET` | `/api/v1/projects/{id}` | Busca projeto por ID |

---

## 💡 Exemplos Práticos

### Exemplo 1: Gerar uma API de tarefas

```bash
curl -X POST http://localhost:8000/api/v1/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "backend",
    "task": "Crie uma API REST para gerenciar tarefas (Todo List) com FastAPI. Deve ter: modelo Task com id, titulo, descricao, concluida, created_at. Endpoints: POST /tasks, GET /tasks, GET /tasks/{id}, PUT /tasks/{id}, DELETE /tasks/{id}. Use SQLAlchemy async com PostgreSQL."
  }'
```

### Exemplo 2: Workflow completo de um blog

```bash
curl -X POST http://localhost:8000/api/v1/agents/workflow \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Crie um sistema de blog. O backend deve ter: modelo Post (id, titulo, conteudo, autor, created_at), endpoints CRUD completos. O frontend deve ter: página de listagem de posts, página de detalhe do post. Use FastAPI no backend e React/Next.js no frontend."
  }'
```

### Exemplo 3: Gerar documentação

```bash
curl -X POST http://localhost:8000/api/v1/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "documentation",
    "task": "Gere documentação técnica para uma API de autenticação JWT com FastAPI. Inclua: visão geral, endpoints, exemplos de requisição/resposta, e instruções de deploy."
  }'
```

### Exemplo 4: Revisar código

```bash
curl -X POST http://localhost:8000/api/v1/agents/execute \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "reviewer",
    "task": "Revise o seguinte código FastAPI: from fastapi import FastAPI\napp = FastAPI()\n\n@app.get(\"/\")\ndef home():\n    return {\"message\": \"Hello\"}\n\n@app.get(\"/users/{id}\")\ndef get_user(id):\n    return {\"user_id\": id}\n\nVerifique: segurança, boas práticas, type hints, tratamento de erros."
  }'
```

---

## 📁 Estrutura do Projeto

```
0 - NAP_Nexus AI Platform/
│
├── backend/                          # 🐍 Backend Python/FastAPI
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # Entry point FastAPI
│   │   ├── api/
│   │   │   ├── __init__.py           # Router aggregation
│   │   │   ├── agents.py             # Agent execution endpoints
│   │   │   ├── health.py             # Health check endpoints
│   │   │   └── projects.py           # Project CRUD endpoints
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Pydantic Settings
│   │   │   └── database.py           # Async SQLAlchemy engine
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── project.py            # Project ORM model
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   └── project.py            # Pydantic schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── openrouter.py         # OpenRouter API client
│   │   │   └── orchestrator.py       # Agent orchestrator
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── logger.py             # Logging configuration
│   ├── alembic/                      # Database migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── alembic.ini
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .dockerignore
│
├── frontend/                         # ⚛️ Frontend Next.js
│   ├── src/
│   │   ├── app/
│   │   │   ├── globals.css           # Tailwind + CSS variables
│   │   │   ├── layout.tsx            # Root layout
│   │   │   └── page.tsx              # Home page
│   │   ├── lib/
│   │   │   └── utils.ts              # cn() utility
│   │   └── types/
│   │       └── index.ts              # TypeScript interfaces
│   ├── Dockerfile
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.js
│   ├── next.config.js
│   └── .dockerignore
│
├── agents/                           # 🤖 Definições dos agentes
│   ├── architect/__init__.py
│   ├── backend_agent/__init__.py
│   ├── frontend_agent/__init__.py
│   ├── documentation/__init__.py
│   └── reviewer/__init__.py
│
├── mcp/                              # 🔌 MCP Tools
│   ├── git/tool.py                   # Version control
│   ├── docker/tool.py                # Container management
│   ├── python/tool.py                # Code execution
│   ├── bash/tool.py                  # Shell commands
│   └── postgresql/tool.py            # Database operations
│
├── knowledge/                        # 📚 Base de conhecimento (V2)
├── workspace/                        # 📂 Código gerado
├── docs/                             # 📄 Documentação técnica
│   ├── ADR-001-arquitetura-mvp.md
│   └── ADR-002-estrategia-containerizacao.md
├── logs/                             # 📝 Logs da aplicação
├── tests/                            # 🧪 Testes
│   ├── backend/
│   │   ├── test_health.py
│   │   ├── test_agents.py
│   │   └── test_projects.py
│   ├── frontend/
│   └── agents/
│
├── docker-compose.yml                # 🐳 Orquestração
├── .env.example                      # Template de configuração
├── .gitignore
└── README.md                         # 📖 Este arquivo
```

---

## 🧪 Testes

### Executar testes do backend

```bash
# Via Docker
docker compose exec backend pytest tests/ -v

# Ou localmente (precisa instalar dependências)
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

### Testes disponíveis

| Arquivo | Testes | O que testa |
|---------|--------|-------------|
| `test_health.py` | 4 testes | Health check, system info, OpenRouter init, Orchestrator init |
| `test_agents.py` | 3 testes | Validação de tipos, execução de agentes, workflow |
| `test_projects.py` | 3 testes | Listagem, schema validation, model repr |

---

## 🔍 Solução de Problemas

### Erro: `401 User not found`

**Causa:** `OPENROUTER_API_KEY` não configurada ou inválida.

**Solução:**
```bash
# 1. Verifique se a chave está no .env
cat .env | grep OPENROUTER_API_KEY

# 2. Se não estiver, configure:
echo "OPENROUTER_API_KEY=sk-or-v1-sua-chave-aqui" >> .env

# 3. Reinicie o backend
docker compose restart backend
```

### Erro: Frontend retorna 500

**Causa:** Problema de CSS/Tailwind ou dependências não instaladas.

**Solução:**
```bash
# Reconstruir o frontend
docker compose up -d --build frontend
```

### Erro: Container não sobe

```bash
# Verificar logs
docker compose logs <serviço>

# Exemplos:
docker compose logs backend
docker compose logs frontend
docker compose logs postgres
```

### Erro: Porta já em uso

```bash
# Verificar o que está usando a porta
sudo lsof -i :8000
sudo lsof -i :3000
sudo lsof -i :5432

# Parar o processo ou mudar a porta no docker-compose.yml
```

### Resetar tudo

```bash
# Parar e remover todos os containers e volumes
docker compose down -v

# Reconstruir e subir
docker compose up -d --build
```

---

## 📋 Roadmap

### ✅ MVP (V1) — Concluído

- [x] Estrutura de diretórios completa
- [x] Docker Compose com PostgreSQL, Redis, Qdrant
- [x] Backend FastAPI com rotas de health, agents, projects
- [x] Frontend Next.js com TailwindCSS
- [x] Serviço OpenRouter para acesso a modelos de IA
- [x] Orchestrator Agent com decomposição de tarefas
- [x] 5 agentes especializados (Architect, Backend, Frontend, Docs, Reviewer)
- [x] 5 MCP Tools (Git, Docker, Python, Bash, PostgreSQL)
- [x] Testes automatizados
- [x] Documentação ADR

### 🔜 V2 — Próximas Features

- [ ] **RAG com Qdrant** — Indexação de documentações técnicas e RFCs para busca semântica
- [ ] **Autenticação JWT** — Login, registro e proteção de rotas
- [ ] **Streaming via WebSocket** — Respostas em tempo real dos agentes
- [ ] **Execução Paralela** — Agentes rodando simultaneamente
- [ ] **Interface Visual** — Dashboard para configurar e monitorar agentes
- [ ] **CI/CD Pipeline** — Integração contínua e deploy automatizado
- [ ] **Histórico de Sessões** — Conversas multi-turn com os agentes

---

## 📄 Arquitetura de Decisões (ADRs)

As decisões arquiteturais são documentadas em `docs/`:

| ADR | Título | Descrição |
|-----|--------|-----------|
| [ADR-001](docs/ADR-001-arquitetura-mvp.md) | Arquitetura do MVP | Stack, agentes, fluxo de dados, MCP Tools |
| [ADR-002](docs/ADR-002-estrategia-containerizacao.md) | Estratégia de Containerização | Serviços, volumes, healthchecks, variáveis de ambiente |

---

## 🤝 Contribuindo

1. Leia os ADRs em `docs/` para entender as decisões arquiteturais
2. Crie uma branch: `git checkout -b feature/nova-feature`
3. Faça suas alterações
4. Execute os testes: `docker compose exec backend pytest tests/ -v`
5. Commit: `git commit -m "feat: descrição da mudança"`
6. Push: `git push origin feature/nova-feature`
7. Abra um Pull Request

---

## 📝 Licença

MIT License — veja o arquivo [LICENSE](LICENSE) para detalhes.

---

<p align="center">
  <strong>NAP — Nexus AI Platform</strong><br>
  <em>Engenharia de Software potencializada por Inteligência Artificial</em>
</p>