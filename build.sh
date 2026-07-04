#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════
# Build Script for NAP CLI — Multiplataforma
# ═══════════════════════════════════════════════════════════════
# Gera executáveis autossuficientes para Linux (.deb) e Windows (.exe)
# usando PyInstaller.
#
# Uso:
#   ./build.sh              # Build para plataforma atual
#   ./build.sh --all        # Build para Linux + Windows (requer cross)
#   ./build.sh --linux      # Apenas Linux .deb
#   ./build.sh --windows    # Apenas Windows .exe
# ═══════════════════════════════════════════════════════════════

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Usar virtual environment existente
VENV_DIR="$SCRIPT_DIR/NAP_Nexus"
PYTHON_BIN="$VENV_DIR/bin/python"
PIP_BIN="$VENV_DIR/bin/pip"

# ─── Cores ────────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ─── Configurações ────────────────────────────────────────────────────────────
APP_NAME="nap"
VERSION="0.2.0"
DIST_DIR="$SCRIPT_DIR/dist"
BUILD_DIR="$SCRIPT_DIR/build"
SPEC_FILE="$SCRIPT_DIR/nap.spec"
DEB_DIR="$DIST_DIR/deb"
ICON_FILE="$SCRIPT_DIR/cli/icon.png"  # Optional icon

# ─── Funções ──────────────────────────────────────────────────────────────────

