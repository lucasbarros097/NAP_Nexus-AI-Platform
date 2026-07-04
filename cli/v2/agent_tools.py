"""
Agent Tools (Theo) — Ferramentas de I/O e Shell para o Agente Local
====================================================================

Fornece ao agente capacidades de:
  - Leitura de arquivos
  - Escrita/edição de arquivos (substituição de blocos ou reescrita total)
  - Criação de pastas
  - Deleção de arquivos
  - Execução de comandos shell com captura de output

Regra da Alice:
  Comandos de terminal considerados perigosos ou de mutação (rm, apt install,
  dpkg, kill, systemctl, chmod, chown, dd, mkfs, etc.) devem pausar o agente
  e exibir um prompt (Y/N) na TUI para o usuário autorizar.
"""

import os
import re
import sys
import shutil
import shlex
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Callable, Awaitable

logger = logging.getLogger("nap.v2.agent_tools")

# ─── Lista de Comandos Perigosos (Regra da Alice) ─────────────────────────────
# Qualquer comando que contenha estes prefixos ou binários será considerado
# perigoso e exigirá autorização explícita do usuário.
DANGEROUS_COMMANDS = [
    "rm", "rmdir",           # Remoção
    "apt", "apt-get",        # Gerenciador de pacotes
    "dpkg", "rpm",           # Gerenciador de pacotes low-level
    "kill", "pkill",         # Mata processos
    "systemctl", "service",  # Gerenciamento de serviços
    "chmod", "chown",        # Permissões
    "dd",                    # Disk destroyer
    "mkfs", "fdisk",         # Formatação
    "mount", "umount",       # Montagem
    "shutdown", "reboot",    # Desligamento
    "passwd", "useradd",     # Gerenciamento de usuários
    "wget", "curl",          # Download (pode ser usado para payloads)
    "sudo", "su",            # Escalação de privilégio
    "pip install",           # Instalação de pacotes Python
    "npm install",           # Instalação de pacotes Node
    "cargo install",         # Instalação de pacotes Rust
    "docker",                # Docker commands
    "> /dev/",               # Redirecionamento para dispositivos
    ":(){ :|:& };:",         # Fork bomb
    "eval",                  # Avaliação de código
    "exec",                  # Substituição de processo
    "source",                # Source de scripts
    "bash -c",               # Shell remoto
    "python -c",             # Python inline
]


class DangerousCommandError(Exception):
    """Exceção levantada quando um comando perigoso é rejeitado pelo usuário."""
    pass


