# Confirmation Agent Management

## Purpose & Responsibilities

The **Confirmation Agent** handles **booking confirmation and guest communication** after successful booking creation. It generates confirmation emails, creates audit logs, and provides comprehensive booking summaries to guests.

## Directory Structure

```
agents/confirmation/
├── __init__.py          # Package initialization
└── agent.py            # Main ConfirmationAgent implementation
```

## Core Components

### Confirmation Agent (`agent.py`)

**Purpose**: Main agent class for post-booking confirmation and communication

**Key Tools**:
```python
async def generate_confirmation_email(
    booking_data: Dict[str, Any],
    property_data: Dict[str, Any],
    guest_data: Dict[str, Any]
) -> Dict[str, str]
# Generates comprehensive confirmation email content
# Returns: Email subject, body, and recipient information

async def create_audit_log(
    booking_id: str,
    action: str,
    details: Dict[str, Any]
) -> Dict[str, Any]
# Creates audit log entry for booking actions
# Returns: Timestamped audit record
```

**Agent Configuration**:
```python
confirmation_agent = Agent(
    name="confirmation_agent",
    model="gemini-2.0-flash",
    description="Handles booking confirmation and guest communication",
    instruction="Provide comprehensive booking confirmation to the guest",
    tools=[generate_confirmation_email, create_audit_log]
)
```

**Confirmation Email Template**:
```python
email_body = f"""
Dear {guest_data.get('name', 'Guest')},

Your booking at {property_data['name']} has been confirmed!

Booking Reference: {booking_data['booking_id'][:8].upper()}
Check-in: {booking_data['check_in_date']}
Check-out: {booking_data['check_out_date']}

Property Address:
{property_data['location']['address']}
{property_data['location']['city']}, {property_data['location']['country']}

Total Amount Paid: ${booking_data['total_price']:.2f}

House Rules:
- Check-in time: {property_data.get('check_in_time', '15:00')}
- Check-out time: {property_data.get('check_out_time', '11:00')}
- Maximum occupancy: {property_data['guest_space']} guests
- No smoking inside the property
- No parties or events
- Respect quiet hours (10 PM - 8 AM)

We'll send you check-in instructions 48 hours before your arrival.

Best regards,
The Hospitality Team
"""
```

**Instruction Flow**:
1. **Summarize booking details** - Clear overview of reservation
2. **Generate confirmation email** - Professional email content
3. **Highlight important information** - Check-in/out times, house rules
4. **Create audit log** - Track booking confirmation action
5. **Inform about next steps** - Pre-checkin process timeline
6. **Thank guest** - Professional and welcoming closure

## How to Use & Extend

### Using the Confirmation Agent

**In Orchestrator**:
```python
from agents.confirmation.agent import confirmation_agent

# Process confirmation after booking
response = await confirmation_agent.process_message(
    message="Send confirmation for booking BOOK123",
    session_data=session_data
)
```

**Direct Tool Usage**:
```python
# Generate confirmation email
email_content = await generate_confirmation_email(
    booking_data={
        "booking_id": "abc123def456",
        "check_in_date": "2025-03-15",
        "check_out_date": "2025-03-18",
        "total_price": 1200.0
    },
    property_data={
        "name": "Luxury Villa Miami",
        "location": {
            "address": "123 Ocean Drive",
            "city": "Miami",
            "country": "USA"
        },
        "guest_space": 8,
        "check_in_time": "15:00",
        "check_out_time": "11:00"
    },
    guest_data={
        "name": "John Smith",
        "email": "john@example.com"
    }
)

# Create audit log
audit_entry = await create_audit_log(
    booking_id="abc123def456",
    action="CONFIRMATION_SENT",
    details={
        "email_sent": True,
        "recipient": "john@example.com",
        "timestamp": "2025-01-15T10:30:00Z"
    }
)
```

### Extending Confirmation Features

