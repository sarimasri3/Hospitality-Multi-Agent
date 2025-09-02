# Notification MCP Server Management Guide

## Overview
The **Notification MCP Server** handles all communication and messaging for the hospitality booking system through the Model Context Protocol (MCP). This server manages email notifications, SMS alerts, push notifications, and integration with external communication services.

## Directory Structure
```
mcp_servers/notify/
├── MANAGE.md           # This management guide
└── (implementation pending)
```

## Core Responsibilities

### 1. **Multi-Channel Communication**
- Email notifications for booking confirmations and updates
- SMS alerts for time-sensitive communications
- Push notifications for mobile app users
- In-app messaging and notifications

### 2. **Template Management**
- Dynamic email template rendering
- Localized message content
- Personalized communication based on user preferences
- Brand-consistent messaging across channels

### 3. **Delivery Management**
- Reliable message delivery with retry logic
- Delivery status tracking and confirmation
- Queue management for high-volume messaging
- Rate limiting and throttling controls

### 4. **Integration Services**
- External email service providers (SendGrid, Mailgun)
- SMS gateway integration (Twilio, AWS SNS)
- Push notification services (Firebase Cloud Messaging)
- Webhook handling for delivery confirmations

## Planned Implementation

### **Core Server Configuration**
```python
notify_server = Server()
initialization_options = InitializationOptions(
    server_name="notify-mcp-server",
    server_version="0.1.0"
)
```

### **Proposed Tools**

#### 1. **send_email**
```python
async def send_email(
    recipient: str,
    template_id: str,
    template_data: Dict[str, Any],
    priority: str = "normal",
    scheduled_time: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send email notification using template.
    
    Args:
        recipient: Email address
        template_id: Email template identifier
        template_data: Data for template rendering
        priority: Message priority (low/normal/high/urgent)
        scheduled_time: Optional scheduled delivery time
    
    Returns:
        Delivery confirmation and tracking ID
    """
```

#### 2. **send_sms**
```python
async def send_sms(
    phone_number: str,
    message: str,
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    Send SMS notification.
    
    Args:
        phone_number: Recipient phone number
        message: SMS message content
        priority: Message priority
    
    Returns:
        SMS delivery status and tracking ID
    """
```

#### 3. **send_push_notification**
```python
async def send_push_notification(
    user_id: str,
    title: str,
    body: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send push notification to user devices.
    
    Args:
        user_id: Target user ID
        title: Notification title
        body: Notification body text
        data: Optional custom data payload
    
    Returns:
        Push notification delivery status
    """
```

#### 4. **create_notification_template**
```python
async def create_notification_template(
    template_id: str,
    template_type: str,
    subject: str,
    content: str,
    variables: List[str]
) -> Dict[str, Any]:
    """
    Create or update notification template.
    
    Args:
        template_id: Unique template identifier
        template_type: Type (email/sms/push)
        subject: Template subject line
        content: Template content with variables
        variables: List of template variables
    
    Returns:
        Template creation confirmation
    """
```

#### 5. **get_delivery_status**
```python
async def get_delivery_status(
    tracking_id: str
) -> Dict[str, Any]:
    """
    Get notification delivery status.
    
    Args:
        tracking_id: Message tracking identifier
    
    Returns:
        Detailed delivery status and metrics
    """
```

## Notification Types

### **Booking Lifecycle Notifications**
- **Inquiry Confirmation**: Welcome message and next steps
- **Availability Results**: Property search results and recommendations
- **Booking Confirmation**: Booking details and payment confirmation
- **Pre-arrival Reminders**: Check-in instructions and preparation
- **Post-stay Survey**: Feedback request and review invitation

### **System Notifications**
- **Account Creation**: Welcome and setup instructions
- **Password Reset**: Security and recovery notifications
- **Payment Alerts**: Transaction confirmations and failures
- **System Maintenance**: Service updates and downtime notices

### **Marketing Communications**
- **Promotional Offers**: Special deals and discounts
- **Upsell Opportunities**: Add-on services and upgrades
- **Loyalty Programs**: Rewards and membership benefits
- **Newsletter Updates**: Property highlights and travel tips

