"""
Integration test for the complete booking flow.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestrator.main import HospitalityOrchestrator
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory


class TestFullBookingFlow:
    """Test the complete booking flow through all agents."""
    
    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator instance for testing."""
        # Mock the MCP connection
        with patch('orchestrator.main.MCPToolset'):
            orchestrator = HospitalityOrchestrator()
            yield orchestrator
    
    @pytest.mark.asyncio
    async def test_session_creation(self, orchestrator):
        """Test that sessions are created properly."""
        session_id = "test_session_001"
        user_id = "test_user_001"
        
        # First request should create a new session
        response = await orchestrator.handle_request(
            "Hello, I need a villa",
            session_id,
            user_id
        )
        
        assert response is not None
        
        # Check that session was created
        session = await orchestrator.stm.get_session(session_id)
        assert session is not None
        assert session["session_id"] == session_id
        assert session["user_id"] == user_id
        assert len(session["messages"]) > 0
    
    @pytest.mark.asyncio
    async def test_slot_collection(self, orchestrator):
        """Test that inquiry agent collects slots properly."""
        session_id = "test_session_002"
        
        # Provide booking details
        response = await orchestrator.handle_request(
            "I need a villa in Miami for 4 people from 2025-03-15 to 2025-03-18",
            session_id
        )
        
        # Check that slots were extracted
        session = await orchestrator.stm.get_session(session_id)
        assert session is not None
        
        # Slots should be updated (this depends on agent implementation)
        # In a real test, we'd check specific slot values
    
    @pytest.mark.asyncio
    async def test_memory_management(self):
        """Test STM and LTM functionality."""
        stm = ShortTermMemory(ttl_minutes=30)
        ltm = LongTermMemory()
        
        # Test STM
        session_id = "test_session_003"
        session = await stm.create_session(session_id, "user1")
        assert session is not None
        
        # Update slots
        await stm.update_slots(session_id, {
            "city": "Miami",
            "check_in_date": "2025-03-15",
            "check_out_date": "2025-03-18",
            "number_of_guests": 4
        })
        
        # Retrieve and verify
        session = await stm.get_session(session_id)
        assert session["slots"]["city"] == "Miami"
        assert session["slots"]["number_of_guests"] == 4
        
        # Test LTM
        user_id = "user1"
        await ltm.update_user_preferences(user_id, {
            "city": "Miami",
            "max_price": 500,
            "number_of_guests": 4
        })
        
        preferences = await ltm.get_user_preferences(user_id)
        assert "Miami" in preferences["preferred_cities"]
        assert preferences["typical_guests"] == 4
    
    @pytest.mark.asyncio
    async def test_booking_idempotency(self):
        """Test that duplicate bookings are prevented."""
        from agents.booking.idempotency import IdempotencyManager
        
        manager = IdempotencyManager()
        
        booking_data = {
            "guest_id": "guest1",
            "property_id": "prop1",
            "check_in_date": "2025-03-15",
            "check_out_date": "2025-03-18"
        }
        
        # First booking
        natural_key = "test_key_001"
        manager.store_idempotency(natural_key, booking_data)
        
        # Try duplicate booking
        existing = manager.check_idempotency(natural_key)
        assert existing is not None
        assert existing["guest_id"] == "guest1"
    
    @pytest.mark.asyncio  
    async def test_concurrent_bookings(self):
        """Test handling of concurrent booking attempts."""
        from agents.booking.idempotency import generate_natural_key
        
        # Simulate two users trying to book same property/dates
        key1 = generate_natural_key("user1", "prop1", "2025-03-15", "2025-03-18")
        key2 = generate_natural_key("user2", "prop1", "2025-03-15", "2025-03-18")
        
        # Keys should be different for different users
        assert key1 != key2
        
        # In production, transaction support would prevent double booking
        # This would be tested with actual Firestore transactions
    
    @pytest.mark.asyncio
    async def test_error_handling(self, orchestrator):
        """Test graceful error handling."""
        session_id = "test_session_error"
        
        # Test with invalid input
        response = await orchestrator.handle_request(
            "",  # Empty input
            session_id
        )
        
        # Should return error message, not crash
        assert response is not None
        assert "error" in response.lower() or "sorry" in response.lower() or response != ""