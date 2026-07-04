"""Docker MCP Tool - Provides container management for NAP agents."""

import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DockerTool:
    """MCP tool for Docker operations."""

    def _run(self, *args: str) -> str:
        """Execute a docker command and return output."""
        try:
            result = subprocess.run(
                ["docker", *args],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                logger.warning("Docker error: %s", result.stderr)
                return result.stderr
            return result.stdout.strip()
        except subprocess.TimeoutExpired:
            return "ERROR: Docker command timed out"
        except FileNotFoundError:
            return "ERROR: Docker not found"

    def ps(self, all: bool = False) -> str:
        """List containers."""
        args = ["ps"]
        if all:
            args.append("-a")
        return self._run(*args)

    def images(self) -> str:
        """List images."""
        return self._run("images")

    def build(self, path: str, tag: str = "nap:latest") -> str:
        """Build a Docker image."""
        return self._run("build", "-t", tag, path)

    def pull(self, image: str) -> str:
        """Pull a Docker image."""
        return self._run("pull", image)

    def compose_up(self, project_dir: str = ".", detach: bool = True) -> str:
        """Run docker compose up."""
        args = ["compose", "-f", f"{project_dir}/docker-compose.yml", "up"]
        if detach:
            args.append("-d")
        return self._run(*args)

    def compose_down(self, project_dir: str = ".") -> str:
        """Run docker compose down."""
        return self._run("compose", "-f", f"{project_dir}/docker-compose.yml", "down")

    def logs(self, container: str, lines: int = 50) -> str:
        """Show container logs."""
        return self._run("logs", "--tail", str(lines), container)

    def exec(self, container: str, command: str) -> str:
        """Execute a command in a running container."""
        return self._run("exec", container, "sh", "-c", command)


docker_tool = DockerTool()