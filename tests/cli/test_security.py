"""Tests for the NAP Security Module (Code Signing, Anti-Virus, Integrity)."""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from cli.security import CodeSigningManager, SecurePackager, security_status, sign_build


class TestCodeSigningManager:
    """Test suite for CodeSigningManager."""

    @pytest.fixture
    def manager(self, tmp_path):
        """Create a CodeSigningManager with temp directories."""
        with patch("cli.security.CERTS_DIR", tmp_path / "certs"):
            with patch("cli.security.SIGNATURES_DIR", tmp_path / "signatures"):
                with patch("cli.security.MANIFEST_FILE", tmp_path / "manifest.json"):
                    m = CodeSigningManager()
                    yield m

    def test_initialization(self, manager):
        """Test that manager creates directories."""
        assert manager.certs_dir.exists()
        assert manager.signatures_dir.exists()

    def test_sha256(self, manager, tmp_path):
        """Test SHA-256 hash computation."""
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"hello world")
        hash_val = manager._sha256(test_file)
        assert len(hash_val) == 64  # SHA-256 hex length
        assert hash_val == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"

    def test_manifest_load_empty(self, manager):
        """Test loading manifest when file doesn't exist."""
        manifest = manager._load_manifest()
        assert manifest == {"signatures": [], "checksums": {}}

    def test_manifest_save_and_load(self, manager):
        """Test saving and loading manifest."""
        manifest = {"signatures": [{"test": True}], "checksums": {}}
        manager._save_manifest(manifest)
        loaded = manager._load_manifest()
        assert loaded == manifest

    def test_record_signature(self, manager, tmp_path):
        """Test recording a signature in manifest."""
        test_file = tmp_path / "nap.exe"
        test_file.write_text("fake binary")
        manager._record_signature(test_file, "windows", "authenticode")
        manifest = manager._load_manifest()
        assert len(manifest["signatures"]) == 1
        assert manifest["signatures"][0]["platform"] == "windows"
        assert manifest["signatures"][0]["method"] == "authenticode"

    def test_verify_integrity_nonexistent(self, manager):
        """Test integrity check on non-existent file."""
        result = manager.verify_integrity(Path("/nonexistent/file"))
        assert result["exists"] is False

    def test_verify_integrity_existing(self, manager, tmp_path):
        """Test integrity check on existing file."""
        test_file = tmp_path / "nap"
        test_file.write_text("fake binary")
        result = manager.verify_integrity(test_file)
        assert result["exists"] is True
        assert result["sha256"] is not None

    def test_generate_self_signed_cert_openssl_missing(self, manager):
        """Test cert generation when OpenSSL is missing."""
        with patch("subprocess.run", side_effect=FileNotFoundError):
            result = manager.generate_self_signed_cert()
            assert result is None

    def test_sign_windows_no_binary(self, manager):
        """Test Windows signing with non-existent binary."""
        result = manager.sign_windows(Path("/nonexistent.exe"))
        assert result is False

    def test_sign_linux_no_binary(self, manager):
        """Test Linux signing with non-existent binary."""
        result = manager.sign_linux(Path("/nonexistent"))
        assert result is False


class TestSecurePackager:
    """Test suite for SecurePackager."""

    @pytest.fixture
    def packager(self):
        """Create a SecurePackager instance."""
        return SecurePackager()

    def test_antivirus_triggers_list(self, packager):
        """Test that trigger list is not empty."""
        assert len(packager.ANTIVIRUS_TRIGGERS) > 0
        assert "crypt" in packager.ANTIVIRUS_TRIGGERS
        assert "exploit" in packager.ANTIVIRUS_TRIGGERS

    def test_scan_for_triggers_clean(self, packager, tmp_path):
        """Test scanning clean code returns empty."""
        clean_file = tmp_path / "clean.py"
        clean_file.write_text("print('hello world')\nimport os\n")
        results = packager.scan_for_triggers(tmp_path)
        assert len(results) == 0

    def test_scan_for_triggers_found(self, packager, tmp_path):
        """Test scanning code with triggers returns matches."""
        dirty_file = tmp_path / "dirty.py"
        dirty_file.write_text("import crypt\nresult = decrypt(data)\n")
        results = packager.scan_for_triggers(tmp_path)
        assert len(results) > 0
        assert any("crypt" in r for r in results)

    def test_add_windows_manifest(self, packager, tmp_path):
        """Test adding Windows manifest to executable."""
        exe_path = tmp_path / "nap.exe"
        exe_path.write_text("fake exe")
        result = packager.add_windows_manifest(exe_path)
        assert result is True
        manifest_path = exe_path.with_suffix(".exe.manifest")
        assert manifest_path.exists()
        content = manifest_path.read_text()
        assert "NAP.Nexus.Platform" in content
        assert "asInvoker" in content

    def test_add_windows_manifest_no_exe(self, packager):
        """Test manifest on non-existent file."""
        result = packager.add_windows_manifest(Path("/nonexistent.exe"))
        assert result is False

    def test_customize_bootloader(self, packager):
        """Test bootloader customization (may not have source)."""
        result = packager.customize_bootloader()
        # Should not crash, returns bool
        assert isinstance(result, bool)


class TestSecurityFunctions:
    """Test suite for security module functions."""

    def test_security_status(self):
        """Test security_status returns dict with expected keys."""
        status = security_status()
        assert "certificates" in status
        assert "signed_binaries" in status
        assert "bootloader_customized" in status
        assert "antivirus_triggers" in status

    def test_sign_build_empty_dir(self, tmp_path):
        """Test sign_build on empty directory."""
        results = sign_build(tmp_path)
        assert "signed" in results
        assert "failed" in results
        assert "skipped" in results
        assert len(results["signed"]) == 0

    def test_sign_build_with_binaries(self, tmp_path):
        """Test sign_build with binaries (will fail without signtool)."""
        # Create fake binaries
        (tmp_path / "nap.exe").write_text("fake exe")
        (tmp_path / "nap.deb").write_text("fake deb")

        with patch("cli.security.CodeSigningManager.sign_windows", return_value=False):
            with patch("cli.security.CodeSigningManager.sign_linux", return_value=False):
                results = sign_build(tmp_path, platform="linux")
                assert len(results["failed"]) > 0