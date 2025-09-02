"""
Firestore MCP Server for Hospitality Booking System.
"""

import asyncio
import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path

from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type
import mcp.server.stdio
from mcp.server.lowlevel import Server
from mcp.server.models import InitializationOptions
from mcp import types as mcp_types

import firebase_admin
from firebase_admin import firestore, credentials
from dotenv import load_dotenv

from .models import (
    User, Property, Booking, FeaturePackage, SessionState,
    UserRole, BookingStatus, PropertyStatus
)
from .transactions import (
    generate_natural_key, check_booking_overlap,
    create_booking_transaction, update_booking_status
)

# Load environment variables
load_dotenv()

# Logging setup
LOG_FILE_PATH = Path(__file__).parent / "firestore_mcp.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE_PATH, mode="w"),
        logging.StreamHandler()
    ],
)
logger = logging.getLogger(__name__)

# Initialize Firebase Admin SDK
try:
    cred_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
    else:
        # Use default credentials (e.g., in Google Cloud environment)
        firebase_admin.initialize_app()
    
    db = firestore.client()
    logger.info("Firebase Admin SDK initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {e}")
    db = None


# Tool Functions

async def create_user(
    name: str,
    email: str,
    role: str = "guest",
    phone: Optional[str] = None,
    preferences: Optional[Dict[str, Any]] = None
) -> Dict:
    """
    Create a new user in the system.
    
    Args:
        name: User's full name
        email: User's email (unique)
        role: User role (guest/host/admin)
        phone: Optional phone number
        preferences: Optional user preferences dictionary
    
    Returns:
        Dict with success status and user ID
    """
    try:
        # Check if user with email already exists
        users_ref = db.collection('users')
        existing = users_ref.where('email', '==', email).limit(1).get()
        
        if existing:
            return {
                "success": False,
                "message": f"User with email {email} already exists"
            }
        
        # Create new user
        user_ref = users_ref.document()
        user_data = {
            "uid": user_ref.id,
            "name": name,
            "email": email,
            "role": role,
            "phone": phone,
            "preferences": preferences or {},
            "created_at": firestore.SERVER_TIMESTAMP,
            "last_login": None
        }
        
        user_ref.set(user_data)
        
        return {
            "success": True,
            "user_id": user_ref.id,
            "message": "User created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return {
            "success": False,
            "message": f"Error creating user: {str(e)}"
        }


async def get_user(user_id: Optional[str] = None, email: Optional[str] = None) -> Dict:
    """
    Get user by ID or email.
    
    Args:
        user_id: Optional user ID
        email: Optional email address
    
    Returns:
        User data dictionary
    """
    try:
        if user_id:
            user_ref = db.collection('users').document(user_id)
            user = user_ref.get()
            if user.exists:
                return {
                    "success": True,
                    "user": user.to_dict()
                }
        elif email:
            users_ref = db.collection('users')
            users = users_ref.where('email', '==', email).limit(1).get()
            if users:
                return {
                    "success": True,
                    "user": users[0].to_dict()
                }
        
        return {
            "success": False,
            "message": "User not found"
        }
    except Exception as e:
        logger.error(f"Error getting user: {e}")
        return {
            "success": False,
            "message": f"Error getting user: {str(e)}"
        }


async def create_property(
    user_id: str,
    name: str,
    description: str,
    city: str,
    country: str,
    address: str,
    lat: float,
    lng: float,
    minimum_price: float,
    property_type: str,
    guest_space: int,
    amenities: List[str],
    images: Optional[List[str]] = None,
    check_in_time: str = "15:00",
    check_out_time: str = "11:00"
) -> Dict:
    """
    Create a new property listing.
    
    Args:
        user_id: Host user ID
        name: Property name
        description: Property description
        city: City location
        country: Country location
        address: Full address
        lat: Latitude
        lng: Longitude
        minimum_price: Minimum nightly price
        property_type: Type of property (villa, apartment, etc.)
        guest_space: Maximum number of guests
        amenities: List of amenities
        images: Optional list of image URLs
        check_in_time: Check-in time (HH:MM format)
        check_out_time: Check-out time (HH:MM format)
    
    Returns:
        Dict with success status and property ID
    """
    try:
        properties_ref = db.collection('properties')
        property_ref = properties_ref.document()
        
        property_data = {
            "property_id": property_ref.id,
            "user_id": user_id,
            "name": name,
            "description": description,
            "status": "active",
            "location": {
                "address": address,
                "city": city,
                "country": country,
                "lat": lat,
                "lng": lng
            },
            "minimum_price": minimum_price,
            "property_type": property_type,
            "guest_space": guest_space,
            "check_in_time": check_in_time,
            "check_out_time": check_out_time,
            "prices": {
                "weekday": minimum_price,
                "weekend": minimum_price * 1.2  # 20% weekend premium
            },
            "amenities": amenities,
            "images": images or [],
            "created_at": firestore.SERVER_TIMESTAMP,
            "updated_at": firestore.SERVER_TIMESTAMP
        }
        
        property_ref.set(property_data)
        
        return {
            "success": True,
            "property_id": property_ref.id,
            "message": "Property created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating property: {e}")
        return {
            "success": False,
            "message": f"Error creating property: {str(e)}"
        }


