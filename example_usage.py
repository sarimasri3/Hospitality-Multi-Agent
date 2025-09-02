#!/usr/bin/env python
"""
Example usage of the Hospitality Booking System.
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Simple example without full orchestrator (for testing without ADK)
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from agents.availability.ranking import PropertyRanker
from agents.booking.idempotency import generate_natural_key, IdempotencyManager


async def test_memory_systems():
    """Test memory management systems."""
    print("\n" + "="*50)
    print("TESTING MEMORY SYSTEMS")
    print("="*50)
    
    # Test STM
    stm = ShortTermMemory(ttl_minutes=30)
    session_id = "test_session_001"
    
    print("\n1. Creating session...")
    session = await stm.create_session(session_id, "user_001")
    print(f"   ✅ Session created: {session_id}")
    
    print("\n2. Updating slots...")
    await stm.update_slots(session_id, {
        "city": "Miami",
        "check_in_date": "2025-03-15",
        "check_out_date": "2025-03-18",
        "number_of_guests": 4,
        "budget": 500
    })
    
    session = await stm.get_session(session_id)
    print(f"   ✅ Slots updated: {session['slots']}")
    
    # Test LTM
    ltm = LongTermMemory()
    user_id = "user_001"
    
    print("\n3. Updating user preferences...")
    await ltm.update_user_preferences(user_id, {
        "city": "Miami",
        "max_price": 500,
        "number_of_guests": 4,
        "amenities": ["pool", "wifi", "parking"]
    })
    
    preferences = await ltm.get_user_preferences(user_id)
    print(f"   ✅ Preferences saved: {preferences['preferred_cities']}")


def test_ranking_engine():
    """Test property ranking engine."""
    print("\n" + "="*50)
    print("TESTING RANKING ENGINE")
    print("="*50)
    
    ranker = PropertyRanker()
    
    # Sample properties
    properties = [
        {
            "property_id": "prop1",
            "name": "Luxury Beach Villa",
            "minimum_price": 450,
            "guest_space": 8,
            "location": {"city": "Miami", "lat": 25.7617, "lng": -80.1918},
            "amenities": ["pool", "beach_access", "wifi", "parking"],
            "property_type": "villa",
            "created_at": datetime.now().isoformat()
        },
        {
            "property_id": "prop2",
            "name": "Downtown Apartment",
            "minimum_price": 250,
            "guest_space": 4,
            "location": {"city": "Miami", "lat": 25.7749, "lng": -80.1937},
            "amenities": ["wifi", "parking", "gym"],
            "property_type": "apartment",
            "created_at": datetime.now().isoformat()
        },
        {
            "property_id": "prop3",
            "name": "Budget Studio",
            "minimum_price": 150,
            "guest_space": 2,
            "location": {"city": "Miami", "lat": 25.7589, "lng": -80.1965},
            "amenities": ["wifi"],
            "property_type": "studio",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    search_criteria = {
        "max_price": 500,
        "number_of_guests": 4
    }
    
    user_preferences = {
        "amenities": ["wifi", "parking"],
        "preferred_type": "apartment"
    }
    
    print("\n1. Ranking properties...")
    ranked = ranker.rank_properties(properties, user_preferences, search_criteria)
    
    print("\n2. Top recommendations:")
    for i, (prop, score, reasons) in enumerate(ranked[:3], 1):
        print(f"\n   {i}. {prop['name']}")
        print(f"      Score: {score:.2f}")
        print(f"      Price: ${prop['minimum_price']}/night")
        print(f"      Capacity: {prop['guest_space']} guests")
        if reasons:
            print(f"      Why: {', '.join(reasons[:2])}")
    
    print("\n3. Formatted recommendations:")
    formatted = ranker.format_recommendations(ranked, max_results=2)
    print(formatted)


def test_idempotency():
    """Test booking idempotency."""
    print("\n" + "="*50)
    print("TESTING IDEMPOTENCY")
    print("="*50)
    
    manager = IdempotencyManager()
    
    # Test natural key generation
    print("\n1. Testing natural key generation...")
    key1 = generate_natural_key("user1", "prop1", "2025-03-15", "2025-03-18")
    key2 = generate_natural_key("user1", "prop1", "2025-03-15", "2025-03-18")
    key3 = generate_natural_key("user2", "prop1", "2025-03-15", "2025-03-18")
    
    print(f"   Same inputs: {key1[:8]}... == {key2[:8]}... : {key1 == key2}")
    print(f"   Different user: {key1[:8]}... != {key3[:8]}... : {key1 != key3}")
    
    # Test idempotency manager
    print("\n2. Testing idempotency manager...")
    booking_data = {
        "booking_id": key1,
        "property_id": "prop1",
        "guest_id": "user1",
        "check_in_date": "2025-03-15",
        "check_out_date": "2025-03-18",
        "total_price": 1350.0
    }
    
    # First attempt
    existing = manager.check_idempotency(key1)
    print(f"   First check (should be None): {existing}")
    
    # Store booking
    manager.store_idempotency(key1, booking_data)
    print(f"   ✅ Booking stored")
    
    # Second attempt (idempotent)
    existing = manager.check_idempotency(key1)
    print(f"   Second check (should exist): Booking {existing['booking_id'][:8]}...")
    
    # Test booking window validation
    print("\n3. Testing date validation...")
    check_in = datetime.now() + timedelta(days=7)
    check_out = check_in + timedelta(days=3)
    
    result = manager.validate_booking_window(check_in, check_out)
    print(f"   Valid booking (7 days out, 3 nights): {result['valid']}")
    print(f"   {result['message']}")


async def test_simple_booking_flow():
    """Test a simple booking flow."""
    print("\n" + "="*50)
    print("SIMULATING BOOKING FLOW")
    print("="*50)
    
    # Initialize components
    stm = ShortTermMemory()
    ltm = LongTermMemory()
    ranker = PropertyRanker()
    idempotency = IdempotencyManager()
    
    session_id = "booking_session_001"
    user_id = "guest_001"
    
    print("\n1. INQUIRY PHASE")
    print("   Guest: I need a place in Miami for 4 people next month")
    
    # Create session and collect slots
    session = await stm.create_session(session_id, user_id)
    await stm.update_slots(session_id, {
        "city": "Miami",
        "check_in_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
        "check_out_date": (datetime.now() + timedelta(days=33)).strftime("%Y-%m-%d"),
        "number_of_guests": 4,
        "budget": 500
    })
    print("   ✅ Slots collected")
    
    print("\n2. AVAILABILITY PHASE")
    # Mock properties (would come from Firestore)
    properties = [
        {
            "property_id": "villa_001",
            "name": "Beach Villa",
            "minimum_price": 450,
            "guest_space": 8,
            "location": {"city": "Miami", "lat": 25.76, "lng": -80.19},
            "amenities": ["pool", "beach", "wifi"],
            "property_type": "villa",
            "created_at": datetime.now().isoformat()
        },
        {
            "property_id": "apt_002",
            "name": "City Apartment",
            "minimum_price": 250,
            "guest_space": 4,
            "location": {"city": "Miami", "lat": 25.77, "lng": -80.19},
            "amenities": ["wifi", "gym", "parking"],
            "property_type": "apartment",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    session = await stm.get_session(session_id)
    ranked = ranker.rank_properties(
        properties,
        {},
        {"max_price": 500, "number_of_guests": 4}
    )
    
    print("   Found 2 properties, showing top recommendation:")
    top_prop = ranked[0][0]
    print(f"   → {top_prop['name']} - ${top_prop['minimum_price']}/night")
    
    print("\n3. BOOKING PHASE")
    print("   Guest: I'll take the City Apartment")
    
    # Generate booking with idempotency
    natural_key = generate_natural_key(
        user_id,
        "apt_002",
        session['slots']['check_in_date'],
        session['slots']['check_out_date']
    )
    
    if not idempotency.check_idempotency(natural_key):
        booking = {
            "booking_id": natural_key[:8].upper(),
            "property_id": "apt_002",
            "guest_id": user_id,
            "check_in_date": session['slots']['check_in_date'],
            "check_out_date": session['slots']['check_out_date'],
            "number_of_guests": 4,
            "nights": 3,
            "base_price": 250,
            "total_price": 891.0,  # Including fees and tax
            "status": "confirmed"
        }
        idempotency.store_idempotency(natural_key, booking)
        print(f"   ✅ Booking confirmed: {booking['booking_id']}")
    else:
        print("   ℹ️  Booking already exists (idempotent)")
    
    print("\n4. CONFIRMATION PHASE")
    print("   Sending confirmation email...")
    print("   ✅ Email sent to guest")
    
    print("\n5. USER PROFILE UPDATE")
    await ltm.update_user_preferences(user_id, session['slots'])
    await ltm.add_booking_to_history(user_id, booking)
    
    context = await ltm.get_personalization_context(user_id)
    print(f"   ✅ Profile updated")
    print(f"   Preferred cities: {context['preferences']['preferred_cities']}")
    print(f"   Booking count: {context['insights']['booking_count']}")


async def main():
    """Run all examples."""
    print("="*50)
    print("HOSPITALITY BOOKING SYSTEM - EXAMPLES")
    print("="*50)
    
    try:
        # Test components
        await test_memory_systems()
        test_ranking_engine()
        test_idempotency()
        await test_simple_booking_flow()
        
        print("\n" + "="*50)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY")
        print("="*50)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Check if we can import required modules
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print("Environment loaded from .env file")
    except ImportError:
        print("Note: python-dotenv not installed. Run: pip install python-dotenv")
    
    # Run examples
    asyncio.run(main())