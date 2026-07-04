"""Python MCP Tool - Executes and validates Python code for NAP agents."""

import subprocess
import ast
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PythonTool:
    """MCP tool for Python code execution and validation."""

    def _run(self, *args: str) -> str:
        """Execute a python command and return output."""
        try:
            result = subprocess.run(
                ["python3", *args],
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout.strip()
            if result.stderr:
                output += f"\nSTDERR: {result.stderr.strip()}"
            return output
        except subprocess.TimeoutExpired:
            return "ERROR: Python command timed out"
        except FileNotFoundError:
            return "ERROR: Python3 not found"

    def check_syntax(self, code: str) -> dict:
        """Check Python code syntax without executing."""
        try:
            ast.parse(code)
            return {"valid": True, "error": None}
        except SyntaxError as e:
            return {"valid": False, "error": str(e)}

    def run_code(self, code: str) -> str:
        """Execute Python code and return output."""
        return self._run("-c", code)

    def run_file(self, filepath: str) -> str:
        """Execute a Python file."""
        return self._run(filepath)

    def install_package(self, package: str) -> str:
        """Install a Python package using pip."""
        return self._run("-m", "pip", "install", package)

    def lint(self, filepath: str) -> str:
        """Run ruff linter on a file."""
        return self._run("-m", "ruff", "check", filepath)

    def format(self, filepath: str) -> str:
        """Format a Python file using ruff."""
        return self._run("-m", "ruff", "format", filepath)


python_tool = PythonTool()