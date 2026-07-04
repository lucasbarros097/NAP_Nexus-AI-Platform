#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Script de Atualização do NAP - Linux (.deb)
# ═══════════════════════════════════════════════════════════════
# Este script demonstra como atualizar o NAP instalado via .deb
#
# Uso:
#   sudo ./docs/update_linux.sh
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DEB_FILE="$PROJECT_DIR/dist/nap_0.2.0-1_amd64.deb"

# ─── Cores ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ─── Funções ──────────────────────────────────────────────────────────────────
info()  { echo -e "${CYAN}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ─── Verificação de root ───────────────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
    error "Este script precisa ser executado como root (sudo)."
    echo "Execute: sudo $0"
    exit 1
fi

# ─── Verificar se o arquivo .deb existe ───────────────────────────────────────
if [ ! -f "$DEB_FILE" ]; then
    error "Arquivo .deb não encontrado: $DEB_FILE"
    echo "Execute primeiro: ./build.sh --linux"
    exit 1
fi

info "Iniciando atualização do NAP..."
echo ""

# ─── 1. Verificar versão atual instalada ─────────────────────────────────────
info "1. Verificando versão atual..."
if dpkg -l | grep -q "nap-nexus"; then
    CURRENT_VERSION=$(dpkg -l | grep "nap-nexus" | awk '{print $3}')
    ok "Versão atual instalada: $CURRENT_VERSION"
else
    warn "NAP não está instalado via .deb. Será uma nova instalação."
fi
echo ""

# ─── 2. Backup do binário atual (se existir) ─────────────────────────────────
info "2. Fazendo backup do binário atual..."
if [ -f "/usr/local/bin/nap" ]; then
    cp /usr/local/bin/nap /usr/local/bin/nap.backup
    ok "Backup criado: /usr/local/bin/nap.backup"
else
    warn "Binário não encontrado em /usr/local/bin/nap"
fi
echo ""

# ─── 3. Instalar/Atualizar o pacote .deb ──────────────────────────────────────
info "3. Instalando o pacote .deb..."
dpkg -i "$DEB_FILE"
ok "Pacote instalado com sucesso"
echo ""

# ─── 4. Verificar nova versão ─────────────────────────────────────────────────
info "4. Verificando nova versão..."
NEW_VERSION=$(dpkg -l | grep "nap-nexus" | awk '{print $3}')
ok "Nova versão instalada: $NEW_VERSION"
echo ""

# ─── 5. Verificar instalação ─────────────────────────────────────────────────
info "5. Verificando instalação..."
if command -v nap &>/dev/null; then
    ok "Comando 'nap' disponível em: $(which nap)"
    ok "Permissões: $(ls -l $(which nap))"
else
    warn "Comando 'nap' não encontrado no PATH"
fi
echo ""

# ─── 6. Limpar backup ────────────────────────────────────────────────────────
info "6. Limpando backup antigo..."
if [ -f "/usr/local/bin/nap.backup" ]; then
    rm /usr/local/bin/nap.backup
    ok "Backup removido"
fi
echo ""

# ─── Resumo ──────────────────────────────────────────────────────────────────
echo "╔══════════════════════════════════════════════╗"
echo "║   ✅ Atualização Concluída!                ║"
echo "╚══════════════════════════════════════════════╝"
echo ""
echo "Versão instalada: $NEW_VERSION"
echo ""
echo "Para usar o NAP:"
echo "  nap"
echo ""
echo "Para verificar o status:"
echo "  dpkg -l | grep nap-nexus"
echo ""
