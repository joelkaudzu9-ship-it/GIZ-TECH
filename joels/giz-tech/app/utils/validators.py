# app/utils/validators.py
import re
from flask import request


def validate_whatsapp_number(number):
    """Validate WhatsApp number format"""
    # Remove any non-digit characters
    clean_number = re.sub(r'\D', '', number)

    # Check if it's a valid number (basic check)
    if len(clean_number) >= 10 and len(clean_number) <= 15:
        return True, clean_number
    return False, "Invalid WhatsApp number format"


def sanitize_input(text, max_length=None):
    """Sanitize user input"""
    if not text:
        return text

    # Remove any HTML tags
    text = re.sub(r'<[^>]*>', '', text)

    # Trim whitespace
    text = text.strip()

    # Truncate if max_length specified
    if max_length and len(text) > max_length:
        text = text[:max_length]

    return text


def validate_image_size(file, max_size_mb=16):
    """Validate image file size"""
    if file:
        # Convert to bytes
        max_size_bytes = max_size_mb * 1024 * 1024
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset position

        if size > max_size_bytes:
            return False, f"File too large. Max size: {max_size_mb}MB"
    return True, "OK"


def is_safe_url(target):
    """Check if URL is safe for redirects"""
    if not target:
        return False

    # Ensure URL is relative and doesn't contain external domains
    if target.startswith(('http://', 'https://')):
        return False

    # Block URLs with protocol handlers
    if ':' in target and not target.startswith('/'):
        return False

    return True


def validate_email(email):
    """Enhanced email validation"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None