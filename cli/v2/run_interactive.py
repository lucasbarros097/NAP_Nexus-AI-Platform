#!/usr/bin/env python3
"""
Script para executar a NAP V2 TUI em modo interativo.
Este é um wrapper conveniente para testar a interface.
"""

import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar o módulo
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def main():
    """Executa a TUI interativa."""
    print("Iniciando NAP V2 TUI...")
    print("Pressione Ctrl+C para sair.\n")
    
    try:
        from cli.v2.tui import main as tui_main
        tui_main()
    except KeyboardInterrupt:
        print("\n\nNAP V2 encerrado pelo usuário.")
        return 0
    except Exception as e:
        print(f"\nErro ao iniciar TUI: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
