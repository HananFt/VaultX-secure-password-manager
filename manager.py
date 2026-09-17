import os
import base64
import secrets
import re
from crypto import derive_key, generate_vault_key, wrap_key, unwrap_key, encrypt, decrypt
from vault import vault_exists, load_vault, save_vault, init_vault

def generate_recovery_codes(count=6, length=8):
    """Generate a list of random recovery codes for the user to save."""
    return [secrets.token_hex(length // 2).upper() for _ in range(count)]

def create_vault(master_password: str):
    """Creates a new vault. Returns (vault_key, vault_data, recovery_codes)."""
    if vault_exists():
        raise ValueError("Vault already exists.")
    
    salt = os.urandom(16)
    salt_b64 = base64.b64encode(salt).decode()
    master_key = derive_key(master_password, salt)
    vault_key = generate_vault_key()
    wrapped = wrap_key(master_key, vault_key)
    
    recovery_codes = generate_recovery_codes()
    init_vault(salt_b64, wrapped)
    
    return vault_key, load_vault(), recovery_codes

def unlock_vault(master_password: str):
    """Unlocks an existing vault. Returns (vault_key, vault_data)."""
    if not vault_exists():
        raise ValueError("Vault does not exist.")
        
    vault = load_vault()
    salt = base64.b64decode(vault["salt"])
    master_key = derive_key(master_password, salt)
    
    try:
        vault_key = unwrap_key(master_key, vault["vault_key"])
        return vault_key, vault
    except Exception:
        raise ValueError("Invalid master password.")

def add_entry(vault_key, vault_data, service, username, password):
    """Adds a new entry and saves the vault."""
    if not service:
        raise ValueError("Service name cannot be empty.")
        
    vault_data["entries"][service] = {
        "username": username,
        "password": encrypt(vault_key, password)
    }
    save_vault(vault_data)

def get_entries(vault_key, vault_data):
    """Returns a list of decrypted entries with metadata."""
    entries = []
    for service, data in vault_data.get("entries", {}).items():
        try:
            pwd = decrypt(vault_key, data["password"])
            entries.append({
                "service": service,
                "username": data.get("username", ""),
                "password": pwd,
                "strength": calculate_password_strength(pwd)
            })
        except Exception:
            entries.append({
                "service": service,
                "username": data.get("username", ""),
                "password": "[Decryption Failed]",
                "strength": 0
            })
    return entries

def calculate_password_strength(password: str) -> int:
    """Returns a score from 0 to 4 based on length and complexity."""
    score = 0
    if len(password) >= 8: score += 1
    if len(password) >= 12: score += 1
    if re.search(r"[A-Z]", password) and re.search(r"[a-z]", password): score += 1
    if re.search(r"\d", password): score += 1
    if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password): score += 1
    return min(score, 4)

def get_security_health(vault_key, vault_data):
    """Calculates the overall security health of the vault."""
    entries = get_entries(vault_key, vault_data)
    total = len(entries)
    weak = sum(1 for e in entries if e["strength"] < 2)
    
    # Check for reused passwords
    passwords = [e["password"] for e in entries if e["password"] != "[Decryption Failed]"]
    reused = total - len(set(passwords))
    
    # Calculate a simple 0-100 score
    score = max(0, 100 - (weak * 10) - (reused * 15))
    
    return {
        "total": total,
        "weak": weak,
        "reused": reused,
        "score": score
    }