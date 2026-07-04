"""
NAP Interactive Shell — Modo Imersivo "Devin-like"

Provides an interactive shell (`nap> `) with:
- Continuous chat with NAP agents
- Context history preservation
- Streaming logs and agent output
- Approval workflow before file modifications
"""

import cmd
import os
import sys
import json
import time
import shlex
import logging
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime

# Ensure the backend is in path for direct imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

# ─── Rich Console for Pretty Output ──────────────────────────────────────────
try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.prompt import Prompt, Confirm
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

# ─── Logging ──────────────────────────────────────────────────────────────────
logger = logging.getLogger("nap.cli")

# ─── Constants ────────────────────────────────────────────────────────────────
NAP_ASCII = """
╔══════════════════════════════════════════════╗
║  ███╗   ██╗ █████╗ ██████╗                 ║
║  ████╗  ██║██╔══██╗██╔══██╗                ║
║  ██╔██╗ ██║███████║██████╔╝                ║
║  ██║╚██╗██║██╔══██║██╔═══╝                 ║
║  ██║ ╚████║██║  ██║██║                     ║
║  ╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝                     ║
║                                              ║
║  Nexus AI Platform — Modo Imersivo          ║
╚══════════════════════════════════════════════╝
"""


class NAPShell(cmd.Cmd):
    """Interactive shell for NAP platform — Modo Devin."""

    intro = (
        f"\n{NAP_ASCII}\n"
        "🧠 Bem-vindo ao Modo Imersivo da NAP!\n"
        "Digite 'help' para comandos ou 'chat <mensagem>' para falar com os agentes.\n"
        "Digite 'exit' para sair.\n"
    )
    prompt = "\n⚡ nap> "
    doc_header = "📋 Comandos Disponíveis (digite help <comando>)"

    def __init__(self):
        super().__init__()
        self.api_base_url = os.getenv("NAP_API_URL", "http://localhost:8000")
        self.session_history: list[dict] = []
        self.pending_approvals: list[dict] = []
        self.console = Console() if RICH_AVAILABLE else None

        # Check if backend is accessible
        self._check_backend()

    # ── Backend Check ──────────────────────────────────────────────────────────
    def _check_backend(self):
        """Verify backend connectivity on startup."""
        try:
            import httpx
            r = httpx.get(f"{self.api_base_url}/health", timeout=5)
            if r.status_code == 200:
                data = r.json()
                self._print(f"[green]✅ Backend conectado:[/] {data['service']} v{data['version']}")
            else:
                self._print(f"[yellow]⚠️  Backend retornou status {r.status_code}[/]")
        except Exception as e:
            self._print(f"[red]❌ Backend não acessível em {self.api_base_url}[/]")
            self._print(f"   Erro: {e}")
            self._print("   Inicie com: docker compose up -d")

    # ── Pretty Print ──────────────────────────────────────────────────────────
    def _print(self, text: str, style: str = "default", markdown: bool = False):
        """Print with rich formatting if available."""
        if self.console and RICH_AVAILABLE:
            if markdown:
                self.console.print(Markdown(text))
            else:
                self.console.print(text)
        else:
            # Strip rich tags for plain terminal
            clean = text.replace("[/]", "").replace("[red]", "").replace("[green]", "")
            clean = clean.replace("[yellow]", "").replace("[blue]", "").replace("[cyan]", "")
            clean = clean.replace("[bold]", "").replace("[dim]", "")
            print(clean)

    def _print_table(self, title: str, columns: list, rows: list[list]):
        """Print a formatted table."""
        if self.console and RICH_AVAILABLE:
            table = Table(title=title, box=box.ROUNDED, header_style="bold cyan")
            for col in columns:
                table.add_column(col)
            for row in rows:
                table.add_row(*[str(c) for c in row])
            self.console.print(table)
        else:
            print(f"\n=== {title} ===")
            print(" | ".join(columns))
            print("-" * 50)
            for row in rows:
                print(" | ".join(str(c) for c in row))

    def _print_panel(self, title: str, content: str, style: str = "blue"):
        """Print content inside a panel."""
        if self.console and RICH_AVAILABLE:
            self.console.print(Panel(content, title=title, border_style=style))
        else:
            print(f"\n─── {title} ───")
            print(content)

    def _prompt_yes_no(self, question: str, default: bool = False) -> bool:
        """Ask for user approval."""
        if self.console and RICH_AVAILABLE:
            return Confirm.ask(f"[yellow]{question}[/]", default=default)
        else:
            resp = input(f"{question} (y/n) [{'Y' if default else 'N'}]: ").strip().lower()
            if default:
                return resp != "n"
            return resp == "y"

    # ── API Helpers ────────────────────────────────────────────────────────────
    def _api_request(self, method: str, path: str, data: Optional[dict] = None) -> Optional[dict]:
        """Make an HTTP request to the NAP backend."""
        try:
            import httpx
            url = f"{self.api_base_url}{path}"
            with httpx.Client(timeout=120) as client:
                if method == "GET":
                    r = client.get(url)
                elif method == "POST":
                    r = client.post(url, json=data)
                else:
                    return None

                if r.status_code in (200, 201):
                    return r.json()
                else:
                    self._print(f"[red]Erro {r.status_code}:[/] {r.text[:200]}")
                    return None
        except Exception as e:
            self._print(f"[red]Erro de conexão:[/] {e}")
            return None

    # ── Local Knowledge Base (fallback quando API key não configurada) ────────
    LOCAL_KNOWLEDGE = {
        "linguagem": (
            "Fui construído com Python 3.13 no backend (FastAPI, SQLAlchemy, Pydantic) "
            "e TypeScript/React no frontend (Next.js 14, TailwindCSS). "
            "Uso Docker Compose para orquestração e OpenRouter para acessar modelos de IA "
            "como DeepSeek, Qwen, Mistral e Llama."
        ),
        "quem criou": (
            "Fui projetado pelo time NAP (Nexus AI Platform) como uma plataforma de "
            "Engenharia de Software baseada em Inteligência Artificial. Meu objetivo é "
            "orquestrar agentes especializados para auxiliar desenvolvedores em todo o "
            "ciclo de vida do software."
        ),
        "o que você faz": (
            "Sou uma plataforma que conecta modelos de IA a agentes especializados. "
            "Posso gerar código backend (Python/FastAPI), frontend (React/Next.js), "
            "documentação técnica, e revisar código. Também tenho MCP Tools para "
            "Git, Docker, Python, Bash e PostgreSQL."
        ),
        "como funciona": (
            "Meu fluxo é: Usuário → Frontend → API → Orchestrator → OpenRouter → "
            "Agentes (Backend, Frontend, Docs, Reviewer) → MCP Tools → Resultado. "
            "Tudo roda localmente via Docker Compose."
        ),
        "stack": (
            "Backend: Python 3.13, FastAPI, SQLAlchemy, Pydantic\n"
            "Frontend: React, Next.js 14, TypeScript, TailwindCSS\n"
            "Database: PostgreSQL 16\n"
            "Cache: Redis 7\n"
            "Vector DB: Qdrant\n"
            "Infraestrutura: Docker Compose\n"
            "Modelos IA: OpenRouter (DeepSeek, Qwen, Mistral, Llama)"
        ),
        "versão": "NAP - Nexus AI Platform v0.2.0 (Modo Imersivo)",
        "docker": (
            "Uso Docker Compose com 5 serviços:\n"
            "  • nap-postgres :5432 — PostgreSQL 16\n"
            "  • nap-redis    :6379 — Redis 7\n"
            "  • nap-qdrant   :6333 — Qdrant vector DB\n"
            "  • nap-backend  :8000 — FastAPI\n"
            "  • nap-frontend :3000 — Next.js\n"
            "Comando: docker compose up -d"
        ),
        "openrouter": (
            "Preciso de uma chave da OpenRouter para acessar modelos de IA.\n"
            "1. Crie uma conta gratuita em https://openrouter.ai/keys\n"
            "2. Gere uma API Key (começa com sk-or-v1-)\n"
            "3. Adicione no .env: OPENROUTER_API_KEY=sk-or-v1-sua-chave\n"
            "4. Reinicie: docker compose restart backend"
        ),
        "exemplo": (
            "Aqui vai um exemplo de uso:\n\n"
            "  nap> chat Crie uma API de tarefas com FastAPI\n\n"
            "Ou via curl:\n\n"
            '  curl -X POST http://localhost:8000/api/v1/agents/execute \\\n'
            '    -H "Content-Type: application/json" \\\n'
            '    -d \'{"agent_type":"backend","task":"Crie uma API de tarefas"}\''
        ),
    }

    def _get_local_answer(self, question: str) -> Optional[str]:
        """Try to answer from local knowledge base when API is unavailable."""
        q = question.lower().strip()
        for keyword, answer in self.LOCAL_KNOWLEDGE.items():
            if keyword in q:
                return answer
        return None

    def _stream_agent_output(self, request_data: dict) -> Optional[dict]:
        """Execute agent with simulated streaming output."""
        task = request_data.get("task", "")
        self._print("[cyan]🤖 Iniciando execução do agente...[/]")
        self._print(f"   Tipo: {request_data.get('agent_type', 'workflow')}")
        self._print(f"   Tarefa: {task[:80]}...")
        self._print("")

        # Simulate streaming with progress
        if self.console and RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
                console=self.console,
            ) as progress:
                task_progress = progress.add_task("[cyan]Processando...", total=None)
                for i in range(5):
                    time.sleep(0.3)
                    progress.update(task_progress, description=f"[cyan]Processando{'·' * (i % 3 + 1)}[/]")
                progress.update(task_progress, description="[green]✔️ Concluído![/]")
        else:
            for i in range(3):
                sys.stdout.write(f"\r⏳ Processando{'.' * (i % 3 + 1)}   ")
                sys.stdout.flush()
                time.sleep(0.3)
            print("\r✅ Concluído!          ")

        # Execute actual API call
        result = self._api_request("POST", "/api/v1/agents/workflow", request_data)

        # Detect if API returned an error (401 = no API key configured)
        api_errored = False
        if result is None:
            api_errored = True
        elif result.get("results"):
            for tid, tres in result["results"].items():
                rdata = tres.get("result", {})
                if rdata.get("error") or ("401" in str(rdata.get("generated_code", ""))):
                    api_errored = True
                    break

        # If API failed, try local knowledge base
        if api_errored:
            local_answer = self._get_local_answer(task)
            if local_answer:
                self._print("[yellow]ℹ️  Modo offline — usando base de conhecimento local[/]")
                return {
                    "status": "completed",
                    "total_tasks": 1,
                    "results": {
                        "local-response": {
                            "agent_type": "nap",
                            "task_id": "local-response",
                            "status": "completed",
                            "result": {
                                "generated_code": local_answer,
                                "source": "local_knowledge_base",
                            },
                        }
                    },
                }
        return result

    # ── Commands ───────────────────────────────────────────────────────────────

    def do_chat(self, arg: str):
        """Chat with NAP agents: chat <sua mensagem>
        
        Envia uma tarefa para o Orchestrator da NAP, que decompõe
        e distribui para os agentes especializados.
        
        Exemplo: chat Crie uma API de tarefas com FastAPI
        """
        if not arg.strip():
            self._print("[yellow]⚠️  Use: chat <sua mensagem>[/]")
            return

        self.session_history.append({
            "role": "user",
            "content": arg,
            "timestamp": datetime.now().isoformat(),
        })

        self._print_panel("📝 Requisição do Usuário", arg, "cyan")

        # Check for approval before modifying files
        if any(word in arg.lower() for word in ["crie", "gere", "criar", "gerar", "modifique", "altere", "escreva"]):
            if not self._prompt_yes_no("⚠️  Esta operação pode criar/alterar arquivos. Prosseguir?", True):
                self._print("[yellow]⏸️  Operação cancelada pelo usuário.[/]")
                return

        data = {"task": arg, "context": {"session_id": len(self.session_history)}}
        result = self._stream_agent_output(data)

        if result:
            self.session_history.append({
                "role": "assistant",
                "content": str(result),
                "timestamp": datetime.now().isoformat(),
            })

            self._print("")
            self._print("[bold green]✅ Resultado do Workflow:[/]")
            self._print(f"   Status: {result.get('status', 'unknown')}")
            self._print(f"   Total de tarefas: {result.get('total_tasks', 0)}")

            results = result.get("results", {})
            for task_id, task_result in results.items():
                agent = task_result.get("agent_type", "?")
                status = task_result.get("status", "?")
                result_data = task_result.get("result", {})

                # Show generated code/documentation if present
                for key in ("generated_code", "documentation", "review_report"):
                    if key in result_data and result_data[key]:
                        content = result_data[key]
                        if len(content) > 500:
                            content = content[:500] + "\n... [truncado]"
                        self._print_panel(
                            f"📄 {agent}: {key}",
                            content,
                            "green" if status == "completed" else "red",
                        )
                        break
        else:
            self._print("[red]❌ Falha ao executar o workflow.[/]")

    def do_run(self, arg: str):
        """Execute um comando shell no workspace: run <comando>
        
        Exemplo: run ls -la
        Exemplo: run python --version
        """
        if not arg.strip():
            self._print("[yellow]⚠️  Use: run <comando>[/]")
            return

        self._print(f"[dim]Executando: $ {arg}[/]")
        try:
            result = subprocess.run(
                ["bash", "-c", arg],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(Path(__file__).resolve().parent.parent / "workspace"),
            )
            if result.stdout:
                self._print(result.stdout)
            if result.stderr:
                self._print(f"[red]{result.stderr}[/]")
            if result.returncode != 0:
                self._print(f"[red]❌ Código de saída: {result.returncode}[/]")
            else:
                self._print(f"[green]✅ Comando concluído (exit: 0)[/]")
        except subprocess.TimeoutExpired:
            self._print("[red]⏰ Comando excedeu o tempo limite (30s)[/]")
        except Exception as e:
            self._print(f"[red]Erro: {e}[/]")

    def do_status(self, arg: str):
        """Exibe o status da plataforma NAP e containers."""
        self._print("[bold]🔍 Status da Plataforma NAP[/]")
        self._print("─" * 50)

        # Check backend
        health = self._api_request("GET", "/health")
        if health:
            self._print(f"[green]✅ Backend:[/] {health.get('service', 'NAP')} v{health.get('version', '?')}")
        else:
            self._print(f"[red]❌ Backend:[/] Não acessível")

        # Check Docker containers
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                rows = []
                for line in lines:
                    parts = line.split("\t", 1)
                    if len(parts) == 2:
                        status_icon = "🟢" if "healthy" in parts[1] or "Up" in parts[1] else "🔴"
                        rows.append([status_icon, parts[0], parts[1]])
                self._print_table("🐳 Containers Docker", ["", "Nome", "Status"], rows)
            else:
                self._print("[yellow]⚠️  Docker não está rodando ou não há containers[/]")
        except FileNotFoundError:
            self._print("[yellow]⚠️  Docker não encontrado[/]")

        # Show OpenRouter config
        api_key = os.getenv("OPENROUTER_API_KEY", "")
        if api_key:
            masked = api_key[:12] + "..." + api_key[-4:] if len(api_key) > 16 else "configurada"
            self._print(f"[green]🔑 OpenRouter API Key:[/] {masked}")
        else:
            self._print(f"[red]❌ OpenRouter API Key:[/] Não configurada")

    def do_agents(self, arg: str):
        """Lista os agentes disponíveis na NAP."""
        self._print_table(
            "🤖 Agentes NAP",
            ["Tipo", "Especialidade", "Gera"],
            [
                ["🧠 architect", "Arquitetura", "Planos de implementação"],
                ["⚙️  backend", "Python/FastAPI", "Código backend"],
                ["🎨 frontend", "React/Next.js", "Componentes UI"],
                ["📝 documentation", "Docs técnicos", "README, ADRs"],
                ["🔍 reviewer", "Qualidade/Segurança", "Relatórios de revisão"],
            ],
        )

    def do_projects(self, arg: str):
        """Lista projetos cadastrados na plataforma."""
        projects = self._api_request("GET", "/api/v1/projects/")
        if projects:
            rows = []
            for p in projects:
                rows.append([str(p.get("id", "")), p.get("name", ""), p.get("status", ""), p.get("created_at", "")[:10]])
            self._print_table("📂 Projetos", ["ID", "Nome", "Status", "Criado"], rows)
        else:
            self._print("[yellow]📂 Nenhum projeto encontrado ou API indisponível[/]")

    def do_history(self, arg: str):
        """Exibe o histórico da sessão atual."""
        if not self.session_history:
            self._print("[yellow]📜 Nenhum histórico na sessão atual.[/]")
            return

        for entry in self.session_history:
            role = entry.get("role", "?")
            content = entry.get("content", "")
            ts = entry.get("timestamp", "")[11:19]
            prefix = "[cyan]🧑 Você[/]" if role == "user" else "[green]🤖 NAP[/]"
            self._print(f"{prefix} ({ts}):")
            self._print(f"   {content[:200]}{'...' if len(content) > 200 else ''}")
            self._print("")

    def do_logs(self, arg: str):
        """Exibe logs recentes da aplicação.
        
        Uso: logs [serviço] [linhas]
        Exemplo: logs backend 20
        """
        parts = shlex.split(arg) if arg else []
        service = parts[0] if parts else "backend"
        lines = parts[1] if len(parts) > 1 else "30"

        self._print(f"[dim]Obtendo logs do {service} (últimas {lines} linhas)...[/]")
        try:
            result = subprocess.run(
                ["docker", "compose", "logs", "--tail", lines, service],
                capture_output=True, text=True, timeout=10,
                cwd=str(Path(__file__).resolve().parent.parent),
            )
            output = result.stdout or result.stderr
            if output.strip():
                self._print_panel(f"📋 Logs: {service}", output.strip()[-3000:], "dim")
            else:
                self._print(f"[yellow]Sem logs para {service}[/]")
        except Exception as e:
            self._print(f"[red]Erro ao obter logs: {e}[/]")

    def do_clear(self, arg: str):
        """Limpa o terminal."""
        os.system("clear" if os.name == "posix" else "cls")

    def do_help(self, arg: str):
        """Mostra ajuda dos comandos disponíveis."""
        if arg:
            # Show help for specific command
            super().do_help(arg)
        else:
            self._print("[bold]📋 Comandos Disponíveis[/]")
            self._print("─" * 50)
            commands = [
                ("chat <mensagem>", "Envia tarefa para os agentes NAP"),
                ("run <comando>", "Executa comando shell no workspace"),
                ("status", "Exibe status da plataforma"),
                ("agents", "Lista agentes disponíveis"),
                ("projects", "Lista projetos cadastrados"),
                ("history", "Histórico da sessão"),
                ("logs [svc] [n]", "Logs do container (ex: logs backend 20)"),
                ("clear", "Limpa o terminal"),
                ("exit / quit", "Sai do modo imersivo"),
                ("help <cmd>", "Ajuda detalhada de um comando"),
            ]
            for cmd, desc in commands:
                self._print(f"  [cyan]{cmd:20s}[/]  {desc}")
            self._print("")
            self._print("[dim]Dica: Use 'chat' para falar com os agentes como se fosse o Devin![/]")

    def do_exit(self, arg: str):
        """Sai do Modo Imersivo NAP."""
        self._print("[cyan]👋 Encerrando NAP Modo Imersivo. Até logo![/]")
        return True

    def do_quit(self, arg: str):
        """Sai do Modo Imersivo NAP."""
        return self.do_exit(arg)

    # ── Default handler for unknown commands ──────────────────────────────────
    def default(self, line: str):
        """If command not recognized, treat as chat."""
        if line.strip():
            self._print(f"[yellow]⚠️  Comando não reconhecido. Interpretando como mensagem...[/]")
            self.do_chat(line)

    # ── Empty line ────────────────────────────────────────────────────────────
    def emptyline(self):
        """Do nothing on empty line."""
        pass

    # ── Command completion ────────────────────────────────────────────────────
    def completenames(self, text, *ignored):
        """Auto-complete command names."""
        d = {}
        for n in self.get_names():
            if n.startswith("do_"):
                d[n[3:]] = None
        return [c for c in d if c.startswith(text)]


# ── Entry Point ────────────────────────────────────────────────────────────────
def main():
    """Main entry point for NAP CLI."""
    shell = NAPShell()

    # If arguments passed, execute as one-off command
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        shell.onecmd(command)
    else:
        try:
            shell.cmdloop()
        except KeyboardInterrupt:
            print("\n👋 Até logo!")
            sys.exit(0)


if __name__ == "__main__":
    main()