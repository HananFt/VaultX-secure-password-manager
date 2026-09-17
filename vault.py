import os
import json
import tempfile
from datetime import datetime

VAULT_FILE = "vault.json"

def vault_exists() -> bool:
    return os.path.exists(VAULT_FILE)

def load_vault() -> dict:
    with open(VAULT_FILE, "r") as f:
        return json.load(f)

def save_vault(data: dict):
    """Write the vault atomically to prevent corruption on crash."""
    directory = os.path.dirname(os.path.abspath(VAULT_FILE)) or "."
    fd, tmp_path = tempfile.mkstemp(prefix=".vault_", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_path, VAULT_FILE)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise

def init_vault(salt_b64: str, wrapped_vault_key: dict) -> dict:
    """Create a brand new empty vault."""
    data = {
        "kdf": "argon2id",  # NEW: Explicitly state the key derivation function
        "salt": salt_b64,
        "vault_key": wrapped_vault_key,
        "entries": {},
        "recovery_codes": [],
        "created_at": datetime.now().isoformat(),
    }
    save_vault(data)
    return data