**Enhanced Email Templates**:
```python
async def generate_premium_confirmation_email(
    booking_data: Dict[str, Any],
    property_data: Dict[str, Any],
    guest_data: Dict[str, Any],
    add_ons: List[str] = None
) -> Dict[str, str]:
    """Enhanced confirmation with add-on services."""
    base_email = await generate_confirmation_email(booking_data, property_data, guest_data)
    
    if add_ons:
        add_on_section = "\n\nYour Add-on Services:\n"
        add_on_descriptions = {
            "early_checkin": "• Early Check-in (12:00 PM)",
            "late_checkout": "• Late Check-out (2:00 PM)",
            "welcome_basket": "• Welcome Basket with local treats",
            "spa_package": "• In-room spa services",
            "chef_service": "• Private chef service"
        }
        
        for addon in add_ons:
            if addon in add_on_descriptions:
                add_on_section += add_on_descriptions[addon] + "\n"
        
        # Insert add-on section before house rules
        base_email["body"] = base_email["body"].replace(
            "House Rules:",
            add_on_section + "\nHouse Rules:"
        )
    
    return base_email

# Add to agent tools
confirmation_agent.tools.append(FunctionTool(generate_premium_confirmation_email))
```

**Multi-language Support**:
```python
async def generate_localized_confirmation(
    booking_data: Dict[str, Any],
    property_data: Dict[str, Any],
    guest_data: Dict[str, Any],
    language: str = "en"
) -> Dict[str, str]:
    """Generate confirmation in guest's preferred language."""
    templates = {
        "en": {
            "subject": "Booking Confirmed - {property_name}",
            "greeting": "Dear {guest_name},",
            "confirmed": "Your booking at {property_name} has been confirmed!",
            "reference": "Booking Reference: {booking_ref}",
            "thanks": "Best regards,\nThe Hospitality Team"
        },
        "es": {
            "subject": "Reserva Confirmada - {property_name}",
            "greeting": "Estimado/a {guest_name},",
            "confirmed": "¡Su reserva en {property_name} ha sido confirmada!",
            "reference": "Referencia de Reserva: {booking_ref}",
            "thanks": "Saludos cordiales,\nEl Equipo de Hospitalidad"
        },
        "fr": {
            "subject": "Réservation Confirmée - {property_name}",
            "greeting": "Cher/Chère {guest_name},",
            "confirmed": "Votre réservation à {property_name} a été confirmée!",
            "reference": "Référence de Réservation: {booking_ref}",
            "thanks": "Cordialement,\nL'Équipe d'Hospitalité"
        }
    }
    
    template = templates.get(language, templates["en"])
    
    # Build localized email
    email_body = f"""
    {template["greeting"].format(guest_name=guest_data.get('name', 'Guest'))}
    
    {template["confirmed"].format(property_name=property_data['name'])}
    
    {template["reference"].format(booking_ref=booking_data['booking_id'][:8].upper())}
    Check-in: {booking_data['check_in_date']}
    Check-out: {booking_data['check_out_date']}
    
    {template["thanks"]}
    """
    
    return {
        "subject": template["subject"].format(property_name=property_data['name']),
        "body": email_body,
        "recipient": guest_data.get('email', ''),
        "language": language
    }
```

**SMS Confirmation**:
```python
async def generate_sms_confirmation(
    booking_data: Dict[str, Any],
    property_data: Dict[str, Any],
    guest_data: Dict[str, Any]
) -> Dict[str, str]:
    """Generate SMS confirmation message."""
    sms_body = f"""
    Booking confirmed! 
    {property_data['name']} 
    Ref: {booking_data['booking_id'][:8].upper()}
    {booking_data['check_in_date']} to {booking_data['check_out_date']}
    Total: ${booking_data['total_price']:.2f}
    Email confirmation sent.
    """
    
    return {
        "message": sms_body.strip(),
        "recipient": guest_data.get('phone', ''),
        "type": "sms"
    }

# Add to agent tools
confirmation_agent.tools.append(FunctionTool(generate_sms_confirmation))
```

