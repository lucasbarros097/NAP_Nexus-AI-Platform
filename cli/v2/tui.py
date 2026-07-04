"""
NAP V2 TUI (Linus + Victor) — Interface Hacker Cyberpunk
==========================================================

Interface TUI interativa usando Rich + prompt-toolkit com:
  - Painéis ASCII com bordas quadradas (estilo hacker)
  - Paleta cyberpunk: Ciano, Cinza, Vermelho, Âmbar (SEM verde)
  - Spinner de status com nome do modelo
  - Slash commands com autocomplete (/model, /exit, /stop, /resume, /clear)
  - Chat contínuo com o agente local
  - Regra da Alice: prompt Y/N para comandos perigosos
"""

import os
import sys
import json
import time
import asyncio
import logging
import threading
import signal
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Any

# ─── Rich ──────────────────────────────────────────────────────────────────────
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich import box
from rich.style import Style
from rich.align import Align

# ─── prompt-toolkit ────────────────────────────────────────────────────────────
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style as PtStyle
from prompt_toolkit.formatted_text import HTML

# ─── Módulos internos ──────────────────────────────────────────────────────────
from .agent_tools import AgentTools, DangerousCommandError

logger = logging.getLogger("nap.v2.tui")

# ═══════════════════════════════════════════════════════════════════════════════
# PALETA CYBERPUNK (SEM VERDE)
# ═══════════════════════════════════════════════════════════════════════════════
# Ciano   → #00FFFF (destaque, títulos, comandos)
# Cinza   → #888888 (metadados, timestamps, info secundária)
# Vermelho → #FF3333 (erros, bloqueios, Alice)
# Âmbar   → #FFB000 (avisos, atenção, prompts)
# Branco  → #FFFFFF (texto principal)
# Preto   → #0A0A0A (fundo)

STYLE_CYAN = Style(color="#00FFFF", bold=True)
STYLE_GRAY = Style(color="#888888")
STYLE_RED = Style(color="#FF3333", bold=True)
STYLE_AMBER = Style(color="#FFB000", bold=True)
STYLE_WHITE = Style(color="#FFFFFF")
STYLE_DIM = Style(color="#666666")

# ═══════════════════════════════════════════════════════════════════════════════
# BORDAS QUADRADAS (ASCII HACKER)
# ═══════════════════════════════════════════════════════════════════════════════
# Usamos boxes padrão do Rich com visual ASCII hacker.

ASCII_BOX = box.ASCII  # Borda com caracteres +-|  (estilo ASCII puro)
DOUBLE_BOX = box.DOUBLE  # Borda com caracteres ╔═╗  (estilo double-line)

# ═══════════════════════════════════════════════════════════════════════════════
# BANNER NAP V2
# ═══════════════════════════════════════════════════════════════════════════════

NAP_V2_BANNER = """
╔══════════════════════════════════════════════════════╗
║  ███╗   ██╗ █████╗ ██████╗     ██╗   ██╗██████╗   ║
║  ████╗  ██║██╔══██╗██╔══██╗    ██║   ██║╚════██╗  ║
║  ██╔██╗ ██║███████║██████╔╝    ██║   ██║ █████╔╝  ║
║  ██║╚██╗██║██╔══██║██╔═══╝     ╚██╗ ██╔╝██╔═══╝   ║
║  ██║ ╚████║██║  ██║██║          ╚████╔╝ ███████╗  ║
║  ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝           ╚═══╝  ╚══════╝  ║
║                                                      ║
║  Nexus AI Platform — V2 — Agente Local + TUI Hacker ║
╚══════════════════════════════════════════════════════╝
"""

# ═══════════════════════════════════════════════════════════════════════════════
# COMPLETION: SLASH COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

SLASH_COMMANDS = {
    "/model": "Trocar modelo ou ver tokens gastos",
    "/exit": "Fechar o processo com segurança",
    "/stop": "Cancelar/interromper a task atual do agente",
    "/resume": "Retomar a última task interrompida",
    "/clear": "Limpar a tela do terminal",
}


