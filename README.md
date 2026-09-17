# VaultX — Secure Password Manager

VaultX is a local password manager written in Python. It started as a CLI password manager and now provides both a desktop GUI and CLI using the same encrypted vault format.

## Features

- AES-256-GCM authenticated encryption
- PBKDF2-HMAC-SHA256 key derivation
- Random 256-bit vault key
- Vault key wrapped by the master-password-derived key
- Recovery-code based vault-key recovery
- Password generator and strength feedback
- Clipboard integration with automatic clearing (20s, only if you haven't copied something else since)
- Configurable auto-lock
- GUI and CLI interfaces
- Windows executable build with PyInstaller

## Security model

```text
Master password
      │
      ▼
PBKDF2-HMAC-SHA256 + random salt
      │
      ▼
256-bit master key
      │
      ▼
AES-256-GCM key wrapping
      │
      ▼
256-bit vault key
      │
      ▼
AES-256-GCM encryption of entries
      │
      ▼
vault.json
```

The master password is not stored. The vault contains the salt and an authenticated, encrypted copy of the vault key. Password entries are encrypted with the vault key.

## Run from source

### Requirements

- Python 3.12+
- Windows, macOS, or Linux for the Python application
- Python packages listed in `requirements.txt`

### Install

```bash
git clone https://github.com/HananFt/VaultX-secure-password-manager.git
cd VaultX-secure-password-manager

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate    # macOS/Linux

pip install -r requirements.txt
```

### Start

GUI:

```bash
python app.py
```

CLI:

```bash
python manager.py
```

On first use, VaultX creates `vault.json` locally. That file is intentionally ignored by Git because it contains your encrypted vault and recovery data.

## Build the Windows executable

The repository keeps the **source and build configuration** in Git, not generated build output.

On Windows:

```text
build_exe.bat
```

The script creates/uses `venv`, installs the build dependencies, and produces:

```text
dist/VaultX.exe
```

The executable is a PyInstaller one-file application and can be launched by double-clicking it.

## GitHub distribution

`VaultX.exe` should normally **not be committed to the Git repository**. GitHub Releases are the cleaner place for compiled binaries.

The included GitHub Actions workflow:

- builds the Windows executable on manual workflow runs
- builds automatically when a tag such as `v1.0.0` is pushed
- attaches the executable to the GitHub Release for version tags

## Project structure

```text
VaultX-secure-password-manager/
├── app.py
├── manager.py
├── crypto.py
├── vault.py
├── launcher.py
├── vault.ico
├── VaultX.spec
├── requirements.txt
├── requirements-build.txt
├── build_exe.bat
├── .gitignore
├── .github/
│   └── workflows/
│       └── build-windows.yml
└── README.md
```

Generated/local files are intentionally excluded:

```text
venv/
build/
dist/
vault.json
__pycache__/
```

## Important security notes

- `vault.json` is encrypted, but it is still sensitive. Do not publish it.
- The master password is not recoverable by design; recovery codes are the recovery mechanism implemented by VaultX.
- The executable is a convenience distribution of the Python application, not a different security layer.
- The cryptographic design should be independently reviewed before treating VaultX as production-grade password-management software.
- Writes to `vault.json` are atomic (written to a temp file, then renamed over the original), so an app crash or power loss mid-save can't leave you with a corrupted vault.

## License

MIT

## Author

**HananFt**
