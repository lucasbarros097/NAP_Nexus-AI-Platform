"""
NAP V2 — Entry Point
=====================

Ponto de entrada principal para a NAP V2 (Agente Local e TUI Hacker).

Uso:
    python -m cli.v2.main
    nap-v2          (após instalação via pip)
"""

import sys
import logging
from pathlib import Path

# ─── Configura logging ─────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stderr),
    ],
)

# Suprime logs muito verbosos de bibliotecas
logging.getLogger("prompt_toolkit").setLevel(logging.WARNING)
logging.getLogger("rich").setLevel(logging.WARNING)


def main():
    """Entry point principal da NAP V2."""
    from .tui import main as tui_main
    tui_main()


if __name__ == "__main__":
    main()