info()  { echo -e "${CYAN}[INFO]${NC} $1"; }
ok()    { echo -e "${GREEN}[OK]${NC}   $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

check_dependencies() {
    info "Verificando dependências..."
    
    # Verificar virtual environment
    if [ ! -d "$VENV_DIR" ]; then
        error "Virtual environment não encontrado em $VENV_DIR"
    fi
    ok "Virtual environment: $VENV_DIR"
    
    # Python
    ok "Python: $($PYTHON_BIN --version)"
    
    # PyInstaller
    if ! "$PYTHON_BIN" -c "import PyInstaller" 2>/dev/null; then
        info "Instalando PyInstaller..."
        "$PIP_BIN" install pyinstaller
    fi
    ok "PyInstaller: $($PYTHON_BIN -m PyInstaller --version 2>/dev/null || echo 'instalado')"
    
    # Rich (para CLI)
    if ! "$PYTHON_BIN" -c "import rich" 2>/dev/null; then
        info "Instalando rich..."
        "$PIP_BIN" install rich httpx
    fi
    ok "Dependências Python instaladas"
    
    # Docker (opcional, para build .deb)
    if command -v docker &>/dev/null; then
        ok "Docker disponível"
    else
        warn "Docker não encontrado (opcional para build .deb)"
    fi
    
    # fpm (opcional, para build .deb)
    if command -v fpm &>/dev/null; then
        ok "fpm disponível"
    else
        warn "fpm não encontrado (opcional para build .deb)"
    fi
}

build_linux() {
    info "🔧 Compilando para Linux..."
    
    mkdir -p "$DIST_DIR"
    
    # PyInstaller: gera executável único
    "$PYTHON_BIN" -m PyInstaller \
        --onefile \
        --name "$APP_NAME" \
        --distpath "$DIST_DIR" \
        --workpath "$BUILD_DIR" \
        --add-data "cli:cli" \
        --hidden-import "httpx" \
        --hidden-import "rich" \
        --hidden-import "rich.console" \
        --hidden-import "rich.markdown" \
        --hidden-import "rich.table" \
        --hidden-import "rich.panel" \
        --hidden-import "rich.syntax" \
        --hidden-import "rich.prompt" \
        --hidden-import "rich.progress" \
        --hidden-import "rich.box" \
        --collect-all "rich" \
        --clean \
        cli/shell.py
    
    # Renomear para nome correto
    if [ -f "$DIST_DIR/shell" ]; then
        mv "$DIST_DIR/shell" "$DIST_DIR/$APP_NAME"
    fi
    
    if [ -f "$DIST_DIR/$APP_NAME" ]; then
        chmod +x "$DIST_DIR/$APP_NAME"
        ok "✅ Linux executável criado: $DIST_DIR/$APP_NAME"
        ls -lh "$DIST_DIR/$APP_NAME"
    else
        error "Falha ao gerar executável Linux"
    fi
}

build_deb() {
    info "📦 Empacotando .deb para Ubuntu/Debian..."
    
    local DEB_VERSION="${VERSION}-1"
    local DEB_DIR="$DIST_DIR/nap_${DEB_VERSION}_amd64"
    local DEB_FILE="$DIST_DIR/nap_${DEB_VERSION}_amd64.deb"
    
    mkdir -p "$DEB_DIR/usr/local/bin"
    mkdir -p "$DEB_DIR/DEBIAN"
    
    # Copiar binário
    cp "$DIST_DIR/$APP_NAME" "$DEB_DIR/usr/local/bin/"
    chmod 755 "$DEB_DIR/usr/local/bin/$APP_NAME"
    
    # Criar arquivo de controle
    cat > "$DEB_DIR/DEBIAN/control" << EOF
Package: nap-nexus
Version: $DEB_VERSION
Section: devel
Priority: optional
Architecture: amd64
Depends: docker (>= 24.0), docker-compose (>= 2.0)
Maintainer: NAP Team <nap@nexus.ai>
Description: NAP - Nexus AI Platform
 CLI interativo para orquestração de agentes de IA.
 Modo Imersivo com chat contínuo, streaming de logs
 e aprovação de alterações em arquivos.
Homepage: https://github.com/nap-nexus
EOF
    
    # Criar script pós-instalação
    cat > "$DEB_DIR/DEBIAN/postinst" << 'EOF'
#!/bin/sh
set -e
echo "🧠 NAP - Nexus AI Platform instalado!"
echo "Digite 'nap' para iniciar o Modo Imersivo."
echo ""
echo "📋 Primeiros passos:"
echo "  1. Configure sua chave OpenRouter: export OPENROUTER_API_KEY=sk-or-v1-..."
echo "  2. Inicie a plataforma: docker compose up -d"
echo "  3. Entre no CLI: nap"
EOF
    chmod 755 "$DEB_DIR/DEBIAN/postinst"
    
    # Construir .deb
    if command -v dpkg-deb &>/dev/null; then
        dpkg-deb --build "$DEB_DIR" "$DEB_FILE"
        ok "✅ Pacote .deb criado: $DEB_FILE"
        ls -lh "$DEB_FILE"
    elif command -v fpm &>/dev/null; then
        fpm -s dir -t deb -n nap-nexus -v "$VERSION" \
            --prefix /usr/local/bin \
            "$DIST_DIR/$APP_NAME=nap"
        ok "✅ Pacote .deb criado via fpm"
    else
        warn "dpkg-deb não encontrado. Instale: sudo apt install dpkg-dev"
        warn "Pulando criação do .deb"
    fi
    
    # Limpar
    rm -rf "$DEB_DIR"
}

build_windows() {
    info "🪟 Compilando para Windows..."
    
    mkdir -p "$DIST_DIR"
    
    # Verificar se está no Linux com wine ou no Windows
    if command -v wine &>/dev/null && command -v wine64 &>/dev/null; then
        info "Usando wine para build cross-platform Windows..."
        
        # Verificar se PyInstaller está disponível via wine
        if ! wine python -c "import PyInstaller" 2>/dev/null; then
            info "Instalando PyInstaller via wine..."
            wine pip install pyinstaller rich httpx
        fi
        
        wine python -m PyInstaller \
            --onefile \
            --name "${APP_NAME}.exe" \
            --distpath "$DIST_DIR" \
            --workpath "$BUILD_DIR/windows" \
            --hidden-import "httpx" \
            --hidden-import "rich" \
            --collect-all "rich" \
            --clean \
            cli/shell.py
        
        if [ -f "$DIST_DIR/${APP_NAME}.exe" ]; then
            ok "✅ Windows executável criado: $DIST_DIR/${APP_NAME}.exe"
            ls -lh "$DIST_DIR/${APP_NAME}.exe"
        else
            error "Falha ao gerar executável Windows"
        fi
    else
        warn "wine não encontrado. Para build Windows em Linux: sudo apt install wine wine64"
        warn "Ou execute o build diretamente no Windows."
        
        # Criar script de build para Windows
        cat > "$DIST_DIR/build_windows.bat" << 'EOF'
@echo off
echo 🪟 Build NAP para Windows
echo ============================
echo.
echo Instalando dependencias...
pip install pyinstaller rich httpx
echo.
echo Compilando...
pyinstaller --onefile --name nap.exe --distpath dist --hidden-import httpx --hidden-import rich --collect-all rich --clean cli/shell.py
echo.
echo ✅ Executavel criado: dist\nap.exe
pause
EOF
        ok "Script de build Windows criado: $DIST_DIR/build_windows.bat"
    fi
}

clean() {
    info "🧹 Limpando diretórios de build..."
    rm -rf "$BUILD_DIR" "$SPEC_FILE" 2>/dev/null || true
    ok "Limpeza concluída"
}

# ─── Main ─────────────────────────────────────────────────────────────────────

main() {
    echo ""
    echo "╔══════════════════════════════════════════════╗"
    echo "║   NAP Build — Multiplataforma               ║"
    echo "║   v${VERSION}                                   ║"
    echo "╚══════════════════════════════════════════════╝"
    echo ""
    
    # Parse arguments
    local BUILD_ALL=false
    local BUILD_LINUX=false
    local BUILD_WIN=false
    
    if [ $# -eq 0 ]; then
        BUILD_LINUX=true
    fi
    
    for arg in "$@"; do
        case "$arg" in
            --all)    BUILD_ALL=true ;;
            --linux)  BUILD_LINUX=true ;;
            --windows) BUILD_WIN=true ;;
            --clean)  clean; exit 0 ;;
            --help)
                echo "Uso: $0 [--all|--linux|--windows|--clean|--help]"
                exit 0
                ;;
            *)
                error "Argumento desconhecido: $arg. Use --help para ajuda."
                ;;
        esac
    done
    
    if [ "$BUILD_ALL" = true ]; then
        BUILD_LINUX=true
        BUILD_WIN=true
    fi
    
    # Check dependencies
    check_dependencies
    
    # Clean before build
    clean
    
    # Build
    if [ "$BUILD_LINUX" = true ]; then
        build_linux
        build_deb
    fi
    
    if [ "$BUILD_WIN" = true ]; then
        build_windows
    fi
    
    # Summary
    echo ""
    echo "╔══════════════════════════════════════════════╗"
    echo "║   📦 Build Concluído!                       ║"
    echo "╚══════════════════════════════════════════════╝"
    echo ""
    echo "Artefatos em: $DIST_DIR"
    ls -lh "$DIST_DIR" 2>/dev/null || echo "(vazio)"
    echo ""
    echo "Para instalar localmente via pip:"
    echo "  pip install -e ."
    echo ""
    echo "Para usar o CLI diretamente:"
    echo "  python cli/shell.py"
    echo ""
}

main "$@"