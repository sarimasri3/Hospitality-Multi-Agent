"""
Tests for the Confirmation Agent.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.confirmation.agent import generate_confirmation_email, create_audit_log


class TestConfirmationAgent:
    """Test cases for Confirmation Agent functions."""
    
    @pytest.mark.asyncio
    async def test_generate_confirmation_email(self):
        """Test confirmation email generation."""
        booking_data = {
            'booking_id': 'abc123def456',
            'check_in_date': '2025-03-15',
            'check_out_date': '2025-03-18',
            'total_price': 1200.50
        }
        
        property_data = {
            'name': 'Beach Villa Miami',
            'location': {
                'address': '123 Ocean Drive',
                'city': 'Miami',
                'country': 'USA'
            },
            'guest_space': 8,
            'check_in_time': '15:00',
            'check_out_time': '11:00'
        }
        
        guest_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com'
        }
        
        result = await generate_confirmation_email(booking_data, property_data, guest_data)
        
        assert result['subject'] == 'Booking Confirmed - Beach Villa Miami'
        assert result['recipient'] == 'john.doe@example.com'
        
        body = result['body']
        assert 'Dear John Doe' in body
        assert 'Beach Villa Miami' in body
        assert 'ABC123DE' in body  # Booking reference (first 8 chars uppercase)
        assert '2025-03-15' in body
        assert '2025-03-18' in body
        assert '123 Ocean Drive' in body
        assert 'Miami, USA' in body
        assert '$1200.50' in body
        assert '15:00' in body  # Check-in time
        assert '11:00' in body  # Check-out time
        assert '8 guests' in body  # Maximum occupancy
        assert 'House Rules' in body
        assert 'No smoking' in body
        assert 'No parties' in body
        assert 'quiet hours' in body
        assert '48 hours before' in body
    
    @pytest.mark.asyncio
    async def test_generate_confirmation_email_missing_guest_name(self):
        """Test confirmation email generation with missing guest name."""
        booking_data = {
            'booking_id': 'abc123def456',
            'check_in_date': '2025-03-15',
            'check_out_date': '2025-03-18',
            'total_price': 1200.50
        }
        
        property_data = {
            'name': 'Beach Villa Miami',
            'location': {
                'address': '123 Ocean Drive',
                'city': 'Miami',
                'country': 'USA'
            },
            'guest_space': 8
        }
        
        guest_data = {'email': 'guest@example.com'}  # No name
        
        result = await generate_confirmation_email(booking_data, property_data, guest_data)
        
        assert 'Dear Guest' in result['body']
        assert result['recipient'] == 'guest@example.com'
    
    @pytest.mark.asyncio
    async def test_generate_confirmation_email_default_times(self):
        """Test confirmation email generation with default check-in/out times."""
        booking_data = {
            'booking_id': 'abc123def456',
            'check_in_date': '2025-03-15',
            'check_out_date': '2025-03-18',
            'total_price': 1200.50
        }
        
        property_data = {
            'name': 'Beach Villa Miami',
            'location': {
                'address': '123 Ocean Drive',
                'city': 'Miami',
                'country': 'USA'
            },
            'guest_space': 8
            # No check_in_time or check_out_time specified
        }
        
        guest_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com'
        }
        
        result = await generate_confirmation_email(booking_data, property_data, guest_data)
        
        body = result['body']
        assert '15:00' in body  # Default check-in time
        assert '11:00' in body  # Default check-out time
    
    @pytest.mark.asyncio
    async def test_create_audit_log(self):
        """Test audit log creation."""
        booking_id = 'booking_123'
        action = 'booking_confirmed'
        details = {
            'guest_id': 'guest_456',
            'property_id': 'prop_789',
            'total_amount': 1200.50,
            'payment_method': 'credit_card'
        }
        
        result = await create_audit_log(booking_id, action, details)
        
        assert result['booking_id'] == booking_id
        assert result['action'] == action
        assert result['details'] == details
        assert result['logged'] is True
        assert 'timestamp' in result
        
        # Verify timestamp is recent (within last minute)
        timestamp = datetime.fromisoformat(result['timestamp'])
        now = datetime.now()
        time_diff = (now - timestamp).total_seconds()
        assert time_diff < 60  # Should be very recent
    
    @pytest.mark.asyncio
    async def test_create_audit_log_empty_details(self):
        """Test audit log creation with empty details."""
        result = await create_audit_log('booking_123', 'status_change', {})
        
        assert result['booking_id'] == 'booking_123'
        assert result['action'] == 'status_change'
        assert result['details'] == {}
        assert result['logged'] is True
    
    @pytest.mark.asyncio
    async def test_create_audit_log_complex_details(self):
        """Test audit log creation with complex details."""
        complex_details = {
            'previous_status': 'pending',
            'new_status': 'confirmed',
            'changes': {
                'guest_count': {'from': 4, 'to': 6},
                'add_ons': {'added': ['early_checkin', 'welcome_basket']}
            },
            'metadata': {
                'user_agent': 'Mozilla/5.0...',
                'ip_address': '192.168.1.1',
                'session_id': 'sess_abc123'
            }
        }
        
        result = await create_audit_log('booking_123', 'booking_modified', complex_details)
        
        assert result['details'] == complex_details
        assert result['details']['changes']['guest_count']['from'] == 4
        assert result['details']['metadata']['ip_address'] == '192.168.1.1'


if __name__ == "__main__":
    pytest.main([__file__])
