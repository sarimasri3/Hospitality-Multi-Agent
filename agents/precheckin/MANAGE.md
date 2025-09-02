# Pre-checkin Agent Management Guide

## Overview
The **Pre-checkin Agent** manages pre-arrival communication and check-in preparation for confirmed bookings. This agent ensures guests receive timely reminders, collect arrival information, and provide detailed check-in instructions for a smooth arrival experience.

## Directory Structure
```
agents/precheckin/
├── MANAGE.md           # This management guide
├── __init__.py         # Package initialization
└── agent.py            # Pre-checkin agent implementation
```

## Core Responsibilities

### 1. **Reminder Scheduling**
- Schedule automated reminders 48 hours before check-in
- Send timely notifications to guests
- Manage reminder timing and delivery

### 2. **Arrival Information Collection**
- Collect estimated arrival times from guests
- Gather transportation method details
- Handle special requests and requirements

### 3. **Check-in Instructions Generation**
- Generate detailed property-specific instructions
- Provide access codes and WiFi credentials
- Include parking and contact information

### 4. **Pre-arrival Coordination**
- Ensure property readiness for guest arrival
- Address special requests and accommodations
- Coordinate with property management

## Agent Implementation

### Core Agent Configuration
```python
precheckin_agent = Agent(
    name="precheckin_agent",
    model="gemini-2.0-flash",
    description="Handles pre-arrival communication and check-in preparation",
    instruction="Manage pre-arrival tasks and communication...",
    tools=[
        FunctionTool(schedule_reminder),
        FunctionTool(collect_arrival_info),
        FunctionTool(generate_checkin_instructions)
    ]
)
```

### Available Tools

#### 1. **schedule_reminder**
```python
async def schedule_reminder(
    booking_id: str,
    check_in_date: str,
    guest_email: str,
    reminder_hours_before: int = 48
) -> Dict[str, Any]
```
- **Purpose**: Schedule pre-checkin reminders
- **Default**: 48 hours before check-in
- **Returns**: Scheduling confirmation with timing details

#### 2. **collect_arrival_info**
```python
async def collect_arrival_info(
    estimated_arrival_time: str,
    transportation_method: str,
    special_requests: Optional[str] = None
) -> Dict[str, Any]
```
- **Purpose**: Gather guest arrival details
- **Collects**: Arrival time, transportation, special requests
- **Returns**: Structured arrival information

#### 3. **generate_checkin_instructions**
```python
async def generate_checkin_instructions(
    property_data: Dict[str, Any],
    booking_data: Dict[str, Any]
) -> str
```
- **Purpose**: Create detailed check-in instructions
- **Includes**: Access codes, WiFi, parking, contact info
- **Returns**: Formatted instruction text

## Workflow Process

### 1. **Pre-arrival Timeline**
```
T-48 hours: Schedule and send reminder
T-24 hours: Collect arrival information
T-12 hours: Generate check-in instructions
T-2 hours:  Final confirmation and readiness check
```

### 2. **Information Flow**
```
Booking Confirmation → Schedule Reminder → Collect Arrival Info → 
Generate Instructions → Send to Guest → Confirm Readiness
```

### 3. **Guest Communication**
- Proactive reminder scheduling
- Interactive arrival information collection
- Clear, detailed instruction delivery
- Responsive support for questions

## Key Features

### **Automated Scheduling**
- Configurable reminder timing (default 48 hours)
- Email-based notification system
- Booking-specific scheduling

### **Dynamic Instructions**
- Property-specific access codes
- Booking ID-based security codes
- WiFi credentials generation
- Parking and contact details

### **Special Request Handling**
- Collection of guest requirements
- Coordination with property management
- Accommodation arrangement

## Usage Examples

### Basic Pre-checkin Flow
```python
# Schedule reminder
reminder_result = await schedule_reminder(
    booking_id="BK123456",
    check_in_date="2024-01-15T15:00:00",
    guest_email="guest@example.com"
)

# Collect arrival info
arrival_info = await collect_arrival_info(
    estimated_arrival_time="14:30",
    transportation_method="Car",
    special_requests="Early check-in if possible"
)

# Generate instructions
instructions = await generate_checkin_instructions(
    property_data={
        "name": "Luxury Villa",
        "location": {"address": "123 Beach Road"},
        "check_in_time": "15:00"
    },
    booking_data={"booking_id": "BK123456"}
)
```

