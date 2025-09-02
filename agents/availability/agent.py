"""
Availability Agent for searching and ranking properties.
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool
from typing import Dict, List, Optional, Any

from .prompts import (
    AVAILABILITY_SYSTEM_PROMPT,
    AVAILABILITY_INSTRUCTION,
    NO_AVAILABILITY_TEMPLATE,
    PROPERTY_PRESENTATION_TEMPLATE
)
from .ranking import PropertyRanker


async def search_and_rank_properties(
    city: str,
    check_in_date: str,
    check_out_date: str,
    number_of_guests: int,
    max_price: Optional[float] = None,
    amenities: Optional[List[str]] = None,
    user_preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Search for properties and rank them by suitability.
    
    This is a wrapper tool that will be connected to the Firestore MCP
    in the orchestrator.
    
    Args:
        city: City to search in
        check_in_date: Check-in date
        check_out_date: Check-out date
        number_of_guests: Number of guests
        max_price: Maximum price per night
        amenities: Required amenities
        user_preferences: User preference data
    
    Returns:
        Ranked property results
    """
    # This will be replaced with actual MCP call in orchestrator
    # For now, return mock data for structure
    return {
        "success": True,
        "properties": [],
        "recommendations": "No properties found"
    }


async def calculate_total_price(
    base_price: float,
    nights: int,
    add_ons: Optional[List[str]] = None,
    service_fee_percentage: float = 0.1,
    tax_percentage: float = 0.08,
    cleaning_fee: float = 50.0
) -> Dict[str, Any]:
    """
    Calculate total price including fees and taxes.
    
    Args:
        base_price: Price per night
        nights: Number of nights
        add_ons: List of add-on services
        service_fee_percentage: Service fee percentage
        tax_percentage: Tax percentage
        cleaning_fee: Flat cleaning fee
    
    Returns:
        Price breakdown
    """
    subtotal = base_price * nights
    service_fee = subtotal * service_fee_percentage
    cleaning = cleaning_fee
    
    # Calculate add-on costs
    add_on_cost = 0
    if add_ons:
        # Add-on prices would come from config
        add_on_prices = {
            "early_checkin": 50,
            "late_checkout": 50,
            "welcome_basket": 75,
            "spa_package": 200,
            "chef_service": 300
        }
        for addon in add_ons:
            add_on_cost += add_on_prices.get(addon, 0)
    
    pre_tax_total = subtotal + service_fee + cleaning + add_on_cost
    tax = pre_tax_total * tax_percentage
    total = pre_tax_total + tax
    
    return {
        "nights": nights,
        "price_per_night": base_price,
        "subtotal": subtotal,
        "service_fee": service_fee,
        "cleaning_fee": cleaning,
        "add_ons_total": add_on_cost,
        "tax": tax,
        "total": total,
        "breakdown": {
            "Accommodation": f"${subtotal:.2f}",
            "Service Fee": f"${service_fee:.2f}",
            "Cleaning Fee": f"${cleaning:.2f}",
            "Add-ons": f"${add_on_cost:.2f}" if add_on_cost > 0 else None,
            "Tax": f"${tax:.2f}",
            "Total": f"${total:.2f}"
        }
    }


async def filter_by_amenities(
    properties: List[Dict],
    required_amenities: List[str]
) -> List[Dict]:
    """
    Filter properties by required amenities.
    
    Args:
        properties: List of properties
        required_amenities: Required amenities
    
    Returns:
        Filtered properties
    """
    if not required_amenities:
        return properties
    
    filtered = []
    required_set = set(required_amenities)
    
    for prop in properties:
        prop_amenities = set(prop.get('amenities', []))
        if required_set.issubset(prop_amenities):
            filtered.append(prop)
    
    return filtered


async def get_alternative_suggestions(
    city: str,
    check_in_date: str,
    check_out_date: str,
    number_of_guests: int
) -> Dict[str, Any]:
    """
    Generate alternative search suggestions when no properties are found.
    
    Args:
        city: Original search city
        check_in_date: Original check-in date
        check_out_date: Original check-out date
        number_of_guests: Original guest count
    
    Returns:
        Alternative suggestions
    """
    suggestions = []
    
    # Suggest nearby cities
    nearby_cities = {
        "Miami": ["Fort Lauderdale", "Miami Beach", "Coral Gables"],
        "Los Angeles": ["Santa Monica", "Beverly Hills", "Malibu"],
        "New York": ["Brooklyn", "Queens", "Jersey City"],
        "San Francisco": ["Oakland", "Berkeley", "San Jose"],
        "Paris": ["Versailles", "Saint-Denis", "Boulogne-Billancourt"],
        "London": ["Westminster", "Camden", "Greenwich"],
    }
    
    if city in nearby_cities:
        suggestions.append({
            "type": "nearby_locations",
            "message": f"Try searching in nearby areas like {', '.join(nearby_cities[city][:3])}",
            "cities": nearby_cities[city][:3]
        })
    
    # Suggest date flexibility
    suggestions.append({
        "type": "date_flexibility",
        "message": "Consider adjusting your dates by a few days for more availability"
    })
    
    # Suggest splitting stay
    if number_of_guests > 6:
        suggestions.append({
            "type": "split_booking",
            "message": f"For {number_of_guests} guests, consider booking 2 properties"
        })
    
    return {
        "suggestions": suggestions,
        "message": NO_AVAILABILITY_TEMPLATE.format(
            city=city,
            check_in=check_in_date,
            check_out=check_out_date
        )
    }


# Create the Availability Agent
availability_agent = Agent(
    name="availability_agent",
    model="gemini-2.0-flash",
    description="Searches for available properties and ranks them by suitability",
    global_instruction=AVAILABILITY_SYSTEM_PROMPT,
    instruction=AVAILABILITY_INSTRUCTION,
    tools=[
        FunctionTool(search_and_rank_properties),
        FunctionTool(calculate_total_price),
        FunctionTool(filter_by_amenities),
        FunctionTool(get_alternative_suggestions),
    ]
)