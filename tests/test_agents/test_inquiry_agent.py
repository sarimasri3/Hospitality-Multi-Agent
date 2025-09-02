"""
Tests for the Inquiry Agent.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agents.inquiry.tools import (
    validate_city, validate_dates, validate_guests, validate_budget,
    extract_slots_from_message, compile_session_slots
)


class TestInquiryAgentTools:
    """Test cases for Inquiry Agent tools."""
    
    @pytest.mark.asyncio
    async def test_validate_city_valid(self):
        """Test city validation with valid city."""
        result = await validate_city("Miami")
        assert result['valid'] is True
        assert result['normalized_city'] == "Miami"
        assert "wonderful destination" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_city_case_insensitive(self):
        """Test city validation is case insensitive."""
        result = await validate_city("miami")
        assert result['valid'] is True
        assert result['normalized_city'] == "Miami"
    
    @pytest.mark.asyncio
    async def test_validate_city_fuzzy_match(self):
        """Test city validation with fuzzy matching."""
        result = await validate_city("Los Angel")
        assert result['valid'] is True
        assert result['normalized_city'] == "Los Angeles"
        assert "match" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_city_invalid(self):
        """Test city validation with invalid city."""
        result = await validate_city("NonexistentCity")
        assert result['valid'] is False
        assert "couldn't find" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_dates_valid(self):
        """Test date validation with valid dates."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        day_after = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
        
        result = await validate_dates(tomorrow, day_after)
        assert result['valid'] is True
        assert result['nights'] == 3
        assert "3-night stay" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_dates_past_checkin(self):
        """Test date validation with past check-in date."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        result = await validate_dates(yesterday, tomorrow)
        assert result['valid'] is False
        assert "cannot be in the past" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_dates_checkout_before_checkin(self):
        """Test date validation with check-out before check-in."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        
        result = await validate_dates(tomorrow, today)
        assert result['valid'] is False
        assert "must be after check-in" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_dates_too_far_advance(self):
        """Test date validation with booking too far in advance."""
        far_future = (datetime.now() + timedelta(days=400)).strftime("%Y-%m-%d")
        even_further = (datetime.now() + timedelta(days=403)).strftime("%Y-%m-%d")
        
        result = await validate_dates(far_future, even_further)
        assert result['valid'] is False
        assert "365 days in advance" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_dates_too_long_stay(self):
        """Test date validation with stay longer than 30 nights."""
        start = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        end = (datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d")
        
        result = await validate_dates(start, end)
        assert result['valid'] is False
        assert "Maximum stay is 30 nights" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_dates_invalid_format(self):
        """Test date validation with invalid date format."""
        result = await validate_dates("2025/03/15", "2025/03/18")
        assert result['valid'] is False
        assert "Invalid date format" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_guests_valid(self):
        """Test guest validation with valid count."""
        result = await validate_guests(4)
        assert result['valid'] is True
        assert result['number_of_guests'] == 4
        assert "4 guests" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_guests_single(self):
        """Test guest validation with single guest."""
        result = await validate_guests(1)
        assert result['valid'] is True
        assert "1 guest" in result['message']
        assert "guests" not in result['message']  # Should be singular
    
    @pytest.mark.asyncio
    async def test_validate_guests_too_few(self):
        """Test guest validation with zero guests."""
        result = await validate_guests(0)
        assert result['valid'] is False
        assert "At least 1 guest" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_guests_too_many(self):
        """Test guest validation with too many guests."""
        result = await validate_guests(15)
        assert result['valid'] is False
        assert "accommodate up to 10 guests" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_budget_single_value(self):
        """Test budget validation with single value."""
        result = await validate_budget("500")
        assert result['valid'] is True
        assert result['max_budget'] == 500
        assert "up to $500" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_budget_with_currency(self):
        """Test budget validation with currency symbol."""
        result = await validate_budget("$750")
        assert result['valid'] is True
        assert result['max_budget'] == 750
    
    @pytest.mark.asyncio
    async def test_validate_budget_range(self):
        """Test budget validation with range."""
        result = await validate_budget("300-500")
        assert result['valid'] is True
        assert result['min_budget'] == 300
        assert result['max_budget'] == 500
        assert "between $300 and $500" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_budget_negative(self):
        """Test budget validation with negative value."""
        result = await validate_budget("-100")
        assert result['valid'] is False
        assert "positive amount" in result['message']
    
    @pytest.mark.asyncio
    async def test_validate_budget_invalid_format(self):
        """Test budget validation with invalid format."""
        result = await validate_budget("not a number")
        assert result['valid'] is False
        assert "couldn't understand" in result['message']
    
    @pytest.mark.asyncio
    async def test_extract_slots_from_message_dates(self):
        """Test slot extraction with dates."""
        message = "I need a place from 2025-03-15 to 2025-03-18"
        slots = await extract_slots_from_message(message)
        
        assert slots['check_in_date'] == "2025-03-15"
        assert slots['check_out_date'] == "2025-03-18"
    
    @pytest.mark.asyncio
    async def test_extract_slots_from_message_guests(self):
        """Test slot extraction with guest count."""
        message = "I need accommodation for 4 people"
        slots = await extract_slots_from_message(message)
        
        assert slots['number_of_guests'] == 4
    
    @pytest.mark.asyncio
    async def test_extract_slots_from_message_budget(self):
        """Test slot extraction with budget."""
        message = "My budget is around $500 per night"
        slots = await extract_slots_from_message(message)
        
        assert '$500' in slots['budget']
    
    @pytest.mark.asyncio
    async def test_extract_slots_from_message_city(self):
        """Test slot extraction with city."""
        message = "I want to stay in Miami"
        slots = await extract_slots_from_message(message)
        
        assert slots['city'] == "Miami"
    
    @pytest.mark.asyncio
    async def test_extract_slots_comprehensive(self):
        """Test comprehensive slot extraction."""
        message = "I need a villa in Miami from 2025-03-15 to 2025-03-18 for 4 people, budget around $500"
        slots = await extract_slots_from_message(message)
        
        assert slots['city'] == "Miami"
        assert slots['check_in_date'] == "2025-03-15"
        assert slots['check_out_date'] == "2025-03-18"
        assert slots['number_of_guests'] == 4
        assert '$500' in slots['budget']
    
    @pytest.mark.asyncio
    async def test_compile_session_slots_merge(self):
        """Test session slot compilation and merging."""
        existing = {'city': 'Miami', 'number_of_guests': 2}
        new = {'check_in_date': '2025-03-15', 'number_of_guests': 4}
        
        merged = await compile_session_slots(existing, new)
        
        assert merged['city'] == 'Miami'
        assert merged['number_of_guests'] == 4  # New value overrides
        assert merged['check_in_date'] == '2025-03-15'
    
    @pytest.mark.asyncio
    async def test_compile_session_slots_completeness(self):
        """Test session slot completeness checking."""
        complete_slots = {
            'city': 'Miami',
            'check_in_date': '2025-03-15',
            'check_out_date': '2025-03-18',
            'number_of_guests': 4
        }
        
        merged = await compile_session_slots({}, complete_slots)
        
        assert merged['_complete'] is True
        assert len(merged['_missing']) == 0
    
    @pytest.mark.asyncio
    async def test_compile_session_slots_incomplete(self):
        """Test session slot incompleteness detection."""
        incomplete_slots = {
            'city': 'Miami',
            'number_of_guests': 4
        }
        
        merged = await compile_session_slots({}, incomplete_slots)
        
        assert merged['_complete'] is False
        assert 'check_in_date' in merged['_missing']
        assert 'check_out_date' in merged['_missing']


if __name__ == "__main__":
    pytest.main([__file__])