async def search_properties(
    city: Optional[str] = None,
    check_in_date: Optional[str] = None,
    check_out_date: Optional[str] = None,
    number_of_guests: Optional[int] = None,
    max_price: Optional[float] = None,
    amenities: Optional[List[str]] = None
) -> Dict:
    """
    Search for available properties based on criteria.
    
    Args:
        city: City to search in
        check_in_date: Check-in date (YYYY-MM-DD)
        check_out_date: Check-out date (YYYY-MM-DD)
        number_of_guests: Number of guests
        max_price: Maximum price per night
        amenities: Required amenities
    
    Returns:
        List of matching properties
    """
    try:
        properties_ref = db.collection('properties')
        query = properties_ref.where('status', '==', 'active')
        
        if city:
            query = query.where('location.city', '==', city)
        
        if number_of_guests:
            query = query.where('guest_space', '>=', number_of_guests)
        
        if max_price:
            query = query.where('minimum_price', '<=', max_price)
        
        properties = []
        for prop in query.stream():
            prop_data = prop.to_dict()
            
            # Check amenities if specified
            if amenities:
                prop_amenities = set(prop_data.get('amenities', []))
                required_amenities = set(amenities)
                if not required_amenities.issubset(prop_amenities):
                    continue
            
            # Check availability if dates provided
            if check_in_date and check_out_date:
                check_in = datetime.fromisoformat(check_in_date)
                check_out = datetime.fromisoformat(check_out_date)
                
                if check_booking_overlap(db, prop.id, check_in, check_out):
                    continue
            
            properties.append(prop_data)
        
        return {
            "success": True,
            "count": len(properties),
            "properties": properties[:10]  # Limit to 10 results
        }
    except Exception as e:
        logger.error(f"Error searching properties: {e}")
        return {
            "success": False,
            "message": f"Error searching properties: {str(e)}"
        }


async def create_booking(
    property_id: str,
    guest_id: str,
    host_id: str,
    check_in_date: str,
    check_out_date: str,
    number_of_guests: int,
    total_price: float,
    add_ons: Optional[List[str]] = None
) -> Dict:
    """
    Create a booking with idempotency and overlap checking.
    
    Args:
        property_id: Property to book
        guest_id: Guest user ID
        host_id: Host user ID
        check_in_date: Check-in date (YYYY-MM-DD)
        check_out_date: Check-out date (YYYY-MM-DD)
        number_of_guests: Number of guests
        total_price: Total booking price
        add_ons: Optional list of add-on services
    
    Returns:
        Booking creation result
    """
    try:
        check_in = datetime.fromisoformat(check_in_date)
        check_out = datetime.fromisoformat(check_out_date)
        
        booking_data = {
            "property_id": property_id,
            "guest_id": guest_id,
            "host_id": host_id,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "number_of_guests": number_of_guests,
            "total_price": total_price,
            "status": "pending",
            "add_ons": add_ons or []
        }
        
        # Run transaction
        transaction = db.transaction()
        result = create_booking_transaction(transaction, db, booking_data)
        
        return result
    except Exception as e:
        logger.error(f"Error creating booking: {e}")
        return {
            "success": False,
            "message": f"Error creating booking: {str(e)}"
        }


async def get_booking(booking_id: str) -> Dict:
    """
    Get booking details by ID.
    
    Args:
        booking_id: Booking ID
    
    Returns:
        Booking data
    """
    try:
        booking_ref = db.collection('bookings').document(booking_id)
        booking = booking_ref.get()
        
        if booking.exists:
            return {
                "success": True,
                "booking": booking.to_dict()
            }
        
        return {
            "success": False,
            "message": "Booking not found"
        }
    except Exception as e:
        logger.error(f"Error getting booking: {e}")
        return {
            "success": False,
            "message": f"Error getting booking: {str(e)}"
        }


async def update_booking_status_tool(
    booking_id: str,
    new_status: str,
    reason: Optional[str] = None
) -> Dict:
    """
    Update the status of a booking.
    
    Args:
        booking_id: Booking to update
        new_status: New status (pending/confirmed/cancelled/completed)
        reason: Optional reason for status change
    
    Returns:
        Update result
    """
    try:
        return update_booking_status(db, booking_id, new_status, reason)
    except Exception as e:
        logger.error(f"Error updating booking status: {e}")
        return {
            "success": False,
            "message": f"Error updating booking status: {str(e)}"
        }


async def get_user_bookings(
    user_id: str,
    role: str = "guest",
    status: Optional[str] = None
) -> Dict:
    """
    Get all bookings for a user.
    
    Args:
        user_id: User ID
        role: User role (guest or host)
        status: Optional filter by booking status
    
    Returns:
        List of user bookings
    """
    try:
        bookings_ref = db.collection('bookings')
        
        if role == "guest":
            query = bookings_ref.where('guest_id', '==', user_id)
        else:
            query = bookings_ref.where('host_id', '==', user_id)
        
        if status:
            query = query.where('status', '==', status)
        
        bookings = []
        for booking in query.stream():
            bookings.append(booking.to_dict())
        
        return {
            "success": True,
            "count": len(bookings),
            "bookings": bookings
        }
    except Exception as e:
        logger.error(f"Error getting user bookings: {e}")
        return {
            "success": False,
            "message": f"Error getting user bookings: {str(e)}"
        }


# Initialize MCP server
async def main():
    """Main entry point for the MCP server."""
    server = Server()
    
    # Register tools
    tools = [
        FunctionTool(create_user),
        FunctionTool(get_user),
        FunctionTool(create_property),
        FunctionTool(search_properties),
        FunctionTool(create_booking),
        FunctionTool(get_booking),
        FunctionTool(update_booking_status_tool),
        FunctionTool(get_user_bookings),
    ]
    
    for tool in tools:
        mcp_tool = adk_to_mcp_tool_type(tool)
        server.register_tool(mcp_tool)
    
    logger.info(f"Registered {len(tools)} tools")
    
    # Run the server
    initialization_options = InitializationOptions(
        server_name="firestore-mcp-server",
        server_version="0.1.0"
    )
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            initialization_options
        )


if __name__ == "__main__":
    asyncio.run(main())