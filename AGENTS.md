# Configurações do Devin CLI para Projeto NAP

## 📋 Informações do Projeto

**Projeto:** NAP - Nexus AI Platform  
**Caminho:** `/home/ghost/Documents/Projetos/0 - NAP_Nexus AI Platform`  
**Stack:** Python/FastAPI (Backend) + React/Next.js (Frontend) + Docker Compose

## 🔧 Configurações Aplicadas

### 1. Permissões Completas (`.devin/config.json`)
```json
{
  "permissions": {
    "allow": [
      "Read(**)",
      "Write(**)",
      "Exec(**)"
    ],
    "deny": [],
    "ask": []
  },
  "agent": {
    "model": "swe-1-6-fast"
  }
}
```

### 2. Configurações Globais (`~/.config/devin/config.json`)
```json
{
  "show_path": true,
  "show_hints": true,
  "notify": "always",
  "agent": {
    "model": "swe-1-6-fast"
  }
}
```

## 🎯 Comandos Úteis do Devin CLI

### Visualização e Feedback
- `Ctrl+O` - Abrir visualizador de pensamento em tela cheia (para ver o que o agente está pensando)
- `Alt+T` (macOS: `Opt+T`) - Ciclar níveis de thinking do modelo
- `/model` - Mostrar seletor de modelos
- `/mode` - Mostrar modo atual
- `Shift+Tab` - Alternar entre modos (Normal, Accept Edits, Plan, Bypass)

### Modelos Disponíveis
- `swe-1-6-fast` - Modelo atual (rápido, bom para tarefas simples)
- `swe-1-6` - Versão completa do SWE (mais inteligente)
- `opus` - Para tarefas complexas e refatoração
- `sonnet` - Balanceado entre velocidade e capacidade
- `gpt` - Modelo GPT da OpenAI

### Modos de Permissão
- `/normal` - Modo padrão (auto-aprova leitura, pergunta para escrita/execução)
- `/accept-edits` - Auto-aprova edições de arquivos
- `/bypass` - Auto-aprova tudo (cuidado!)
- `/plan` - Modo planejamento (não faz mudanças)
- `/ask <pergunta>` - Pergunta sem fazer mudanças

## 🚀 Comandos do Projeto NAP

### Docker Compose
```bash
# Subir todos os serviços
docker compose up -d --build

# Parar todos os serviços
docker compose down

# Ver logs de um serviço
docker compose logs backend
docker compose logs frontend

# Reiniciar um serviço
docker compose restart backend

# Executar comando no container
docker compose exec backend bash
docker compose exec backend pytest tests/ -v
```

### Testes
```bash
# Executar testes do backend
docker compose exec backend pytest tests/ -v

# Testar health check
curl http://localhost:8000/health

# Testar frontend
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000
```

### Build e Atualização
```bash
# Compilar versão para Linux (.deb)
./build.sh --linux

# Compilar versão para Windows (.exe)
./build.sh --windows

# Compilar para todas as plataformas
./build.sh --all

# Atualizar NAP instalado via .deb (Ubuntu/Debian)
sudo ./docs/update_linux.sh

# OU atualização manual
sudo dpkg -i dist/nap_0.2.0-1_amd64.deb
```

### Serviços
- **Frontend:** http://localhost:3000
- **API (FastAPI):** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Qdrant Dashboard:** http://localhost:6333/dashboard

## 📝 Estrutura do Projeto

```
backend/          # Python/FastAPI
frontend/         # React/Next.js
agents/           # Definições dos agentes IA
mcp/              # MCP Tools (Git, Docker, Python, Bash, PostgreSQL)
knowledge/        # Base de conhecimento
workspace/        # Código gerado pelos agentes
docs/             # Documentação técnica
logs/             # Logs da aplicação
tests/            # Testes
cli/v2/           # NAP V2 - Agente Local + TUI Hacker
```

## 🔑 Configuração OpenRouter

O projeto usa OpenRouter com modelo `openrouter/free` configurado no `.env`:
```
OPENROUTER_API_KEY=sk-or-v1-***
OPENROUTER_MODEL=openrouter/free
```

## ✅ Testes de Acesso Realizados

- ✅ Leitura do README.md
- ✅ Leitura de arquivos de configuração
- ✅ Criação de arquivo de teste
- ✅ Exclusão de arquivo de teste
- ✅ Execução de comandos shell

O Devin agora tem acesso completo ao projeto NAP e pode ler, escrever, criar e excluir arquivos e pastas conforme necessário.

## 🚀 NAP V2 - Agente Local + TUI Hacker

### Visão Geral

NAP V2 é a versão 2 da Nexus AI Platform, focada em um agente local com interface TUI (Terminal User Interface) hacker.

### Equipe

- **Victor** - Arquitetura e coordenação
- **Theo** - Ferramentas do agente (I/O e Shell)
- **Linus** - Interface TUI hacker
- **Ada** - Integração com modelos de IA (pendente)
- **Alice** - Sistema de segurança e aprovação de comandos perigosos

### Características

- Interface TUI hacker com Rich + prompt-toolkit
- Paleta Cyberpunk: Ciano, Cinza, Vermelho, Âmbar (SEM verde)
- Spinner de status com nome do modelo
- Slash commands: /model, /exit, /stop, /resume, /clear
- Ferramentas: read_file, write_file, replace_in_file, create_directory, delete_file, delete_directory, list_directory, execute_shell
- Regra da Alice: aprovação Y/N para comandos perigosos

### Execução

```bash
# Instalar dependências
cd cli/v2
pip install -r requirements.txt

# Executar testes
python cli/v2/test_tui.py

# Executar TUI interativa
python cli/v2/run_interactive.py
```

### Documentação

Veja `cli/v2/README.md` para documentação completa e `cli/v2/IMPLEMENTACAO.md` para detalhes da implementação.

## 📦 Atualização do NAP

### Documentação de Atualização

Para atualizar o NAP instalado via `.deb` no Ubuntu/Debian, consulte:
- **Guia completo:** `docs/ATUALIZACAO_LINUX.md`
- **Script automatizado:** `docs/update_linux.sh`
- **Demonstração interativa:** `./docs/demo_update.sh`

### Resumo Rápido

```bash
# 1. Compilar nova versão
./build.sh --linux

# 2. Atualizar (automático - recomendado)
sudo ./docs/update_linux.sh

# 3. Verificar versão
dpkg -l | grep nap-nexus

# 4. Testar
nap
```

### Arquivos Gerados

- `dist/nap` - Executável Linux
- `dist/nap_0.2.0-1_amd64.deb` - Pacote Debian/Ubuntu
- `dist/nap.exe` - Executável Windows (quando compilado)