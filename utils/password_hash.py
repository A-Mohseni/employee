import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash using bcrypt"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