## Template System

### **Email Templates**
```html
<!-- Booking Confirmation Template -->
<html>
<head>
    <title>Booking Confirmation - {{property_name}}</title>
</head>
<body>
    <h1>Your booking is confirmed!</h1>
    <p>Dear {{guest_name}},</p>
    <p>We're excited to confirm your reservation at {{property_name}}.</p>
    
    <div class="booking-details">
        <h2>Booking Details</h2>
        <p><strong>Booking ID:</strong> {{booking_id}}</p>
        <p><strong>Check-in:</strong> {{check_in_date}}</p>
        <p><strong>Check-out:</strong> {{check_out_date}}</p>
        <p><strong>Guests:</strong> {{number_of_guests}}</p>
        <p><strong>Total:</strong> ${{total_price}}</p>
    </div>
    
    <div class="next-steps">
        <h2>What's Next?</h2>
        <ul>
            <li>You'll receive check-in instructions 48 hours before arrival</li>
            <li>Contact us anytime with questions</li>
            <li>Review our property guide for local recommendations</li>
        </ul>
    </div>
</body>
</html>
```

### **SMS Templates**
```text
# Booking Confirmation SMS
Hi {{guest_name}}! Your booking at {{property_name}} is confirmed for {{check_in_date}}. Booking ID: {{booking_id}}. Check-in details coming soon!

# Pre-arrival Reminder SMS
{{guest_name}}, you're checking in tomorrow at {{property_name}}! Access code: {{access_code}}. WiFi: {{wifi_password}}. Need help? Reply HELP.
```

## Integration Points

### **With Agents**
- **Confirmation Agent**: Booking confirmation emails
- **Pre-checkin Agent**: Arrival instructions and reminders
- **Survey Agent**: Post-stay feedback requests
- **Inquiry Agent**: Welcome messages and follow-ups

### **With External Services**
- **SendGrid/Mailgun**: Email delivery infrastructure
- **Twilio**: SMS and voice communication
- **Firebase Cloud Messaging**: Push notifications
- **Slack/Teams**: Internal team notifications

### **With User Preferences**
- Communication channel preferences (email/SMS/push)
- Notification frequency settings
- Language and localization preferences
- Opt-out and unsubscribe management

## Proposed Configuration

### **Environment Variables**
```bash
# Email service configuration
EMAIL_PROVIDER=sendgrid
SENDGRID_API_KEY=your_api_key
EMAIL_FROM_ADDRESS=noreply@yourdomain.com
EMAIL_FROM_NAME=Your Company

# SMS service configuration
SMS_PROVIDER=twilio
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
SMS_FROM_NUMBER=+1234567890

# Push notification configuration
FCM_SERVER_KEY=your_fcm_server_key
FCM_PROJECT_ID=your_project_id

# Notification settings
NOTIFICATION_RETRY_ATTEMPTS=3
NOTIFICATION_RATE_LIMIT=100
TEMPLATE_CACHE_TTL=3600
```

### **Delivery Channels**
```yaml
channels:
  email:
    enabled: true
    provider: sendgrid
    rate_limit: 100/minute
    retry_attempts: 3
  
  sms:
    enabled: true
    provider: twilio
    rate_limit: 10/minute
    retry_attempts: 2
  
  push:
    enabled: true
    provider: fcm
    rate_limit: 1000/minute
    retry_attempts: 1
```

## Usage Examples

### **Booking Confirmation Flow**
```python
# Send booking confirmation email
email_result = await send_email(
    recipient="guest@example.com",
    template_id="booking_confirmation",
    template_data={
        "guest_name": "John Doe",
        "property_name": "Luxury Beach Villa",
        "booking_id": "BK123456",
        "check_in_date": "June 15, 2024",
        "check_out_date": "June 20, 2024",
        "number_of_guests": 4,
        "total_price": "1,500.00"
    },
    priority="high"
)

# Send SMS confirmation
sms_result = await send_sms(
    phone_number="+1234567890",
    message="Hi John! Your booking at Luxury Beach Villa is confirmed for June 15. Booking ID: BK123456.",
    priority="normal"
)
```

