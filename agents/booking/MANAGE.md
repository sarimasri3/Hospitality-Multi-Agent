# Booking Agent Management

## Purpose & Responsibilities

The **Booking Agent** handles **secure transactional booking creation** with idempotency protection, payment processing, and comprehensive validation. It ensures no duplicate bookings while providing accurate pricing and confirmation details.

## Directory Structure

```
agents/booking/
├── __init__.py          # Package initialization
├── agent.py            # Main BookingAgent implementation
├── idempotency.py      # Idempotency management and validation
└── prompts.py          # Agent prompts and templates
```

## Core Components

### Booking Agent (`agent.py`)

**Purpose**: Main agent class with booking creation and validation tools

**Key Tools**:
```python
async def process_booking(
    property_id: str,
    property_name: str,
    guest_id: str,
    host_id: str,
    check_in_date: str,
    check_out_date: str,
    number_of_guests: int,
    base_price: float,
    add_ons: Optional[List[str]] = None
) -> Dict[str, Any]
# Creates booking with idempotency protection
# Returns: Booking confirmation with reference ID

async def validate_booking_capacity(
    property_capacity: int,
    requested_guests: int
) -> Dict[str, Any]
# Validates guest count against property capacity
# Returns: Validation result with error messages

async def simulate_payment_authorization(
    amount: float,
    currency: str = "USD",
    payment_method: str = "card"
) -> Dict[str, Any]
# Simulates payment gateway authorization (95% success rate)
# Returns: Authorization result with transaction ID

async def format_booking_confirmation(
    booking_data: Dict[str, Any],
    property_details: Dict[str, Any]
) -> str
# Formats comprehensive booking confirmation
# Returns: Formatted confirmation message

async def check_availability_before_booking(
    property_id: str,
    check_in_date: str,
    check_out_date: str
) -> Dict[str, Any]
# Final availability check to prevent race conditions
# Returns: Real-time availability status
```

**Agent Configuration**:
```python
booking_agent = Agent(
    name="booking_agent",
    model="gemini-2.0-flash",
    description="Handles secure booking creation with transaction support",
    global_instruction=BOOKING_SYSTEM_PROMPT,
    instruction=BOOKING_INSTRUCTION,
    tools=[process_booking, validate_booking_capacity, 
           simulate_payment_authorization, format_booking_confirmation,
           check_availability_before_booking]
)
```

**Pricing Calculation Logic**:
```python
# Standard pricing structure
accommodation = base_price * nights
service_fee = accommodation * 0.1      # 10% service fee
cleaning_fee = 50.0                    # Flat cleaning fee
tax = pre_tax_total * 0.08            # 8% tax

# Add-on pricing
add_on_prices = {
    "early_checkin": 50,    # Early check-in
    "late_checkout": 50,    # Late check-out
    "welcome_basket": 75,   # Welcome amenities
    "spa_package": 200,     # Spa services
    "chef_service": 300     # Private chef
}

total_price = accommodation + service_fee + cleaning_fee + add_on_cost + tax
```

### Idempotency Manager (`idempotency.py`)

**Purpose**: Prevents duplicate bookings through natural key generation and caching

**Core Functions**:
```python
def generate_natural_key(
    guest_id: str,
    property_id: str,
    check_in_date: str,
    check_out_date: str
) -> str
    # Creates SHA256 hash from booking components
    # Ensures same request always generates same key
    # Returns: Deterministic booking identifier

def generate_request_signature(request_data: Dict[str, Any]) -> str
    # Creates signature for entire request payload
    # Detects exact request retries
    # Returns: Request fingerprint hash

class IdempotencyManager:
    def check_idempotency(
        self,
        natural_key: str,
        request_signature: Optional[str] = None
    ) -> Optional[Dict[str, Any]]
        # Checks if booking already exists
        # Returns: Existing booking data or None
    
    def store_idempotency(
        self,
        natural_key: str,
        booking_data: Dict[str, Any],
        request_signature: Optional[str] = None
    ) -> None
        # Stores booking for future idempotency checks
        # Includes timestamp and signature
    
    def validate_booking_window(
        self,
        check_in_date: datetime,
        check_out_date: datetime
    ) -> Dict[str, Any]
        # Validates booking dates against business rules
        # Returns: Validation result with specific errors
```

