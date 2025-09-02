"""
Tests for input validation utilities.
"""

import pytest
from datetime import datetime, timedelta

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.validators import (
    validate_email, validate_phone, validate_date_string,
    validate_booking_dates, validate_guest_count, validate_price,
    sanitize_input
)


class TestValidators:
    """Test cases for validation utilities."""
    
    def test_validate_email_valid(self):
        """Test valid email validation."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@456.com",
            "test_email@sub.domain.com"
        ]
        
        for email in valid_emails:
            assert validate_email(email) is True
    
    def test_validate_email_invalid(self):
        """Test invalid email validation."""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@.com",
            "",
            None,
            "test@example",
            "test space@example.com"
        ]
        
        for email in invalid_emails:
            assert validate_email(email) is False
    
    def test_validate_phone_valid(self):
        """Test valid phone number validation."""
        valid_phones = [
            "+1234567890",
            "+44 20 7946 0958",
            "+33 1 42 86 83 26",
            "+81-3-1234-5678",
            "+1 (555) 123-4567",
            "+49 30 12345678"
        ]
        
        for phone in valid_phones:
            assert validate_phone(phone) is True
    
    def test_validate_phone_invalid(self):
        """Test invalid phone number validation."""
        invalid_phones = [
            "123456",  # Too short
            "abc123def",  # Contains letters
            "123-456-7890",  # No country code
            "",
            None,
            "+1 123",  # Too short with country code
            "++1234567890"  # Double plus
        ]
        
        for phone in invalid_phones:
            assert validate_phone(phone) is False
    
    def test_validate_date_string_valid(self):
        """Test valid date string parsing."""
        valid_dates = [
            "2025-03-15",
            "2025-12-31",
            "2024-02-29",  # Leap year
            "2025-01-01"
        ]
        
        for date_str in valid_dates:
            result = validate_date_string(date_str)
            assert result is not None
            assert isinstance(result, datetime)
    
    def test_validate_date_string_invalid(self):
        """Test invalid date string parsing."""
        invalid_dates = [
            "2025-13-15",  # Invalid month
            "2025-02-30",  # Invalid day for February
            "2023-02-29",  # Not a leap year
            "invalid-date",
            "2025/03/15",  # Wrong format
            "",
            None,
            "2025-3-15",  # Single digit month
            "25-03-15"  # Wrong year format
        ]
        
        for date_str in invalid_dates:
            result = validate_date_string(date_str)
            assert result is None
    
    def test_validate_booking_dates_valid(self):
        """Test valid booking date validation."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        result = validate_booking_dates(tomorrow, day_after)
        
        assert result['valid'] is True
        assert 'check_in' in result
        assert 'check_out' in result
        assert 'nights' in result
        assert result['nights'] == 1
    
    def test_validate_booking_dates_past_checkin(self):
        """Test booking dates with past check-in."""
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        result = validate_booking_dates(yesterday, tomorrow)
        
        assert result['valid'] is False
        assert "past" in result['error'].lower()
    
    def test_validate_booking_dates_checkout_before_checkin(self):
        """Test booking dates with check-out before check-in."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        today = datetime.now().strftime("%Y-%m-%d")
        
        result = validate_booking_dates(tomorrow, today)
        
        assert result['valid'] is False
        assert "before" in result['error'].lower()
    
    def test_validate_booking_dates_same_day(self):
        """Test booking dates with same check-in and check-out."""
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        result = validate_booking_dates(tomorrow, tomorrow)
        
        assert result['valid'] is False
        assert "same day" in result['error'].lower()
    
    def test_validate_booking_dates_too_long(self):
        """Test booking dates exceeding maximum stay."""
        start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=32)).strftime("%Y-%m-%d")  # 31 nights
        
        result = validate_booking_dates(start_date, end_date)
        
        assert result['valid'] is False
        assert "30 nights" in result['error']
    
    def test_validate_booking_dates_invalid_format(self):
        """Test booking dates with invalid format."""
        result = validate_booking_dates("invalid-date", "2025-03-15")
        
        assert result['valid'] is False
        assert "format" in result['error'].lower()
    
    def test_validate_guest_count_valid(self):
        """Test valid guest count validation."""
        valid_counts = [1, 2, 4, 8, 12]
        
        for count in valid_counts:
            result = validate_guest_count(count)
            assert result['valid'] is True
            assert result['guests'] == count
    
    def test_validate_guest_count_zero(self):
        """Test guest count validation with zero guests."""
        result = validate_guest_count(0)
        
        assert result['valid'] is False
        assert "at least 1" in result['error']
    
    def test_validate_guest_count_negative(self):
        """Test guest count validation with negative guests."""
        result = validate_guest_count(-5)
        
        assert result['valid'] is False
        assert "at least 1" in result['error']
    
    def test_validate_guest_count_too_many(self):
        """Test guest count validation exceeding maximum."""
        result = validate_guest_count(25)  # Assuming max is 20
        
        assert result['valid'] is False
        assert "maximum" in result['error'].lower()
    
    def test_validate_price_valid(self):
        """Test valid price validation."""
        valid_prices = [50.0, 100.5, 1000.0, 2500.99]
        
        for price in valid_prices:
            result = validate_price(price)
            assert result['valid'] is True
            assert result['price'] == price
    
    def test_validate_price_zero(self):
        """Test price validation with zero price."""
        result = validate_price(0.0)
        
        assert result['valid'] is False
        assert "greater than 0" in result['error']
    
    def test_validate_price_negative(self):
        """Test price validation with negative price."""
        result = validate_price(-100.0)
        
        assert result['valid'] is False
        assert "greater than 0" in result['error']
    
    def test_validate_price_too_high(self):
        """Test price validation exceeding maximum."""
        result = validate_price(15000.0)  # Assuming max is 10000
        
        assert result['valid'] is False
        assert "maximum" in result['error'].lower()
    
    def test_sanitize_input_basic(self):
        """Test basic input sanitization."""
        test_cases = [
            ("Hello World", "Hello World"),
            ("  spaces  ", "spaces"),
            ("Multiple   spaces", "Multiple spaces"),
            ("", ""),
            ("NoChange", "NoChange")
        ]
        
        for input_text, expected in test_cases:
            result = sanitize_input(input_text)
            assert result == expected
    
    def test_sanitize_input_special_characters(self):
        """Test sanitization with special characters."""
        test_cases = [
            ("Hello<script>", "Hello"),  # Remove script tags
            ("Test & Co.", "Test & Co."),  # Keep safe characters
            ("Price: $100", "Price: $100"),  # Keep currency
            ("Email@domain.com", "Email@domain.com"),  # Keep email format
            ("Phone: +1-555-123", "Phone: +1-555-123")  # Keep phone format
        ]
        
        for input_text, expected in test_cases:
            result = sanitize_input(input_text)
            assert result == expected
    
    def test_sanitize_input_html_injection(self):
        """Test sanitization against HTML injection."""
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<iframe src='javascript:alert(1)'></iframe>"
        ]
        
        for malicious in malicious_inputs:
            result = sanitize_input(malicious)
            # Should not contain script tags or javascript
            assert "<script>" not in result.lower()
            assert "javascript:" not in result.lower()
            assert "<iframe>" not in result.lower()
    
    def test_sanitize_input_sql_injection(self):
        """Test sanitization against SQL injection patterns."""
        sql_patterns = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "UNION SELECT * FROM passwords",
            "'; DELETE FROM bookings; --"
        ]
        
        for pattern in sql_patterns:
            result = sanitize_input(pattern)
            # Should remove dangerous SQL keywords
            assert "DROP" not in result.upper()
            assert "DELETE" not in result.upper()
            assert "UNION" not in result.upper()
    
    def test_sanitize_input_none_and_empty(self):
        """Test sanitization with None and empty inputs."""
        assert sanitize_input(None) == ""
        assert sanitize_input("") == ""
        assert sanitize_input("   ") == ""
    
    def test_validate_booking_dates_edge_cases(self):
        """Test booking date validation edge cases."""
        # Test minimum stay (1 night)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        day_after = (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d")
        
        result = validate_booking_dates(tomorrow, day_after)
        assert result['valid'] is True
        assert result['nights'] == 1
        
        # Test maximum stay (30 nights)
        start_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=31)).strftime("%Y-%m-%d")  # 30 nights
        
        result = validate_booking_dates(start_date, end_date)
        assert result['valid'] is True
        assert result['nights'] == 30
    
    def test_validate_guest_count_edge_cases(self):
        """Test guest count validation edge cases."""
        # Test minimum guests (1)
        result = validate_guest_count(1)
        assert result['valid'] is True
        
        # Test maximum guests (assuming 20)
        result = validate_guest_count(20)
        assert result['valid'] is True
    
    def test_validate_price_edge_cases(self):
        """Test price validation edge cases."""
        # Test minimum price (just above 0)
        result = validate_price(0.01)
        assert result['valid'] is True
        
        # Test reasonable maximum price
        result = validate_price(10000.0)
        assert result['valid'] is True
    
    def test_validate_email_edge_cases(self):
        """Test email validation edge cases."""
        edge_cases = [
            ("a@b.co", True),  # Minimal valid email
            ("test@localhost", False),  # No TLD
            ("test@example.c", False),  # TLD too short
            ("test@example.com.", False),  # Trailing dot
            (".test@example.com", False),  # Leading dot
            ("test.@example.com", False),  # Trailing dot in local part
        ]
        
        for email, expected in edge_cases:
            assert validate_email(email) == expected
    
    def test_validate_phone_edge_cases(self):
        """Test phone validation edge cases."""
        edge_cases = [
            ("+1234567890", True),  # Minimal international format
            ("+123456789012345", True),  # Long but valid
            ("+12345", False),  # Too short
            ("+123456789012345678901", False),  # Too long
        ]
        
        for phone, expected in edge_cases:
            assert validate_phone(phone) == expected


if __name__ == "__main__":
    pytest.main([__file__])