### **Pre-arrival Notifications**
```python
# Schedule pre-arrival email
await send_email(
    recipient="guest@example.com",
    template_id="pre_arrival_instructions",
    template_data={
        "guest_name": "John Doe",
        "property_name": "Luxury Beach Villa",
        "access_code": "1234",
        "wifi_password": "Welcome1234",
        "check_in_time": "3:00 PM"
    },
    scheduled_time="2024-06-13T10:00:00Z"  # 48 hours before
)
```

## Delivery Management

### **Queue Processing**
- Priority-based message queuing
- Batch processing for efficiency
- Dead letter queue for failed messages
- Automatic retry with exponential backoff

### **Status Tracking**
```python
# Delivery status states
DELIVERY_STATES = {
    "queued": "Message queued for delivery",
    "sending": "Message being sent",
    "delivered": "Message successfully delivered",
    "failed": "Delivery failed",
    "bounced": "Message bounced",
    "unsubscribed": "Recipient unsubscribed"
}
```

### **Analytics and Reporting**
- Delivery success rates by channel
- Open and click-through rates for emails
- Response rates for SMS campaigns
- User engagement metrics

## Error Handling

### **Common Failure Scenarios**
- **Invalid Recipients**: Email/phone validation
- **Service Outages**: External provider downtime
- **Rate Limiting**: API quota exceeded
- **Template Errors**: Missing variables or syntax issues

### **Retry Logic**
```python
# Exponential backoff retry strategy
RETRY_DELAYS = [30, 120, 300, 900]  # seconds
MAX_RETRY_ATTEMPTS = 4

async def retry_delivery(message_id: str, attempt: int):
    if attempt < MAX_RETRY_ATTEMPTS:
        delay = RETRY_DELAYS[attempt]
        await asyncio.sleep(delay)
        # Retry delivery
```

## Security and Compliance

### **Data Protection**
- PII encryption in message content
- Secure credential storage
- GDPR compliance for EU users
- CAN-SPAM compliance for email marketing

### **Authentication**
- API key rotation and management
- Webhook signature verification
- Rate limiting and abuse prevention
- Audit logging for all communications

## Performance Considerations

### **Scalability**
- Horizontal scaling for high-volume messaging
- Message queue partitioning
- Caching for templates and user preferences
- Connection pooling for external services

### **Optimization**
- Template pre-compilation and caching
- Batch API calls where supported
- Asynchronous processing for non-critical messages
- Intelligent retry scheduling

## Troubleshooting

### **Common Commands**
```bash
# Test notification server
python -c "from mcp_servers.notify.server import send_email; print('Notify server available')"

# Validate email templates
python scripts/validate_templates.py

# Check delivery status
curl -X GET "http://localhost:8080/notify/status/tracking_id"
```

### **Debug Information**
- Monitor external service API status
- Check template rendering errors
- Verify recipient data validity
- Track delivery failure patterns

## Related Documentation
- [Root Management Guide](../../MANAGE.md) - System overview and architecture
- [MCP Servers Overview](../MANAGE.md) - MCP server system documentation
- [Agents Overview](../../agents/MANAGE.md) - Agent integration for notifications
- [Configuration](../../config/MANAGE.md) - System configuration and settings

## Implementation Status
**Current Status**: Planning phase - directory structure created, implementation pending

**Next Steps**:
1. Implement core notification server with MCP protocol
2. Set up email service provider integration (SendGrid/Mailgun)
3. Implement SMS gateway integration (Twilio)
4. Create template management system
5. Build delivery tracking and status reporting
6. Integrate with existing agents and workflows

## Development Notes
- Server will implement MCP protocol for tool exposure to agents
- Support for multiple communication channels with failover capabilities
- Template system with variable substitution and localization
- Designed for high-volume messaging with queue management
- Integration with external services for reliable delivery
- Comprehensive tracking and analytics for communication effectiveness
