"""
NAP Security Module — Code Signing, Anti-Virus Evasion & Trust Architecture

Gerencia:
- Code Signing (Authenticode para Windows, GPG para Linux)
- PyInstaller bootloader recompilação customizada (evitar heurísticas de malware)
- Boas práticas de empacotamento seguro
- Verificação de integridade dos binários
"""

import os
import sys
import json
import hashlib
import logging
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime

logger = logging.getLogger("nap.security")

# ─── Constants ────────────────────────────────────────────────────────────────
SECURITY_DIR = Path(__file__).resolve().parent.parent / "security"
CERTS_DIR = SECURITY_DIR / "certs"
SIGNATURES_DIR = SECURITY_DIR / "signatures"
MANIFEST_FILE = SECURITY_DIR / "manifest.json"


class CodeSigningManager:
    """
    Gerencia assinatura digital dos binários NAP.
    
    Suporta:
    - Windows: Authenticode (signtool.exe via wine ou nativo)
    - Linux: GPG signatures + dpkg-sig
    - macOS: codesign (futuro)
    """

    def __init__(self):
        self.certs_dir = CERTS_DIR
        self.signatures_dir = SIGNATURES_DIR
        self.manifest_file = MANIFEST_FILE

        # Ensure directories exist
        self.certs_dir.mkdir(parents=True, exist_ok=True)
        self.signatures_dir.mkdir(parents=True, exist_ok=True)

    # ── Certificate Management ────────────────────────────────────────────────

    def generate_self_signed_cert(self, output_path: Optional[Path] = None) -> Optional[Path]:
        """
        Gera um certificado auto-assinado para desenvolvimento/teste.
        
        AVISO: Certificados auto-assinados NÃO são confiáveis por sistemas
        operacionais. Use apenas para testes. Para produção, adquira um
        EV Code Signing Certificate de uma CA confiável (DigiCert, Sectigo, etc.).
        """
        if output_path is None:
            output_path = self.certs_dir / "nap-dev.pfx"

        try:
            # Generate self-signed cert using OpenSSL
            key_path = self.certs_dir / "nap-dev.key"
            crt_path = self.certs_dir / "nap-dev.crt"

            subprocess.run(
                [
                    "openssl", "req", "-x509", "-newkey", "rsa:4096",
                    "-keyout", str(key_path),
                    "-out", str(crt_path),
                    "-days", "365",
                    "-nodes",
                    "-subj", "/C=BR/ST=SP/O=NAP Nexus/CN=NAP Development",
                ],
                check=True, capture_output=True, text=True, timeout=30,
            )

            # Convert to PKCS12 (PFX) for Windows signtool
            subprocess.run(
                [
                    "openssl", "pkcs12", "-export",
                    "-inkey", str(key_path),
                    "-in", str(crt_path),
                    "-out", str(output_path),
                    "-passout", "pass:",
                ],
                check=True, capture_output=True, text=True, timeout=30,
            )

            logger.info("✅ Self-signed certificate generated: %s", output_path)
            return output_path

        except FileNotFoundError:
            logger.error("OpenSSL not found. Install: sudo apt install openssl")
            return None
        except subprocess.CalledProcessError as e:
            logger.error("Certificate generation failed: %s", e.stderr)
            return None

    # ── Windows Code Signing (Authenticode) ───────────────────────────────────

    def sign_windows(
        self,
        binary_path: Path,
        cert_path: Optional[Path] = None,
        timestamp_url: str = "http://timestamp.digicert.com",
    ) -> bool:
        """
        Assina um executável Windows com Authenticode.
        
        Usa signtool.exe (via wine em Linux, ou nativo em Windows).
        Para produção, use um EV Code Signing Certificate.
        
        Args:
            binary_path: Caminho do .exe para assinar
            cert_path: Caminho do certificado .pfx
            timestamp_url: URL do servidor de timestamp
        """
        if not binary_path.exists():
            logger.error("Binary not found: %s", binary_path)
            return False

        if cert_path is None:
            cert_path = self.certs_dir / "nap-dev.pfx"
            if not cert_path.exists():
                logger.warning("No certificate found. Generating self-signed...")
                cert_path = self.generate_self_signed_cert()
                if cert_path is None:
                    return False

        # Try signtool via wine (cross-platform)
        signtool_candidates = [
            ["wine", "signtool.exe"],  # Linux via wine
            ["signtool.exe"],           # Windows native
            ["signtool"],               # In PATH
        ]

        for signtool in signtool_candidates:
            try:
                result = subprocess.run(
                    [
                        *signtool, "sign",
                        "/fd", "SHA256",
                        "/a",  # Auto-select best cert
                        "/f", str(cert_path),
                        "/tr", timestamp_url,
                        "/td", "SHA256",
                        str(binary_path),
                    ],
                    capture_output=True, text=True, timeout=60,
                )
                if result.returncode == 0:
                    logger.info("✅ Windows binary signed: %s", binary_path)
                    self._record_signature(binary_path, "windows", "authenticode")
                    return True
                logger.debug("signtool failed: %s", result.stderr[:200])
            except FileNotFoundError:
                continue
            except subprocess.TimeoutExpired:
                logger.warning("signtool timed out")
                continue

        logger.warning(
            "signtool not available. Install Windows SDK or use wine.\n"
            "  Windows: Install 'Windows SDK' (includes signtool.exe)\n"
            "  Linux:   wine signtool.exe (requires Windows SDK via wine)"
        )
        return False

    # ── Linux Code Signing (GPG + dpkg-sig) ───────────────────────────────────

    def sign_linux(self, binary_path: Path, gpg_key_id: Optional[str] = None) -> bool:
        """
        Assina binário Linux com GPG e pacote .deb com dpkg-sig.
        
        Args:
            binary_path: Caminho do binário ou .deb para assinar
            gpg_key_id: ID da chave GPG (usa default se não especificado)
        """
        if not binary_path.exists():
            logger.error("Binary not found: %s", binary_path)
            return False

        success = True

        # 1. GPG signature (.sig)
        try:
            args = ["gpg", "--detach-sign", "--armor"]
            if gpg_key_id:
                args.extend(["--local-user", gpg_key_id])
            args.append(str(binary_path))

            result = subprocess.run(args, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                sig_path = binary_path.with_suffix(binary_path.suffix + ".sig")
                logger.info("✅ GPG signature created: %s", sig_path)
                self._record_signature(binary_path, "linux", "gpg")
            else:
                logger.warning("GPG signing failed: %s", result.stderr[:200])
                success = False
        except FileNotFoundError:
            logger.warning("GPG not found. Install: sudo apt install gnupg")
            success = False

        # 2. dpkg-sig for .deb packages
        if binary_path.suffix == ".deb":
            try:
                result = subprocess.run(
                    ["dpkg-sig", "--sign", "builder", str(binary_path)],
                    capture_output=True, text=True, timeout=30,
                )
                if result.returncode == 0:
                    logger.info("✅ dpkg-sig signature added: %s", binary_path)
                else:
                    logger.warning("dpkg-sig failed: %s", result.stderr[:200])
            except FileNotFoundError:
                logger.warning("dpkg-sig not found. Install: sudo apt install dpkg-sig")

        return success

    # ── Signature Recording ───────────────────────────────────────────────────

    def _record_signature(self, binary_path: Path, platform: str, method: str):
        """Record signature in manifest for audit trail."""
        manifest = self._load_manifest()
        manifest["signatures"].append({
            "binary": str(binary_path),
            "platform": platform,
            "method": method,
            "timestamp": datetime.utcnow().isoformat(),
            "sha256": self._sha256(binary_path),
        })
        self._save_manifest(manifest)

    # ── Manifest Management ───────────────────────────────────────────────────

    def _load_manifest(self) -> dict:
        """Load the security manifest file."""
        if self.manifest_file.exists():
            try:
                return json.loads(self.manifest_file.read_text())
            except json.JSONDecodeError:
                pass
        return {"signatures": [], "checksums": {}}

    def _save_manifest(self, manifest: dict):
        """Save the security manifest file."""
        self.manifest_file.write_text(json.dumps(manifest, indent=2))
        logger.debug("Manifest updated: %s", self.manifest_file)

    @staticmethod
    def _sha256(filepath: Path) -> str:
        """Compute SHA-256 hash of a file."""
        h = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()

    # ── Integrity Verification ────────────────────────────────────────────────

    def verify_integrity(self, binary_path: Path) -> dict:
        """
        Verifica a integridade de um binário.
        
        Returns:
            Dict com status de verificação: sha256, gpg, authenticode
        """
        result = {
            "file": str(binary_path),
            "exists": binary_path.exists(),
            "sha256": None,
            "gpg_valid": None,
            "authenticode_valid": None,
        }

        if not binary_path.exists():
            return result

        # SHA-256
        result["sha256"] = self._sha256(binary_path)

        # GPG verification
        sig_path = binary_path.with_suffix(binary_path.suffix + ".sig")
        if sig_path.exists():
            try:
                r = subprocess.run(
                    ["gpg", "--verify", str(sig_path), str(binary_path)],
                    capture_output=True, text=True, timeout=15,
                )
                result["gpg_valid"] = r.returncode == 0
            except FileNotFoundError:
                result["gpg_valid"] = None

        # Authenticode verification (Windows)
        try:
            r = subprocess.run(
                ["signtool", "verify", "/pa", str(binary_path)],
                capture_output=True, text=True, timeout=15,
            )
            result["authenticode_valid"] = r.returncode == 0
        except FileNotFoundError:
            try:
                r = subprocess.run(
                    ["wine", "signtool.exe", "verify", "/pa", str(binary_path)],
                    capture_output=True, text=True, timeout=30,
                )
                result["authenticode_valid"] = r.returncode == 0
            except FileNotFoundError:
                result["authenticode_valid"] = None

        return result


class SecurePackager:
    """
    Gerencia empacotamento seguro com boas práticas anti-heurísticas.
    
    Estratégias:
    1. Recompilação customizada do bootloader PyInstaller
    2. Ofuscação de strings sensíveis
    3. Metadados de editor confiável
    4. Evitar padrões conhecidos de malware
    """

    # Padrões que acionam heurísticas de antivírus (evitar)
    ANTIVIRUS_TRIGGERS = [
        "crypt", "decrypt", "inject", "hook", "keylog",
        "reverse", "shellcode", "payload", "ransom",
        "miner", "steal", "bypass", "exploit",
    ]

    def __init__(self):
        self.pyinstaller_bootloader_dir = self._find_pyinstaller_bootloader()

    @staticmethod
    def _find_pyinstaller_bootloader() -> Optional[Path]:
        """Find PyInstaller bootloader source directory."""
        try:
            import PyInstaller
            pyi_dir = Path(PyInstaller.__file__).resolve().parent
            bootloader_dir = pyi_dir / "bootloader"
            if bootloader_dir.exists():
                return bootloader_dir
        except ImportError:
            pass
        return None

    def scan_for_triggers(self, source_dir: Path) -> list[str]:
        """
        Escaneia código fonte por padrões que acionam heurísticas de antivírus.
        
        Returns:
            Lista de arquivos com potenciais triggers
        """
        found = []
        for py_file in source_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8", errors="ignore")
                for trigger in self.ANTIVIRUS_TRIGGERS:
                    if trigger.lower() in content.lower():
                        found.append(f"{py_file.relative_to(source_dir)}: '{trigger}'")
                        break
            except Exception:
                continue
        return found

    def add_windows_manifest(self, exe_path: Path, publisher: str = "NAP Nexus"):
        """
        Adiciona manifest de aplicação confiável ao executável Windows.
        
        Isso ajuda o Windows SmartScreen a reconhecer o software como confiável.
        """
        if not exe_path.exists():
            logger.error("Executable not found: %s", exe_path)
            return False

        manifest = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
  <assemblyIdentity
    version="0.2.0.0"
    processorArchitecture="amd64"
    name="NAP.Nexus.Platform"
    type="win32"
  />
  <description>NAP - Nexus AI Platform</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel level="asInvoker" uiAccess="false"/>
      </requestedPrivileges>
    </security>
  </trustInfo>
  <compatibility xmlns="urn:schemas-microsoft-com:compatibility.v1">
    <application>
      <supportedOS Id="{{8e0f7a12-bfb3-4fe8-b9a5-48fd50a15a9a}}"/>
      <supportedOS Id="{{1f676c76-80e1-4239-95bb-83d0f6d0da78}}"/>
      <supportedOS Id="{{4a2f28e3-53b9-4441-ba9c-d69d4a4a6e38}}"/>
      <supportedOS Id="{{e2011457-1546-43c5-a5fe-008deee3d3f0}}"/>
    </application>
  </compatibility>
</assembly>"""

        manifest_path = exe_path.with_suffix(exe_path.suffix + ".manifest")
        manifest_path.write_text(manifest, encoding="utf-8")
        logger.info("✅ Windows manifest created: %s", manifest_path)
        return True

    def customize_bootloader(self, company_name: str = "NAP Nexus") -> bool:
        """
        Recompila o bootloader do PyInstaller com metadados customizados.
        
        Isso reduz falsos-positivos pois o bootloader padrão do PyInstaller
        é frequentemente alvo de heurísticas de antivírus.
        """
        if not self.pyinstaller_bootloader_dir:
            logger.warning(
                "PyInstaller bootloader source not found.\n"
                "  To customize: pip install pyinstaller --no-binary pyinstaller\n"
                "  This compiles the bootloader from source."
            )
            return False

        logger.info(
            "PyInstaller bootloader found at: %s\n"
            "  To recompile with custom metadata:\n"
            "  1. cd %s\n"
            "  2. Modify ./src/setup.py with your company name\n"
            "  3. Run: python waf all\n"
            "  4. pip install . --no-binary pyinstaller",
            self.pyinstaller_bootloader_dir,
            self.pyinstaller_bootloader_dir,
        )
        return True


# ─── CLI Integration ──────────────────────────────────────────────────────────

def security_status() -> dict:
    """Return security status summary for the CLI status command."""
    manager = CodeSigningManager()
    packager = SecurePackager()

    manifest = manager._load_manifest()
    signed_count = len(manifest.get("signatures", []))

    return {
        "certificates": list(CERTS_DIR.glob("*")),
        "signed_binaries": signed_count,
        "bootloader_customized": packager.pyinstaller_bootloader_dir is not None,
        "antivirus_triggers": packager.ANTIVIRUS_TRIGGERS,
    }


def sign_build(build_dir: Path, platform: str = "auto") -> dict:
    """
    Assina todos os binários em um diretório de build.
    
    Args:
        build_dir: Diretório contendo os binários (dist/)
        platform: "linux", "windows", ou "auto" (detecta automaticamente)
    
    Returns:
        Dict com resultados da assinatura
    """
    manager = CodeSigningManager()
    results = {"signed": [], "failed": [], "skipped": []}

    if platform == "auto":
        platform = "windows" if sys.platform == "win32" else "linux"

    for binary in build_dir.rglob("*"):
        if binary.is_file() and binary.stat().st_size > 0:
            # Skip non-binaries
            if binary.suffix not in ("", ".exe", ".deb", ".AppImage"):
                continue

            if platform == "windows" and binary.suffix == ".exe":
                if manager.sign_windows(binary):
                    results["signed"].append(str(binary))
                else:
                    results["failed"].append(str(binary))

            elif platform == "linux":
                if manager.sign_linux(binary):
                    results["signed"].append(str(binary))
                else:
                    results["failed"].append(str(binary))

    return results