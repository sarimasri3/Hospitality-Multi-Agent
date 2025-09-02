"""
Tools for the Inquiry Agent.
"""

from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import re


async def validate_city(city: str) -> Dict[str, Any]:
    """
    Validate if the city is a supported destination.
    
    Args:
        city: City name to validate
    
    Returns:
        Validation result with normalized city name
    """
    # List of supported cities (in production, this would query a database)
    supported_cities = [
        "Miami", "Los Angeles", "New York", "San Francisco", "Chicago",
        "Austin", "Seattle", "Boston", "Denver", "Portland",
        "Las Vegas", "Orlando", "San Diego", "Phoenix", "Nashville",
        "Paris", "London", "Rome", "Barcelona", "Amsterdam",
        "Tokyo", "Sydney", "Dubai", "Singapore", "Bangkok"
    ]
    
    # Normalize city name
    normalized_city = city.strip().title()
    
    # Check if city is supported
    if normalized_city in supported_cities:
        return {
            "valid": True,
            "normalized_city": normalized_city,
            "message": f"Great choice! {normalized_city} is a wonderful destination."
        }
    
    # Try fuzzy matching for common misspellings
    for supported in supported_cities:
        if supported.lower() in city.lower() or city.lower() in supported.lower():
            return {
                "valid": True,
                "normalized_city": supported,
                "message": f"I found {supported} as a match. Is that correct?"
            }
    
    return {
        "valid": False,
        "message": f"I couldn't find {city} in our destinations. Could you try another city?"
    }


async def validate_dates(
    check_in_date: str,
    check_out_date: str
) -> Dict[str, Any]:
    """
    Validate check-in and check-out dates.
    
    Args:
        check_in_date: Check-in date string (YYYY-MM-DD)
        check_out_date: Check-out date string (YYYY-MM-DD)
    
    Returns:
        Validation result with parsed dates
    """
    try:
        # Parse dates
        check_in = datetime.strptime(check_in_date, "%Y-%m-%d")
        check_out = datetime.strptime(check_out_date, "%Y-%m-%d")
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check if dates are in the past
        if check_in < today:
            return {
                "valid": False,
                "message": "Check-in date cannot be in the past. Please select a future date."
            }
        
        # Check if check-out is after check-in
        if check_out <= check_in:
            return {
                "valid": False,
                "message": "Check-out date must be after check-in date."
            }
        
        # Check if booking is too far in advance (365 days)
        max_advance = today + timedelta(days=365)
        if check_in > max_advance:
            return {
                "valid": False,
                "message": "Bookings can only be made up to 365 days in advance."
            }
        
        # Calculate number of nights
        nights = (check_out - check_in).days
        
        # Check minimum and maximum stay
        if nights < 1:
            return {
                "valid": False,
                "message": "Minimum stay is 1 night."
            }
        
        if nights > 30:
            return {
                "valid": False,
                "message": "Maximum stay is 30 nights. For longer stays, please contact support."
            }
        
        return {
            "valid": True,
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "nights": nights,
            "message": f"Perfect! That's a {nights}-night stay."
        }
        
    except ValueError as e:
        return {
            "valid": False,
            "message": "Invalid date format. Please use YYYY-MM-DD format (e.g., 2025-03-15)."
        }


async def validate_guests(number_of_guests: int) -> Dict[str, Any]:
    """
    Validate number of guests.
    
    Args:
        number_of_guests: Number of guests
    
    Returns:
        Validation result
    """
    if number_of_guests < 1:
        return {
            "valid": False,
            "message": "At least 1 guest is required."
        }
    
    if number_of_guests > 10:
        return {
            "valid": False,
            "message": "Our villas accommodate up to 10 guests. For larger groups, consider booking multiple properties."
        }
    
    return {
        "valid": True,
        "number_of_guests": number_of_guests,
        "message": f"Great! I'll search for properties that can accommodate {number_of_guests} guest{'s' if number_of_guests > 1 else ''}."
    }


