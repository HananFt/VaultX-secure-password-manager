import os
import base64
import getpass
from crypto import derive_key, generate_vault_key, wrap_key, unwrap_key, encrypt, decrypt
from vault import vault_exists, load_vault, save_vault, init_vault
from hibp import check_password_breach  # NEW IMPORT

def unlock() -> tuple[bytes, dict]:
    """Either initializes a new vault or unlocks an existing one."""
    if not vault_exists():
        print("\n🔒 No vault found. Creating a new one.\n")
        master = getpass.getpass("Set your master password: ")
        confirm = getpass.getpass("Confirm master password: ")
        if master != confirm:
            print("❌ Passwords don't match. Exiting.")
            exit()
        
        salt = os.urandom(16)
        salt_b64 = base64.b64encode(salt).decode()
        master_key = derive_key(master, salt)
        vault_key = generate_vault_key()
        wrapped = wrap_key(master_key, vault_key)
        init_vault(salt_b64, wrapped)
        print("\n✅ Vault created successfully with Argon2id encryption!\n")
        return vault_key, load_vault()
    else:
        master = getpass.getpass("Master password: ")
        vault = load_vault()
        salt = base64.b64decode(vault["salt"])
        master_key = derive_key(master, salt)
        try:
            vault_key = unwrap_key(master_key, vault["vault_key"])
        except Exception:
            print("❌ Wrong password.")
            exit()
        return vault_key, vault

def add_entry(key: bytes, vault: dict):
    service = input("Service name (ex: gmail, github): ").strip()
    username = input("Username/email: ").strip()
    password = getpass.getpass("Password: ")
    
    # NEW: HIBP Breach Check
    print("\n🔍 Checking password against known data breaches...")
    breach_count = check_password_breach(password)
    if breach_count == -1:
        print("⚠️  Could not verify breach status (network error). Proceeding anyway.")
    elif breach_count > 0:
        print(f"🚨 WARNING: This password has been found in {breach_count} known data breaches!")
        print("   It is highly recommended to use a different, unique password.")
        confirm = input("   Do you still want to save this password? (y/N): ").strip().lower()
        if confirm != 'y':
            print("❌ Entry cancelled.")
            return
    else:
        print("✅ Password looks safe (not found in known breaches).\n")

    vault["entries"][service] = {
        "username": username,
        "password": encrypt(key, password)
    }
    save_vault(vault)
    print(f"✅ Entry for '{service}' saved securely.\n")

def get_entry(key: bytes, vault: dict):
    service = input("Service name to retrieve: ").strip()
    if service not in vault["entries"]:
        print(f"\n❌ No entry found for '{service}'.\n")
        return
    entry = vault["entries"][service]
    try:
        password = decrypt(key, entry["password"])
        print(f"\n Service  : {service}")
        print(f" Username : {entry['username']}")
        print(f" Password : {password}\n")
    except Exception:
        print("\n❌ Decryption failed. Corrupted data or wrong key.\n")