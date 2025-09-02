# Logs Management Guide

## Overview
The **Logs** directory contains system logs and logging configuration for the hospitality booking system. This centralized logging system captures application events, errors, performance metrics, and audit trails across all system components.

## Directory Structure
```
logs/
├── MANAGE.md           # This management guide
└── hospitality.log     # Main application log file
```

## Core Logging Responsibilities

### 1. **Application Event Logging**
- Agent execution and decision logging
- User interaction and conversation tracking
- System state changes and transitions
- Business process workflow logging

### 2. **Error and Exception Tracking**
- Error details with stack traces
- Exception context and recovery actions
- System failure analysis
- Performance degradation alerts

### 3. **Audit and Compliance Logging**
- User authentication and authorization
- Data access and modification tracking
- Booking transaction audit trails
- Compliance reporting support

### 4. **Performance and Monitoring**
- Response time measurements
- Resource utilization tracking
- Database query performance
- External service interaction logs

## Log File Structure

### **Main Application Log** (`hospitality.log`)
Centralized log file containing all system events with structured format:

```
2024-01-15 10:30:15,123 - INFO - [orchestrator.main:45] - Session started: session_12345
2024-01-15 10:30:15,124 - DEBUG - [agents.inquiry.agent:23] - Processing inquiry: "Looking for villa in Miami"
2024-01-15 10:30:15,156 - INFO - [mcp_servers.firestore.server:89] - Database query executed: search_properties
2024-01-15 10:30:15,234 - WARNING - [agents.availability.ranking:67] - Low property availability for dates
2024-01-15 10:30:15,345 - ERROR - [mcp_servers.notify.server:123] - Email delivery failed: SMTP timeout
```

### **Log Entry Components**
- **Timestamp**: ISO format with milliseconds
- **Level**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Module**: Source module and line number
- **Message**: Descriptive event information
- **Context**: Additional structured data (JSON format)

## Logging Configuration

### **Log Levels**
```python
LOGGING_LEVELS = {
    "DEBUG": 10,    # Detailed diagnostic information
    "INFO": 20,     # General operational messages
    "WARNING": 30,  # Warning conditions
    "ERROR": 40,    # Error conditions
    "CRITICAL": 50  # Critical system failures
}
```

### **Logger Configuration**
```python
import logging
import logging.handlers
from pathlib import Path

# Configure main logger
LOG_FILE_PATH = Path("logs/hospitality.log")
LOG_FORMAT = "%(asctime)s - %(levelname)s - [%(name)s:%(lineno)d] - %(message)s"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.handlers.RotatingFileHandler(
            LOG_FILE_PATH,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()  # Console output
    ]
)

# Component-specific loggers
orchestrator_logger = logging.getLogger("orchestrator")
agent_logger = logging.getLogger("agents")
mcp_logger = logging.getLogger("mcp_servers")
```

### **Structured Logging**
```python
import json
import logging

class StructuredLogger:
    """Enhanced logger with structured data support."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def log_event(self, level: str, message: str, **context):
        """Log event with structured context."""
        
        log_entry = {
            "message": message,
            "context": context,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        getattr(self.logger, level.lower())(
            f"{message} | Context: {json.dumps(context)}"
        )
    
    def log_booking_event(self, event_type: str, booking_id: str, **details):
        """Log booking-related events."""
        
        self.log_event(
            "info",
            f"Booking {event_type}",
            booking_id=booking_id,
            event_type=event_type,
            **details
        )
    
    def log_agent_transition(self, from_agent: str, to_agent: str, session_id: str, reason: str):
        """Log agent handoff events."""
        
        self.log_event(
            "info",
            f"Agent transition: {from_agent} -> {to_agent}",
            session_id=session_id,
            from_agent=from_agent,
            to_agent=to_agent,
            transition_reason=reason
        )
```

## Log Categories

