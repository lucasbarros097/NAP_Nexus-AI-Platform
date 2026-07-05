# 📐 Diagramas de Arquitetura - NAP Platform

Esta pasta contém os diagramas de arquitetura da plataforma NAP (Nexus AI Platform) em formato Mermaid.

## 📊 Diagramas Disponíveis

| Diagrama | Arquivo | Descrição |
|----------|--------|-----------|
| **Arquitetura Geral** | `01-arquitetura-geral.mmd` | Visão completa da arquitetura do sistema com todas as camadas |
| **Fluxo de Agentes** | `02-fluxo-agentes.mmd` | Sequência detalhada de interação entre os agentes |
| **Modelo de Dados** | `03-modelo-dados.mmd` | Diagrama Entidade-Relacionamento do banco de dados |
| **Fluxo de Dados** | `04-fluxo-dados.mmd` | Pipeline de processamento de informações |
| **Deploy & Infra** | `05-deploy-infra.mmd` | Arquitetura de produção e escala |

## 🛠️ Como Visualizar

### Opção 1: GitHub/GitLab
Os diagramas Mermaid são renderizados automaticamente no GitHub e GitLab. Basta abrir os arquivos `.mmd` diretamente no navegador.

### Opção 2: VS Code
1. Instale a extensão [Mermaid Preview](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid)
2. Abra o arquivo `.mmd`
3. Pressione `Ctrl+Shift+V` (Windows/Linux) ou `Cmd+Shift+V` (Mac) para visualizar

### Opção 3: Mermaid Live Editor
1. Acesse [https://mermaid.live](https://mermaid.live)
2. Copie o conteúdo do arquivo `.mmd`
3. Cole no editor para visualizar

### Opção 4: CLI (mermaid-cli)
```bash
# Instalar
npm install -g @mermaid-js/mermaid-cli

# Gerar PNG
mmdc -i 01-arquitetura-geral.mmd -o arquitetura-geral.png

# Gerar SVG
mmdc -i 01-arquitetura-geral.mmd -o arquitetura-geral.svg
```

## 📝 Convenções

### Cores
- **Azul (#3b82f6)**: Usuário/Interface
- **Roxo (#8b5cf6)**: Orquestração/Planejamento
- **Verde (#10b981)**: Execução/Desenvolvimento
- **Âmbar (#f59e0b)**: Revisão/Documentação
- **Vermelho (#ef4444)**: Decisões/Alertas
- **Ciano (#06b6d4)**: Dados/Armazenamento

### Ícones
- 👤 Usuário/Engenheiro
- 🧠 Inteligência/Orquestração
- 💻 Backend/Desenvolvimento
- 🎨 Frontend/Interface
- 🔍 Revisão/Segurança
- 📝 Documentação
- 💾 Armazenamento/Dados
- 🚀 API/Serviços

## 🔄 Atualização

Ao modificar a arquitetura do sistema, atualize os diagramas correspondentes para manter a documentação sincronizada.

---

**NAP - Nexus AI Platform**