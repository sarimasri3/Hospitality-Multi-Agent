# Config Directory Management

## Purpose & Responsibilities

The `config/` directory manages **system configuration, environment settings, and business rules** for the hospitality booking platform. It centralizes all configurable parameters, feature flags, database indexes, and application settings to enable flexible deployment and easy maintenance.

## Directory Structure

```
config/
├── settings.py              # Main configuration & environment variables
├── feature_flags.yaml       # Feature toggles & experimental features
└── firestore_indexes.json   # Database index definitions
```

## Core Components

### Application Settings (`settings.py`)

**Purpose**: Centralized configuration management with environment variable integration

**Configuration Categories**:

#### **Environment & Infrastructure**
```python
# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = BASE_DIR / "logs"

# Google Cloud / Firebase
FIRESTORE_PROJECT_ID = os.getenv("FIRESTORE_PROJECT_ID", "hospitality-booking-dev")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# ADK Configuration
ADK_MODEL = os.getenv("ADK_MODEL", "gemini-2.0-flash")
```

#### **Session & Memory Management**
```python
# Rate Limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

# Session Configuration
SESSION_TTL_MINUTES = int(os.getenv("SESSION_TTL_MINUTES", "30"))
STM_MAX_SIZE_MB = int(os.getenv("STM_MAX_SIZE_MB", "100"))
```

#### **Business Rules**
```python
# Booking Constraints
MIN_BOOKING_DAYS = 1              # Minimum nights
MAX_BOOKING_DAYS = 30             # Maximum nights
MAX_GUESTS_PER_BOOKING = 10       # Guest limit
BOOKING_ADVANCE_DAYS = 365        # Booking window

# Pricing Configuration
BASE_CLEANING_FEE = 50.0
SERVICE_FEE_PERCENTAGE = 0.1      # 10% service fee
TAX_PERCENTAGE = 0.08             # 8% tax
```

#### **Feature Flags**
```python
# Feature Toggles
ENABLE_UPSELL = os.getenv("ENABLE_UPSELL", "true").lower() == "true"
ENABLE_SURVEY = os.getenv("ENABLE_SURVEY", "true").lower() == "true"
ENABLE_PRECHECKIN = os.getenv("ENABLE_PRECHECKIN", "true").lower() == "true"
```

#### **Service Configuration**
```python
# Upsell Packages
UPSELL_PACKAGES = {
    "early_checkin": {"name": "Early Check-in", "price": 50.0},
    "late_checkout": {"name": "Late Check-out", "price": 50.0},
    "welcome_basket": {"name": "Welcome Basket", "price": 75.0},
    "spa_package": {"name": "Spa Package", "price": 200.0},
    "chef_service": {"name": "Private Chef", "price": 300.0}
}

# Timing Configuration
SURVEY_DELAY_HOURS = 24           # Post-checkout survey delay
PRECHECKIN_REMINDER_HOURS = 48    # Pre-arrival reminder timing
```

### Feature Flags (`feature_flags.yaml`)

**Purpose**: Runtime feature toggles for A/B testing and gradual rollouts

**Structure**:
```yaml
# Core Features
booking:
  enable_upsell: true
  enable_survey: true
  enable_precheckin: true
  enable_payment_simulation: true

# Agent Features
agents:
  enable_availability_ranking: true
  enable_personalization: true
  enable_alternative_suggestions: true

# Experimental Features
experimental:
  enable_ai_pricing: false
  enable_smart_recommendations: false
  enable_voice_interface: false

# Monitoring & Analytics
monitoring:
  enable_metrics_collection: true
  enable_performance_tracking: true
  enable_error_reporting: true
```

### Database Indexes (`firestore_indexes.json`)

**Purpose**: Firestore composite index definitions for optimal query performance

**Index Structure**:
```json
{
  "indexes": [
    {
      "collectionGroup": "properties",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "status", "order": "ASCENDING"},
        {"fieldPath": "location.city", "order": "ASCENDING"},
        {"fieldPath": "minimum_price", "order": "ASCENDING"}
      ]
    },
    {
      "collectionGroup": "bookings",
      "queryScope": "COLLECTION", 
      "fields": [
        {"fieldPath": "property_id", "order": "ASCENDING"},
        {"fieldPath": "check_in_date", "order": "ASCENDING"},
        {"fieldPath": "check_out_date", "order": "ASCENDING"}
      ]
    },
    {
      "collectionGroup": "users",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "email", "order": "ASCENDING"}
      ]
    }
  ]
}
```

## How to Use & Extend

### Using Configuration Settings