### Advanced Audit Logging

**Detailed Audit System**:
```python
async def create_comprehensive_audit_log(
    booking_id: str,
    action: str,
    details: Dict[str, Any],
    user_id: str = None,
    ip_address: str = None
) -> Dict[str, Any]:
    """Enhanced audit logging with user context."""
    audit_entry = {
        "booking_id": booking_id,
        "action": action,
        "details": details,
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "ip_address": ip_address,
        "session_id": details.get('session_id'),
        "user_agent": details.get('user_agent'),
        "logged": True
    }
    
    # Add action-specific metadata
    if action == "CONFIRMATION_SENT":
        audit_entry["communication_type"] = details.get("type", "email")
        audit_entry["recipient"] = details.get("recipient")
        audit_entry["delivery_status"] = details.get("delivery_status", "pending")
    
    return audit_entry

async def log_confirmation_metrics(
    booking_id: str,
    email_sent: bool,
    sms_sent: bool = False,
    delivery_time_ms: int = None
) -> Dict[str, Any]:
    """Log confirmation delivery metrics."""
    metrics = {
        "booking_id": booking_id,
        "action": "CONFIRMATION_METRICS",
        "metrics": {
            "email_sent": email_sent,
            "sms_sent": sms_sent,
            "delivery_time_ms": delivery_time_ms,
            "timestamp": datetime.now().isoformat()
        },
        "logged": True
    }
    
    return metrics
```

## Integration with Other Components

### → `orchestrator/`
- **Request Routing**: Handles confirmation phase requests
- **Session Management**: Maintains booking context for confirmation
- **Workflow Coordination**: Triggers confirmation after booking success

### → `mcp_servers/notify/`
- **Email Delivery**: Sends confirmation emails via notification MCP
- **SMS Delivery**: Sends SMS confirmations if enabled
- **Delivery Tracking**: Monitors confirmation delivery status

### → `mcp_servers/firestore/`
- **Audit Logging**: Stores audit logs in database
- **Booking Updates**: Updates booking status to "confirmed"
- **Guest Communication**: Records communication history

### → `memory/`
- **Guest Preferences**: Stores communication preferences (email/SMS)
- **Language Preferences**: Remembers guest's preferred language
- **Communication History**: Tracks past confirmations

### → `utils/`
- **Email Formatting**: Uses formatters for consistent email styling
- **Date Formatting**: Formats dates for guest-friendly display
- **Template Rendering**: Renders confirmation templates

### → `config/`
- **Communication Settings**: Email templates and SMS settings
- **Business Rules**: Confirmation timing and requirements
- **Feature Flags**: Enable/disable SMS confirmations

### → `agents/booking/`
- **Booking Data**: Receives booking details for confirmation
- **Success Trigger**: Activated after successful booking creation
- **Data Consistency**: Uses same booking reference format

## Confirmation Workflow

### Standard Confirmation Process

1. **Receive Booking Data**
   ```python
   booking_data = {
       "booking_id": "abc123def456",
       "property_id": "prop_789",
       "guest_id": "user_123",
       "check_in_date": "2025-03-15",
       "check_out_date": "2025-03-18",
       "total_price": 1200.0,
       "status": "confirmed"
   }
   ```

2. **Generate Confirmation Content**
   ```python
   email_content = await generate_confirmation_email(
       booking_data, property_data, guest_data
   )
   ```

3. **Send Confirmation**
   ```python
   # Via MCP notification server
   await send_email(
       to=email_content["recipient"],
       subject=email_content["subject"],
       body=email_content["body"]
   )
   ```

4. **Create Audit Log**
   ```python
   audit_log = await create_audit_log(
       booking_id=booking_data["booking_id"],
       action="CONFIRMATION_SENT",
       details={
           "email_sent": True,
           "recipient": guest_data["email"],
           "timestamp": datetime.now().isoformat()
       }
   )
   ```