async def validate_budget(budget_string: str) -> Dict[str, Any]:
    """
    Parse and validate budget from user input.
    
    Args:
        budget_string: Budget string from user (e.g., "$500", "500", "300-500")
    
    Returns:
        Validation result with parsed budget
    """
    # Remove currency symbols and spaces
    cleaned = re.sub(r'[^0-9\-.]', '', budget_string)
    
    # Check for range (e.g., "300-500")
    if '-' in cleaned:
        parts = cleaned.split('-')
        if len(parts) == 2:
            try:
                min_budget = float(parts[0])
                max_budget = float(parts[1])
                
                if min_budget <= 0 or max_budget <= 0:
                    return {
                        "valid": False,
                        "message": "Budget must be a positive amount."
                    }
                
                if min_budget > max_budget:
                    min_budget, max_budget = max_budget, min_budget
                
                return {
                    "valid": True,
                    "min_budget": min_budget,
                    "max_budget": max_budget,
                    "message": f"I'll search for properties between ${min_budget:.0f} and ${max_budget:.0f} per night."
                }
            except ValueError:
                pass
    
    # Try single value
    try:
        budget = float(cleaned)
        
        if budget <= 0:
            return {
                "valid": False,
                "message": "Budget must be a positive amount."
            }
        
        # Assume this is max budget
        return {
            "valid": True,
            "min_budget": 0,
            "max_budget": budget,
            "message": f"I'll search for properties up to ${budget:.0f} per night."
        }
        
    except ValueError:
        return {
            "valid": False,
            "message": "I couldn't understand that budget. Could you provide a number (e.g., 500 or 300-500)?"
        }


async def extract_slots_from_message(message: str) -> Dict[str, Any]:
    """
    Extract booking slots from a user message using NLP patterns.
    
    Args:
        message: User message
    
    Returns:
        Dictionary of extracted slots
    """
    slots = {}
    
    # Extract dates (look for YYYY-MM-DD pattern)
    date_pattern = r'\b(\d{4}-\d{2}-\d{2})\b'
    dates = re.findall(date_pattern, message)
    if len(dates) >= 2:
        slots['check_in_date'] = dates[0]
        slots['check_out_date'] = dates[1]
    elif len(dates) == 1:
        slots['check_in_date'] = dates[0]
    
    # Extract number of guests (look for patterns like "2 people", "3 guests", etc.)
    guest_patterns = [
        r'(\d+)\s*(?:people|guests|persons|adults)',
        r'(?:for|party of)\s*(\d+)',
        r'(\d+)\s*of us'
    ]
    for pattern in guest_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            slots['number_of_guests'] = int(match.group(1))
            break
    
    # Extract budget (look for dollar amounts)
    budget_pattern = r'\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'
    budget_match = re.search(budget_pattern, message)
    if budget_match:
        slots['budget'] = budget_match.group(0)
    
    # Extract city (look for known cities or "in [city]" pattern)
    city_pattern = r'(?:in|to|at|near)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
    city_match = re.search(city_pattern, message)
    if city_match:
        slots['city'] = city_match.group(1)
    
    return slots


async def compile_session_slots(
    existing_slots: Dict[str, Any],
    new_slots: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge new slots with existing session slots.
    
    Args:
        existing_slots: Current session slots
        new_slots: Newly extracted slots
    
    Returns:
        Merged slots dictionary
    """
    # Start with existing slots
    merged = existing_slots.copy()
    
    # Update with new slots (new values override old ones)
    for key, value in new_slots.items():
        if value is not None and value != "":
            merged[key] = value
    
    # Check completeness
    required_slots = ['city', 'check_in_date', 'check_out_date', 'number_of_guests']
    missing_slots = [slot for slot in required_slots if slot not in merged or merged[slot] is None]
    
    merged['_complete'] = len(missing_slots) == 0
    merged['_missing'] = missing_slots
    
    return merged