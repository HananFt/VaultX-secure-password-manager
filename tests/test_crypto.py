import os
import pytest
from crypto import derive_key, generate_vault_key, wrap_key, unwrap_key, encrypt, decrypt

def test_derive_key_consistency():
    """Same password and salt should always produce the same key."""
    password = "SuperSecretPassword123!"
    salt = os.urandom(16)
    key1 = derive_key(password, salt)
    key2 = derive_key(password, salt)
    assert key1 == key2
    assert len(key1) == 32  # 256-bit key

def test_derive_key_uniqueness():
    """Different passwords or salts should produce different keys."""
    password = "SuperSecretPassword123!"
    salt1 = os.urandom(16)
    salt2 = os.urandom(16)
    assert derive_key(password, salt1) != derive_key(password, salt2)
    assert derive_key(password, salt1) != derive_key("WrongPassword!", salt1)

def test_vault_key_wrap_unwrap():
    """A wrapped vault key should successfully unwrap with the correct key."""
    master_key = os.urandom(32)
    vault_key = generate_vault_key()
    
    wrapped = wrap_key(master_key, vault_key)
    assert "nonce" in wrapped
    assert "ciphertext" in wrapped
    
    unwrapped = unwrap_key(master_key, wrapped)
    assert unwrapped == vault_key

def test_vault_key_unwrap_fails_with_wrong_key():
    """Unwrapping with the wrong key should raise an exception."""
    master_key = os.urandom(32)
    wrong_key = os.urandom(32)
    vault_key = generate_vault_key()
    
    wrapped = wrap_key(master_key, vault_key)
    with pytest.raises(Exception):
        unwrap_key(wrong_key, wrapped)

def test_encrypt_decrypt_roundtrip():
    """Encrypted data should decrypt back to the original plaintext."""
    key = generate_vault_key()
    plaintext = "MySuperSecretPassword!@#"
    
    encrypted = encrypt(key, plaintext)
    assert "nonce" in encrypted
    assert "ciphertext" in encrypted
    
    decrypted = decrypt(key, encrypted)
    assert decrypted == plaintext

def test_decrypt_fails_with_wrong_key():
    """Decrypting with the wrong key should raise an exception (tamper detection)."""
    key1 = generate_vault_key()
    key2 = generate_vault_key()
    plaintext = "MySuperSecretPassword!@#"
    
    encrypted = encrypt(key1, plaintext)
    with pytest.raises(Exception):
        decrypt(key2, encrypted)