class AgentTools:
    """
    Conjunto de ferramentas que o agente local pode usar para interagir
    com o sistema de arquivos e executar comandos.

    Attributes:
        workspace_dir: Diretório base para operações (default: workspace/).
        approval_callback: Função chamada para solicitar aprovação do usuário
                          quando um comando perigoso é detectado.
                          Deve retornar True (aprovado) ou False (rejeitado).
    """

    def __init__(
        self,
        workspace_dir: Optional[Path] = None,
        approval_callback: Optional[Callable[[str], bool]] = None,
    ):
        self.workspace_dir = Path(workspace_dir or Path.cwd() / "workspace")
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        self.approval_callback = approval_callback

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _resolve_path(self, path: str) -> Path:
        """
        Resolve um caminho relativo ao workspace_dir.
        Previne path traversal attacks (escapar do workspace).
        """
        # Se for caminho absoluto, usa como está (mas ainda verifica traversal)
        p = Path(path)
        if p.is_absolute():
            resolved = p.resolve()
        else:
            resolved = (self.workspace_dir / p).resolve()

        # Verifica se está dentro do workspace (segurança)
        # Permite caminhos absolutos que estejam dentro do projeto
        project_root = Path.cwd().resolve()
        if not str(resolved).startswith(str(project_root)):
            raise PermissionError(
                f"Acesso negado: {resolved} está fora do diretório do projeto ({project_root})"
            )
        return resolved

    def _is_dangerous(self, command: str) -> Optional[str]:
        """
        Verifica se um comando shell é perigoso segundo a Regra da Alice.

        Returns:
            O nome do padrão perigoso detectado, ou None se seguro.
        """
        cmd_lower = command.strip().lower()
        for pattern in DANGEROUS_COMMANDS:
            # Verifica se o comando começa com o padrão ou contém como palavra
            if cmd_lower.startswith(pattern) or re.search(
                rf'(^|\||;|&&|\|\|)\s*{re.escape(pattern)}\s',
                cmd_lower,
            ):
                return pattern
        return None

    # ── Ferramenta: Ler Arquivo ────────────────────────────────────────────────

    def read_file(self, path: str, start_line: int = 1, end_line: Optional[int] = None) -> dict:
        """
        Lê o conteúdo de um arquivo.

        Args:
            path: Caminho do arquivo (relativo ao workspace ou absoluto).
            start_line: Linha inicial (1-based, inclusive).
            end_line: Linha final (inclusive). Se None, lê até o final.

        Returns:
            Dict com 'content', 'total_lines', 'file_path'.
        """
        try:
            filepath = self._resolve_path(path)
            if not filepath.exists():
                return {"error": f"Arquivo não encontrado: {filepath}", "success": False}
            if not filepath.is_file():
                return {"error": f"Não é um arquivo: {filepath}", "success": False}

            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            total = len(lines)
            start_idx = max(0, start_line - 1)
            end_idx = min(end_line or total, total)

            selected = lines[start_idx:end_idx]
            content = "".join(selected)

            return {
                "content": content,
                "total_lines": total,
                "start_line": start_line,
                "end_line": end_idx,
                "file_path": str(filepath),
                "success": True,
            }
        except PermissionError as e:
            return {"error": str(e), "success": False}
        except Exception as e:
            return {"error": f"Erro ao ler arquivo: {e}", "success": False}

    # ── Ferramenta: Escrever/Reescrever Arquivo ────────────────────────────────

    def write_file(self, path: str, content: str) -> dict:
        """
        Escreve conteúdo em um arquivo (cria ou sobrescreve completamente).

        Args:
            path: Caminho do arquivo.
            content: Conteúdo completo a ser escrito.

        Returns:
            Dict com status da operação.
        """
        try:
            filepath = self._resolve_path(path)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            return {
                "file_path": str(filepath),
                "bytes_written": len(content.encode("utf-8")),
                "success": True,
            }
        except PermissionError as e:
            return {"error": str(e), "success": False}
        except Exception as e:
            return {"error": f"Erro ao escrever arquivo: {e}", "success": False}

    # ── Ferramenta: Substituir Bloco em Arquivo ────────────────────────────────

    def replace_in_file(self, path: str, search: str, replace: str) -> dict:
        """
        Substitui um bloco de texto em um arquivo existente.

        Args:
            path: Caminho do arquivo.
            search: Texto exato a ser procurado (deve corresponder exatamente).
            replace: Novo texto que substituirá o bloco encontrado.

        Returns:
            Dict com status e número de substituições.
        """
        try:
            filepath = self._resolve_path(path)
            if not filepath.exists():
                return {"error": f"Arquivo não encontrado: {filepath}", "success": False}

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            if search not in content:
                return {
                    "error": "Bloco de busca não encontrado no arquivo. "
                             "A busca deve corresponder exatamente (incluindo espaços e quebras de linha).",
                    "success": False,
                }

            count = content.count(search)
            new_content = content.replace(search, replace, 1)  # Substitui apenas o primeiro

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)

            return {
                "file_path": str(filepath),
                "replacements": count,
                "success": True,
            }
        except PermissionError as e:
            return {"error": str(e), "success": False}
        except Exception as e:
            return {"error": f"Erro ao substituir no arquivo: {e}", "success": False}

    # ── Ferramenta: Criar Pasta ────────────────────────────────────────────────

    def create_directory(self, path: str) -> dict:
        """
        Cria um diretório (e subdiretórios se necessário).

        Args:
            path: Caminho do diretório a ser criado.

        Returns:
            Dict com status.
        """
        try:
            dirpath = self._resolve_path(path)
            dirpath.mkdir(parents=True, exist_ok=True)
            return {
                "directory": str(dirpath),
                "success": True,
            }
        except PermissionError as e:
            return {"error": str(e), "success": False}
        except Exception as e:
            return {"error": f"Erro ao criar diretório: {e}", "success": False}

    # ── Ferramenta: Deletar Arquivo ────────────────────────────────────────────

    def delete_file(self, path: str) -> dict:
        """
        Deleta um arquivo.

        Args:
            path: Caminho do arquivo a ser deletado.

        Returns:
            Dict com status.
        """
        try:
            filepath = self._resolve_path(path)
            if not filepath.exists():
                return {"error": f"Arquivo não encontrado: {filepath}", "success": False}
            if not filepath.is_file():
                return {"error": f"Não é um arquivo: {filepath}", "success": False}

            filepath.unlink()
            return {
                "file_path": str(filepath),
                "success": True,
            }
        except PermissionError as e:
            return {"error": str(e), "success": False}
        except Exception as e:
            return {"error": f"Erro ao deletar arquivo: {e}", "success": False}

    # ── Ferramenta: Deletar Pasta ──────────────────────────────────────────────

    def delete_directory(self, path: str, recursive: bool = False) -> dict:
        """
        Deleta um diretório.

        Args:
            path: Caminho do diretório.
            recursive: Se True, deleta recursivamente (como rm -rf).

        Returns:
            Dict com status.
        """
        try:
            dirpath = self._resolve_path(path)
            if not dirpath.exists():
                return {"error": f"Diretório não encontrado: {dirpath}", "success": False}
            if not dirpath.is_dir():
                return {"error": f"Não é um diretório: {dirpath}", "success": False}

            if recursive:
                shutil.rmtree(dirpath)
            else:
                dirpath.rmdir()  # Só funciona se vazio

            return {
                "directory": str(dirpath),
                "recursive": recursive,
                "success": True,
            }
        except OSError as e:
            if "Directory not empty" in str(e):
                return {
                    "error": "Diretório não está vazio. Use recursive=True para deletar recursivamente.",
                    "success": False,
                }
            return {"error": f"Erro ao deletar diretório: {e}", "success": False}
        except PermissionError as e:
            return {"error": str(e), "success": False}
        except Exception as e:
            return {"error": f"Erro ao deletar diretório: {e}", "success": False}

    # ── Ferramenta: Listar Diretório ───────────────────────────────────────────

    def list_directory(self, path: str = ".") -> dict:
        """
        Lista o conteúdo de um diretório.

        Args:
            path: Caminho do diretório.

        Returns:
            Dict com lista de arquivos/pastas.
        """
        try:
            dirpath = self._resolve_path(path)
            if not dirpath.exists():
                return {"error": f"Diretório não encontrado: {dirpath}", "success": False}
            if not dirpath.is_dir():
                return {"error": f"Não é um diretório: {dirpath}", "success": False}

            items = []
            for entry in sorted(dirpath.iterdir()):
                items.append({
                    "name": entry.name,
                    "type": "directory" if entry.is_dir() else "file",
                    "size": entry.stat().st_size if entry.is_file() else 0,
                })

            return {
                "directory": str(dirpath),
                "items": items,
                "total": len(items),
                "success": True,
            }
        except PermissionError as e:
            return {"error": str(e), "success": False}
        except Exception as e:
            return {"error": f"Erro ao listar diretório: {e}", "success": False}

    # ── Ferramenta: Executar Comando Shell (com Regra da Alice) ────────────────

    def execute_shell(
        self,
        command: str,
        timeout: int = 30,
        cwd: Optional[str] = None,
        silent: bool = True,
    ) -> dict:
        """
        Executa um comando shell silenciosamente e captura o output.

        Regra da Alice:
          Comandos perigosos (rm, apt, kill, etc.) disparam um prompt de
          autorização (Y/N) antes de executar.

        Args:
            command: Comando shell a ser executado.
            timeout: Tempo máximo de execução em segundos.
            cwd: Diretório de trabalho (default: workspace_dir).
            silent: Se True, não exibe output no terminal (apenas captura).

        Returns:
            Dict com stdout, stderr, return_code, success.
        """
        # ── Regra da Alice: Verificar comando perigoso ─────────────────────
        dangerous_pattern = self._is_dangerous(command)
        if dangerous_pattern:
            msg = (
                f"[bold red]⚠ ALICE: COMANDO PERIGOSO DETECTADO[/]\n"
                f"  Padrão: [amber]'{dangerous_pattern}'[/]\n"
                f"  Comando: [cyan]{command[:200]}[/]\n"
                f"  [bold yellow]Deseja autorizar a execução?[/]"
            )
            if self.approval_callback:
                approved = self.approval_callback(msg)
                if not approved:
                    return {
                        "stdout": "",
                        "stderr": f"Comando rejeitado pela Regra da Alice: "
                                  f"'{dangerous_pattern}' detectado. "
                                  f"Execução cancelada pelo usuário.",
                        "return_code": -1,
                        "success": False,
                        "blocked_by": "alice",
                    }
            else:
                # Sem callback de aprovação — bloqueia por segurança
                return {
                    "stdout": "",
                    "stderr": f"Comando bloqueado pela Regra da Alice: "
                              f"'{dangerous_pattern}' detectado. "
                              f"Nenhum callback de aprovação configurado.",
                    "return_code": -1,
                    "success": False,
                    "blocked_by": "alice",
                }

        # ── Execução segura ────────────────────────────────────────────────
        try:
            exec_cwd = cwd or str(self.workspace_dir)
            result = subprocess.run(
                ["bash", "-c", command],
                capture_output=silent,
                text=True,
                timeout=timeout,
                cwd=exec_cwd,
            )
            return {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "return_code": result.returncode,
                "success": result.returncode == 0,
            }
        except subprocess.TimeoutExpired:
            return {
                "stdout": "",
                "stderr": f"Comando excedeu o tempo limite de {timeout}s",
                "return_code": -1,
                "success": False,
            }
        except Exception as e:
            return {
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "success": False,
            }

    # ── Listar ferramentas disponíveis (para o agente) ────────────────────────

    def list_tools(self) -> list[dict]:
        """
        Retorna a lista de ferramentas disponíveis para o agente.
        Usado para montar o system prompt com as tools disponíveis.
        """
        return [
            {
                "name": "read_file",
                "description": "Lê o conteúdo de um arquivo. Parâmetros: path (obrigatório), "
                               "start_line (opcional, 1-based), end_line (opcional).",
                "parameters": {
                    "path": "string (obrigatório)",
                    "start_line": "int (opcional, default=1)",
                    "end_line": "int (opcional, default=final do arquivo)",
                },
            },
            {
                "name": "write_file",
                "description": "Escreve conteúdo em um arquivo (cria ou sobrescreve). "
                               "Parâmetros: path (obrigatório), content (obrigatório).",
                "parameters": {
                    "path": "string (obrigatório)",
                    "content": "string (obrigatório) — conteúdo completo do arquivo",
                },
            },
            {
                "name": "replace_in_file",
                "description": "Substitui um bloco de texto em um arquivo existente. "
                               "A busca deve corresponder exatamente. "
                               "Parâmetros: path, search, replace.",
                "parameters": {
                    "path": "string (obrigatório)",
                    "search": "string (obrigatório) — texto exato a ser procurado",
                    "replace": "string (obrigatório) — novo texto",
                },
            },
            {
                "name": "create_directory",
                "description": "Cria um diretório (e subdiretórios se necessário). "
                               "Parâmetros: path (obrigatório).",
                "parameters": {
                    "path": "string (obrigatório)",
                },
            },
            {
                "name": "delete_file",
                "description": "Deleta um arquivo. Parâmetros: path (obrigatório).",
                "parameters": {
                    "path": "string (obrigatório)",
                },
            },
            {
                "name": "delete_directory",
                "description": "Deleta um diretório. Parâmetros: path (obrigatório), "
                               "recursive (opcional, default=False).",
                "parameters": {
                    "path": "string (obrigatório)",
                    "recursive": "bool (opcional, default=False)",
                },
            },
            {
                "name": "list_directory",
                "description": "Lista o conteúdo de um diretório. "
                               "Parâmetros: path (opcional, default='.').",
                "parameters": {
                    "path": "string (opcional, default='.')",
                },
            },
            {
                "name": "execute_shell",
                "description": "Executa um comando shell silenciosamente e captura o output. "
                               "Comandos perigosos (rm, apt, kill, etc.) exigem aprovação do usuário "
                               "(Regra da Alice). "
                               "Parâmetros: command (obrigatório), timeout (opcional, default=30), "
                               "cwd (opcional).",
                "parameters": {
                    "command": "string (obrigatório) — comando shell",
                    "timeout": "int (opcional, default=30)",
                    "cwd": "string (opcional) — diretório de trabalho",
                },
            },
        ]