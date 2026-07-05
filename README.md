<div align="center">

# NAP — Nexus AI Platform

### Plataforma de Engenharia de Software por Inteligência Artificial

<p>
<img alt="Python" src="https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python">
<img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0052CC?logo=fastapi">
<img alt="React" src="https://img.shields.io/badge/React-18-61DAFB?logo=react">
<img alt="Next.js" src="https://img.shields.io/badge/Next.js-14-000000?logo=nextdotjs">
<img alt="Docker" src="https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker">
<img alt="PostgreSQL" src="https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql">
<img alt="Redis" src="https://img.shields.io/badge/Redis-7-DC382D?logo=redis">
<img alt="OpenRouter" src="https://img.shields.io/badge/OpenRouter-IA-10B981">
</p>

> Orquestração de agentes especializados para arquitetura, código, documentação e revisão em um único fluxo.

</div>

---

## O que a NAP faz

<div align="center">

| Recurso | Descrição |
|---------|-----------|
| **Orquestrador de IA** | Decompõe tarefas complexas e coordena agentes especializados |
| **Multiagentes** | Backend, Frontend, Docs, Reviewer e Architect |
| **Interface Web** | Painel Next.js para execução, status e acompanhamento |
| **API Documentada** | FastAPI com Swagger e ReDoc |
| **CLI Imersiva** | Terminal interativo estilo Devin com aprovações |
| **OpenRouter** | Integração real com modelos gratuitos como DeepSeek, Qwen, Mistral e Llama |
| **Infra Pronta** | Suba tudo com Docker Compose em um comando |

</div>

---

## Arquitetura

```text
                          Usuário / Operador
                                   │
           ┌───────────────────────┴───────────────────────┐
           │                                               │
        Navegador                                      Terminal
           │                                               │
           ▼                                               ▼
 ┌──────────────────┐                          ┌───────────────────┐
 │  Frontend Web    │                          │  CLI / TUI Hacker │
 │  Next.js 14      │                          │  Rich + Prompt    │
 │  Porta 3000      │                          │  nap-tui / nap-v2 │
 └────────┬─────────┘                          └────────┬──────────┘
          │                                               │
          │ HTTP / WebSocket                              │ API / CLI
          └──────────────────────┬──────────────────────┘
                                 ▼
                     ┌─────────────────────┐
                     │      FastAPI        │
                     │    Backend API      │
                     │    Porta 8000       │
                     └──────────┬──────────┘
                                │
                ┌───────────────┼───────────────┐
                ▼               ▼               ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │ Orchestrator │ │  Services    │ │  MCP Tools   │
      │  Architect   │ │ OpenRouter   │ │ Git / Docker │
      │  Decomposição│ │ Cron / Task  │ │ Python / Bash│
      └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
             │                │                │
             ▼                ▼                ▼
       ┌──────────────────────────────────────────┐
       │               OpenRouter                │
       │  deepseek / qwen / mistral / llama      │
       └──────────────────────┬──────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
      ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
      │  Backend     │ │  Frontend    │ │  Reviewer    │
      │  Agent       │ │  Agent       │ │  Agent       │
      └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
             │                │                │
             ▼                ▼                ▼
       ┌──────────────────────────────────────────┐
       │            Banco de Dados                │
       │  Postgres / Redis / Qdrant / FileSystem  │
       └──────────────────────────────────────────┘
```

---

## Fluxo

```text
Requisito em linguagem natural
     │
     ▼
Orchestrator analisa e quebra em tarefas
     │
     ▼
Agentes especializados geram código / docs / revisão
     │
     ▼
MCP Tools aplicam mudanças com segurança
     │
     ▼
Resultado consolidado para o usuário
```

---

## Stack

<details>
<summary><strong>Backend</strong></summary>

- Python 3.10+
- FastAPI
- SQLAlchemy + Alembic
- Pydantic v2
- Uvicorn
- httpx

</details>

<details>
<summary><strong>Frontend</strong></summary>

- React 18
- Next.js 14
- TypeScript
- TailwindCSS
- Lucide React
- CVA + clsx + tailwind-merge

</details>

<details>
<summary><strong>Dados</strong></summary>

- PostgreSQL 16
- Redis 7
- Qdrant

</details>

<details>
<summary><strong>IA</strong></summary>

- OpenRouter API
- Modelos gratuitos: DeepSeek, Qwen, Mistral, Llama

</details>

<details>
<summary><strong>Infra</strong></summary>

- Docker
- Docker Compose

</details>

<details>
<summary><strong>CLI / TUI</strong></summary>

- Rich
- prompt-toolkit

</details>

<details>
<summary><strong>Distribuição</strong></summary>

- PyInstaller
- Linux `.deb`
- Windows `.exe`
- macOS `.app`

</details>

---

## Download e Instalação

### Linux

```bash
sudo dpkg -i dist-pkg/nap-nexus_*_all.deb
sudo apt-get install -f
nap-tui
```

```bash
chmod +x install.sh
./install.sh
nap-tui
```

### Windows

```powershell
# executável gerado pelo build
.\dist-pkg\nap.exe
```

```bash
python3 -m venv venv
./venv/bin/pip install .
python -m cli.v2.main
```

---

## Pré-requisitos

| Ferramenta | Versão mínima | Verificar |
|-----------|--------------|----------|
| Docker | 24+ | `docker --version` |
| Docker Compose | v2+ | `docker compose version` |
| Git | 2.x | `git --version` |
| Python | 3.10+ | `python3 --version` |
| Node | 18+ | `node --version` |
| OpenRouter API Key | — | https://openrouter.ai/keys |

> OpenRouter oferece modelos gratuitos sem cartão.

---

## Execução

```bash
# 1. Clone o repositório
git clone <repo> && cd "<repo>"

# 2. Configure o ambiente
cp .env.example .env

# 3. Suba a plataforma
docker compose up -d --build

# 4. Acesse
# Frontend:  http://localhost:3000
# API:       http://localhost:8000
# Docs:      http://localhost:8000/docs
# Qdrant:    http://localhost:6333/dashboard
```

```bash
# Verificação rápida
curl http://localhost:8000/health

# Parar tudo
docker compose down
```

---

## Como usar

### Web
Acesse `http://localhost:3000` para ver status, endpoints e painel de acompanhamento.

### API
Acesse `http://localhost:8000/docs` para chamadas interativas.

### Terminal
```bash
./nap.sh
nap-tui
python -m cli.v2.main
```

---

## Dev

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## Projeto

```text
backend/           API FastAPI
frontend/          Painel web
agents/            Agentes especializados
mcp/               Ferramentas MCP
cli/               CLI e TUI
docs/              ADRs e materiais
build.sh           Build multiplataforma
install.sh         Instalador local
nap.spec           Spec PyInstaller
setup.py           Entrada do pacote
```

---

## Segurança

- Comandos perigosos pedem aprovação `Y/N` antes de executar
- Integração com OpenRouter via token em `.env`
- Build assinado para distribuição

---

## Próximos passos

- RAG com Qdrant
- Autenticação JWT
- Streaming via WebSocket
- Execução paralela de agentes
- Histórico multi-sessão
- Multi-modelo em runtime

---

<div align="center">

NAP — Nexus AI Platform<br>
Engenharia de Software potencializada por Inteligência Artificial

</div>