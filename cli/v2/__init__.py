"""
NAP V2 — Agente Local e TUI Hacker
====================================

Módulo principal da NAP V2 com interface TUI cyberpunk usando Rich + prompt-toolkit,
sistema de slash commands, e ferramentas de agente para I/O local e shell.

Equipe:
  - Victor: Arquitetura do CLI e loop interativo
  - Theo: Sistema de ferramentas (tools) do agente
  - Linus: Interface TUI e estilização cyberpunk
  - Ada: Segurança e regra de autorização (Alice)
  - Alice: Supervisão de comandos perigosos
"""

from .tui import NAPV2TUI
from .agent_tools import AgentTools, DangerousCommandError

__all__ = ["NAPV2TUI", "AgentTools", "DangerousCommandError"]