# auth/utils/validators.py
import re
from typing import Tuple

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> Tuple[bool, str]:
    """Validate phone number format."""
    # Remove all non-digits except +
    phone = ''.join(c for c in phone if c.isdigit() or c == '+')
    
    # Check Madagascar format
    if phone.startswith('+261'):
        pattern = r'^\+261[3238]\d{8}$'
    # Check China format
    elif phone.startswith('+86'):
        pattern = r'^\+86\d{11}$'
    else:
        return False, "Unsupported country code"
    
    return bool(re.match(pattern, phone)), phone

def validate_password(password: str) -> Tuple[bool, str]:
    """Validate password strength."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"