**Business Rule Validation**:
```python
# Booking window constraints
- No past bookings: check_in_date >= now
- Max advance booking: <= 365 days
- Minimum stay: >= 1 night
- Maximum stay: <= 30 nights
- Valid date sequence: check_out > check_in
```

**Natural Key Generation**:
```python
# Key components (normalized)
key_components = [
    guest_id.strip().lower(),
    property_id.strip().lower(), 
    check_in_date.strip(),
    check_out_date.strip()
]

key_string = ":".join(key_components)
natural_key = hashlib.sha256(key_string.encode('utf-8')).hexdigest()
```

### Agent Prompts (`prompts.py`)

**System Prompt** (`BOOKING_SYSTEM_PROMPT`):
- Defines agent as reliable booking specialist
- Emphasizes 100% accuracy and no double-bookings
- Sets security and transparency requirements

**Instruction Prompt** (`BOOKING_INSTRUCTION`):
- 6-step booking process with validation
- Idempotent creation with natural keys
- Payment simulation and confirmation
- Comprehensive error handling

**Templates**:
```python
BOOKING_CONFIRMATION_TEMPLATE = """
✅ **Booking Confirmed!**

**Booking Reference:** `{booking_id}`
**Property:** {property_name}
**Location:** {location}
**Check-in:** {check_in_date} at {check_in_time}
**Check-out:** {check_out_date} at {check_out_time}

**Price Breakdown:**
• Accommodation ({nights} nights): ${accommodation}
• Service Fee: ${service_fee}
• Cleaning Fee: ${cleaning_fee}
• Tax: ${tax}
**Total Charged:** ${total}

**Payment Status:** ✅ Authorized
"""

BOOKING_ERROR_MESSAGES = {
    "unavailable": "Property no longer available for selected dates",
    "payment_failed": "Payment authorization unsuccessful", 
    "capacity_exceeded": "Property capacity ({capacity}) exceeded by request ({requested})",
    "invalid_dates": "Issue with selected dates: {reason}",
    "system_error": "Technical issue - no charges made"
}

IDEMPOTENT_RESPONSE_TEMPLATE = """
I found an existing booking matching your request:
**Booking Reference:** `{booking_id}`
**Status:** {status}
**Created:** {created_at}

No new charges have been made.
"""
```

## How to Use & Extend

### Using the Booking Agent

**In Orchestrator**:
```python
from agents.booking.agent import booking_agent

# Process booking request
response = await booking_agent.process_message(
    message="Book property PROP123 for john@example.com from March 15-18",
    session_data=session_data
)
```

**Direct Tool Usage**:
```python
# Create booking with idempotency
booking_result = await process_booking(
    property_id="prop_123",
    property_name="Luxury Villa Miami",
    guest_id="user_456",
    host_id="host_789",
    check_in_date="2025-03-15",
    check_out_date="2025-03-18",
    number_of_guests=4,
    base_price=400.0,
    add_ons=["early_checkin", "welcome_basket"]
)

# Check result
if booking_result["success"]:
    if booking_result["idempotent"]:
        print("Booking already exists")
    else:
        print(f"New booking created: {booking_result['booking_id']}")
```

### Extending Idempotency Logic

**Custom Idempotency Keys**:
```python
def generate_extended_natural_key(
    guest_id: str,
    property_id: str,
    check_in_date: str,
    check_out_date: str,
    special_requests: Optional[str] = None
) -> str:
    """Extended natural key including special requests."""
    components = [guest_id, property_id, check_in_date, check_out_date]
    
    if special_requests:
        # Normalize special requests
        normalized_requests = special_requests.strip().lower()
        components.append(normalized_requests)
    
    key_string = ":".join(components)
    return hashlib.sha256(key_string.encode('utf-8')).hexdigest()
```

**Redis Integration** (Production):
```python
import redis

class RedisIdempotencyManager(IdempotencyManager):
    def __init__(self, redis_client: redis.Redis, ttl: int = 86400):
        self.redis = redis_client
        self.ttl = ttl  # 24 hours default
    
    def check_idempotency(self, natural_key: str, request_signature: Optional[str] = None):
        """Check idempotency using Redis."""
        cached = self.redis.get(f"booking:{natural_key}")
        if cached:
            return json.loads(cached)
        return None
    
    def store_idempotency(self, natural_key: str, booking_data: Dict[str, Any], request_signature: Optional[str] = None):
        """Store in Redis with TTL."""
        data = {**booking_data, 'signature': request_signature, 'stored_at': datetime.now().isoformat()}
        self.redis.setex(f"booking:{natural_key}", self.ttl, json.dumps(data, default=str))
```

