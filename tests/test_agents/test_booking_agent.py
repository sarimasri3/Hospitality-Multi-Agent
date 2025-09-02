"""
Tests for the Booking Agent.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.booking.agent import (
    process_booking, validate_booking_capacity, simulate_payment_authorization,
    format_booking_confirmation, check_availability_before_booking
)
from agents.booking.idempotency import (
    generate_natural_key, generate_request_signature, IdempotencyManager
)


class TestBookingAgent:
    """Test cases for Booking Agent functions."""
    
    @pytest.mark.asyncio
    async def test_process_booking_new(self):
        """Test processing a new booking."""
        result = await process_booking(
            property_id="prop123",
            property_name="Beach Villa",
            guest_id="guest123",
            host_id="host123",
            check_in_date="2025-03-15",
            check_out_date="2025-03-18",
            number_of_guests=4,
            base_price=300.0
        )
        
        assert result['success'] is True
        assert result['idempotent'] is False
        assert 'booking_id' in result
        assert result['booking_data']['nights'] == 3
        assert result['booking_data']['total_price'] > 900  # Base + fees + tax
    
    @pytest.mark.asyncio
    async def test_process_booking_with_addons(self):
        """Test processing booking with add-ons."""
        result = await process_booking(
            property_id="prop123",
            property_name="Beach Villa",
            guest_id="guest123",
            host_id="host123",
            check_in_date="2025-03-15",
            check_out_date="2025-03-18",
            number_of_guests=4,
            base_price=300.0,
            add_ons=["early_checkin", "welcome_basket"]
        )
        
        assert result['success'] is True
        assert result['booking_data']['add_on_cost'] == 125.0  # 50 + 75
        assert "early_checkin" in result['booking_data']['add_ons']
        assert "welcome_basket" in result['booking_data']['add_ons']
    
    @pytest.mark.asyncio
    async def test_validate_booking_capacity_valid(self):
        """Test booking capacity validation with valid request."""
        result = await validate_booking_capacity(
            property_capacity=8,
            requested_guests=6
        )
        
        assert result['valid'] is True
        assert "can accommodate" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_booking_capacity_exceeded(self):
        """Test booking capacity validation when exceeded."""
        result = await validate_booking_capacity(
            property_capacity=4,
            requested_guests=6
        )
        
        assert result['valid'] is False
        assert "capacity" in result['message'].lower()
    
    @pytest.mark.asyncio
    async def test_simulate_payment_authorization_success(self):
        """Test successful payment authorization simulation."""
        with patch('random.random', return_value=0.9):  # Force success
            result = await simulate_payment_authorization(1000.0)
            
            assert result['success'] is True
            assert result['amount'] == 1000.0
            assert 'authorization_id' in result
    
    @pytest.mark.asyncio
    async def test_simulate_payment_authorization_failure(self):
        """Test failed payment authorization simulation."""
        with patch('random.random', return_value=0.96):  # Force failure
            result = await simulate_payment_authorization(1000.0)
            
            assert result['success'] is False
            assert result['error'] == "PAYMENT_DECLINED"
    
    @pytest.mark.asyncio
    async def test_format_booking_confirmation(self):
        """Test booking confirmation formatting."""
        booking_data = {
            'booking_id': 'abc123def456',
            'property_name': 'Beach Villa',
            'check_in_date': '2025-03-15',
            'check_out_date': '2025-03-18',
            'number_of_guests': 4,
            'nights': 3,
            'accommodation': 900.0,
            'service_fee': 90.0,
            'cleaning_fee': 50.0,
            'tax': 83.2,
            'add_on_cost': 0,
            'total_price': 1123.2
        }
        
        property_details = {
            'location': {'city': 'Miami'},
            'check_in_time': '15:00',
            'check_out_time': '11:00'
        }
        
        result = await format_booking_confirmation(booking_data, property_details)
        
        assert 'ABC123DE' in result  # Booking ID should be uppercase and truncated
        assert 'Beach Villa' in result
        assert 'Miami' in result
        assert '2025-03-15' in result
        assert '2025-03-18' in result
        assert '4' in result  # Number of guests
        assert '1123.2' in result  # Total price
    
    @pytest.mark.asyncio
    async def test_format_booking_confirmation_with_addons(self):
        """Test booking confirmation formatting with add-ons."""
        booking_data = {
            'booking_id': 'abc123def456',
            'property_name': 'Beach Villa',
            'check_in_date': '2025-03-15',
            'check_out_date': '2025-03-18',
            'number_of_guests': 4,
            'nights': 3,
            'accommodation': 900.0,
            'service_fee': 90.0,
            'cleaning_fee': 50.0,
            'tax': 83.2,
            'add_on_cost': 125.0,
            'total_price': 1248.2
        }
        
        property_details = {
            'location': {'city': 'Miami'},
            'check_in_time': '15:00',
            'check_out_time': '11:00'
        }
        
        result = await format_booking_confirmation(booking_data, property_details)
        
        assert 'Add-ons: $125.00' in result
    
    @pytest.mark.asyncio
    async def test_check_availability_before_booking(self):
        """Test availability check before booking."""
        result = await check_availability_before_booking(
            property_id="prop123",
            check_in_date="2025-03-15",
            check_out_date="2025-03-18"
        )
        
        assert result['available'] is True
        assert 'available' in result['message']


class TestIdempotency:
    """Test cases for idempotency functions."""
    
    def test_generate_natural_key_consistency(self):
        """Test that natural key generation is consistent."""
        key1 = generate_natural_key("user1", "prop1", "2025-03-15", "2025-03-18")
        key2 = generate_natural_key("user1", "prop1", "2025-03-15", "2025-03-18")
        
        assert key1 == key2
        assert len(key1) == 64  # SHA256 hex length
    
    def test_generate_natural_key_different_inputs(self):
        """Test that different inputs generate different keys."""
        key1 = generate_natural_key("user1", "prop1", "2025-03-15", "2025-03-18")
        key2 = generate_natural_key("user2", "prop1", "2025-03-15", "2025-03-18")
        key3 = generate_natural_key("user1", "prop2", "2025-03-15", "2025-03-18")
        
        assert key1 != key2
        assert key1 != key3
        assert key2 != key3
    
    def test_generate_natural_key_datetime_objects(self):
        """Test natural key generation with datetime objects."""
        date1 = datetime(2025, 3, 15)
        date2 = datetime(2025, 3, 18)
        
        key1 = generate_natural_key("user1", "prop1", date1, date2)
        key2 = generate_natural_key("user1", "prop1", "2025-03-15", "2025-03-18")
        
        assert key1 == key2  # Should normalize to same format
    
    def test_generate_request_signature(self):
        """Test request signature generation."""
        request1 = {"user": "user1", "property": "prop1", "amount": 100}
        request2 = {"property": "prop1", "user": "user1", "amount": 100}  # Different order
        request3 = {"user": "user1", "property": "prop1", "amount": 200}  # Different amount
        
        sig1 = generate_request_signature(request1)
        sig2 = generate_request_signature(request2)
        sig3 = generate_request_signature(request3)
        
        assert sig1 == sig2  # Order shouldn't matter
        assert sig1 != sig3  # Different data should produce different signature
    
    def test_idempotency_manager_new_booking(self):
        """Test idempotency manager with new booking."""
        manager = IdempotencyManager()
        key = "test_key_123"
        
        result = manager.check_idempotency(key)
        assert result is None
    
    def test_idempotency_manager_existing_booking(self):
        """Test idempotency manager with existing booking."""
        manager = IdempotencyManager()
        key = "test_key_123"
        booking_data = {"booking_id": key, "amount": 100}
        
        manager.store_idempotency(key, booking_data)
        result = manager.check_idempotency(key)
        
        assert result is not None
        assert result['booking_id'] == key
        assert result['amount'] == 100
        assert 'stored_at' in result
    
    def test_idempotency_manager_with_signature(self):
        """Test idempotency manager with request signature."""
        manager = IdempotencyManager()
        key = "test_key_123"
        signature = "test_signature"
        booking_data = {"booking_id": key}
        
        manager.store_idempotency(key, booking_data, signature)
        result = manager.check_idempotency(key, signature)
        
        assert result is not None
        assert result['is_retry'] is True
        assert result['signature'] == signature
    
    def test_validate_booking_window_valid(self):
        """Test booking window validation with valid dates."""
        manager = IdempotencyManager()
        check_in = datetime.now() + timedelta(days=7)
        check_out = check_in + timedelta(days=3)
        
        result = manager.validate_booking_window(check_in, check_out)
        
        assert result['valid'] is True
        assert result['nights'] == 3
    
    def test_validate_booking_window_past_date(self):
        """Test booking window validation with past date."""
        manager = IdempotencyManager()
        check_in = datetime.now() - timedelta(days=1)
        check_out = datetime.now() + timedelta(days=2)
        
        result = manager.validate_booking_window(check_in, check_out)
        
        assert result['valid'] is False
        assert result['error'] == "PAST_BOOKING"
    
    def test_validate_booking_window_too_far_advance(self):
        """Test booking window validation with date too far in advance."""
        manager = IdempotencyManager()
        check_in = datetime.now() + timedelta(days=400)
        check_out = check_in + timedelta(days=3)
        
        result = manager.validate_booking_window(check_in, check_out)
        
        assert result['valid'] is False
        assert result['error'] == "TOO_FAR_ADVANCE"
    
    def test_validate_booking_window_min_stay(self):
        """Test booking window validation with minimum stay violation."""
        manager = IdempotencyManager()
        check_in = datetime.now() + timedelta(days=7)
        check_out = check_in  # Same day
        
        result = manager.validate_booking_window(check_in, check_out)
        
        assert result['valid'] is False
        assert result['error'] == "MIN_STAY"
    
    def test_validate_booking_window_max_stay(self):
        """Test booking window validation with maximum stay violation."""
        manager = IdempotencyManager()
        check_in = datetime.now() + timedelta(days=7)
        check_out = check_in + timedelta(days=35)  # 35 nights
        
        result = manager.validate_booking_window(check_in, check_out)
        
        assert result['valid'] is False
        assert result['error'] == "MAX_STAY"


if __name__ == "__main__":
    pytest.main([__file__])
