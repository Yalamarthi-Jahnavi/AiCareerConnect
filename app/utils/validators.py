"""
Input Validators
==================
Validation helpers for request data sanitization.

WHY THIS FILE EXISTS:
    Centralizing validation logic prevents duplicated checks across
    routes and ensures consistent error messages. Also protects
    against malformed input before it hits the database.
"""

import re


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError('Invalid email format')
    return email.lower().strip()


def validate_password(password):
    """
    Validate password strength.
    Requirements: min 8 chars, at least 1 uppercase, 1 lowercase, 1 digit.
    """
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters long')
    if not re.search(r'[A-Z]', password):
        raise ValueError('Password must contain at least one uppercase letter')
    if not re.search(r'[a-z]', password):
        raise ValueError('Password must contain at least one lowercase letter')
    if not re.search(r'\d', password):
        raise ValueError('Password must contain at least one digit')
    return password


def validate_username(username):
    """Validate username: 3-80 chars, alphanumeric and underscores only."""
    if not username or len(username) < 3 or len(username) > 80:
        raise ValueError('Username must be between 3 and 80 characters')
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        raise ValueError('Username can only contain letters, numbers, and underscores')
    return username.strip()


def validate_required_fields(data, required_fields):
    """
    Check that all required fields are present in the request data.
    
    Args:
        data: Request JSON data dict
        required_fields: List of required field names
        
    Raises:
        ValueError with the name of the missing field
    """
    missing = [field for field in required_fields if field not in data or not data[field]]
    if missing:
        raise ValueError(f'Missing required fields: {", ".join(missing)}')
    return True
