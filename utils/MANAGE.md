# Utils Directory Management

## Purpose & Responsibilities

The `utils/` directory provides **shared utility functions** for input validation, response formatting, and common operations used across the hospitality booking system. These utilities ensure consistency, data integrity, and proper formatting throughout the application.

## Directory Structure

```
utils/
├── __init__.py              # Package initialization
├── validators.py           # Input validation utilities
└── formatters.py           # Response formatting utilities
```

## Core Components

### Input Validators (`validators.py`)

**Purpose**: Centralized validation functions for data integrity

**Key Functions**:
```python
def validate_email(email: str) -> bool
# Validates email format using regex pattern
# Returns: True if valid email format

def validate_phone(phone: str) -> bool  
# Validates phone number format (international/domestic)
# Returns: True if valid phone format

def validate_date_range(start_date: str, end_date: str) -> Dict[str, Any]
# Validates date range and calculates nights
# Returns: Validation result with parsed dates

def validate_price(price: float, min_price: float = 0) -> Dict[str, Any]
# Validates price values and ranges
# Returns: Validation result with normalized price

def sanitize_input(input_string: str) -> str
# Sanitizes user input to prevent injection attacks
# Returns: Cleaned input string

def validate_coordinates(lat: float, lng: float) -> bool
# Validates latitude/longitude coordinates
# Returns: True if valid coordinates
```

**Validation Patterns**:
- **Email**: RFC-compliant regex pattern
- **Phone**: International format support (+1-555-123-4567)
- **Dates**: ISO format validation with business rule checks
- **Prices**: Positive values with currency support
- **Coordinates**: Valid lat/lng ranges

### Response Formatters (`formatters.py`)

**Purpose**: Consistent response formatting across agents and components

**Key Functions**:
```python
def format_currency(amount: float, currency: str = "USD") -> str
# Formats monetary amounts with currency symbols
# Supports: USD ($), EUR (€), GBP (£), JPY (¥)

def format_date(date_obj: datetime, format_type: str = "friendly") -> str
# Formats dates for user display
# Types: "friendly", "iso", "short", "long"

def format_property_summary(property_data: Dict) -> str
# Formats property information for agent responses
# Returns: Structured property description

def format_booking_confirmation(booking_data: Dict) -> str
# Formats booking confirmation details
# Returns: Complete confirmation message

def format_price_breakdown(pricing: Dict) -> str
# Formats detailed price breakdown
# Returns: Itemized pricing display

def format_error_message(error_type: str, context: Dict = None) -> str
# Formats user-friendly error messages
# Returns: Contextual error message
```

**Formatting Standards**:
- **Currency**: Localized symbols and comma separators
- **Dates**: Human-readable formats with timezone awareness
- **Properties**: Consistent structure with key highlights
- **Errors**: User-friendly language with actionable guidance

## How to Use & Extend

### Using Validators

**In Agent Tools**:
```python
from utils.validators import validate_email, validate_date_range

async def create_user_tool(email: str, check_in: str, check_out: str):
    # Validate email
    if not validate_email(email):
        return {"error": "Invalid email format"}
    
    # Validate dates
    date_result = validate_date_range(check_in, check_out)
    if not date_result["valid"]:
        return {"error": date_result["message"]}
    
    # Continue with validated data
    return {"success": True}
```

**In MCP Servers**:
```python
from utils.validators import validate_coordinates, sanitize_input

async def create_property(name: str, lat: float, lng: float):
    # Sanitize input
    clean_name = sanitize_input(name)
    
    # Validate coordinates
    if not validate_coordinates(lat, lng):
        return {"error": "Invalid coordinates"}
    
    # Process with clean data
```

### Using Formatters

**In Agent Responses**:
```python
from utils.formatters import format_currency, format_property_summary

async def present_properties(properties: List[Dict]):
    formatted_properties = []
    for prop in properties:
        summary = format_property_summary(prop)
        price = format_currency(prop["price"])
        formatted_properties.append(f"{summary}\nPrice: {price}")
    
    return "\n\n".join(formatted_properties)
```