**In Application Code**:
```python
from config.settings import (
    FIRESTORE_PROJECT_ID,
    SESSION_TTL_MINUTES,
    ENABLE_UPSELL,
    UPSELL_PACKAGES
)

# Use in orchestrator
class HospitalityOrchestrator:
    def __init__(self):
        self.project_id = FIRESTORE_PROJECT_ID
        self.session_ttl = SESSION_TTL_MINUTES
```

**In Agent Logic**:
```python
from config.settings import ENABLE_UPSELL, UPSELL_PACKAGES

async def suggest_upsells(booking_data):
    if not ENABLE_UPSELL:
        return []
    
    suggestions = []
    for key, package in UPSELL_PACKAGES.items():
        # Logic to determine relevant upsells
        suggestions.append(package)
    
    return suggestions
```

### Environment Variable Management

**Development Setup** (`.env`):
```bash
# Core Configuration
FIRESTORE_PROJECT_ID=hospitality-dev
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
ADK_MODEL=gemini-2.0-flash

# Feature Flags
ENABLE_UPSELL=true
ENABLE_SURVEY=true
ENABLE_PRECHECKIN=true

# Performance Settings
SESSION_TTL_MINUTES=30
RATE_LIMIT_PER_MINUTE=60
```

**Production Setup**:
```bash
# Production values
FIRESTORE_PROJECT_ID=hospitality-prod
SESSION_TTL_MINUTES=60
RATE_LIMIT_PER_MINUTE=120
LOG_LEVEL=INFO
```

### Adding New Configuration

**1. Add to `settings.py`**:
```python
# New business rule
MAX_CONCURRENT_BOOKINGS = int(os.getenv("MAX_CONCURRENT_BOOKINGS", "5"))

# New feature flag
ENABLE_NEW_FEATURE = os.getenv("ENABLE_NEW_FEATURE", "false").lower() == "true"

# New service configuration
NEW_SERVICE_CONFIG = {
    "timeout": int(os.getenv("NEW_SERVICE_TIMEOUT", "30")),
    "retry_count": int(os.getenv("NEW_SERVICE_RETRIES", "3"))
}
```

**2. Update `.env.example`**:
```bash
# New Feature Configuration
MAX_CONCURRENT_BOOKINGS=5
ENABLE_NEW_FEATURE=false
NEW_SERVICE_TIMEOUT=30
```

**3. Use in Application**:
```python
from config.settings import ENABLE_NEW_FEATURE, NEW_SERVICE_CONFIG

if ENABLE_NEW_FEATURE:
    # New feature implementation
    service = NewService(**NEW_SERVICE_CONFIG)
```

### Feature Flag Management

**Runtime Feature Toggles**:
```python
import yaml
from pathlib import Path

def load_feature_flags():
    """Load feature flags from YAML file."""
    flags_path = Path(__file__).parent / "feature_flags.yaml"
    with open(flags_path, 'r') as f:
        return yaml.safe_load(f)

def is_feature_enabled(feature_path: str) -> bool:
    """Check if a feature is enabled."""
    flags = load_feature_flags()
    keys = feature_path.split('.')
    
    current = flags
    for key in keys:
        if key not in current:
            return False
        current = current[key]
    
    return bool(current)

# Usage
if is_feature_enabled('experimental.ai_pricing'):
    # Use AI pricing
    pass
```

### Database Index Management

**Deploy Indexes**:
```bash
# Deploy to Firebase
firebase deploy --only firestore:indexes

# Verify deployment
firebase firestore:indexes
```

**Add New Index**:
```json
{
  "collectionGroup": "new_collection",
  "queryScope": "COLLECTION",
  "fields": [
    {"fieldPath": "field1", "order": "ASCENDING"},
    {"fieldPath": "field2", "order": "DESCENDING"}
  ]
}
```

## Configuration Patterns

### Environment-Specific Settings

**Multi-Environment Support**:
```python
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    # Production settings
    DEBUG = False
    SESSION_TTL_MINUTES = 60
    RATE_LIMIT_PER_MINUTE = 120
elif ENVIRONMENT == "staging":
    # Staging settings
    DEBUG = True
    SESSION_TTL_MINUTES = 45
    RATE_LIMIT_PER_MINUTE = 90
else:
    # Development settings
    DEBUG = True
    SESSION_TTL_MINUTES = 30
    RATE_LIMIT_PER_MINUTE = 60
```

### Configuration Validation

**Startup Validation**:
```python
def validate_configuration():
    """Validate critical configuration on startup."""
    errors = []
    
    if not FIRESTORE_PROJECT_ID:
        errors.append("FIRESTORE_PROJECT_ID is required")
    
    if not GOOGLE_APPLICATION_CREDENTIALS:
        errors.append("GOOGLE_APPLICATION_CREDENTIALS is required")
    
    if SESSION_TTL_MINUTES < 1:
        errors.append("SESSION_TTL_MINUTES must be positive")
    
    if errors:
        raise ValueError(f"Configuration errors: {', '.join(errors)}")

# Call on startup
validate_configuration()
```

