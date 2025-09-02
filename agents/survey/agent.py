"""
Survey Agent for post-stay feedback collection.
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from typing import Dict, Any, Optional


async def create_survey(
    booking_id: str,
    property_id: str,
    guest_id: str
) -> Dict[str, Any]:
    """
    Create a post-stay survey.
    """
    return {
        "survey_id": f"survey_{booking_id[:8]}",
        "questions": [
            {"id": "overall", "text": "How would you rate your overall stay?", "type": "rating", "scale": 5},
            {"id": "cleanliness", "text": "How clean was the property?", "type": "rating", "scale": 5},
            {"id": "accuracy", "text": "How accurate was the listing?", "type": "rating", "scale": 5},
            {"id": "checkin", "text": "How smooth was check-in?", "type": "rating", "scale": 5},
            {"id": "value", "text": "How was the value for money?", "type": "rating", "scale": 5},
            {"id": "recommend", "text": "Would you recommend this property?", "type": "nps", "scale": 10},
            {"id": "comments", "text": "Any additional comments?", "type": "text"}
        ],
        "created": True
    }


async def calculate_metrics(
    ratings: Dict[str, int],
    nps_score: int
) -> Dict[str, Any]:
    """
    Calculate CSAT and NPS metrics from survey responses.
    """
    # Calculate average rating (CSAT)
    rating_values = list(ratings.values())
    csat = sum(rating_values) / len(rating_values) if rating_values else 0
    
    # Categorize NPS
    if nps_score >= 9:
        nps_category = "promoter"
    elif nps_score >= 7:
        nps_category = "passive"
    else:
        nps_category = "detractor"
    
    return {
        "csat": round(csat, 2),
        "csat_percentage": round(csat * 20, 1),  # Convert 5-scale to percentage
        "nps_score": nps_score,
        "nps_category": nps_category,
        "metrics_calculated": True
    }


async def schedule_survey_send(
    booking_id: str,
    check_out_date: str,
    delay_hours: int = 24
) -> Dict[str, Any]:
    """
    Schedule survey to be sent after checkout.
    """
    from datetime import datetime, timedelta
    
    checkout = datetime.fromisoformat(check_out_date)
    send_time = checkout + timedelta(hours=delay_hours)
    
    return {
        "scheduled": True,
        "booking_id": booking_id,
        "send_time": send_time.isoformat(),
        "message": f"Survey scheduled for {delay_hours} hours after checkout"
    }


# Create the Survey Agent
survey_agent = Agent(
    name="survey_agent",
    model="gemini-2.0-flash",
    description="Collects post-stay feedback and calculates satisfaction metrics",
    instruction="""Manage post-stay survey and feedback collection.
    
    Steps:
    1. Schedule survey to be sent 24 hours after checkout
    2. Create survey with relevant questions
    3. When responses received, calculate CSAT and NPS
    4. Thank guest for feedback
    5. If issues mentioned, flag for follow-up
    
    Be appreciative of feedback and professional.""",
    tools=[
        FunctionTool(create_survey),
        FunctionTool(calculate_metrics),
        FunctionTool(schedule_survey_send)
    ]
)