**In Confirmation Messages**:
```python
from utils.formatters import format_booking_confirmation

async def send_confirmation(booking_data: Dict):
    confirmation = format_booking_confirmation(booking_data)
    # Send via email/SMS
    return confirmation
```

### Adding New Utilities

**New Validator**:
```python
# In validators.py
def validate_guest_count(count: int, max_guests: int = 10) -> Dict[str, Any]:
    """
    Validate number of guests for booking.
    
    Args:
        count: Number of guests
        max_guests: Maximum allowed guests
    
    Returns:
        Validation result
    """
    if count < 1:
        return {
            "valid": False,
            "message": "At least 1 guest required"
        }
    
    if count > max_guests:
        return {
            "valid": False,
            "message": f"Maximum {max_guests} guests allowed"
        }
    
    return {
        "valid": True,
        "normalized_count": count,
        "message": f"Valid guest count: {count}"
    }
```

**New Formatter**:
```python
# In formatters.py
def format_amenity_list(amenities: List[str], max_display: int = 5) -> str:
    """
    Format amenity list for display.
    
    Args:
        amenities: List of amenity names
        max_display: Maximum amenities to show
    
    Returns:
        Formatted amenity string
    """
    if not amenities:
        return "No amenities listed"
    
    displayed = amenities[:max_display]
    formatted = ", ".join(displayed)
    
    if len(amenities) > max_display:
        remaining = len(amenities) - max_display
        formatted += f" and {remaining} more"
    
    return formatted
```

## Configuration & Standards

### Validation Rules

**Business Rules** (from `config/settings.py`):
```python
# Date validation
MIN_BOOKING_DAYS = 1
MAX_BOOKING_DAYS = 30
BOOKING_ADVANCE_DAYS = 365

# Guest validation
MAX_GUESTS_PER_BOOKING = 10

# Price validation
MIN_PROPERTY_PRICE = 50.0
MAX_PROPERTY_PRICE = 10000.0
```

**Regex Patterns**:
```python
EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
PHONE_PATTERN = r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'
DATE_PATTERN = r'^\d{4}-\d{2}-\d{2}$'
```

### Formatting Standards

**Currency Formatting**:
```python
CURRENCY_SYMBOLS = {
    "USD": "$",
    "EUR": "€", 
    "GBP": "£",
    "JPY": "¥"
}

# Format: $1,234.56
def format_currency(amount, currency="USD"):
    symbol = CURRENCY_SYMBOLS.get(currency, currency + " ")
    return f"{symbol}{amount:,.2f}"
```

**Date Formatting**:
```python
DATE_FORMATS = {
    "friendly": "%B %d, %Y",      # March 15, 2025
    "short": "%m/%d/%Y",          # 03/15/2025
    "iso": "%Y-%m-%d",            # 2025-03-15
    "long": "%A, %B %d, %Y"       # Monday, March 15, 2025
}
```

## Integration with Other Directories

### → `agents/`
- **Input Validation**: Agents use validators in tool functions
- **Response Formatting**: Agents use formatters for consistent output
- **Error Handling**: Standardized error message formatting

### → `mcp_servers/`
- **Data Validation**: MCP tools validate inputs before database operations
- **Response Formatting**: Consistent data formatting in MCP responses
- **Security**: Input sanitization prevents injection attacks

### → `orchestrator/`
- **Request Validation**: Validates user inputs before agent processing
- **Response Formatting**: Formats final responses to users
- **Error Handling**: Standardized error responses

### → `memory/`
- **Data Validation**: Validates session and profile data
- **Data Formatting**: Consistent data structure formatting
- **Sanitization**: Cleans user data before storage

## Testing & Quality Assurance

### Unit Testing

