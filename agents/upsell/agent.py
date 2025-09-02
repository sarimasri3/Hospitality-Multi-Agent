"""
Upsell Agent for add-on suggestions.
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from typing import Dict, List, Optional, Any


async def suggest_add_ons(
    property_type: str,
    number_of_guests: int,
    trip_purpose: Optional[str] = None,
    user_preferences: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Suggest relevant add-on services based on booking context.
    """
    add_ons = [
        {
            "id": "early_checkin",
            "name": "Early Check-in (12 PM)",
            "price": 50,
            "description": "Start your vacation earlier with noon check-in",
            "relevance": 0.8
        },
        {
            "id": "late_checkout", 
            "name": "Late Check-out (2 PM)",
            "price": 50,
            "description": "Enjoy a leisurely departure with extended check-out",
            "relevance": 0.8
        },
        {
            "id": "welcome_basket",
            "name": "Welcome Basket",
            "price": 75,
            "description": "Local treats, wine, and artisanal snacks waiting in your villa",
            "relevance": 0.7 if number_of_guests > 2 else 0.5
        },
        {
            "id": "spa_package",
            "name": "In-Villa Spa Treatment",
            "price": 200,
            "description": "Professional massage therapist for 90-minute couples treatment",
            "relevance": 0.9 if trip_purpose == "honeymoon" else 0.6
        },
        {
            "id": "chef_service",
            "name": "Private Chef Experience",
            "price": 300,
            "description": "Personal chef prepares gourmet dinner for your group",
            "relevance": 0.9 if number_of_guests >= 4 else 0.5
        }
    ]
    
    # Sort by relevance
    add_ons.sort(key=lambda x: x['relevance'], reverse=True)
    return add_ons[:3]  # Return top 3 suggestions


# Create the Upsell Agent
upsell_agent = Agent(
    name="upsell_agent",
    model="gemini-2.0-flash",
    description="Suggests relevant add-on services to enhance the guest experience",
    instruction="""Present add-on services that would enhance the guest's stay.
    
    Steps:
    1. Analyze the booking context (property type, guest count, preferences)
    2. Select 2-3 most relevant add-ons
    3. Present them attractively with clear value propositions
    4. Allow guest to select any combination or skip
    5. Calculate updated total if add-ons are selected
    
    Be persuasive but not pushy. Focus on value and experience enhancement.""",
    tools=[FunctionTool(suggest_add_ons)]
)