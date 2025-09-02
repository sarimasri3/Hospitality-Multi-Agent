"""
Confirmation Agent for booking confirmation and communication.
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from typing import Dict, Any
from datetime import datetime


async def generate_confirmation_email(
    booking_data: Dict[str, Any],
    property_data: Dict[str, Any],
    guest_data: Dict[str, Any]
) -> Dict[str, str]:
    """
    Generate confirmation email content.
    """
    email_body = f"""
    Dear {guest_data.get('name', 'Guest')},
    
    Your booking at {property_data['name']} has been confirmed!
    
    Booking Reference: {booking_data['booking_id'][:8].upper()}
    Check-in: {booking_data['check_in_date']}
    Check-out: {booking_data['check_out_date']}
    
    Property Address:
    {property_data['location']['address']}
    {property_data['location']['city']}, {property_data['location']['country']}
    
    Total Amount Paid: ${booking_data['total_price']:.2f}
    
    House Rules:
    - Check-in time: {property_data.get('check_in_time', '15:00')}
    - Check-out time: {property_data.get('check_out_time', '11:00')}
    - Maximum occupancy: {property_data['guest_space']} guests
    - No smoking inside the property
    - No parties or events
    - Respect quiet hours (10 PM - 8 AM)
    
    We'll send you check-in instructions 48 hours before your arrival.
    
    Best regards,
    The Hospitality Team
    """
    
    return {
        "subject": f"Booking Confirmed - {property_data['name']}",
        "body": email_body,
        "recipient": guest_data.get('email', '')
    }


async def create_audit_log(
    booking_id: str,
    action: str,
    details: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create an audit log entry for the booking.
    """
    return {
        "booking_id": booking_id,
        "action": action,
        "details": details,
        "timestamp": datetime.now().isoformat(),
        "logged": True
    }


# Create the Confirmation Agent
confirmation_agent = Agent(
    name="confirmation_agent",
    model="gemini-2.0-flash",
    description="Handles booking confirmation and guest communication",
    instruction="""Provide comprehensive booking confirmation to the guest.
    
    Steps:
    1. Summarize the booking details clearly
    2. Generate confirmation email content
    3. Highlight important information (check-in/out times, house rules)
    4. Create audit log for the booking
    5. Inform guest about next steps
    6. Thank them for their booking
    
    Be thorough, professional, and welcoming.""",
    tools=[
        FunctionTool(generate_confirmation_email),
        FunctionTool(create_audit_log)
    ]
)