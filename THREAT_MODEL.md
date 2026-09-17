# VaultX Threat Model

This document outlines the security assumptions, protections, and limitations of VaultX.

## What VaultX Protects Against
1. **Offline Brute-Force Attacks**: Master passwords are processed through Argon2id (memory-hard, 64MB memory cost, 3 iterations), making GPU/ASIC brute-force attacks computationally infeasible.
2. **Data Tampering**: All vault entries and the vault key itself are encrypted using AES-256-GCM, which provides authenticated encryption. Any modification to the `vault.json` file will cause decryption to fail safely.
3. **Casual Local Access**: The `vault.json` file is completely unreadable without the master password or a valid recovery code.
4. **Clipboard Snooping**: Copied passwords are automatically cleared from the system clipboard after 20 seconds (if unchanged).

## What VaultX Does NOT Protect Against
1. **Active Keyloggers / Screen Recorders**: If the host operating system is compromised by malware that records keystrokes or the screen, the master password or decrypted entries can be captured. VaultX cannot protect against a compromised host.
2. **Cold Boot / Memory Scraping Attacks**: Because VaultX is written in Python, decrypted keys and passwords reside in the system's RAM while the application is unlocked. Advanced attackers with physical access to the machine could potentially extract this data from memory.
3. **Cloud Sync Compromise**: If the user manually syncs `vault.json` to a cloud service (e.g., Dropbox, Google Drive) and their cloud account is compromised, the attacker still cannot read the data, but they could delete or corrupt the file. (Atomic saves mitigate corruption, but backups are the user's responsibility).

## Cryptographic Primitives Used
- **Key Derivation**: Argon2id (via `argon2-cffi`)
- **Symmetric Encryption**: AES-256-GCM (via `cryptography.hazmat`)
- **Randomness**: `os.urandom` and `secrets` module (CSPRNG)