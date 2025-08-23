import hashlib
import secrets

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    hashed = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    try:
        salt, hash_value = hashed_password.split('$')
        return hashlib.sha256((password + salt).encode()).hexdigest() == hash_value
    except:
        return False
