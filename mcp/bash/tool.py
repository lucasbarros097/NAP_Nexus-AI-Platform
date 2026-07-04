"""Bash MCP Tool - Executes shell commands for NAP agents."""

import subprocess
import logging
import shlex
from typing import Optional

logger = logging.getLogger(__name__)


class BashTool:
    """MCP tool for bash command execution."""

    def execute(self, command: str, timeout: int = 30) -> dict:
        """Execute a shell command and return result.

        Args:
            command: Shell command to execute.
            timeout: Maximum execution time in seconds.

        Returns:
            Dict with stdout, stderr, return_code, and success status.
        """
        try:
            result = subprocess.run(
                ["bash", "-c", command],
                capture_output=True,
                text=True,
                timeout=timeout,
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
                "stderr": f"Command timed out after {timeout}s",
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

    def read_file(self, filepath: str) -> str:
        """Read a file using cat."""
        result = self.execute(f"cat {shlex.quote(filepath)}")
        return result["stdout"]

    def write_file(self, filepath: str, content: str) -> bool:
        """Write content to a file."""
        escaped = content.replace("'", "'\\''")
        result = self.execute(
            f"cat > {shlex.quote(filepath)} << 'EOF'\n{content}\nEOF"
        )
        return result["success"]

    def list_directory(self, path: str = ".") -> str:
        """List directory contents."""
        result = self.execute(f"ls -la {shlex.quote(path)}")
        return result["stdout"]

    def make_directory(self, path: str) -> bool:
        """Create a directory."""
        result = self.execute(f"mkdir -p {shlex.quote(path)}")
        return result["success"]


bash_tool = BashTool()