### **Business Process Logs**
```python
# Booking workflow logging
logger.info("Booking process started", extra={
    "session_id": "sess_123",
    "guest_id": "guest_456",
    "property_id": "prop_789"
})

# Agent decision logging
logger.info("Property ranking completed", extra={
    "properties_found": 5,
    "ranking_factors": ["price", "distance", "amenities"],
    "top_property": "prop_789"
})

# Payment processing
logger.info("Payment processed", extra={
    "booking_id": "book_123",
    "amount": 1500.00,
    "payment_method": "credit_card",
    "transaction_id": "txn_456"
})
```

### **System Performance Logs**
```python
# Response time tracking
logger.info("Agent response time", extra={
    "agent": "availability",
    "response_time_ms": 234,
    "tool_calls": 3,
    "database_queries": 2
})

# Resource utilization
logger.info("System metrics", extra={
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "active_sessions": 12,
    "database_connections": 8
})
```

### **Error and Exception Logs**
```python
# Database errors
logger.error("Database connection failed", extra={
    "error_type": "ConnectionError",
    "database": "firestore",
    "retry_attempt": 2,
    "max_retries": 3
}, exc_info=True)

# Agent errors
logger.error("Agent tool execution failed", extra={
    "agent": "booking",
    "tool": "create_booking",
    "error_message": "Invalid property ID",
    "session_id": "sess_123"
})
```

### **Security and Audit Logs**
```python
# Authentication events
logger.info("User authentication", extra={
    "user_id": "user_123",
    "auth_method": "email",
    "ip_address": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "success": True
})

# Data access logging
logger.info("Data access", extra={
    "user_id": "user_123",
    "resource": "booking_details",
    "resource_id": "book_456",
    "action": "read",
    "authorized": True
})
```

## Log Analysis and Monitoring

### **Log Parsing and Analysis**
```bash
# Search for specific events
grep "Booking created" logs/hospitality.log

# Filter by log level
grep "ERROR" logs/hospitality.log | tail -20

# Extract booking-related logs
grep "booking_id" logs/hospitality.log | jq '.context.booking_id'

# Monitor real-time logs
tail -f logs/hospitality.log | grep "ERROR\|WARNING"
```

### **Performance Analysis**
```bash
# Agent response times
grep "Agent response time" logs/hospitality.log | \
  jq '.context.response_time_ms' | \
  awk '{sum+=$1; count++} END {print "Average:", sum/count "ms"}'

# Database query performance
grep "Database query executed" logs/hospitality.log | \
  grep -o "duration:[0-9]*" | \
  cut -d: -f2 | \
  sort -n | tail -10
```

### **Error Pattern Detection**
```bash
# Most common errors
grep "ERROR" logs/hospitality.log | \
  cut -d'-' -f4- | \
  sort | uniq -c | sort -nr | head -10

# Error trends by hour
grep "ERROR" logs/hospitality.log | \
  cut -d' ' -f2 | cut -d: -f1 | \
  sort | uniq -c
```

## Log Rotation and Retention

### **Rotation Configuration**
```python
# Rotating file handler configuration
rotating_handler = logging.handlers.RotatingFileHandler(
    filename="logs/hospitality.log",
    maxBytes=10*1024*1024,  # 10MB per file
    backupCount=5,          # Keep 5 backup files
    encoding='utf-8'
)

# Time-based rotation
time_handler = logging.handlers.TimedRotatingFileHandler(
    filename="logs/hospitality.log",
    when='midnight',        # Rotate at midnight
    interval=1,             # Every day
    backupCount=30,         # Keep 30 days
    encoding='utf-8'
)
```

### **Log Cleanup Script**
```bash
#!/bin/bash
# cleanup_logs.sh - Log cleanup and archival script

LOG_DIR="logs"
ARCHIVE_DIR="logs/archive"
RETENTION_DAYS=30

# Create archive directory
mkdir -p "$ARCHIVE_DIR"

# Archive old logs
find "$LOG_DIR" -name "*.log.*" -mtime +7 -exec mv {} "$ARCHIVE_DIR/" \;

# Compress archived logs
find "$ARCHIVE_DIR" -name "*.log.*" -not -name "*.gz" -exec gzip {} \;

# Remove old archived logs
find "$ARCHIVE_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete

echo "Log cleanup completed: $(date)"
```

## Monitoring and Alerting

