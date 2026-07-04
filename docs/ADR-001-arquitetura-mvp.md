# ADR-001: Arquitetura do MVP da NAP (Nexus AI Platform)

## Status
**Aprovado** — 2026-07-03

## Contexto
A NAP precisa de uma arquitetura mínima viável que permita a orquestração de agentes de IA especializados para gerar código de software. A decisão arquitetural prioriza simplicidade, containerização total e baixo acoplamento entre componentes.

## Decisão

### Stack Tecnológica
- **Backend:** Python 3.13 + FastAPI + SQLAlchemy async + Alembic
- **Frontend:** Next.js 14 + TypeScript + TailwindCSS
- **Banco:** PostgreSQL 16 via asyncpg
- **Cache/Mensageria:** Redis 7
- **Vector DB:** Qdrant (presente na infra, sem uso ativo na V1)
- **Infraestrutura:** Docker Compose
- **Modelos:** OpenRouter Free Tier (DeepSeek, Qwen, Mistral, Llama)

### Arquitetura de Agentes
- **Orchestrator**: coordena decomposição de tarefas usando LLM via OpenRouter
- **Backend Agent**: gera código Python/FastAPI via LLM
- **Frontend Agent**: gera código React/Next.js via LLM
- **Documentation Agent**: gera documentação e ADRs
- **Reviewer Agent**: valida código gerado por outros agentes

### Fluxo de Dados
```
Usuário → Frontend (Next.js) → API (FastAPI) → Orchestrator → 
OpenRouter → Agentes Especializados → Resultado → Frontend
```

### MCP Tools (Model Context Protocol)
- **GitTool**: versionamento e operações git
- **DockerTool**: gerenciamento de containers
- **PythonTool**: validação e execução de código Python
- **BashTool**: execução de comandos shell
- **PostgreSQLTool**: operações de banco de dados

## Consequências
- **Positivas:** Stack simples, bem conhecida, fácil de containerizar
- **Negativas:** Execução sequencial de agentes (não paralela na V1)
- **Riscos:** Dependência de API externa (OpenRouter) para funcionamento completo

## Fora do Escopo (V2)
- RAG com Qdrant para busca semântica em documentações
- Autenticação/autorização
- WebSockets para streaming de respostas
- Execução paralela de agentes