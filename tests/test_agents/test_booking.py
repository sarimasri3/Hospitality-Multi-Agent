"""
Unit tests for the Booking Agent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.booking.idempotency import (
    generate_natural_key,
    IdempotencyManager
)


class TestIdempotency:
    """Test idempotency functionality."""
    
    def test_natural_key_generation(self):
        """Test that natural keys are generated consistently."""
        # Same inputs should generate same key
        key1 = generate_natural_key(
            "guest1", "prop1", "2025-02-01", "2025-02-05"
        )
        key2 = generate_natural_key(
            "guest1", "prop1", "2025-02-01", "2025-02-05"
        )
        assert key1 == key2
        
        # Different inputs should generate different keys
        key3 = generate_natural_key(
            "guest2", "prop1", "2025-02-01", "2025-02-05"
        )
        assert key1 != key3
    
    def test_natural_key_normalization(self):
        """Test that inputs are normalized properly."""
        # Test with different case and spacing
        key1 = generate_natural_key(
            "GUEST1", "PROP1", "2025-02-01", "2025-02-05"
        )
        key2 = generate_natural_key(
            "guest1", "prop1", "2025-02-01", "2025-02-05"
        )
        assert key1 == key2
    
    @pytest.mark.asyncio
    async def test_idempotency_manager(self):
        """Test the idempotency manager."""
        manager = IdempotencyManager()
        
        # First check should return None
        result = manager.check_idempotency("test_key")
        assert result is None
        
        # Store data
        booking_data = {
            "booking_id": "test_key",
            "property_id": "prop1",
            "guest_id": "guest1"
        }
        manager.store_idempotency("test_key", booking_data)
        
        # Second check should return stored data
        result = manager.check_idempotency("test_key")
        assert result is not None
        assert result["booking_id"] == "test_key"
    
    def test_booking_window_validation(self):
        """Test booking date validation."""
        manager = IdempotencyManager()
        
        # Test past booking
        past_date = datetime(2020, 1, 1)
        future_date = datetime(2020, 1, 5)
        result = manager.validate_booking_window(past_date, future_date)
        assert not result["valid"]
        assert result["error"] == "PAST_BOOKING"
        
        # Test valid booking
        check_in = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        check_in = check_in.replace(day=check_in.day + 7)  # 7 days from now
        check_out = check_in.replace(day=check_in.day + 3)  # 3 night stay
        result = manager.validate_booking_window(check_in, check_out)
        assert result["valid"]
        assert result["nights"] == 3


class TestBookingAgent:
    """Test the booking agent functionality."""
    
    @pytest.mark.asyncio
    async def test_booking_capacity_validation(self):
        """Test capacity validation."""
        from agents.booking.agent import validate_booking_capacity
        
        # Valid capacity
        result = await validate_booking_capacity(6, 4)
        assert result["valid"] is True
        
        # Exceeded capacity
        result = await validate_booking_capacity(4, 6)
        assert result["valid"] is False
        assert "accommodate" in result["message"]
    
    @pytest.mark.asyncio
    async def test_payment_simulation(self):
        """Test payment authorization simulation."""
        from agents.booking.agent import simulate_payment_authorization
        
        # Test payment authorization
        result = await simulate_payment_authorization(500.0, "USD")
        
        # Should return either success or failure
        assert "success" in result
        assert "message" in result
        
        if result["success"]:
            assert "authorization_id" in result
            assert result["amount"] == 500.0
        else:
            assert "error" in result