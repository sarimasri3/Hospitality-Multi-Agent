"""
Tests for Long-term Memory management.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from memory.long_term import LongTermMemory


class TestLongTermMemory:
    """Test cases for LongTermMemory."""
    
    @pytest.fixture
    def ltm(self):
        """Create LTM instance for testing."""
        return LongTermMemory()
    
    @pytest.mark.asyncio
    async def test_get_user_profile_nonexistent(self, ltm):
        """Test getting non-existent user profile."""
        profile = await ltm.get_user_profile("nonexistent_user")
        assert profile is None
    
    @pytest.mark.asyncio
    async def test_update_user_profile_new(self, ltm):
        """Test updating profile for new user."""
        user_id = "user_001"
        profile_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'phone': '+1234567890'
        }
        
        success = await ltm.update_user_profile(user_id, profile_data)
        assert success is True
        
        # Verify profile was created
        profile = await ltm.get_user_profile(user_id)
        assert profile['user_id'] == user_id
        assert profile['name'] == 'John Doe'
        assert profile['email'] == 'john@example.com'
        assert profile['phone'] == '+1234567890'
        assert 'created_at' in profile
        assert 'updated_at' in profile
    
    @pytest.mark.asyncio
    async def test_update_user_profile_existing(self, ltm):
        """Test updating existing user profile."""
        user_id = "user_002"
        
        # Create initial profile
        await ltm.update_user_profile(user_id, {'name': 'Jane Doe'})
        
        # Update profile
        await ltm.update_user_profile(user_id, {
            'name': 'Jane Smith',
            'email': 'jane.smith@example.com'
        })
        
        # Verify update
        profile = await ltm.get_user_profile(user_id)
        assert profile['name'] == 'Jane Smith'
        assert profile['email'] == 'jane.smith@example.com'
        assert 'updated_at' in profile
    
    @pytest.mark.asyncio
    async def test_get_user_preferences_new_user(self, ltm):
        """Test getting preferences for new user."""
        preferences = await ltm.get_user_preferences("new_user")
        
        # Should return default empty preferences
        assert preferences['preferred_cities'] == []
        assert preferences['average_budget'] is None
        assert preferences['typical_guests'] is None
        assert preferences['favorite_amenities'] == []
        assert preferences['preferred_property_types'] == []
        assert preferences['typical_stay_length'] is None
        assert preferences['frequently_selected_addons'] == []
    
    @pytest.mark.asyncio
    async def test_update_user_preferences_city(self, ltm):
        """Test updating user preferences with city data."""
        user_id = "user_003"
        booking_data = {
            'city': 'Miami',
            'max_price': 500,
            'number_of_guests': 4
        }
        
        success = await ltm.update_user_preferences(user_id, booking_data)
        assert success is True
        
        preferences = await ltm.get_user_preferences(user_id)
        assert 'Miami' in preferences['preferred_cities']
        assert preferences['average_budget'] == 500
        assert preferences['typical_guests'] == 4
    
    @pytest.mark.asyncio
    async def test_update_user_preferences_amenities(self, ltm):
        """Test updating user preferences with amenity data."""
        user_id = "user_004"
        booking_data = {
            'amenities': ['pool', 'wifi', 'parking']
        }
        
        await ltm.update_user_preferences(user_id, booking_data)
        
        preferences = await ltm.get_user_preferences(user_id)
        assert 'pool' in preferences['favorite_amenities']
        assert 'wifi' in preferences['favorite_amenities']
        assert 'parking' in preferences['favorite_amenities']
    
    @pytest.mark.asyncio
    async def test_update_user_preferences_addons(self, ltm):
        """Test updating user preferences with add-on data."""
        user_id = "user_005"
        
        # First booking with add-ons
        await ltm.update_user_preferences(user_id, {
            'add_ons': ['early_checkin', 'welcome_basket']
        })
        
        # Second booking with same add-on (should become frequent)
        await ltm.update_user_preferences(user_id, {
            'add_ons': ['early_checkin', 'spa_package']
        })
        
        preferences = await ltm.get_user_preferences(user_id)
        assert 'early_checkin' in preferences['frequently_selected_addons']
    
    @pytest.mark.asyncio
    async def test_update_user_preferences_multiple_cities(self, ltm):
        """Test preferences with multiple city bookings."""
        user_id = "user_006"
        
        # Book in different cities
        await ltm.update_user_preferences(user_id, {'city': 'Miami'})
        await ltm.update_user_preferences(user_id, {'city': 'Los Angeles'})
        await ltm.update_user_preferences(user_id, {'city': 'Miami'})  # Repeat
        
        preferences = await ltm.get_user_preferences(user_id)
        assert 'Miami' in preferences['preferred_cities']
        assert 'Los Angeles' in preferences['preferred_cities']
        assert len(preferences['preferred_cities']) == 2
    
    @pytest.mark.asyncio
    async def test_update_user_preferences_budget_averaging(self, ltm):
        """Test budget averaging across bookings."""
        user_id = "user_007"
        
        # Multiple bookings with different budgets
        await ltm.update_user_preferences(user_id, {'max_price': 300})
        await ltm.update_user_preferences(user_id, {'max_price': 500})
        await ltm.update_user_preferences(user_id, {'max_price': 400})
        
        preferences = await ltm.get_user_preferences(user_id)
        assert preferences['average_budget'] == 400  # (300 + 500 + 400) / 3
    
    @pytest.mark.asyncio
    async def test_update_user_preferences_typical_guests(self, ltm):
        """Test typical guest count calculation."""
        user_id = "user_008"
        
        # Multiple bookings with different guest counts
        await ltm.update_user_preferences(user_id, {'number_of_guests': 2})
        await ltm.update_user_preferences(user_id, {'number_of_guests': 4})
        await ltm.update_user_preferences(user_id, {'number_of_guests': 4})
        await ltm.update_user_preferences(user_id, {'number_of_guests': 2})
        
        preferences = await ltm.get_user_preferences(user_id)
        # Should be 2 or 4 (most common), implementation uses max with count
        assert preferences['typical_guests'] in [2, 4]
    
    @pytest.mark.asyncio
    async def test_add_booking_to_history(self, ltm):
        """Test adding booking to user history."""
        user_id = "user_009"
        booking = {
            'booking_id': 'booking_001',
            'property_id': 'prop_001',
            'city': 'Miami',
            'total_price': 1200,
            'status': 'confirmed'
        }
        
        success = await ltm.add_booking_to_history(user_id, booking)
        assert success is True
        
        history = await ltm.get_booking_history(user_id)
        assert len(history) == 1
        assert history[0]['booking_id'] == 'booking_001'
        assert 'added_to_history' in history[0]
    
    @pytest.mark.asyncio
    async def test_add_booking_to_history_limit(self, ltm):
        """Test booking history limit enforcement."""
        user_id = "user_010"
        
        # Add 55 bookings (more than 50 limit)
        for i in range(55):
            booking = {
                'booking_id': f'booking_{i:03d}',
                'property_id': f'prop_{i:03d}',
                'total_price': 1000 + i
            }
            await ltm.add_booking_to_history(user_id, booking)
        
        history = await ltm.get_booking_history(user_id, limit=100)
        assert len(history) == 50  # Should be limited to 50
        assert history[0]['booking_id'] == 'booking_005'  # First 5 should be dropped
        assert history[-1]['booking_id'] == 'booking_054'
    
    @pytest.mark.asyncio
    async def test_get_booking_history_with_limit(self, ltm):
        """Test getting booking history with custom limit."""
        user_id = "user_011"
        
        # Add 20 bookings
        for i in range(20):
            booking = {'booking_id': f'booking_{i:03d}'}
            await ltm.add_booking_to_history(user_id, booking)
        
        # Get limited history
        history = await ltm.get_booking_history(user_id, limit=5)
        assert len(history) == 5
        assert history[-1]['booking_id'] == 'booking_019'  # Most recent
    
    @pytest.mark.asyncio
    async def test_get_booking_history_empty(self, ltm):
        """Test getting booking history for user with no bookings."""
        history = await ltm.get_booking_history("user_no_bookings")
        assert history == []
    
    @pytest.mark.asyncio
    async def test_get_personalization_context_new_user(self, ltm):
        """Test personalization context for new user."""
        context = await ltm.get_personalization_context("new_user")
        
        assert context['preferences']['preferred_cities'] == []
        assert context['recent_bookings'] == []
        assert context['insights']['is_repeat_customer'] is False
        assert context['insights']['booking_count'] == 0
        assert context['insights']['favorite_city'] is None
        assert context['insights']['average_budget'] is None
        assert context['insights']['typical_party_size'] is None
        assert context['insights']['prefers_addons'] is False
    
    @pytest.mark.asyncio
    async def test_get_personalization_context_existing_user(self, ltm):
        """Test personalization context for existing user."""
        user_id = "user_012"
        
        # Add some booking history and preferences
        booking1 = {
            'city': 'Miami',
            'max_price': 500,
            'number_of_guests': 4,
            'add_ons': ['early_checkin']
        }
        booking2 = {
            'city': 'Miami',
            'max_price': 600,
            'number_of_guests': 4,
            'add_ons': ['early_checkin', 'welcome_basket']
        }
        
        await ltm.add_booking_to_history(user_id, booking1)
        await ltm.add_booking_to_history(user_id, booking2)
        
        context = await ltm.get_personalization_context(user_id)
        
        assert context['insights']['is_repeat_customer'] is True
        assert context['insights']['booking_count'] == 2
        assert context['insights']['favorite_city'] == 'Miami'
        assert context['insights']['average_budget'] == 550  # (500 + 600) / 2
        assert context['insights']['typical_party_size'] == 4
        assert context['insights']['prefers_addons'] is True
        assert len(context['recent_bookings']) == 2
    
    @pytest.mark.asyncio
    async def test_preferences_update_triggers_from_booking_history(self, ltm):
        """Test that adding to booking history updates preferences."""
        user_id = "user_013"
        
        booking = {
            'city': 'Paris',
            'max_price': 800,
            'number_of_guests': 2,
            'amenities': ['wifi', 'breakfast'],
            'add_ons': ['late_checkout']
        }
        
        await ltm.add_booking_to_history(user_id, booking)
        
        # Check that preferences were updated
        preferences = await ltm.get_user_preferences(user_id)
        assert 'Paris' in preferences['preferred_cities']
        assert preferences['average_budget'] == 800
        assert preferences['typical_guests'] == 2
        assert 'wifi' in preferences['favorite_amenities']
        assert 'breakfast' in preferences['favorite_amenities']
    
    @pytest.mark.asyncio
    async def test_amenity_frequency_tracking(self, ltm):
        """Test amenity frequency tracking across bookings."""
        user_id = "user_014"
        
        # Multiple bookings with overlapping amenities
        bookings = [
            {'amenities': ['wifi', 'pool', 'parking']},
            {'amenities': ['wifi', 'gym', 'pool']},
            {'amenities': ['wifi', 'spa', 'pool']},
            {'amenities': ['wifi', 'restaurant']}
        ]
        
        for booking in bookings:
            await ltm.update_user_preferences(user_id, booking)
        
        preferences = await ltm.get_user_preferences(user_id)
        
        # wifi should be #1 (4 times), pool should be #2 (3 times)
        assert preferences['favorite_amenities'][0] == 'wifi'
        assert preferences['favorite_amenities'][1] == 'pool'
        assert len(preferences['favorite_amenities']) <= 5  # Limited to top 5


if __name__ == "__main__":
    pytest.main([__file__])
