"""
Pre-checkin Agent for reminders and preparation.
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from typing import Dict, Any, Optional
from datetime import datetime, timedelta


async def schedule_reminder(
    booking_id: str,
    check_in_date: str,
    guest_email: str,
    reminder_hours_before: int = 48
) -> Dict[str, Any]:
    """
    Schedule a pre-checkin reminder.
    """
    check_in = datetime.fromisoformat(check_in_date)
    reminder_time = check_in - timedelta(hours=reminder_hours_before)
    
    return {
        "scheduled": True,
        "booking_id": booking_id,
        "reminder_time": reminder_time.isoformat(),
        "recipient": guest_email,
        "message": "Pre-checkin reminder scheduled"
    }


async def collect_arrival_info(
    estimated_arrival_time: str,
    transportation_method: str,
    special_requests: Optional[str] = None
) -> Dict[str, Any]:
    """
    Collect guest arrival information.
    """
    return {
        "arrival_time": estimated_arrival_time,
        "transportation": transportation_method,
        "special_requests": special_requests,
        "collected": True
    }


async def generate_checkin_instructions(
    property_data: Dict[str, Any],
    booking_data: Dict[str, Any]
) -> str:
    """
    Generate detailed check-in instructions.
    """
    return f"""
    CHECK-IN INSTRUCTIONS
    
    Property: {property_data['name']}
    Address: {property_data['location']['address']}
    
    Check-in Time: {property_data.get('check_in_time', '15:00')}
    
    Access Instructions:
    1. The key will be in a lockbox at the front door
    2. Lockbox code: {booking_data['booking_id'][:4].upper()}
    3. WiFi Network: {property_data['name']}_Guest
    4. WiFi Password: Welcome{booking_data['booking_id'][:4]}
    
    Parking:
    - Free parking available in the driveway
    - Additional street parking available
    
    Contact Information:
    - Host: Available through the app
    - Emergency: Call our 24/7 support line
    
    We look forward to hosting you!
    """


# Create the Pre-checkin Agent
precheckin_agent = Agent(
    name="precheckin_agent",
    model="gemini-2.0-flash",
    description="Handles pre-arrival communication and check-in preparation",
    instruction="""Manage pre-arrival tasks and communication.
    
    Steps:
    1. Schedule reminder 48 hours before check-in
    2. Collect arrival information from guest
    3. Generate and send check-in instructions
    4. Address any special requests
    5. Confirm everything is ready for arrival
    
    Be helpful and ensure smooth arrival experience.""",
    tools=[
        FunctionTool(schedule_reminder),
        FunctionTool(collect_arrival_info),
        FunctionTool(generate_checkin_instructions)
    ]
)