### Adding New Validation Rules

**Custom Validation Tools**:
```python
async def validate_booking_restrictions(
    property_id: str,
    check_in_date: str,
    guest_count: int
) -> Dict[str, Any]:
    """Validate property-specific booking restrictions."""
    # Get property restrictions from database
    restrictions = await get_property_restrictions(property_id)
    
    # Check minimum stay requirements
    if restrictions.get('min_stay', 1) > calculate_nights(check_in_date, check_out_date):
        return {
            "valid": False,
            "error": "MIN_STAY_VIOLATION",
            "message": f"This property requires minimum {restrictions['min_stay']} nights"
        }
    
    # Check seasonal restrictions
    if is_blackout_period(check_in_date, restrictions.get('blackout_dates', [])):
        return {
            "valid": False,
            "error": "BLACKOUT_PERIOD", 
            "message": "Property not available during this period"
        }
    
    return {"valid": True, "message": "All restrictions satisfied"}

# Add to agent tools
booking_agent.tools.append(FunctionTool(validate_booking_restrictions))
```

**Enhanced Payment Processing**:
```python
async def process_payment_with_retry(
    amount: float,
    payment_method: Dict[str, Any],
    max_retries: int = 3
) -> Dict[str, Any]:
    """Payment processing with automatic retry logic."""
    for attempt in range(max_retries):
        try:
            result = await simulate_payment_authorization(
                amount=amount,
                currency=payment_method.get('currency', 'USD'),
                payment_method=payment_method.get('type', 'card')
            )
            
            if result['success']:
                return result
            
            # Wait before retry
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
        except Exception as e:
            if attempt == max_retries - 1:
                return {
                    "success": False,
                    "error": "PAYMENT_PROCESSING_FAILED",
                    "message": f"Payment failed after {max_retries} attempts: {str(e)}"
                }
    
    return {
        "success": False,
        "error": "MAX_RETRIES_EXCEEDED",
        "message": "Payment processing failed after maximum retries"
    }
```

## Integration with Other Components

### → `orchestrator/`
- **Request Routing**: Handles booking phase requests
- **Session Management**: Maintains booking state and user context
- **Transaction Coordination**: Manages multi-step booking process

### → `mcp_servers/firestore/`
- **Booking Creation**: `create_booking` tool via MCP
- **Availability Verification**: Real-time availability checks
- **Transaction Support**: Atomic booking operations

### → `memory/`
- **User Profiles**: Stores payment methods and preferences
- **Booking History**: Maintains past booking records
- **Session State**: Tracks current booking progress

### → `utils/`
- **Date Validation**: Validates booking date formats and ranges
- **Price Formatting**: Formats currency displays in confirmations
- **Input Sanitization**: Cleans booking parameters

### → `config/`
- **Business Rules**: Booking constraints and pricing rules
- **Feature Flags**: Enable/disable booking features
- **Payment Configuration**: Service fees, tax rates, processing settings

### → `agents/availability/`
- **Property Selection**: Receives selected property from availability
- **Pricing Consistency**: Uses same pricing calculation logic
- **Availability Verification**: Final check before booking

## Error Handling & Recovery

### Common Error Scenarios

1. **Property Unavailable**
   ```python
   if not availability_check["available"]:
       return {
           "success": False,
           "error": "PROPERTY_UNAVAILABLE",
           "message": BOOKING_ERROR_MESSAGES["unavailable"],
           "suggested_action": "search_alternatives"
       }
   ```

2. **Payment Failures**
   ```python
   if not payment_result["success"]:
       return {
           "success": False,
           "error": "PAYMENT_FAILED",
           "message": BOOKING_ERROR_MESSAGES["payment_failed"],
           "retry_options": ["different_card", "try_again_later"]
       }
   ```

3. **Capacity Exceeded**
   ```python
   capacity_check = await validate_booking_capacity(property_capacity, requested_guests)
   if not capacity_check["valid"]:
       return {
           "success": False,
           "error": "CAPACITY_EXCEEDED",
           "message": capacity_check["message"],
           "suggested_action": "search_larger_properties"
       }
   ```

