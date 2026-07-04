"""PostgreSQL MCP Tool - Database operations for NAP agents."""

import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class PostgreSQLTool:
    """MCP tool for PostgreSQL database operations."""

    def __init__(
        self,
        host: str = "postgres",
        port: str = "5432",
        user: str = "nap_user",
        password: str = "nap_pass",
        database: str = "nap_nexus",
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def _psql(self, command: str) -> str:
        """Execute a psql command."""
        try:
            result = subprocess.run(
                [
                    "psql",
                    "-h", self.host,
                    "-p", self.port,
                    "-U", self.user,
                    "-d", self.database,
                    "-c", command,
                ],
                capture_output=True,
                text=True,
                timeout=15,
                env={"PGPASSWORD": self.password},
            )
            output = result.stdout.strip()
            if result.stderr:
                output += f"\nSTDERR: {result.stderr.strip()}"
            return output
        except subprocess.TimeoutExpired:
            return "ERROR: PostgreSQL command timed out"
        except FileNotFoundError:
            return "ERROR: psql not found"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def query(self, sql: str) -> str:
        """Execute a SQL query."""
        logger.info("Executing SQL: %s", sql[:100])
        return self._psql(sql)

    def list_tables(self) -> str:
        """List all tables in the database."""
        return self.query(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name;"
        )

    def describe_table(self, table: str) -> str:
        """Describe a table structure."""
        return self.query(
            f"SELECT column_name, data_type, is_nullable "
            f"FROM information_schema.columns "
            f"WHERE table_name = '{table}' ORDER BY ordinal_position;"
        )

    def run_migrations(self, alembic_dir: str = "/app") -> str:
        """Run Alembic migrations."""
        try:
            result = subprocess.run(
                ["alembic", "upgrade", "head"],
                cwd=alembic_dir,
                capture_output=True,
                text=True,
                timeout=30,
                env={"PGPASSWORD": self.password},
            )
            return result.stdout.strip() or result.stderr.strip()
        except Exception as e:
            return f"ERROR: Migration failed: {str(e)}"


postgresql_tool = PostgreSQLTool()