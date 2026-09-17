import json
import os
import tempfile
from datetime import datetime

VAULT_FILE = "vault.json"


def vault_exists() -> bool:
    return os.path.exists(VAULT_FILE)


def load_vault() -> dict:
    with open(VAULT_FILE, "r") as f:
        return json.load(f)


def save_vault(data: dict):
    """
    Write the vault atomically.

    Writing straight to vault.json risks leaving a half-written, corrupted
    file if the app crashes or loses power mid-write. Instead we write to a
    temp file in the same directory and then atomically rename it over the
    real file, so vault.json is always either the old version or the new
    version, never something in between.
    """
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
    """
    Create a brand new empty vault.
    - salt: used for PBKDF2 to derive the master key from the master password
    - wrapped_vault_key: the vault key encrypted under the master key
      The vault key is what actually encrypts entries, so changing the master
      password only requires re-wrapping this key, not re-encrypting all entries.
    """
    data = {
        "salt": salt_b64,
        "vault_key": wrapped_vault_key,
        "entries": {},
        "recovery_codes": [],
        "created_at": datetime.now().isoformat(),
    }
    save_vault(data)
    return data