### Recovery Strategies

**Automatic Retry Logic**:
```python
async def create_booking_with_retry(booking_params: Dict, max_retries: int = 3):
    """Booking creation with automatic retry on transient failures."""
    for attempt in range(max_retries):
        try:
            result = await process_booking(**booking_params)
            if result["success"]:
                return result
            
            # Check if error is retryable
            if result.get("error") in ["SYSTEM_ERROR", "TIMEOUT"]:
                await asyncio.sleep(1 * (attempt + 1))  # Linear backoff
                continue
            else:
                return result  # Non-retryable error
                
        except Exception as e:
            if attempt == max_retries - 1:
                return {
                    "success": False,
                    "error": "BOOKING_FAILED",
                    "message": f"Booking failed after {max_retries} attempts: {str(e)}"
                }
```

## Performance Optimization

### Idempotency Caching

**Memory Optimization**:
```python
from functools import lru_cache
from datetime import datetime, timedelta

class OptimizedIdempotencyManager:
    def __init__(self, max_cache_size: int = 10000):
        self._cache = {}
        self.max_size = max_cache_size
    
    @lru_cache(maxsize=1000)
    def _generate_key_cached(self, guest_id: str, property_id: str, check_in: str, check_out: str):
        """Cached key generation for repeated requests."""
        return generate_natural_key(guest_id, property_id, check_in, check_out)
    
    def cleanup_expired_entries(self, ttl_hours: int = 24):
        """Remove expired idempotency entries."""
        cutoff = datetime.now() - timedelta(hours=ttl_hours)
        expired_keys = []
        
        for key, data in self._cache.items():
            stored_at = datetime.fromisoformat(data.get('stored_at', ''))
            if stored_at < cutoff:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
```

### Batch Operations

**Bulk Validation**:
```python
async def validate_multiple_bookings(booking_requests: List[Dict]) -> List[Dict]:
    """Validate multiple booking requests in parallel."""
    validation_tasks = []
    
    for request in booking_requests:
        task = asyncio.create_task(
            validate_booking_parameters(request)
        )
        validation_tasks.append(task)
    
    results = await asyncio.gather(*validation_tasks, return_exceptions=True)
    
    return [
        result if not isinstance(result, Exception) 
        else {"valid": False, "error": str(result)}
        for result in results
    ]
```

## Troubleshooting

### Common Issues

1. **Duplicate Booking Detection**
   ```python
   # Debug idempotency
   natural_key = generate_natural_key(guest_id, property_id, check_in, check_out)
   print(f"Natural key: {natural_key}")
   
   existing = idempotency_manager.check_idempotency(natural_key)
   print(f"Existing booking: {existing}")
   ```

2. **Pricing Calculation Errors**
   ```python
   # Debug pricing
   print(f"Base price: ${base_price}")
   print(f"Nights: {nights}")
   print(f"Accommodation: ${base_price * nights}")
   print(f"Service fee: ${(base_price * nights) * 0.1}")
   print(f"Total: ${total_price}")
   ```

3. **Payment Simulation Issues**
   ```python
   # Test payment simulation
   for i in range(10):
       result = await simulate_payment_authorization(100.0)
       print(f"Attempt {i+1}: {result['success']}")
   ```

### Debug Commands

```python
# Test booking agent tools
from agents.booking.agent import booking_agent

# Test idempotency
from agents.booking.idempotency import generate_natural_key, IdempotencyManager

key = generate_natural_key("user123", "prop456", "2025-03-15", "2025-03-18")
print(f"Natural key: {key}")

# Test validation
manager = IdempotencyManager()
validation = manager.validate_booking_window(
    datetime(2025, 3, 15),
    datetime(2025, 3, 18)
)
print(f"Validation: {validation}")

# Test booking creation
booking_result = await process_booking(
    property_id="test_prop",
    property_name="Test Property",
    guest_id="test_user",
    host_id="test_host",
    check_in_date="2025-03-15",
    check_out_date="2025-03-18",
    number_of_guests=2,
    base_price=200.0
)
print(f"Booking result: {booking_result}")
```

---

**Next Steps**: See [agents/MANAGE.md](../MANAGE.md) for agent coordination and [mcp_servers/firestore/MANAGE.md](../../mcp_servers/firestore/MANAGE.md) for database integration.