**Validator Tests**:
```python
import pytest
from utils.validators import validate_email, validate_date_range

def test_email_validation():
    assert validate_email("user@example.com") == True
    assert validate_email("invalid-email") == False

def test_date_range_validation():
    result = validate_date_range("2025-03-15", "2025-03-18")
    assert result["valid"] == True
    assert result["nights"] == 3
```

**Formatter Tests**:
```python
from utils.formatters import format_currency, format_date

def test_currency_formatting():
    assert format_currency(1234.56) == "$1,234.56"
    assert format_currency(1000, "EUR") == "€1,000.00"

def test_date_formatting():
    date_obj = datetime(2025, 3, 15)
    assert format_date(date_obj, "friendly") == "March 15, 2025"
```

### Performance Considerations

**Validation Optimization**:
- **Regex Compilation**: Pre-compile regex patterns
- **Caching**: Cache validation results for repeated inputs
- **Early Returns**: Fail fast on invalid inputs

**Formatting Optimization**:
- **String Templates**: Use format strings for performance
- **Lazy Loading**: Load formatting data on demand
- **Memoization**: Cache formatted results

## Troubleshooting

### Common Issues

1. **Validation Failures**
   ```python
   # Debug validation
   from utils.validators import validate_email
   
   email = "test@example.com"
   result = validate_email(email)
   print(f"Email '{email}' valid: {result}")
   ```

2. **Formatting Errors**
   ```python
   # Debug formatting
   from utils.formatters import format_currency
   
   try:
       formatted = format_currency(amount)
       print(f"Formatted: {formatted}")
   except Exception as e:
       print(f"Formatting error: {e}")
   ```

3. **Import Issues**
   ```python
   # Test imports
   try:
       from utils.validators import validate_email
       from utils.formatters import format_currency
       print("Utils imported successfully")
   except ImportError as e:
       print(f"Import error: {e}")
   ```

### Debug Commands

```python
# Test all validators
from utils.validators import *

test_cases = [
    ("email", validate_email, "test@example.com"),
    ("phone", validate_phone, "+1-555-123-4567"),
    ("dates", validate_date_range, ("2025-03-15", "2025-03-18"))
]

for name, func, args in test_cases:
    try:
        if isinstance(args, tuple):
            result = func(*args)
        else:
            result = func(args)
        print(f"{name}: {result}")
    except Exception as e:
        print(f"{name} error: {e}")
```

## Testing

### Test Coverage
- **Test Files**: 
  - `tests/test_utils/test_validators.py` - Input validation functions, edge cases, security
  - `tests/test_utils/test_formatters.py` - Response formatting, currency, dates, properties
- **Coverage**: Validation logic, formatting functions, error handling
- **Test Types**: Unit tests, edge case tests, security tests

### Running Tests
```bash
# Run all utils tests
pytest tests/test_utils/ -v

# Run specific util tests
pytest tests/test_utils/test_validators.py -v

# Run with coverage
pytest tests/test_utils/ --cov=utils --cov-report=html
```

### Test Scenarios Covered
- Email and phone validation with edge cases
- Date validation and business rule enforcement
- Price validation and range checking
- Input sanitization and security
- Currency formatting with multiple currencies
- Date formatting in various styles
- Property and booking summary formatting

## Related Tasks

### High Priority
- **Production Deployment** (TASK_PLAN.md #1): Ensure validation rules match production requirements
- **Advanced Security** (TASK_PLAN.md #9): Enhance input sanitization and validation
- **Error Handling Enhancement** (TASK_PLAN.md #2): Improve validation error messages

### Medium Priority
- **User Experience Enhancement** (TASK_PLAN.md #6): Add multi-language formatting support
- **Enhanced Property Management** (TASK_PLAN.md #5): Extend property formatting capabilities

### Ongoing
- **Code Quality** (TASK_PLAN.md #10): Optimize validation and formatting performance
- **Testing QA** (TASK_PLAN.md #11): Expand utility function test coverage

---

**Next Steps**: See root `MANAGE.md` for complete system overview and integration details.
