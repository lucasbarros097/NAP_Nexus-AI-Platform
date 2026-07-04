# ADR-003: Modo Imersivo CLI (Modo Devin)

## Status
**Aprovado** — 2026-07-04

## Contexto
A NAP precisa de uma interface de linha de comando interativa que permita ao usuário manter uma conversa contínua com os agentes de IA, similar ao modo "Devin". O terminal não deve apenas disparar comandos e morrer, mas sim manter um shell persistente com histórico, streaming de logs e aprovações antes de modificar arquivos.

## Decisão

### Arquitetura do CLI
- **Base:** Python `cmd.Cmd` — framework nativo para shells interativos
- **Renderização:** `rich` library para output colorido, tabelas, painéis e spinners
- **Comunicação:** HTTP para o backend FastAPI via `httpx`
- **Entry point:** `nap` via `console_scripts` no `setup.py`

### Comandos Implementados

| Comando | Função |
|---------|--------|
| `chat <mensagem>` | Envia tarefa para o Orchestrator NAP |
| `run <comando>` | Executa comando shell no workspace |
| `status` | Exibe status da plataforma e containers |
| `agents` | Lista agentes disponíveis |
| `projects` | Lista projetos cadastrados |
| `history` | Histórico da sessão atual |
| `logs [svc] [n]` | Logs de containers Docker |
| `clear` | Limpa terminal |
| `exit / quit` | Sai do modo imersivo |

### Fluxo de Aprovação
Antes de executar comandos que criam/alteram arquivos (detectado por palavras-chave como "crie", "gere", "modifique"), o CLI solicita confirmação explícita do usuário:

```
⚠️  Esta operação pode criar/alterar arquivos. Prosseguir? [Y/n]:
```

### Build Multiplataforma

| Plataforma | Formato | Ferramenta |
|-----------|---------|-----------|
| Linux (Ubuntu/Debian) | `.deb` + executável | PyInstaller + dpkg-deb |
| Windows | `.exe` autossuficiente | PyInstaller (via wine ou nativo) |

### Estrutura de Diretórios
```
cli/
├── __init__.py      # Package marker
└── shell.py         # NAPShell class (cmd.Cmd)
setup.py             # Entry point `nap`
build.sh             # Script de build multiplataforma
```

## Consequências
- **Positivas:** Experiência "Devin-like" com chat contínuo, sem necessidade de re-digitar comandos
- **Positivas:** Executável único sem dependências Python para o usuário final
- **Positivas:** Suporte nativo a Linux (.deb) e Windows (.exe)
- **Negativas:** Dependência do backend FastAPI rodando (docker compose up -d)
- **Riscos:** PyInstaller pode aumentar significativamente o tamanho do binário

## Como Usar
```bash
# Modo desenvolvimento (requer Python)
pip install -e .
nap

# Modo produção (executável único)
./dist/nap          # Linux
dist/nap.exe        # Windows

# Build
./build.sh --all    # Linux + Windows