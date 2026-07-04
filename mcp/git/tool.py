"""Git MCP Tool - Provides version control operations for NAP agents."""

import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class GitTool:
    """MCP tool for Git operations."""

    def __init__(self, workspace: str = "/workspace"):
        self.workspace = Path(workspace)

    def _run(self, *args: str, cwd: Optional[Path] = None) -> str:
        """Execute a git command and return output."""
        work_dir = cwd or self.workspace
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                logger.warning("Git error: %s", result.stderr)
                return result.stderr
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "ERROR: Git command timed out"
        except FileNotFoundError:
            return "ERROR: Git not found"

    def init(self, path: Optional[str] = None) -> str:
        """Initialize a new git repository."""
        target = self.workspace / path if path else self.workspace
        return self._run("init", cwd=target)

    def clone(self, url: str, dest: Optional[str] = None) -> str:
        """Clone a repository."""
        args = ["clone", url]
        if dest:
            args.append(dest)
        return self._run(*args)

    def add(self, files: str = ".") -> str:
        """Stage files for commit."""
        return self._run("add", files)

    def commit(self, message: str) -> str:
        """Create a commit with the given message."""
        return self._run("commit", "-m", message)

    def status(self) -> str:
        """Show working tree status."""
        return self._run("status")

    def diff(self) -> str:
        """Show changes not yet staged."""
        return self._run("diff")

    def log(self, max_count: int = 10) -> str:
        """Show commit log."""
        return self._run("log", f"--max-count={max_count}", "--oneline")

    def push(self, remote: str = "origin", branch: str = "main") -> str:
        """Push to remote repository."""
        return self._run("push", remote, branch)

    def pull(self, remote: str = "origin", branch: str = "main") -> str:
        """Pull from remote repository."""
        return self._run("pull", remote, branch)

    def branch(self, name: Optional[str] = None) -> str:
        """List or create branches."""
        if name:
            return self._run("checkout", "-b", name)
        return self._run("branch")


git_tool = GitTool()