# ADR-004: Code Signing, Segurança e Confiança de Binários

## Status
**Aprovado** — 2026-07-04

## Contexto
A entrega de binários executáveis da NAP precisa ser confiável e não pode ser barrada por antivírus (Windows Defender, SmartScreen) ou sistemas de integridade. É necessário implementar:

1. **Code Signing** — Assinatura digital para Windows (Authenticode) e Linux (GPG)
2. **Anti-Heurística** — Evitar falsos-positivos de antivírus
3. **Integridade** — Verificação de checksums e assinaturas
4. **Bootloader Customizado** — Recompilação do PyInstaller para evitar detecção

## Decisão

### Arquitetura de Segurança

```
┌─────────────────────────────────────────────────────────────┐
│                    NAP Security Module                       │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │ CodeSigningMgr   │  │ SecurePackager   │                 │
│  │                  │  │                  │                 │
│  │ • Windows:       │  │ • Bootloader     │                 │
│  │   Authenticode   │  │   Customization  │                 │
│  │ • Linux: GPG     │  │ • AV Trigger     │                 │
│  │ • macOS: (futuro)│  │   Scanner        │                 │
│  │ • Manifest JSON  │  │ • Windows        │                 │
│  └──────────────────┘  │   Manifest       │                 │
│                        └──────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### Code Signing

| Plataforma | Método | Ferramenta | Certificado |
|-----------|--------|-----------|-------------|
| **Windows** | Authenticode (SHA256) | `signtool.exe` | EV Code Signing (DigiCert/Sectigo) |
| **Linux** | GPG + dpkg-sig | `gpg`, `dpkg-sig` | Chave GPG pessoal/organizacional |
| **Dev/Teste** | Auto-assinado | OpenSSL | `nap-dev.pfx` (gerado localmente) |

### Anti-Heurística (Evitar Falsos-Positivos)

1. **Scanner de Triggers** — Varre código por padrões que acionam antivírus
2. **Bootloader Customizado** — Recompilar PyInstaller com metadados da NAP
3. **Windows Manifest** — Adicionar metadados de editor confiável
4. **Ofuscação Mínima** — Apenas strings sensíveis, sem ofuscação agressiva

### Fluxo de Build Seguro

```
Código Fonte → PyInstaller → Binário → 
  ├── Windows: signtool sign + timestamp → .exe assinado
  ├── Linux:   gpg --detach-sign + dpkg-sig → .deb assinado
  └── Manifest: sha256 + metadados → manifest.json
```

## Consequências
- **Positivas:** Binários reconhecidos como confiáveis pelo SO
- **Positivas:** Redução de falsos-positivos em antivírus
- **Positivas:** Audit trail completo de assinaturas
- **Negativas:** Custo de EV Code Signing Certificate (~$200-500/ano)
- **Negativas:** Complexidade adicional no pipeline de build
- **Riscos:** Certificado auto-assinado não é confiável em produção

## Como Usar

```bash
# Gerar certificado de desenvolvimento
python -c "from cli.security import CodeSigningManager; CodeSigningManager().generate_self_signed_cert()"

# Assinar build completo
python -c "from cli.security import sign_build; print(sign_build('dist'))"

# Verificar integridade
python -c "from cli.security import CodeSigningManager; print(CodeSigningManager().verify_integrity('dist/nap'))"

# Escanear por triggers de antivírus
python -c "from cli.security import SecurePackager; print(SecurePackager().scan_for_triggers('cli'))"