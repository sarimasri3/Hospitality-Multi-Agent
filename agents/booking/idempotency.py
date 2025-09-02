"""
Idempotency handling for booking creation.
"""

import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime


def generate_natural_key(
    guest_id: str,
    property_id: str,
    check_in_date: str,
    check_out_date: str
) -> str:
    """
    Generate a deterministic natural key for booking idempotency.
    
    This ensures that the same booking request always generates the same key,
    preventing duplicate bookings even if the request is retried.
    
    Args:
        guest_id: Guest user ID
        property_id: Property ID
        check_in_date: Check-in date string
        check_out_date: Check-out date string
    
    Returns:
        SHA256 hash as the natural key
    """
    # Normalize dates to ensure consistency
    if isinstance(check_in_date, datetime):
        check_in_date = check_in_date.isoformat()
    if isinstance(check_out_date, datetime):
        check_out_date = check_out_date.isoformat()
    
    # Create deterministic key string
    key_components = [
        guest_id.strip().lower(),
        property_id.strip().lower(),
        check_in_date.strip(),
        check_out_date.strip()
    ]
    
    key_string = ":".join(key_components)
    
    # Generate SHA256 hash
    return hashlib.sha256(key_string.encode('utf-8')).hexdigest()


def generate_request_signature(request_data: Dict[str, Any]) -> str:
    """
    Generate a signature for the entire booking request.
    
    This can be used to detect if the exact same request is being retried.
    
    Args:
        request_data: Complete booking request data
    
    Returns:
        Request signature hash
    """
    # Sort keys for consistency
    sorted_data = json.dumps(request_data, sort_keys=True, default=str)
    return hashlib.sha256(sorted_data.encode('utf-8')).hexdigest()


class IdempotencyManager:
    """Manages idempotency for booking operations."""
    
    def __init__(self):
        # In production, this would use Redis or similar
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def check_idempotency(
        self,
        natural_key: str,
        request_signature: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Check if a booking with this key already exists.
        
        Args:
            natural_key: Natural key for the booking
            request_signature: Optional request signature
        
        Returns:
            Existing booking data if found, None otherwise
        """
        if natural_key in self._cache:
            cached = self._cache[natural_key]
            
            # If signatures match, it's an exact retry
            if request_signature and cached.get('signature') == request_signature:
                cached['is_retry'] = True
            
            return cached
        
        return None
    
    def store_idempotency(
        self,
        natural_key: str,
        booking_data: Dict[str, Any],
        request_signature: Optional[str] = None
    ) -> None:
        """
        Store booking data for idempotency.
        
        Args:
            natural_key: Natural key for the booking
            booking_data: Booking data to store
            request_signature: Optional request signature
        """
        self._cache[natural_key] = {
            **booking_data,
            'signature': request_signature,
            'stored_at': datetime.now().isoformat()
        }
    
    def validate_booking_window(
        self,
        check_in_date: datetime,
        check_out_date: datetime
    ) -> Dict[str, Any]:
        """
        Validate that booking dates are within acceptable windows.
        
        Args:
            check_in_date: Proposed check-in date
            check_out_date: Proposed check-out date
        
        Returns:
            Validation result
        """
        now = datetime.now()
        
        # Check if booking is in the past
        if check_in_date < now:
            return {
                "valid": False,
                "error": "PAST_BOOKING",
                "message": "Cannot create bookings for past dates"
            }
        
        # Check if booking is too far in advance (365 days)
        max_advance = now.replace(hour=0, minute=0, second=0, microsecond=0)
        max_advance = max_advance.replace(year=max_advance.year + 1)
        
        if check_in_date > max_advance:
            return {
                "valid": False,
                "error": "TOO_FAR_ADVANCE",
                "message": "Bookings can only be made up to 365 days in advance"
            }
        
        # Check minimum stay (1 night)
        nights = (check_out_date - check_in_date).days
        if nights < 1:
            return {
                "valid": False,
                "error": "MIN_STAY",
                "message": "Minimum stay is 1 night"
            }
        
        # Check maximum stay (30 nights)
        if nights > 30:
            return {
                "valid": False,
                "error": "MAX_STAY",
                "message": "Maximum stay is 30 nights"
            }
        
        return {
            "valid": True,
            "nights": nights,
            "message": f"Valid {nights}-night stay"
        }