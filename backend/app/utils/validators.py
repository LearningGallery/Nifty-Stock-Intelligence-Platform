"""
Validation Utilities
"""
import re
from typing import Optional


def validate_stock_symbol(symbol: str) -> bool:
    """
    Validate stock symbol format
    Must be 2-10 uppercase letters
    """
    if not symbol:
        return False
    
    pattern = r'^[A-Z]{2,10}$'
    return bool(re.match(pattern, symbol.upper()))


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_input(text: str) -> str:
    """
    Sanitize user input
    Remove potentially dangerous characters
    """
    # Remove null bytes
    text = text.replace('\x00', '')
    
    # Trim whitespace
    text = text.strip()
    
    return text


def validate_session_id(session_id: str) -> bool:
    """Validate session ID format (UUID)"""
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(uuid_pattern, session_id.lower()))