### **Log-based Alerts**
```python
# Error rate monitoring
def monitor_error_rate():
    """Monitor error rate and trigger alerts."""
    
    error_count = count_log_entries("ERROR", last_minutes=5)
    total_count = count_log_entries("INFO|WARNING|ERROR", last_minutes=5)
    
    error_rate = error_count / total_count if total_count > 0 else 0
    
    if error_rate > 0.05:  # 5% error rate threshold
        send_alert(
            severity="warning",
            message=f"High error rate detected: {error_rate:.2%}",
            details={"error_count": error_count, "total_count": total_count}
        )

# Performance degradation detection
def monitor_response_times():
    """Monitor agent response times."""
    
    recent_times = extract_response_times(last_minutes=10)
    avg_time = sum(recent_times) / len(recent_times) if recent_times else 0
    
    if avg_time > 2000:  # 2 second threshold
        send_alert(
            severity="warning",
            message=f"Slow response times detected: {avg_time:.0f}ms average",
            details={"sample_size": len(recent_times)}
        )
```

### **Dashboard Integration**
```python
# Log metrics for dashboard
def generate_log_metrics():
    """Generate metrics from log data."""
    
    return {
        "total_requests": count_log_entries("Session started", last_hours=24),
        "successful_bookings": count_log_entries("Booking confirmed", last_hours=24),
        "error_rate": calculate_error_rate(last_hours=24),
        "avg_response_time": calculate_avg_response_time(last_hours=24),
        "active_sessions": count_active_sessions(),
        "top_errors": get_top_errors(last_hours=24, limit=5)
    }
```

## Development and Debugging

### **Debug Logging**
```python
# Enable debug logging for development
import logging
logging.getLogger().setLevel(logging.DEBUG)

# Component-specific debug logging
logging.getLogger("agents.booking").setLevel(logging.DEBUG)
logging.getLogger("mcp_servers.firestore").setLevel(logging.DEBUG)

# Conditional debug logging
if os.getenv("DEBUG_MODE") == "true":
    logging.getLogger().setLevel(logging.DEBUG)
```

### **Log Context Management**
```python
import contextvars
from typing import Optional

# Context variables for request tracking
session_id_var = contextvars.ContextVar('session_id', default=None)
user_id_var = contextvars.ContextVar('user_id', default=None)

class ContextualLogger:
    """Logger that automatically includes context variables."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def _add_context(self, extra: dict) -> dict:
        """Add context variables to log extra data."""
        
        context = extra or {}
        
        if session_id := session_id_var.get():
            context['session_id'] = session_id
        
        if user_id := user_id_var.get():
            context['user_id'] = user_id
        
        return context
    
    def info(self, message: str, **extra):
        self.logger.info(message, extra=self._add_context(extra))
    
    def error(self, message: str, **extra):
        self.logger.error(message, extra=self._add_context(extra))
```

## Troubleshooting

### **Common Log Analysis Commands**
```bash
# Check log file size and rotation
ls -lh logs/hospitality.log*

# Monitor log growth rate
watch -n 5 'ls -lh logs/hospitality.log'

# Check for log permission issues
ls -la logs/

# Validate log format
head -20 logs/hospitality.log | python -m json.tool

# Search for specific session
grep "session_12345" logs/hospitality.log | head -10
```

### **Log File Issues**
```bash
# Fix log file permissions
chmod 644 logs/hospitality.log
chown app:app logs/hospitality.log

# Check disk space
df -h logs/

# Manually rotate logs if needed
mv logs/hospitality.log logs/hospitality.log.$(date +%Y%m%d)
touch logs/hospitality.log
```

## Related Documentation
- [Root Management Guide](../MANAGE.md) - System overview and architecture
- [Orchestrator](../orchestrator/MANAGE.md) - Main system coordination
- [Monitoring MCP Server](../mcp_servers/monitoring/MANAGE.md) - System monitoring
- [Configuration](../config/MANAGE.md) - System configuration and settings

## Development Notes
- Centralized logging system for all components
- Structured logging with JSON context data
- Automatic log rotation and retention management
- Integration with monitoring and alerting systems
- Support for different log levels and filtering
- Performance-optimized logging with minimal overhead
