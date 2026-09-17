import os
import base64
from argon2.low_level import hash_secret_raw, Type
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Argon2id parameters (OWASP recommended for password hashing)
ARGON2_TIME_COST = 3
ARGON2_MEMORY_COST = 65536  # 64 MB
ARGON2_PARALLELISM = 4
ARGON2_HASH_LEN = 32  # 256-bit key

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Turns a master password + salt into a 32-byte (256-bit) AES key
    using Argon2id. This is memory-hard and resists GPU/ASIC brute-force attacks.
    """
    return hash_secret_raw(
        secret=password.encode('utf-8'),
        salt=salt,
        time_cost=ARGON2_TIME_COST,
        memory_cost=ARGON2_MEMORY_COST,
        parallelism=ARGON2_PARALLELISM,
        hash_len=ARGON2_HASH_LEN,
        type=Type.ID
    )

def generate_vault_key() -> bytes:
    """Generate a random 32-byte vault key. This key encrypts all entries."""
    return os.urandom(32)

def wrap_key(wrapping_key: bytes, vault_key: bytes) -> dict:
    """
    Encrypt the vault key with a wrapping key. Returns a dict with nonce + ciphertext.
    """
    nonce = os.urandom(12)
    aesgcm = AESGCM(wrapping_key)
    ciphertext = aesgcm.encrypt(nonce, vault_key, None)
    return {
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }

def unwrap_key(wrapping_key: bytes, wrapped: dict) -> bytes:
    """
    Decrypt the vault key using the wrapping key.
    Raises an exception if the wrapping key is wrong or data is tampered.
    """
    nonce = base64.b64decode(wrapped["nonce"])
    ciphertext = base64.b64decode(wrapped["ciphertext"])
    aesgcm = AESGCM(wrapping_key)
    return aesgcm.decrypt(nonce, ciphertext, None)

def encrypt(key: bytes, plaintext: str) -> dict:
    """
    Encrypts a string using AES-256-GCM.
    Returns a dict with the nonce + ciphertext (both base64-encoded).
    """
    nonce = os.urandom(12)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return {
        "nonce": base64.b64encode(nonce).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode()
    }

def decrypt(key: bytes, encrypted: dict) -> str:
    """
    Reverses encrypt(). Raises an exception if the key is wrong or data is tampered.
    """
    nonce = base64.b64decode(encrypted["nonce"])
    ciphertext = base64.b64decode(encrypted["ciphertext"])
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode('utf-8')