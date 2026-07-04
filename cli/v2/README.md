# NAP V2 - Nexus AI Platform V2

## Visão Geral

NAP V2 é a versão 2 da Nexus AI Platform, focada em um **agente local com interface TUI (Terminal User Interface) hacker**. 

### Equipe

- **Victor** - Arquitetura e coordenação
- **Theo** - Ferramentas do agente (I/O e Shell)
- **Linus** - Interface TUI hacker
- **Ada** - Integração com modelos de IA
- **Alice** - Sistema de segurança e aprovação de comandos perigosos

## Características

### Interface Hacker (TUI)

- **Framework**: Rich + prompt-toolkit
- **Estilo**: Painéis ASCII com bordas quadradas
- **Paleta Cyberpunk**: Ciano, Cinza, Vermelho, Âmbar (SEM verde)
- **Spinner de Status**: Indica "Pensando...", "Carregando contexto...", "Escrevendo arquivo..." com nome do modelo atual

### Sistema de Comandos (Slash Commands)

Autocompletar ao digitar `/`:

- `/model` - Trocar modelo ou ver tokens gastos
- `/exit` - Fechar o processo com segurança
- `/stop` - Cancelar/interromper a task atual do agente
- `/resume` - Retomar a última task interrompida
- `/clear` - Limpar a tela do terminal

### Capacidades do Agente (Theo)

Ferramentas disponíveis:

- `read_file` - Ler arquivos (com suporte a range de linhas)
- `write_file` - Escrever/reescrever arquivos
- `replace_in_file` - Substituir blocos em arquivos
- `create_directory` - Criar pastas
- `delete_file` - Deletar arquivos
- `delete_directory` - Deletar pastas (com opção recursiva)
- `list_directory` - Listar diretórios
- `execute_shell` - Executar comandos shell com captura de output

### Regra da Alice (Segurança)

Comandos de terminal considerados perigosos ou de mutação (rm, apt install, kill, etc.) pausam o agente e exibem um prompt **Y/N** na TUI para autorização do usuário.

Comandos perigosos detectados:
- `rm`, `rmdir` - Remoção
- `apt`, `apt-get`, `dpkg`, `rpm` - Gerenciadores de pacotes
- `kill`, `pkill` - Mata processos
- `systemctl`, `service` - Gerenciamento de serviços
- `chmod`, `chown` - Permissões
- `dd`, `mkfs`, `fdisk` - Operações de disco
- `mount`, `umount` - Montagem
- `shutdown`, `reboot` - Desligamento
- `passwd`, `useradd` - Gerenciamento de usuários
- `wget`, `curl` - Download
- `sudo`, `su` - Escalação de privilégios
- `pip install`, `npm install`, `cargo install` - Instalação de pacotes
- `docker` - Comandos Docker
- E outros...

## Instalação

### Pré-requisitos

- Python 3.10+
- Ubuntu/Linux (testado)

### Dependências

```bash
cd cli/v2
pip install -r requirements.txt
```

## Execução

### Modo Direto

```bash
python -m cli.v2.main
```

### Após Instalação (via pip)

```bash
nap-v2
```

## Estrutura do Código

```
cli/v2/
├── __init__.py          # Init do módulo
├── main.py              # Entry point
├── tui.py               # Interface TUI principal (Linus)
├── agent_tools.py       # Ferramentas do agente (Theo)
├── requirements.txt     # Dependências
└── README.md           # Este arquivo
```

## Arquivos Principais

### main.py

Entry point da aplicação. Configura logging e inicializa a TUI.

### tui.py

Interface TUI hacker implementada com Rich e prompt-toolkit:

- `NAPV2TUI` - Classe principal da TUI
- `StatusSpinner` - Spinner de status com nome do modelo
- `SlashCommandCompleter` - Autocompletar para slash commands
- Cores cyberpunk (ciano, cinza, vermelho, âmbar)
- Painéis ASCII com bordas quadradas

### agent_tools.py

Ferramentas do agente local (Theo):

- `AgentTools` - Classe principal com todas as ferramentas
- `read_file` - Leitura de arquivos
- `write_file` - Escrita de arquivos
- `replace_in_file` - Substituição de blocos
- `create_directory` - Criação de diretórios
- `delete_file` - Deleção de arquivos
- `delete_directory` - Deleção de diretórios
- `list_directory` - Listagem de diretórios
- `execute_shell` - Execução de comandos shell com segurança (Regra da Alice)

## Configuração

O modelo atual é configurado via variável de ambiente `OPENROUTER_MODEL` no arquivo `.env`:

```
OPENROUTER_API_KEY=sk-or-v1-***
OPENROUTER_MODEL=openrouter/free
```

## Roadmap

- [ ] Integração com OpenRouter (Ada)
- [ ] Sistema de context window e gerenciamento de tokens
- [ ] Persistência de sessões
- [ ] Modo de agente autônomo (sem interação)
- [ ] Integração com MCP Tools
- [ ] Sistema de plugins/extensões

## Licença

Proprietário - NAP Nexus AI Platform
