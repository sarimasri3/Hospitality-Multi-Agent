"""
Input validation utilities.
"""

import re
from typing import Any, Dict, Optional
from datetime import datetime, timedelta


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
    
    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
    
    Returns:
        True if valid phone format
    """
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    # Check if it's a valid length (10-15 digits)
    return 10 <= len(digits) <= 15


def validate_date_string(date_string: str) -> Optional[datetime]:
    """
    Validate and parse date string.
    
    Args:
        date_string: Date string in YYYY-MM-DD format
    
    Returns:
        Parsed datetime or None if invalid
    """
    try:
        return datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        return None


def validate_booking_dates(
    check_in: str,
    check_out: str
) -> Dict[str, Any]:
    """
    Validate booking dates.
    
    Args:
        check_in: Check-in date string
        check_out: Check-out date string
    
    Returns:
        Validation result dictionary
    """
    check_in_date = validate_date_string(check_in)
    check_out_date = validate_date_string(check_out)
    
    if not check_in_date or not check_out_date:
        return {
            "valid": False,
            "error": "Invalid date format. Use YYYY-MM-DD"
        }
    
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    if check_in_date < today:
        return {
            "valid": False,
            "error": "Check-in date cannot be in the past"
        }
    
    if check_out_date <= check_in_date:
        return {
            "valid": False,
            "error": "Check-out must be after check-in"
        }
    
    nights = (check_out_date - check_in_date).days
    
    if nights < 1:
        return {
            "valid": False,
            "error": "Minimum stay is 1 night"
        }
    
    if nights > 30:
        return {
            "valid": False,
            "error": "Maximum stay is 30 nights"
        }
    
    return {
        "valid": True,
        "check_in": check_in_date,
        "check_out": check_out_date,
        "nights": nights
    }


def validate_guest_count(count: int) -> Dict[str, Any]:
    """
    Validate number of guests.
    
    Args:
        count: Number of guests
    
    Returns:
        Validation result
    """
    if count < 1:
        return {
            "valid": False,
            "error": "At least 1 guest required"
        }
    
    if count > 10:
        return {
            "valid": False,
            "error": "Maximum 10 guests per booking"
        }
    
    return {
        "valid": True,
        "count": count
    }


def validate_price(price: float) -> Dict[str, Any]:
    """
    Validate price value.
    
    Args:
        price: Price to validate
    
    Returns:
        Validation result
    """
    if price < 0:
        return {
            "valid": False,
            "error": "Price cannot be negative"
        }
    
    if price > 10000:
        return {
            "valid": False,
            "error": "Price exceeds maximum allowed"
        }
    
    return {
        "valid": True,
        "price": round(price, 2)
    }


def sanitize_input(text: str) -> str:
    """
    Sanitize user input text.
    
    Args:
        text: Input text to sanitize
    
    Returns:
        Sanitized text
    """
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove potentially harmful characters
    text = re.sub(r'[<>&\"\'`]', '', text)
    
    return text