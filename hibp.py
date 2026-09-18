import hashlib
import requests

def check_password_breach(password: str) -> int:
    """
    Checks if a password has been exposed in known data breaches
    using the Have I Been Pwned (HIBP) k-Anonymity API.
    
    Returns:
        int: Number of times the password was found in breaches.
             0 means safe. -1 means the network check failed (fail securely).
    """
    
    # 1. Hash the password with SHA-1 (Required by HIBP k-Anonymity API)
    sha1_hash = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()  # nosec B324
    
    # 2. Split into prefix (5 chars) and suffix (remaining 35 chars)
    prefix = sha1_hash[:5]
    suffix = sha1_hash[5:]
    
    # 3. Query the API with ONLY the prefix
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        # 4. Check if our suffix is in the response
        for line in response.text.splitlines():
            hash_suffix, count = line.split(':')
            if hash_suffix == suffix:
                return int(count)
                
        return 0  # Not found in breaches
    except requests.RequestException:
        # Fail securely: if network fails, return -1 to indicate unknown status
        return -1