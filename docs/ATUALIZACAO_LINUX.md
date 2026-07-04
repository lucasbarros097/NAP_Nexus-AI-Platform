# 🔄 Atualização do NAP no Linux (Ubuntu/Debian)

Este guia explica como atualizar o NAP instalado via pacote `.deb` no Ubuntu/Debian.

## 📋 Pré-requisitos

- NAP instalado via pacote `.deb`
- Acesso `sudo` no sistema
- Novo arquivo `.deb` compilado (veja `build.sh`)

## 🚀 Processo de Atualização

### Opção 1: Usar o script automatizado (Recomendado)

O projeto inclui um script automatizado que faz todo o processo de atualização:

```bash
# Executar o script de atualização
sudo ./docs/update_linux.sh
```

O script irá:
1. ✅ Verificar a versão atual instalada
2. ✅ Fazer backup do binário atual
3. ✅ Instalar o novo pacote `.deb`
4. ✅ Verificar a nova versão
5. ✅ Limpar arquivos temporários

### Opção 2: Atualização manual

Se preferir fazer manualmente, siga estes passos:

#### 1. Verificar versão atual

```bash
dpkg -l | grep nap-nexus
```

Saída esperada:
```
ii  nap-nexus  0.1.0-1  amd64  NAP - Nexus AI Platform
```

#### 2. Fazer backup (opcional, mas recomendado)

```bash
sudo cp /usr/local/bin/nap /usr/local/bin/nap.backup
```

#### 3. Instalar o novo pacote

```bash
sudo dpkg -i dist/nap_0.2.0-1_amd64.deb
```

O `dpkg` irá:
- Sobrescrever a versão anterior
- Manter as configurações existentes
- Executar o script pós-instalação

#### 4. Verificar nova versão

```bash
dpkg -l | grep nap-nexus
```

Saída esperada:
```
ii  nap-nexus  0.2.0-1  amd64  NAP - Nexus AI Platform
```

#### 5. Testar a instalação

```bash
nap
```

## 🔧 Solução de Problemas

### Erro: "dpkg: error: requested operation requires superuser privilege"

**Causa:** O comando precisa ser executado com `sudo`

**Solução:**
```bash
sudo dpkg -i dist/nap_0.2.0-1_amd64.deb
```

### Erro: "package nap-nexus is not installed"

**Causa:** O NAP não está instalado via `.deb`

**Solução:** É uma nova instalação, não uma atualização:
```bash
sudo dpkg -i dist/nap_0.2.0-1_amd64.deb
```

### Erro: "Dependencies are not satisfied"

**Causa:** Faltam dependências (Docker, Docker Compose)

**Solução:** Instale as dependências:
```bash
sudo apt update
sudo apt install docker.io docker-compose
```

### Comando `nap` não encontrado após atualização

**Causa:** O PATH não inclui `/usr/local/bin`

**Solução:**
```bash
# Verificar onde está instalado
which nap

# Se não estiver no PATH, adicione ao seu ~/.bashrc
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

## 📊 Comparação: Instalação vs Atualização

| Operação | Comando | O que acontece |
|----------|---------|----------------|
| **Nova Instalação** | `sudo dpkg -i nap.deb` | Instala o pacote pela primeira vez |
| **Atualização** | `sudo dpkg -i nap.deb` | Sobrescreve a versão anterior |
| **Remoção** | `sudo dpkg -r nap-nexus` | Remove o pacote mas mantém configs |
| **Remoção Completa** | `sudo dpkg -P nap-nexus` | Remove pacote e arquivos de configuração |

## 🔄 Fluxo Completo de Atualização

```bash
# 1. Compilar nova versão
./build.sh --linux

# 2. Verificar versão atual
dpkg -l | grep nap-nexus

# 3. Atualizar (manual ou script)
sudo dpkg -i dist/nap_0.2.0-1_amd64.deb
# OU
sudo ./docs/update_linux.sh

# 4. Verificar nova versão
dpkg -l | grep nap-nexus

# 5. Testar
nap
```

## 📝 Notas Importantes

- **Backup automático:** O script de atualização cria backup automaticamente
- **Configurações preservadas:** Atualizações via `.deb` mantêm suas configurações
- **Rollback:** Se algo der errado, você pode restaurar o backup:
  ```bash
  sudo cp /usr/local/bin/nap.backup /usr/local/bin/nap
  ```
- **Dependências:** O `.deb` requer Docker e Docker Compose instalados

## 🎯 Próximos Passos

Após atualizar:
1. Verifique se o Docker está rodando: `docker ps`
2. Inicie a plataforma: `docker compose up -d`
3. Execute o NAP: `nap`

## 📚 Recursos Adicionais

- [Script de build](../build.sh) - Para compilar novas versões
- [Script de atualização](./update_linux.sh) - Para atualizar automaticamente
- [Documentação principal](../README.md) - Informações gerais do projeto