## Integration with Other Directories

### → `orchestrator/`
- **Environment Settings**: Database connection, model configuration
- **Feature Flags**: Conditional agent execution
- **Business Rules**: Booking constraints and validation

### → `agents/`
- **Feature Flags**: Agent availability and behavior
- **Business Rules**: Validation limits and pricing rules
- **Service Configuration**: Upsell packages and timing

### → `memory/`
- **TTL Settings**: Session expiration configuration
- **Size Limits**: Memory usage thresholds
- **Cleanup Settings**: Maintenance intervals

### → `mcp_servers/`
- **Database Configuration**: Firestore project and credentials
- **Index Definitions**: Query optimization
- **Connection Settings**: Timeouts and retry logic

### → `utils/`
- **Validation Rules**: Business constraint enforcement
- **Formatting Standards**: Currency and date formats
- **Error Messages**: Standardized error responses

## Monitoring & Maintenance

### Configuration Monitoring

**Health Checks**:
```python
def health_check():
    """Check configuration health."""
    checks = {
        "firestore_configured": bool(FIRESTORE_PROJECT_ID),
        "credentials_exist": os.path.exists(GOOGLE_APPLICATION_CREDENTIALS or ""),
        "feature_flags_loaded": load_feature_flags() is not None
    }
    
    return {
        "healthy": all(checks.values()),
        "checks": checks
    }
```

**Configuration Drift Detection**:
```python
def detect_config_drift():
    """Detect configuration changes."""
    current_config = get_current_config()
    baseline_config = load_baseline_config()
    
    differences = compare_configs(current_config, baseline_config)
    if differences:
        logger.warning(f"Configuration drift detected: {differences}")
```

## Troubleshooting

### Common Issues

1. **Missing Environment Variables**
   ```python
   # Check required variables
   required_vars = [
       "FIRESTORE_PROJECT_ID",
       "GOOGLE_APPLICATION_CREDENTIALS"
   ]
   
   missing = [var for var in required_vars if not os.getenv(var)]
   if missing:
       print(f"Missing required variables: {missing}")
   ```

2. **Feature Flag Issues**
   ```python
   # Debug feature flags
   try:
       flags = load_feature_flags()
       print("Feature flags loaded:", flags)
   except Exception as e:
       print(f"Feature flag error: {e}")
   ```

3. **Index Deployment Failures**
   ```bash
   # Check index status
   firebase firestore:indexes
   
   # Redeploy if needed
   firebase deploy --only firestore:indexes --force
   ```

### Debug Commands

```python
# Test configuration loading
from config.settings import *

print("Configuration loaded:")
print(f"Project ID: {FIRESTORE_PROJECT_ID}")
print(f"Model: {ADK_MODEL}")
print(f"Session TTL: {SESSION_TTL_MINUTES}")
print(f"Upsell enabled: {ENABLE_UPSELL}")

# Test feature flags
from config.settings import load_feature_flags
flags = load_feature_flags()
print("Feature flags:", flags)
```

## Testing

### Test Coverage
- **Test Files**: Configuration testing integrated into system tests
- **Coverage**: Environment variable loading, feature flag validation, business rules
- **Test Types**: Configuration validation tests, environment setup tests

### Running Tests
```bash
# Test configuration loading
python -c "from config.settings import *; print('Config loaded successfully')"

# Validate feature flags
python -c "from config.settings import load_feature_flags; print(load_feature_flags())"

# Test environment variables
python -c "import os; print('Required vars:', [v for v in ['FIRESTORE_PROJECT_ID'] if os.getenv(v)])"
```

### Configuration Validation
- Environment variable presence and format
- Feature flag YAML syntax and structure
- Business rule consistency and ranges
- Database index deployment verification

## Related Tasks

### High Priority
- **Production Deployment** (TASK_PLAN.md #1): Configure production environment variables and settings
- **Advanced Security** (TASK_PLAN.md #9): Secure configuration management and secrets
- **Performance Optimization** (TASK_PLAN.md #3): Optimize configuration loading and caching

### Medium Priority
- **Enhanced Property Management** (TASK_PLAN.md #5): Add property-specific configuration options
- **User Experience Enhancement** (TASK_PLAN.md #6): Configure personalization settings

### Ongoing
- **Code Quality** (TASK_PLAN.md #10): Regular configuration review and cleanup
- **Testing QA** (TASK_PLAN.md #11): Expand configuration validation testing

---

**Next Steps**: See root `MANAGE.md` for complete system overview and configuration integration details.