class SlashCommandCompleter(Completer):
    """
    Autocompletar para slash commands.
    Ao digitar "/", mostra as opções disponíveis.
    """

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if text.startswith("/"):
            for cmd, desc in SLASH_COMMANDS.items():
                if cmd.startswith(text):
                    yield Completion(
                        cmd,
                        start_position=-len(text),
                        display=cmd,
                        display_meta=desc,
                    )


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT-TOOLKIT STYLE
# ═══════════════════════════════════════════════════════════════════════════════

PT_STYLE = PtStyle.from_dict({
    "prompt": "ansicyan bold",
    "completion-menu.completion": "bg:#1a1a2e #00ffff",
    "completion-menu.completion.current": "bg:#00ffff #000000",
    "completion-menu.meta": "bg:#1a1a2e #888888",
    "completion-menu.meta.current": "bg:#00ffff #000000",
    "scrollbar.arrow": "bg:#1a1a2e #00ffff",
    "scrollbar": "bg:#1a1a2e #00ffff",
})


# ═══════════════════════════════════════════════════════════════════════════════
# SPINNER PERSONALIZADO (SEM VERDE)
# ═══════════════════════════════════════════════════════════════════════════════

class StatusSpinner:
    """
    Gerenciador de spinner de status para a TUI.
    Mostra "Pensando...", "Carregando contexto...", "Escrevendo arquivo..."
    com o nome do modelo atual.
    """

    def __init__(self, console: Console):
        self.console = console
        self._spinner = None
        self._thread = None
        self._running = False
        self._message = ""
        self._model_name = "openrouter/free"

    def set_model(self, model_name: str):
        """Atualiza o nome do modelo exibido no spinner."""
        self._model_name = model_name

    def start(self, message: str = "Pensando"):
        """Inicia o spinner com uma mensagem."""
        self._message = message
        if self._running:
            self.stop()
        self._running = True
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()

    def _spin(self):
        """Loop do spinner em thread separada."""
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        while self._running:
            frame = frames[i % len(frames)]
            text = Text()
            text.append(f" {frame} ", style=STYLE_CYAN)
            text.append(f"{self._message}", style=STYLE_WHITE)
            text.append(f"  [{self._model_name}]", style=STYLE_GRAY)
            self.console.print(text, end="\r")
            time.sleep(0.08)
            i += 1
        # Limpa a linha quando para
        self.console.print(" " * 80, end="\r")

    def stop(self):
        """Para o spinner."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=0.5)
            self._thread = None
        self.console.print(" " * 80, end="\r")

    def update(self, message: str):
        """Atualiza a mensagem do spinner em tempo real."""
        self._message = message


# ═══════════════════════════════════════════════════════════════════════════════
# CLASSE PRINCIPAL: NAPV2TUI
# ═══════════════════════════════════════════════════════════════════════════════

class NAPV2TUI:
    """
    Interface TUI principal da NAP V2.

    Gerencia:
      - Loop interativo com prompt-toolkit
      - Renderização de painéis com Rich
      - Slash commands (/model, /exit, /stop, /resume, /clear)
      - Spinner de status
      - Histórico de conversa
      - Integração com AgentTools (Theo) e Regra da Alice
    """

    def __init__(self):
        self.console = Console()
        self.spinner = StatusSpinner(self.console)

        # ── Estado ────────────────────────────────────────────────────────
        self.model_name = "openrouter/free"
        self.tokens_used = 0
        self.tokens_cost = 0.0
        self.session_history: list[dict] = []
        self.current_task: Optional[dict] = None
        self.interrupted_task: Optional[dict] = None
        self.is_processing = False
        self.stop_requested = False

        # ── Agent Tools (Theo) ────────────────────────────────────────────
        self.agent_tools = AgentTools(
            workspace_dir=Path.cwd() / "workspace",
            approval_callback=self._alice_approval_prompt,
        )

        # ── Prompt Session ────────────────────────────────────────────────
        history_path = Path.home() / ".nap_v2_history"
        self.session = PromptSession(
            history=FileHistory(str(history_path)),
            auto_suggest=AutoSuggestFromHistory(),
            completer=SlashCommandCompleter(),
            style=PT_STYLE,
            key_bindings=self._setup_key_bindings(),
            complete_while_typing=True,
        )

        # ── Signal handlers ───────────────────────────────────────────────
        signal.signal(signal.SIGINT, self._handle_sigint)

    # ── Key Bindings ──────────────────────────────────────────────────────────

    def _setup_key_bindings(self) -> KeyBindings:
        """Configura atalhos de teclado."""
        kb = KeyBindings()

        @kb.add("c-c")
        def _(event):
            """Ctrl+C: interrompe task ou sai."""
            if self.is_processing:
                self.stop_requested = True
                self._print_status("[bold red]⏹  INTERROMPIDO[/] Task cancelada pelo usuário.")
            else:
                self._handle_sigint(None, None)

        @kb.add("c-d")
        def _(event):
            """Ctrl+D: sai."""
            self._handle_sigint(None, None)

        return kb

    def _handle_sigint(self, sig, frame):
        """Handler para SIGINT."""
        if self.is_processing:
            self.stop_requested = True
        else:
            self._print_exit()
            sys.exit(0)

    # ── Alice: Prompt de Aprovação ────────────────────────────────────────────

    def _alice_approval_prompt(self, message: str) -> bool:
        """
        Callback para a Regra da Alice.
        Exibe um prompt Y/N na TUI para o usuário autorizar comandos perigosos.
        """
        self.spinner.stop()
        self.console.print()
        self.console.print(Panel(
            message,
            title="[bold red]⚠ ALICE[/]",
            border_style="red",
            box=ASCII_BOX,
            padding=(1, 2),
        ))
        self.console.print()

        while True:
            try:
                resp = self.session.prompt(
                    HTML("<ansired>  ALICE (Y/N) > </ansired>"),
                    style=PT_STYLE,
                )
                resp = resp.strip().lower()
                if resp in ("y", "yes"):
                    self.console.print(
                        "  [bold #FFB000]➜ AUTORIZADO[/]  Comando liberado por Alice.\n"
                    )
                    return True
                elif resp in ("n", "no"):
                    self.console.print(
                        "  [bold red]➜ BLOQUEADO[/]  Comando rejeitado por Alice.\n"
                    )
                    return False
                else:
                    self.console.print("  [bold #FFB000]Resposta inválida. Digite Y ou N.[/]")
            except (KeyboardInterrupt, EOFError):
                return False

    # ── Print Helpers ─────────────────────────────────────────────────────────

    def _print_panel(self, title: str, content: str, style: str = "cyan"):
        """Exibe um painel com borda quadrada ASCII."""
        style_map = {
            "cyan": "#00FFFF",
            "red": "#FF3333",
            "amber": "#FFB000",
            "gray": "#888888",
        }
        border = style_map.get(style, "#00FFFF")
        self.console.print(Panel(
            content,
            title=f"[bold #{border}]{title}[/]",
            border_style=border,
            box=ASCII_BOX,
            padding=(1, 2),
        ))

    def _print_status(self, text: str):
        """Exibe uma linha de status formatada."""
        self.console.print(f"  {text}")

    def _print_banner(self):
        """Exibe o banner de inicialização."""
        self.console.clear()
        self.console.print()
        self.console.print(NAP_V2_BANNER, style="#00FFFF")
        self.console.print()
        self._print_status(f"[bold #00FFFF]Modelo:[/] [#888888]{self.model_name}[/]")
        self._print_status(f"[bold #00FFFF]Tokens:[/] [#888888]{self.tokens_used} usados "
                           f"(${self.tokens_cost:.6f})[/]")
        self._print_status(f"[bold #00FFFF]Workspace:[/] [#888888]{self.agent_tools.workspace_dir}[/]")
        self.console.print()
        self._print_panel(
            "COMANDOS",
            "  [bold #00FFFF]/model[/]     Trocar modelo ou ver tokens\n"
            "  [bold #00FFFF]/exit[/]      Fechar o processo\n"
            "  [bold #00FFFF]/stop[/]      Cancelar task atual\n"
            "  [bold #00FFFF]/resume[/]    Retomar última task\n"
            "  [bold #00FFFF]/clear[/]     Limpar a tela\n"
            "\n"
            "  [#888888]Digite qualquer mensagem para conversar com o agente.[/]",
            "gray",
        )
        self.console.print()

    def _print_exit(self):
        """Exibe mensagem de saída."""
        self.console.print()
        self.console.print(Panel(
            "  [bold #00FFFF]NAP V2 encerrado.[/]  [#888888]Até logo, operador.[/]",
            border_style="#00FFFF",
            box=ASCII_BOX,
            padding=(1, 2),
        ))
        self.console.print()

    def _print_chat_message(self, role: str, content: str, timestamp: str = ""):
        """
        Exibe uma mensagem do chat dentro de um painel.
        role: "user" ou "agent"
        """
        ts = f" [#888888]{timestamp}[/]" if timestamp else ""
        if role == "user":
            title = f"[bold #00FFFF]🧑 OPERADOR{ts}[/]"
            border = "#00FFFF"
        else:
            title = f"[bold #FFB000]🤖 AGENTE{ts}[/]"
            border = "#FFB000"

        self.console.print(Panel(
            content,
            title=title,
            border_style=border,
            box=ASCII_BOX,
            padding=(1, 2),
        ))
        self.console.print()

    # ── Slash Commands ────────────────────────────────────────────────────────

    def _cmd_model(self, args: str = ""):
        """
        Comando /model: Trocar modelo ou ver tokens gastos.
        """
        self.console.print()
        self._print_panel(
            "MODELO",
            f"  [bold #00FFFF]Modelo atual:[/]  {self.model_name}\n"
            f"  [bold #00FFFF]Tokens usados:[/]  {self.tokens_used}\n"
            f"  [bold #00FFFF]Custo total:[/]    ${self.tokens_cost:.6f}\n"
            "\n"
            f"  [#888888]Para trocar, edite a variável OPENROUTER_MODEL no .env[/]\n"
            f"  [#888888]Exemplos: deepseek/deepseek-chat:free, qwen/qwen-2.5-72b-instruct:free[/]",
            "cyan",
        )
        self.console.print()

    def _cmd_exit(self):
        """Comando /exit: Fecha o processo com segurança."""
        if self.is_processing:
            self._print_status("[bold #FFB000]⏳ Task em andamento. Use /stop primeiro ou force com /exit novamente.[/]")
            return
        self._print_exit()
        sys.exit(0)

    def _cmd_stop(self):
        """Comando /stop: Cancela/interrompe a task atual do agente."""
        if self.is_processing:
            self.stop_requested = True
            self._print_status("[bold red]⏹  STOP solicitado. Aguardando interrupção...[/]")
        else:
            self._print_status("[bold #FFB000]⏸  Nenhuma task em andamento.[/]")

    def _cmd_resume(self):
        """Comando /resume: Retoma a última task interrompida."""
        if self.interrupted_task:
            self._print_status("[bold #00FFFF]⏩ Retomando última task interrompida...[/]")
            task_content = self.interrupted_task.get("content", "")
            self._process_user_input(task_content)
        else:
            self._print_status("[bold #FFB000]⏸  Nenhuma task interrompida para retomar.[/]")

    def _cmd_clear(self):
        """Comando /clear: Limpa a tela do terminal."""
        self.console.clear()
        self._print_banner()

    # ── Processamento de Input ────────────────────────────────────────────────

    def _process_user_input(self, user_input: str):
        """
        Processa a entrada do usuário simulando a execução do agente.
        Em uma implementação completa, isso chamaria o OpenRouter/agente local.
        """
        self.is_processing = True
        self.stop_requested = False

        # Salva como task atual (para possível interrupção)
        self.current_task = {
            "content": user_input,
            "timestamp": datetime.now().isoformat(),
        }

        # Timestamp
        ts = datetime.now().strftime("%H:%M:%S")

        # Exibe a mensagem do usuário
        self._print_chat_message("user", user_input, ts)

        # ── Fase 1: Carregando contexto ───────────────────────────────────
        self.spinner.start("Carregando contexto...")
        for i in range(10):
            if self.stop_requested:
                self.spinner.stop()
                self._print_status("[bold red]⏹  Task interrompida durante carregamento de contexto.[/]")
                self.interrupted_task = self.current_task
                self.is_processing = False
                self.stop_requested = False
                return
            time.sleep(0.1)
        self.spinner.stop()

        # ── Fase 2: Pensando ──────────────────────────────────────────────
        self.spinner.start("Pensando...")
        for i in range(15):
            if self.stop_requested:
                self.spinner.stop()
                self._print_status("[bold red]⏹  Task interrompida durante raciocínio.[/]")
                self.interrupted_task = self.current_task
                self.is_processing = False
                self.stop_requested = False
                return
            time.sleep(0.1)
        self.spinner.stop()

        # ── Fase 3: Escrevendo arquivo (simulado) ─────────────────────────
        self.spinner.start("Escrevendo arquivo...")
        for i in range(8):
            if self.stop_requested:
                self.spinner.stop()
                self._print_status("[bold red]⏹  Task interrompida durante escrita.[/]")
                self.interrupted_task = self.current_task
                self.is_processing = False
                self.stop_requested = False
                return
            time.sleep(0.1)
        self.spinner.stop()

        # ── Resposta simulada do agente ───────────────────────────────────
        ts_response = datetime.now().strftime("%H:%M:%S")
        response = (
            f"[#888888]Análise concluída para:[/]\n"
            f"  {user_input[:100]}{'...' if len(user_input) > 100 else ''}\n"
            f"\n"
            f"[#888888]Ferramentas disponíveis:[/]\n"
            f"  • read_file — Ler arquivos\n"
            f"  • write_file — Escrever/reescrever arquivos\n"
            f"  • replace_in_file — Substituir blocos em arquivos\n"
            f"  • create_directory — Criar pastas\n"
            f"  • delete_file — Deletar arquivos\n"
            f"  • delete_directory — Deletar pastas\n"
            f"  • list_directory — Listar diretórios\n"
            f"  • execute_shell — Executar comandos shell\n"
            f"\n"
            f"[#FFB000]Modo agente local ativo.[/]  [#888888]Use as tools acima para interagir com o sistema.[/]"
        )

        self._print_chat_message("agent", response, ts_response)

        # Atualiza histórico
        self.session_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": ts,
        })
        self.session_history.append({
            "role": "agent",
            "content": response,
            "timestamp": ts_response,
        })

        # Simula consumo de tokens
        self.tokens_used += 150
        self.tokens_cost += 0.00015

        self.is_processing = False
        self.current_task = None

    # ── Loop Principal ────────────────────────────────────────────────────────

    def run(self):
        """Loop principal da TUI."""
        self._print_banner()

        while True:
            try:
                # ── Prompt ────────────────────────────────────────────────
                user_input = self.session.prompt(
                    HTML("<ansicyan><b>  ⚡ nap></b></ansicyan> "),
                    style=PT_STYLE,
                )

                # ── Pula linhas vazias ────────────────────────────────────
                if not user_input.strip():
                    continue

                # ── Slash Commands ────────────────────────────────────────
                if user_input.startswith("/"):
                    cmd_parts = user_input.strip().split(maxsplit=1)
                    cmd = cmd_parts[0].lower()
                    args = cmd_parts[1] if len(cmd_parts) > 1 else ""

                    if cmd == "/model":
                        self._cmd_model(args)
                    elif cmd == "/exit":
                        self._cmd_exit()
                    elif cmd == "/stop":
                        self._cmd_stop()
                    elif cmd == "/resume":
                        self._cmd_resume()
                    elif cmd == "/clear":
                        self._cmd_clear()
                    else:
                        self._print_status(
                            f"[bold #FF3333]Comando desconhecido:[/] {cmd}\n"
                            f"  [#888888]Comandos disponíveis: /model, /exit, /stop, /resume, /clear[/]"
                        )
                    continue

                # ── Processa input do usuário ─────────────────────────────
                self._process_user_input(user_input)

            except KeyboardInterrupt:
                if self.is_processing:
                    self.stop_requested = True
                    self._print_status("[bold red]⏹  INTERROMPIDO[/]")
                else:
                    self._print_exit()
                    break
            except EOFError:
                self._print_exit()
                break
            except Exception as e:
                self._print_status(f"[bold #FF3333]Erro:[/] {e}")
                logger.exception("Erro no loop principal da TUI")


# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """Entry point para a NAP V2 TUI."""
    tui = NAPV2TUI()
    tui.run()


if __name__ == "__main__":
    main()