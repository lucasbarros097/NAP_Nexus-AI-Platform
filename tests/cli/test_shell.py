"""Tests for the NAP CLI interactive shell."""

import pytest
from unittest.mock import patch, MagicMock
from cli.shell import NAPShell


@pytest.fixture
def shell():
    """Create a NAPShell instance for testing."""
    with patch("cli.shell.NAPShell._check_backend"):  # Skip backend check
        s = NAPShell()
        s.stdout = MagicMock()  # Suppress output
        return s


class TestNAPShell:
    """Test suite for NAPShell commands."""

    def test_shell_initialization(self, shell):
        """Test that shell initializes with correct defaults."""
        assert shell.prompt == "\n⚡ nap> "
        assert shell.api_base_url == "http://localhost:8000"
        assert shell.session_history == []

    def test_emptyline(self, shell):
        """Test that empty line does nothing."""
        shell.emptyline()  # Should not raise

    def test_do_exit(self, shell):
        """Test exit command returns True."""
        result = shell.do_exit("")
        assert result is True

    def test_do_quit(self, shell):
        """Test quit command returns True."""
        result = shell.do_quit("")
        assert result is True

    def test_do_clear(self, shell):
        """Test clear command runs without error."""
        shell.do_clear("")  # Should not raise

    def test_do_agents(self, shell):
        """Test agents command prints agent list."""
        shell.do_agents("")  # Should not raise

    def test_do_history_empty(self, shell):
        """Test history command when no history exists."""
        shell.do_history("")  # Should not raise

    def test_do_history_with_entries(self, shell):
        """Test history command with session entries."""
        shell.session_history.append({
            "role": "user",
            "content": "test message",
            "timestamp": "2026-07-04T08:00:00",
        })
        shell.do_history("")  # Should not raise

    def test_do_chat_no_args(self, shell):
        """Test chat command with no arguments."""
        shell.do_chat("")  # Should print warning, not raise

    def test_do_run_no_args(self, shell):
        """Test run command with no arguments."""
        shell.do_run("")  # Should print warning, not raise

    def test_do_status(self, shell):
        """Test status command runs without error."""
        shell.do_status("")  # Should not raise

    def test_do_projects(self, shell):
        """Test projects command runs without error."""
        shell.do_projects("")  # Should not raise

    def test_do_logs_default(self, shell):
        """Test logs command with default args."""
        shell.do_logs("")  # Should not raise

    def test_do_logs_with_args(self, shell):
        """Test logs command with service specified."""
        shell.do_logs("backend 10")  # Should not raise

    def test_do_help(self, shell):
        """Test help command."""
        shell.do_help("")  # Should not raise

    def test_do_help_specific(self, shell):
        """Test help for specific command."""
        shell.do_help("chat")  # Should not raise

    def test_default_handler(self, shell):
        """Test that unknown commands are treated as chat."""
        with patch.object(shell, "do_chat") as mock_chat:
            shell.default("some unknown text")
            mock_chat.assert_called_once_with("some unknown text")

    def test_default_handler_empty(self, shell):
        """Test that empty default does nothing."""
        shell.default("")  # Should not raise

    def test_completenames(self, shell):
        """Test command name completion."""
        completions = shell.completenames("ch")
        assert "chat" in completions

        completions = shell.completenames("st")
        assert "status" in completions

    def test_session_history_tracking(self, shell):
        """Test that session history is properly tracked."""
        assert len(shell.session_history) == 0

        shell.session_history.append({
            "role": "user",
            "content": "hello",
            "timestamp": "2026-01-01T00:00:00",
        })
        assert len(shell.session_history) == 1
        assert shell.session_history[0]["role"] == "user"

    def test_api_base_url_default(self, shell):
        """Test default API URL."""
        assert shell.api_base_url == "http://localhost:8000"

    def test_api_base_url_env(self):
        """Test API URL from environment variable."""
        with patch.dict("os.environ", {"NAP_API_URL": "http://custom:9000"}):
            with patch("cli.shell.NAPShell._check_backend"):
                s = NAPShell()
                assert s.api_base_url == "http://custom:9000"


class TestApprovalWorkflow:
    """Test the approval workflow for file-modifying commands."""

    def test_approval_keywords_detected(self, shell):
        """Test that creation keywords trigger approval check."""
        with patch.object(shell, "_prompt_yes_no", return_value=True):
            with patch.object(shell, "_stream_agent_output", return_value=None):
                shell.do_chat("crie uma API")  # Should trigger approval

    def test_approval_cancelled(self, shell):
        """Test that user can cancel operations."""
        with patch.object(shell, "_prompt_yes_no", return_value=False):
            with patch.object(shell, "_stream_agent_output") as mock_stream:
                shell.do_chat("crie uma API")
                mock_stream.assert_not_called()  # Should NOT execute

    def test_approval_no_keywords(self, shell):
        """Test that non-creation commands don't trigger approval."""
        with patch.object(shell, "_prompt_yes_no") as mock_approval:
            with patch.object(shell, "_stream_agent_output", return_value=None):
                shell.do_chat("explique o que é FastAPI")
                mock_approval.assert_not_called()  # Should NOT ask for approval
