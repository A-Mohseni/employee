import secrets
import string

def generate_otp(length: int = 6) -> str:
    """Generate a random OTP of specified length"""
    digits = string.digits
    return ''.join(secrets.choice(digits) for _ in range(length))

def verify_otp(input_otp: str, stored_otp: str) -> bool:
    """Verify OTP input against stored OTP"""
    return input_otp == stored_otp