5. **Update Booking Status**
   ```python
   # Via MCP firestore server
   await update_booking_status(
       booking_id=booking_data["booking_id"],
       status="confirmation_sent"
   )
   ```

### Error Handling

**Email Delivery Failures**:
```python
async def handle_confirmation_failure(
    booking_id: str,
    error: str,
    retry_count: int = 0
) -> Dict[str, Any]:
    """Handle confirmation delivery failures."""
    if retry_count < 3:
        # Retry with exponential backoff
        await asyncio.sleep(2 ** retry_count)
        return await retry_confirmation(booking_id, retry_count + 1)
    else:
        # Log failure and alert support
        await create_audit_log(
            booking_id=booking_id,
            action="CONFIRMATION_FAILED",
            details={
                "error": error,
                "retry_count": retry_count,
                "requires_manual_intervention": True
            }
        )
        
        return {
            "success": False,
            "error": "CONFIRMATION_DELIVERY_FAILED",
            "message": "Unable to deliver confirmation after 3 attempts"
        }
```

## Performance Optimization

### Batch Confirmations

```python
async def process_batch_confirmations(
    bookings: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Process multiple confirmations in parallel."""
    confirmation_tasks = []
    
    for booking in bookings:
        task = asyncio.create_task(
            process_single_confirmation(booking)
        )
        confirmation_tasks.append(task)
    
    results = await asyncio.gather(*confirmation_tasks, return_exceptions=True)
    
    return [
        result if not isinstance(result, Exception)
        else {"success": False, "error": str(result)}
        for result in results
    ]
```

### Template Caching

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_template(template_name: str, language: str = "en") -> str:
    """Cache frequently used confirmation templates."""
    return load_template(template_name, language)
```

## Troubleshooting

### Common Issues

1. **Missing Booking Data**
   ```python
   # Validate required fields
   required_fields = ["booking_id", "check_in_date", "check_out_date", "total_price"]
   missing_fields = [field for field in required_fields if field not in booking_data]
   
   if missing_fields:
       return {
           "success": False,
           "error": "MISSING_BOOKING_DATA",
           "missing_fields": missing_fields
       }
   ```

2. **Email Generation Errors**
   ```python
   # Debug email generation
   try:
       email_content = await generate_confirmation_email(
           booking_data, property_data, guest_data
       )
       print(f"Email generated: {email_content['subject']}")
   except Exception as e:
       print(f"Email generation error: {e}")
   ```

3. **Audit Log Issues**
   ```python
   # Test audit logging
   try:
       audit_entry = await create_audit_log(
           booking_id="test_booking",
           action="TEST_ACTION",
           details={"test": True}
       )
       print(f"Audit log created: {audit_entry}")
   except Exception as e:
       print(f"Audit log error: {e}")
   ```

### Debug Commands

```python
# Test confirmation agent tools
from agents.confirmation.agent import confirmation_agent

# Test email generation
email_result = await generate_confirmation_email(
    booking_data={"booking_id": "test123", "check_in_date": "2025-03-15", 
                  "check_out_date": "2025-03-18", "total_price": 500.0},
    property_data={"name": "Test Property", "location": {"city": "Test City", "address": "123 Test St", "country": "USA"}, 
                   "guest_space": 4},
    guest_data={"name": "Test Guest", "email": "test@example.com"}
)
print(f"Email result: {email_result}")

# Test audit logging
audit_result = await create_audit_log(
    booking_id="test123",
    action="TEST_CONFIRMATION",
    details={"test": True}
)
print(f"Audit result: {audit_result}")
```

---

**Next Steps**: See [agents/MANAGE.md](../MANAGE.md) for agent coordination and [mcp_servers/notify/MANAGE.md](../../mcp_servers/notify/MANAGE.md) for notification delivery.
