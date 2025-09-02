"""
Tests for response formatting utilities.
"""

import pytest
from datetime import datetime
from decimal import Decimal

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.formatters import (
    format_currency, format_date, format_property_card,
    format_booking_summary, format_price_breakdown,
    format_error_message, format_success_message
)


class TestFormatters:
    """Test cases for formatting utilities."""
    
    def test_format_currency_usd_default(self):
        """Test USD currency formatting (default)."""
        test_cases = [
            (100.0, "$100.00"),
            (1234.56, "$1,234.56"),
            (0.99, "$0.99"),
            (1000000.0, "$1,000,000.00"),
            (0.0, "$0.00")
        ]
        
        for amount, expected in test_cases:
            result = format_currency(amount)
            assert result == expected
    
    def test_format_currency_different_currencies(self):
        """Test formatting with different currencies."""
        test_cases = [
            (100.0, "EUR", "€100.00"),
            (1234.56, "GBP", "£1,234.56"),
            (500.0, "JPY", "¥500.00"),
            (299.99, "CAD", "CA$299.99")
        ]
        
        for amount, currency, expected in test_cases:
            result = format_currency(amount, currency)
            assert result == expected
    
    def test_format_currency_edge_cases(self):
        """Test currency formatting edge cases."""
        # Very large amounts
        result = format_currency(999999999.99)
        assert "999,999,999.99" in result
        
        # Very small amounts
        result = format_currency(0.01)
        assert result == "$0.01"
        
        # Negative amounts (shouldn't happen in booking context but test anyway)
        result = format_currency(-100.0)
        assert "-$100.00" in result or "$-100.00" in result
    
    def test_format_date_long_format(self):
        """Test long date formatting."""
        test_date = datetime(2025, 3, 15, 14, 30, 0)
        
        result = format_date(test_date, "long")
        assert "March" in result
        assert "15" in result
        assert "2025" in result
    
    def test_format_date_short_format(self):
        """Test short date formatting."""
        test_date = datetime(2025, 3, 15, 14, 30, 0)
        
        result = format_date(test_date, "short")
        assert result == "2025-03-15"
    
    def test_format_date_display_format(self):
        """Test display date formatting."""
        test_date = datetime(2025, 3, 15, 14, 30, 0)
        
        result = format_date(test_date, "display")
        assert "Mar" in result
        assert "15" in result
        assert "2025" in result
    
    def test_format_date_time_format(self):
        """Test date with time formatting."""
        test_date = datetime(2025, 3, 15, 14, 30, 0)
        
        result = format_date(test_date, "time")
        assert "2:30" in result or "14:30" in result
        assert "PM" in result or "14:30" in result
    
    def test_format_property_card_complete(self):
        """Test property card formatting with complete data."""
        property_data = {
            'name': 'Luxury Beach Villa',
            'location': {
                'city': 'Miami',
                'country': 'USA'
            },
            'guest_space': 8,
            'minimum_price': 350.0,
            'amenities': ['pool', 'wifi', 'parking', 'beach_access'],
            'property_type': 'villa',
            'description': 'Beautiful oceanfront villa with stunning views'
        }
        
        result = format_property_card(property_data)
        
        assert "Luxury Beach Villa" in result
        assert "Miami, USA" in result
        assert "8 guests" in result
        assert "$350.00" in result
        assert "pool" in result.lower()
        assert "wifi" in result.lower()
        assert "villa" in result.lower()
    
    def test_format_property_card_minimal(self):
        """Test property card formatting with minimal data."""
        property_data = {
            'name': 'Simple Apartment',
            'location': {'city': 'New York'},
            'guest_space': 2,
            'minimum_price': 150.0
        }
        
        result = format_property_card(property_data)
        
        assert "Simple Apartment" in result
        assert "New York" in result
        assert "2 guests" in result
        assert "$150.00" in result
    
    def test_format_property_card_missing_fields(self):
        """Test property card formatting with missing fields."""
        property_data = {
            'name': 'Test Property'
        }
        
        result = format_property_card(property_data)
        
        # Should handle missing fields gracefully
        assert "Test Property" in result
        assert result is not None
        assert len(result) > 0
    
    def test_format_booking_summary_complete(self):
        """Test booking summary formatting with complete data."""
        booking = {
            'booking_id': 'BK123456',
            'property_name': 'Ocean View Villa',
            'location': {
                'city': 'Malibu',
                'country': 'USA'
            },
            'check_in_date': '2025-03-15',
            'check_out_date': '2025-03-18',
            'number_of_guests': 6,
            'total_price': 1800.0,
            'status': 'confirmed',
            'guest_name': 'John Doe',
            'guest_email': 'john@example.com'
        }
        
        result = format_booking_summary(booking)
        
        assert "BK123456" in result
        assert "Ocean View Villa" in result
        assert "Malibu, USA" in result
        assert "March 15" in result or "2025-03-15" in result
        assert "6 guests" in result
        assert "$1,800.00" in result
        assert "confirmed" in result.lower()
        assert "John Doe" in result
    
    def test_format_booking_summary_minimal(self):
        """Test booking summary with minimal data."""
        booking = {
            'booking_id': 'BK789',
            'total_price': 500.0,
            'status': 'pending'
        }
        
        result = format_booking_summary(booking)
        
        assert "BK789" in result
        assert "$500.00" in result
        assert "pending" in result.lower()
    
    def test_format_price_breakdown_complete(self):
        """Test complete price breakdown formatting."""
        result = format_price_breakdown(
            accommodation=1000.0,
            service_fee=150.0,
            cleaning_fee=75.0,
            tax=125.0,
            add_ons=50.0
        )
        
        assert "$1,000.00" in result  # Accommodation
        assert "$150.00" in result   # Service fee
        assert "$75.00" in result    # Cleaning fee
        assert "$125.00" in result   # Tax
        assert "$50.00" in result    # Add-ons
        assert "$1,400.00" in result # Total
        
        # Check structure
        assert "Accommodation" in result
        assert "Service Fee" in result
        assert "Cleaning Fee" in result
        assert "Tax" in result
        assert "Add-ons" in result
        assert "Total" in result
    
    def test_format_price_breakdown_no_addons(self):
        """Test price breakdown without add-ons."""
        result = format_price_breakdown(
            accommodation=800.0,
            service_fee=120.0,
            cleaning_fee=60.0,
            tax=98.0
        )
        
        assert "$800.00" in result
        assert "$120.00" in result
        assert "$60.00" in result
        assert "$98.00" in result
        assert "$1,078.00" in result  # Total without add-ons
        
        # Should not include add-ons line
        assert "Add-ons" not in result or "$0.00" in result
    
    def test_format_price_breakdown_zero_fees(self):
        """Test price breakdown with zero fees."""
        result = format_price_breakdown(
            accommodation=500.0,
            service_fee=0.0,
            cleaning_fee=0.0,
            tax=0.0
        )
        
        assert "$500.00" in result  # Accommodation
        assert "$500.00" in result  # Total (should appear twice)
    
    def test_format_error_message_with_details(self):
        """Test error message formatting with details."""
        result = format_error_message("INVALID_DATE", "Check-in date must be in the future")
        
        assert "error" in result.lower() or "invalid" in result.lower()
        assert "date" in result.lower()
        assert "future" in result.lower()
    
    def test_format_error_message_without_details(self):
        """Test error message formatting without details."""
        result = format_error_message("BOOKING_FAILED")
        
        assert "error" in result.lower() or "failed" in result.lower()
        assert "booking" in result.lower()
    
    def test_format_error_message_common_codes(self):
        """Test error message formatting for common error codes."""
        test_cases = [
            ("PROPERTY_NOT_FOUND", "property"),
            ("INVALID_GUESTS", "guest"),
            ("PAYMENT_FAILED", "payment"),
            ("BOOKING_CONFLICT", "conflict"),
            ("VALIDATION_ERROR", "validation")
        ]
        
        for error_code, expected_word in test_cases:
            result = format_error_message(error_code)
            assert expected_word.lower() in result.lower()
    
    def test_format_success_message_with_details(self):
        """Test success message formatting with details."""
        result = format_success_message("BOOKING_CREATED", "Your reservation BK123456 has been confirmed")
        
        assert "success" in result.lower() or "confirmed" in result.lower()
        assert "BK123456" in result
        assert "reservation" in result.lower()
    
    def test_format_success_message_without_details(self):
        """Test success message formatting without details."""
        result = format_success_message("PAYMENT_PROCESSED")
        
        assert "success" in result.lower() or "processed" in result.lower()
        assert "payment" in result.lower()
    
    def test_format_success_message_common_actions(self):
        """Test success message formatting for common actions."""
        test_cases = [
            ("BOOKING_CONFIRMED", "booking"),
            ("PAYMENT_COMPLETED", "payment"),
            ("EMAIL_SENT", "email"),
            ("PROFILE_UPDATED", "profile"),
            ("SEARCH_COMPLETED", "search")
        ]
        
        for action, expected_word in test_cases:
            result = format_success_message(action)
            assert expected_word.lower() in result.lower()
    
    def test_format_date_edge_cases(self):
        """Test date formatting edge cases."""
        # New Year's Day
        new_years = datetime(2025, 1, 1, 0, 0, 0)
        result = format_date(new_years, "long")
        assert "January" in result
        assert "1" in result
        assert "2025" in result
        
        # Leap year date
        leap_day = datetime(2024, 2, 29, 12, 0, 0)
        result = format_date(leap_day, "short")
        assert result == "2024-02-29"
        
        # End of year
        new_years_eve = datetime(2025, 12, 31, 23, 59, 59)
        result = format_date(new_years_eve, "display")
        assert "Dec" in result
        assert "31" in result
    
    def test_format_property_card_amenities_formatting(self):
        """Test property card amenities formatting."""
        property_data = {
            'name': 'Test Villa',
            'amenities': ['wifi', 'pool', 'parking', 'gym', 'spa', 'beach_access']
        }
        
        result = format_property_card(property_data)
        
        # Should format amenities nicely
        assert "wifi" in result.lower() or "wi-fi" in result.lower()
        assert "pool" in result.lower()
        assert "parking" in result.lower()
        
        # Should handle long amenity lists appropriately
        assert len(result) > 0
    
    def test_format_booking_summary_date_formatting(self):
        """Test booking summary date formatting."""
        booking = {
            'booking_id': 'BK123',
            'check_in_date': '2025-03-15',
            'check_out_date': '2025-03-18',
            'total_price': 900.0
        }
        
        result = format_booking_summary(booking)
        
        # Should format dates in a readable way
        assert "2025" in result
        assert ("March" in result or "Mar" in result or "03" in result)
        assert "15" in result
        assert "18" in result
    
    def test_format_currency_precision(self):
        """Test currency formatting precision."""
        test_cases = [
            (99.999, "$100.00"),  # Should round up
            (99.991, "$99.99"),   # Should round down
            (100.005, "$100.01"), # Should round up
            (100.004, "$100.00")  # Should round down
        ]
        
        for amount, expected in test_cases:
            result = format_currency(amount)
            assert result == expected
    
    def test_format_property_card_guest_space_formatting(self):
        """Test property card guest space formatting."""
        test_cases = [
            ({'guest_space': 1}, "1 guest"),
            ({'guest_space': 2}, "2 guests"),
            ({'guest_space': 10}, "10 guests")
        ]
        
        for property_data, expected in test_cases:
            property_data['name'] = 'Test Property'
            result = format_property_card(property_data)
            assert expected in result


if __name__ == "__main__":
    pytest.main([__file__])