### Integration with Other Agents
```python
# From confirmation agent
confirmation_agent.trigger_precheckin(booking_data)

# To property management
property_manager.prepare_for_arrival(arrival_info)
```

## Extension Points

### **Custom Reminder Types**
```python
# Add SMS reminders
async def schedule_sms_reminder(phone_number: str, message: str):
    pass

# Add in-app notifications
async def schedule_app_notification(user_id: str, notification: dict):
    pass
```

### **Enhanced Instructions**
```python
# Add local recommendations
async def generate_local_guide(property_location: dict):
    pass

# Add weather updates
async def include_weather_forecast(check_in_date: str, location: dict):
    pass
```

### **Integration Enhancements**
```python
# Smart lock integration
async def program_smart_lock(booking_id: str, access_code: str):
    pass

# Concierge services
async def arrange_concierge_services(special_requests: list):
    pass
```

## Integration Points

### **With Confirmation Agent**
- Receives booking confirmation data
- Triggered after successful booking confirmation
- Shares guest contact information

### **With Property Management**
- Coordinates property preparation
- Manages access code programming
- Handles special request fulfillment

### **With Notification System**
- Sends scheduled reminders
- Delivers check-in instructions
- Manages communication preferences

### **With Guest Support**
- Escalates complex requests
- Provides arrival support
- Handles emergency situations

## Configuration

### **Environment Variables**
```bash
# Reminder timing
PRECHECKIN_REMINDER_HOURS=48
PRECHECKIN_FOLLOWUP_HOURS=24

# Communication preferences
PRECHECKIN_EMAIL_ENABLED=true
PRECHECKIN_SMS_ENABLED=false

# Access code settings
ACCESS_CODE_LENGTH=4
WIFI_PASSWORD_PREFIX=Welcome
```

### **Feature Flags**
```yaml
precheckin:
  enabled: true
  reminder_scheduling: true
  arrival_collection: true
  instruction_generation: true
  special_requests: true
```

## Error Handling

### **Common Issues**
- **Reminder Scheduling Failures**: Retry with exponential backoff
- **Invalid Arrival Times**: Validate and request correction
- **Missing Property Data**: Fetch from property database
- **Communication Failures**: Use alternative channels

### **Error Recovery**
```python
# Retry failed reminders
async def retry_reminder_schedule(booking_id: str, max_retries: int = 3):
    pass

# Validate arrival information
async def validate_arrival_info(arrival_data: dict) -> bool:
    pass

# Fallback instruction generation
async def generate_basic_instructions(booking_id: str) -> str:
    pass
```

## Performance Considerations

### **Scheduling Optimization**
- Batch reminder scheduling for efficiency
- Use queue-based processing for high volume
- Implement rate limiting for external communications

### **Caching Strategy**
- Cache property instruction templates
- Store frequently used access patterns
- Optimize database queries for booking data

### **Monitoring Metrics**
- Reminder delivery success rates
- Guest response times to information requests
- Check-in instruction effectiveness
- Special request fulfillment rates

## Troubleshooting

### **Common Commands**
```bash
# Check reminder schedules
python -c "from agents.precheckin.agent import schedule_reminder; print('Reminder scheduling available')"

# Validate arrival info collection
python -c "from agents.precheckin.agent import collect_arrival_info; print('Arrival collection available')"

# Test instruction generation
python -c "from agents.precheckin.agent import generate_checkin_instructions; print('Instruction generation available')"
```

### **Debug Information**
- Check booking confirmation data availability
- Verify guest contact information accuracy
- Validate property data completeness
- Monitor communication delivery status

### **Log Analysis**
```bash
# Check precheckin logs
grep "precheckin" logs/hospitality.log | tail -20

# Monitor reminder scheduling
grep "schedule_reminder" logs/hospitality.log | grep ERROR

# Track instruction generation
grep "generate_checkin_instructions" logs/hospitality.log
```

## Related Documentation
- [Root Management Guide](../../MANAGE.md) - System overview and architecture
- [Agents Overview](../MANAGE.md) - Agent system documentation
- [Confirmation Agent](../confirmation/MANAGE.md) - Booking confirmation process
- [Memory Management](../../memory/MANAGE.md) - Session and data persistence
- [Configuration](../../config/MANAGE.md) - System configuration and settings

## Development Notes
- Agent uses Google ADK framework with Gemini 2.0 Flash model
- Implements async/await patterns for non-blocking operations
- Follows hospitality industry best practices for guest communication
- Designed for scalability and high-volume booking processing
- Integrates with external notification and property management systems
