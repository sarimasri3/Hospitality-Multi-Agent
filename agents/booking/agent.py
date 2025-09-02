"""
Booking Agent for transactional booking creation.
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from typing import Dict, Optional, List, Any
from datetime import datetime

from .prompts import (
    BOOKING_SYSTEM_PROMPT,
    BOOKING_INSTRUCTION,
    BOOKING_CONFIRMATION_TEMPLATE,
    BOOKING_ERROR_MESSAGES,
    IDEMPOTENT_RESPONSE_TEMPLATE
)
from .idempotency import (
    generate_natural_key,
    generate_request_signature,
    IdempotencyManager
)


# Initialize idempotency manager (in production, this would use Redis)
idempotency_manager = IdempotencyManager()


async def process_booking(
    property_id: str,
    property_name: str,
    guest_id: str,
    host_id: str,
    check_in_date: str,
    check_out_date: str,
    number_of_guests: int,
    base_price: float,
    add_ons: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Process a booking with idempotency and transaction support.
    
    This tool will be connected to the Firestore MCP in the orchestrator.
    
    Args:
        property_id: Property to book
        property_name: Property name for confirmation
        guest_id: Guest user ID
        host_id: Host user ID
        check_in_date: Check-in date (YYYY-MM-DD)
        check_out_date: Check-out date (YYYY-MM-DD)
        number_of_guests: Number of guests
        base_price: Price per night
        add_ons: Optional add-on services
    
    Returns:
        Booking result with confirmation details
    """
    try:
        # Generate natural key for idempotency
        natural_key = generate_natural_key(
            guest_id, property_id, check_in_date, check_out_date
        )
        
        # Check for existing booking
        existing = idempotency_manager.check_idempotency(natural_key)
        if existing:
            return {
                "success": True,
                "idempotent": True,
                "booking_id": natural_key,
                "message": "Booking already exists",
                "existing_booking": existing
            }
        
        # Calculate pricing
        check_in = datetime.fromisoformat(check_in_date)
        check_out = datetime.fromisoformat(check_out_date)
        nights = (check_out - check_in).days
        
        accommodation = base_price * nights
        service_fee = accommodation * 0.1
        cleaning_fee = 50.0
        
        # Calculate add-on costs
        add_on_cost = 0
        if add_ons:
            add_on_prices = {
                "early_checkin": 50,
                "late_checkout": 50,
                "welcome_basket": 75,
                "spa_package": 200,
                "chef_service": 300
            }
            for addon in add_ons:
                add_on_cost += add_on_prices.get(addon, 0)
        
        pre_tax_total = accommodation + service_fee + cleaning_fee + add_on_cost
        tax = pre_tax_total * 0.08
        total_price = pre_tax_total + tax
        
        # Create booking data
        booking_data = {
            "booking_id": natural_key,
            "property_id": property_id,
            "property_name": property_name,
            "guest_id": guest_id,
            "host_id": host_id,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "number_of_guests": number_of_guests,
            "nights": nights,
            "base_price": base_price,
            "accommodation": accommodation,
            "service_fee": service_fee,
            "cleaning_fee": cleaning_fee,
            "add_ons": add_ons or [],
            "add_on_cost": add_on_cost,
            "tax": tax,
            "total_price": total_price,
            "status": "confirmed",
            "created_at": datetime.now().isoformat()
        }
        
        # Store for idempotency
        idempotency_manager.store_idempotency(natural_key, booking_data)
        
        # In production, this would call the Firestore MCP to create the booking
        # For now, return success
        return {
            "success": True,
            "idempotent": False,
            "booking_id": natural_key,
            "booking_data": booking_data,
            "message": "Booking created successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to create booking"
        }


async def validate_booking_capacity(
    property_capacity: int,
    requested_guests: int
) -> Dict[str, Any]:
    """
    Validate that the property can accommodate the requested number of guests.
    
    Args:
        property_capacity: Maximum guests the property can accommodate
        requested_guests: Number of guests in the booking request
    
    Returns:
        Validation result
    """
    if requested_guests > property_capacity:
        return {
            "valid": False,
            "message": BOOKING_ERROR_MESSAGES["capacity_exceeded"].format(
                capacity=property_capacity,
                requested=requested_guests
            )
        }
    
    return {
        "valid": True,
        "message": f"Property can accommodate {requested_guests} guests"
    }


async def simulate_payment_authorization(
    amount: float,
    currency: str = "USD",
    payment_method: str = "card"
) -> Dict[str, Any]:
    """
    Simulate payment authorization (in production, this would use a payment gateway).
    
    Args:
        amount: Amount to authorize
        currency: Currency code
        payment_method: Payment method type
    
    Returns:
        Authorization result
    """
    # Simulate 95% success rate
    import random
    success = random.random() < 0.95
    
    if success:
        return {
            "success": True,
            "authorization_id": f"auth_{natural_key[:8]}",
            "amount": amount,
            "currency": currency,
            "message": "Payment authorized successfully"
        }
    else:
        return {
            "success": False,
            "error": "PAYMENT_DECLINED",
            "message": "Payment authorization failed"
        }


async def format_booking_confirmation(
    booking_data: Dict[str, Any],
    property_details: Dict[str, Any]
) -> str:
    """
    Format a booking confirmation message.
    
    Args:
        booking_data: Booking data
        property_details: Property information
    
    Returns:
        Formatted confirmation message
    """
    add_ons_line = ""
    if booking_data.get('add_on_cost', 0) > 0:
        add_ons_line = f"• Add-ons: ${booking_data['add_on_cost']:.2f}\n"
    
    return BOOKING_CONFIRMATION_TEMPLATE.format(
        booking_id=booking_data['booking_id'][:8].upper(),
        property_name=booking_data['property_name'],
        location=property_details.get('location', {}).get('city', 'Unknown'),
        check_in_date=booking_data['check_in_date'],
        check_in_time=property_details.get('check_in_time', '15:00'),
        check_out_date=booking_data['check_out_date'],
        check_out_time=property_details.get('check_out_time', '11:00'),
        number_of_guests=booking_data['number_of_guests'],
        nights=booking_data['nights'],
        accommodation=f"{booking_data['accommodation']:.2f}",
        service_fee=f"{booking_data['service_fee']:.2f}",
        cleaning_fee=f"{booking_data['cleaning_fee']:.2f}",
        tax=f"{booking_data['tax']:.2f}",
        add_ons_line=add_ons_line,
        total=f"{booking_data['total_price']:.2f}"
    )


async def check_availability_before_booking(
    property_id: str,
    check_in_date: str,
    check_out_date: str
) -> Dict[str, Any]:
    """
    Final availability check before creating a booking.
    
    This ensures no race conditions where property becomes unavailable
    between search and booking.
    
    Args:
        property_id: Property to check
        check_in_date: Check-in date
        check_out_date: Check-out date
    
    Returns:
        Availability status
    """
    # In production, this would query Firestore to check for overlaps
    # For now, simulate availability check
    return {
        "available": True,
        "message": "Property is available for the selected dates"
    }


# Create the Booking Agent
booking_agent = Agent(
    name="booking_agent",
    model="gemini-2.0-flash",
    description="Handles secure booking creation with transaction support",
    global_instruction=BOOKING_SYSTEM_PROMPT,
    instruction=BOOKING_INSTRUCTION,
    tools=[
        FunctionTool(process_booking),
        FunctionTool(validate_booking_capacity),
        FunctionTool(simulate_payment_authorization),
        FunctionTool(format_booking_confirmation),
        FunctionTool(check_availability_before_booking),
    ]
)