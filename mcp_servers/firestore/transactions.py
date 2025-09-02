"""
Transaction handlers for critical operations.
"""

import hashlib
from datetime import datetime
from typing import Dict, Optional, List
from firebase_admin import firestore


def generate_natural_key(
    guest_id: str,
    property_id: str,
    check_in_date: str,
    check_out_date: str
) -> str:
    """
    Generate a natural key for booking idempotency.
    
    Args:
        guest_id: Guest user ID
        property_id: Property ID
        check_in_date: Check-in date string
        check_out_date: Check-out date string
    
    Returns:
        SHA256 hash of the combined parameters
    """
    key_string = f"{guest_id}:{property_id}:{check_in_date}:{check_out_date}"
    return hashlib.sha256(key_string.encode()).hexdigest()


def check_booking_overlap(
    db,
    property_id: str,
    check_in_date: datetime,
    check_out_date: datetime,
    exclude_booking_id: Optional[str] = None
) -> bool:
    """
    Check if there are any overlapping bookings for a property.
    
    Args:
        db: Firestore database client
        property_id: Property to check
        check_in_date: Proposed check-in date
        check_out_date: Proposed check-out date
        exclude_booking_id: Booking ID to exclude from check (for updates)
    
    Returns:
        True if there's an overlap, False otherwise
    """
    bookings_ref = db.collection('bookings')
    
    # Query for bookings of the same property with active status
    query = bookings_ref.where('property_id', '==', property_id).where(
        'status', 'in', ['pending', 'confirmed']
    )
    
    for booking in query.stream():
        if exclude_booking_id and booking.id == exclude_booking_id:
            continue
            
        booking_data = booking.to_dict()
        existing_check_in = booking_data['check_in_date']
        existing_check_out = booking_data['check_out_date']
        
        # Check for overlap: new booking overlaps if:
        # - It starts before existing ends AND
        # - It ends after existing starts
        if (check_in_date < existing_check_out and 
            check_out_date > existing_check_in):
            return True
    
    return False


@firestore.transactional
def create_booking_transaction(
    transaction,
    db,
    booking_data: Dict
) -> Dict:
    """
    Create a booking within a transaction to ensure consistency.
    
    Args:
        transaction: Firestore transaction object
        db: Firestore database client
        booking_data: Booking data dictionary
    
    Returns:
        Result dictionary with success status and message
    """
    # Generate natural key for idempotency
    natural_key = generate_natural_key(
        booking_data['guest_id'],
        booking_data['property_id'],
        booking_data['check_in_date'].isoformat(),
        booking_data['check_out_date'].isoformat()
    )
    
    # Check for existing booking with same natural key
    booking_ref = db.collection('bookings').document(natural_key)
    existing = booking_ref.get(transaction=transaction)
    
    if existing.exists:
        return {
            "success": True,
            "booking_id": natural_key,
            "message": "Booking already exists (idempotent)",
            "existing": True
        }
    
    # Check for overlapping bookings
    # Note: In a real transaction, we'd need to handle this differently
    # as Firestore transactions have limitations on queries
    bookings_ref = db.collection('bookings')
    overlap_query = bookings_ref.where(
        'property_id', '==', booking_data['property_id']
    ).where('status', 'in', ['pending', 'confirmed'])
    
    for booking in overlap_query.stream(transaction=transaction):
        existing_data = booking.to_dict()
        if (booking_data['check_in_date'] < existing_data['check_out_date'] and 
            booking_data['check_out_date'] > existing_data['check_in_date']):
            return {
                "success": False,
                "message": "Property not available for selected dates",
                "conflict_booking": booking.id
            }
    
    # Create the booking
    booking_data['booking_id'] = natural_key
    booking_data['created_at'] = firestore.SERVER_TIMESTAMP
    booking_data['updated_at'] = firestore.SERVER_TIMESTAMP
    
    transaction.set(booking_ref, booking_data)
    
    # Update property availability calendar (optional optimization)
    # This creates a denormalized calendar for O(1) availability checks
    calendar_ref = db.collection('availability_calendar').document(
        f"{booking_data['property_id']}_{booking_data['check_in_date'].strftime('%Y-%m')}"
    )
    
    # Add booked dates to calendar
    booked_dates = []
    current_date = booking_data['check_in_date']
    while current_date < booking_data['check_out_date']:
        booked_dates.append(current_date.strftime('%Y-%m-%d'))
        current_date = current_date.replace(day=current_date.day + 1)
    
    transaction.set(
        calendar_ref,
        {'booked_dates': firestore.ArrayUnion(booked_dates)},
        merge=True
    )
    
    return {
        "success": True,
        "booking_id": natural_key,
        "message": "Booking created successfully",
        "existing": False
    }


def update_booking_status(
    db,
    booking_id: str,
    new_status: str,
    reason: Optional[str] = None
) -> Dict:
    """
    Update booking status with audit trail.
    
    Args:
        db: Firestore database client
        booking_id: Booking to update
        new_status: New status value
        reason: Optional reason for status change
    
    Returns:
        Result dictionary
    """
    booking_ref = db.collection('bookings').document(booking_id)
    booking = booking_ref.get()
    
    if not booking.exists:
        return {
            "success": False,
            "message": "Booking not found"
        }
    
    update_data = {
        'status': new_status,
        'updated_at': firestore.SERVER_TIMESTAMP
    }
    
    if reason:
        update_data['status_change_reason'] = reason
    
    booking_ref.update(update_data)
    
    # Create audit log entry
    audit_ref = db.collection('booking_audit').document()
    audit_ref.set({
        'booking_id': booking_id,
        'old_status': booking.to_dict()['status'],
        'new_status': new_status,
        'reason': reason,
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    
    return {
        "success": True,
        "message": f"Booking status updated to {new_status}"
    }