# Hospitality Booking System - Master Management Guide

## System Overview

The **Hospitality Multi-Agent Booking System** is a sophisticated AI-powered platform designed for luxury villa and property rental management. It orchestrates 7 specialized AI agents through a complete booking lifecycle, from initial inquiry to post-stay survey, using Google ADK and Firebase Firestore via MCP (Model Context Protocol).

## Architecture & Core Components

### 🏗️ **System Architecture**
```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 ORCHESTRATOR                                │
│  • Request routing & agent coordination                     │
│  • Session management & memory integration                  │
│  • Error handling & response formatting                     │
└─────────────┬───────────────────────────┬───────────────────┘
              │                           │
    ┌─────────▼─────────┐       ┌─────────▼─────────┐
    │     AGENTS        │       │      MEMORY       │
    │  • 7 Specialized  │       │  • STM (Session)  │
    │  • Phase-specific │       │  • LTM (Profile)  │
    │  • Tool-equipped  │       │  • Auto-cleanup   │
    └─────────┬─────────┘       └───────────────────┘
              │
    ┌─────────▼─────────┐       ┌───────────────────┐
    │   MCP SERVERS     │       │      CONFIG       │
    │  • Firestore      │       │  • Settings       │
    │  • Monitoring     │       │  • Feature Flags  │
    │  • Notifications  │       │  • Business Rules │
    └─────────┬─────────┘       └───────────────────┘
              │
    ┌─────────▼─────────┐       ┌───────────────────┐
    │     DATABASE      │       │      UTILS        │
    │  • Firebase       │       │  • Validators     │
    │  • Transactions   │       │  • Formatters     │
    │  • Indexes        │       │  • Helpers        │
    └───────────────────┘       └───────────────────┘
```

### 🤖 **Agent Ecosystem**
The system employs **7 specialized agents** handling distinct phases:

1. **InquiryAgent** - Captures and validates booking requirements
2. **AvailabilityAgent** - Searches and ranks available properties  
3. **BookingAgent** - Processes reservations with idempotency
4. **UpsellAgent** - Suggests premium services and upgrades
5. **ConfirmationAgent** - Sends booking confirmations and details
6. **PreCheckinAgent** - Manages pre-arrival communications
7. **SurveyAgent** - Collects post-stay feedback and ratings

## Directory Structure & Navigation

### 📁 **Core Directories**

| Directory | Purpose | Key Files | Management Guide |
|-----------|---------|-----------|------------------|
| **`orchestrator/`** | Central coordination & request routing | `main.py` | [orchestrator/MANAGE.md](orchestrator/MANAGE.md) |
| **`agents/`** | Specialized AI agents for booking phases | 7 agent subdirectories | [agents/MANAGE.md](agents/MANAGE.md) |
| **`mcp_servers/`** | Database & external service integration | `firestore/server.py` | [mcp_servers/MANAGE.md](mcp_servers/MANAGE.md) |
| **`memory/`** | Session & user profile management | `short_term.py`, `long_term.py` | [memory/MANAGE.md](memory/MANAGE.md) |
| **`config/`** | System configuration & feature flags | `settings.py`, `feature_flags.yaml` | [config/MANAGE.md](config/MANAGE.md) |
| **`utils/`** | Shared utilities & helper functions | `validators.py`, `formatters.py` | [utils/MANAGE.md](utils/MANAGE.md) |
| **`tests/`** | Comprehensive test suite | Unit & integration tests | [tests/MANAGE.md](tests/MANAGE.md) |

### 📋 **Root-Level Files**

| File | Purpose | Description |
|------|---------|-------------|
| `IMPLEMENTATION_GUIDE.md` | Complete system documentation | Setup, usage, architecture, troubleshooting |
| `IMPLEMENTATION_SUMMARY.md` | High-level project overview | Components, features, validation results |
| `example_usage.py` | Usage examples & demonstrations | Memory, ranking, idempotency examples |
| `requirements.txt` | Python dependencies | All required packages with versions |
| `pyproject.toml` | Project metadata & tool configs | Build system, linting, testing configs |
| `.env.example` | Environment variable template | Required settings for deployment |

## Request Flow & Agent Orchestration

### 🔄 **Complete Booking Flow**
```
User Request → Orchestrator → Agent Selection → Tool Execution → Response
     ↓              ↓              ↓              ↓              ↓
Session Mgmt → Memory Access → MCP Integration → DB Operations → Formatted Output
```

### 📋 **Agent Execution Sequence**
1. **Inquiry** → Validate requirements (city, dates, guests, budget)
2. **Availability** → Search properties, rank by preferences, calculate pricing
3. **Booking** → Create reservation with idempotency, handle payments
4. **Upsell** → Suggest premium services (early checkin, spa, chef)
5. **Confirmation** → Send booking details, payment receipts, instructions
6. **PreCheckin** → Pre-arrival reminders, check-in instructions
7. **Survey** → Post-stay feedback collection and rating requests

## Key Technologies & Dependencies

### 🛠️ **Core Technologies**
- **Python 3.10+** - Primary development language
- **Google ADK** - Agent Development Kit for AI agents
- **Firebase Firestore** - NoSQL database with real-time sync
- **MCP Protocol** - Model Context Protocol for tool integration
- **Pydantic** - Data validation and serialization
- **Gemini 2.0 Flash** - Large Language Model

### 📦 **Key Dependencies**
```python
google-adk>=0.1.0          # Agent framework
firebase-admin>=6.0.0      # Firebase integration  
mcp>=0.1.0                 # Model Context Protocol
pydantic>=2.0.0            # Data validation
python-dotenv>=1.0.0       # Environment management
pytest>=7.0.0              # Testing framework
```

## Environment Setup & Configuration

### 🔧 **Required Environment Variables**
```bash
# Core Configuration
FIRESTORE_PROJECT_ID=your-firebase-project
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
ADK_MODEL=gemini-2.0-flash

# Feature Flags
ENABLE_UPSELL=true
ENABLE_SURVEY=true
ENABLE_PRECHECKIN=true

# Performance Settings
SESSION_TTL_MINUTES=30
RATE_LIMIT_PER_MINUTE=60
```

### ⚙️ **Configuration Management**
- **Settings**: Centralized in `config/settings.py`
- **Feature Flags**: Runtime toggles in `config/feature_flags.yaml`
- **Database Indexes**: Optimized queries in `config/firestore_indexes.json`
- **Business Rules**: Booking constraints and pricing rules

## Data Models & Storage

### 🗄️ **Core Data Models**
```python
# User Profile
{
    "user_id": "uuid",
    "email": "user@example.com", 
    "preferences": {...},
    "booking_history": [...]
}

# Property Listing
{
    "property_id": "uuid",
    "name": "Luxury Villa",
    "location": {"city": "Miami", "coordinates": {...}},
    "capacity": 8,
    "amenities": ["pool", "wifi", "kitchen"],
    "pricing": {...}
}

# Booking Record
{
    "booking_id": "uuid",
    "property_id": "uuid",
    "user_id": "uuid", 
    "dates": {"check_in": "2025-03-15", "check_out": "2025-03-18"},
    "guests": 4,
    "total_price": 1200.0,
    "status": "confirmed"
}
```

### 💾 **Storage Systems**
- **Firestore Collections**: `users`, `properties`, `bookings`, `sessions`
- **Short-Term Memory**: Session state (30min TTL)
- **Long-Term Memory**: User profiles and preferences
- **Caching**: Redis recommended for production STM

## Usage & Getting Started

### 🚀 **Quick Start**
```bash
# 1. Clone and setup
git clone <repository>
cd hospitality_booking
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your Firebase credentials

# 3. Run example
python example_usage.py

# 4. Start orchestrator
python -m orchestrator.main
```

### 💬 **Basic Usage Example**
```python
from orchestrator.main import HospitalityOrchestrator

# Initialize orchestrator
orchestrator = HospitalityOrchestrator()

# Process user request
response = await orchestrator.process_message(
    user_id="user123",
    message="I need a villa in Miami for 4 guests from March 15-18"
)

print(response)
```

## Extension & Development

### 🔧 **Adding New Agents**
1. **Create agent directory**: `agents/new_agent/`
2. **Implement agent class**: Inherit from `google_adk.Agent`
3. **Define tools**: Create agent-specific functionality
4. **Add to orchestrator**: Register in agent flow
5. **Write tests**: Unit and integration tests

### 🛠️ **Adding MCP Tools**
1. **Define tool function**: In appropriate MCP server
2. **Register tool**: Add to MCP server tool list
3. **Update agent**: Add tool to agent's available tools
4. **Test integration**: Verify tool functionality

### 📊 **Extending Memory Systems**
1. **STM Extensions**: Add new session data types
2. **LTM Extensions**: Expand user profile schema
3. **Cleanup Logic**: Update expiration and maintenance
4. **Performance**: Monitor memory usage and optimize

## Monitoring & Operations

### 📈 **Key Metrics**
- **Request Volume**: Requests per minute/hour
- **Agent Performance**: Response times by agent
- **Booking Success Rate**: Completed vs failed bookings
- **Memory Usage**: STM/LTM storage consumption
- **Database Performance**: Query times and index usage

### 🔍 **Health Checks**
```python
# System health endpoint
GET /health
{
    "status": "healthy",
    "components": {
        "orchestrator": "up",
        "agents": "7/7 available", 
        "mcp_servers": "connected",
        "database": "connected",
        "memory": "optimal"
    }
}
```

### 📝 **Logging & Debugging**
- **Log Location**: `logs/hospitality.log`
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Structured Logging**: JSON format with request IDs
- **Error Tracking**: Comprehensive error context

## Security & Best Practices

### 🔒 **Security Measures**
- **Input Validation**: All user inputs sanitized
- **Authentication**: Firebase Auth integration
- **Data Encryption**: At rest and in transit
- **API Rate Limiting**: Configurable request limits
- **Audit Logging**: All booking operations logged

### ✅ **Best Practices**
- **Idempotency**: Prevent duplicate bookings
- **Transaction Safety**: Database consistency
- **Error Handling**: Graceful failure recovery
- **Testing**: Comprehensive test coverage
- **Documentation**: Keep guides updated

## Troubleshooting & Support

### 🚨 **Common Issues**

1. **Agent Not Responding**
   ```bash
   # Check agent status
   python -c "from orchestrator.main import HospitalityOrchestrator; print(HospitalityOrchestrator().get_agent_status())"
   ```

2. **Database Connection Issues**
   ```bash
   # Test Firestore connection
   python test_firestore.py
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   python -c "from memory import short_term; print(short_term.get_memory_stats())"
   ```

### 🔧 **Debug Commands**
```bash
# Validate system structure
python validate_structure.py

# Run comprehensive tests
pytest tests/ -v

# Check configuration
python -c "from config.settings import *; print('Config loaded successfully')"
```

## Performance & Scaling

### ⚡ **Performance Targets**
- **Response Time**: < 2 seconds for simple queries
- **Throughput**: 100+ concurrent requests
- **Availability**: 99.9% uptime
- **Memory Usage**: < 1GB per orchestrator instance

### 📈 **Scaling Strategies**
- **Horizontal Scaling**: Multiple orchestrator instances
- **Agent Scaling**: Independent agent deployment
- **Database Scaling**: Firestore auto-scaling
- **Caching**: Redis for STM in production
- **Load Balancing**: Distribute requests across instances

## Development Workflow

### 🔄 **Development Process**
1. **Feature Planning**: Define requirements and scope
2. **Implementation**: Code new features with tests
3. **Testing**: Unit, integration, and E2E tests
4. **Code Review**: Peer review and quality checks
5. **Deployment**: Staged rollout with monitoring

### 🧪 **Testing Strategy**
- **Unit Tests**: Individual component testing
- **Integration Tests**: Cross-component workflows
- **E2E Tests**: Complete booking scenarios
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability assessments

## Future Roadmap

### 🚀 **Planned Features**
- **Voice Interface**: Natural language voice booking
- **AI Pricing**: Dynamic pricing based on demand
- **Smart Recommendations**: ML-powered property suggestions
- **Mobile App**: Native iOS/Android applications
- **Multi-language**: International market support

### 🔮 **Technical Improvements**
- **GraphQL API**: More efficient data fetching
- **Event Streaming**: Real-time updates via Kafka
- **Microservices**: Service decomposition for scale
- **Kubernetes**: Container orchestration
- **Observability**: Enhanced monitoring and tracing

---

## Quick Navigation

### 📚 **Essential Reading**
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Complete setup and usage guide
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - High-level project overview

### 🗂️ **Directory Guides**
- **[Orchestrator](orchestrator/MANAGE.md)** - Central coordination and request routing
- **[Memory Management](memory/MANAGE.md)** - Session state and long-term storage
- **[Configuration](config/MANAGE.md)** - System settings and feature flags
- **[Utilities](utils/MANAGE.md)** - Shared validation and formatting functions
- **[Agents Overview](agents/MANAGE.md)** - Multi-agent system architecture
- **[Inquiry Agent](agents/inquiry/MANAGE.md)** - Initial guest interaction and slot collection
- **[Availability Agent](agents/availability/MANAGE.md)** - Property search and ranking
- **[Booking Agent](agents/booking/MANAGE.md)** - Reservation processing and confirmation
- **[Upsell Agent](agents/upsell/MANAGE.md)** - Add-on services and revenue optimization
- **[Confirmation Agent](agents/confirmation/MANAGE.md)** - Booking confirmation and communication
- **[Pre-checkin Agent](agents/precheckin/MANAGE.md)** - Pre-arrival preparation and instructions
- **[Survey Agent](agents/survey/MANAGE.md)** - Post-stay feedback and satisfaction metrics
- **[MCP Servers Overview](mcp_servers/MANAGE.md)** - Model Context Protocol integration
- **[Firestore Server](mcp_servers/firestore/MANAGE.md)** - Database operations and transactions
- **[Monitoring Server](mcp_servers/monitoring/MANAGE.md)** - System health and performance tracking
- **[Notification Server](mcp_servers/notify/MANAGE.md)** - Multi-channel communication system
- **[Tests Overview](tests/MANAGE.md)** - Comprehensive testing framework
- **[Agent Tests](tests/test_agents/MANAGE.md)** - Individual agent functionality testing
- **[Integration Tests](tests/test_integration/MANAGE.md)** - End-to-end workflow validation
- **[MCP Tests](tests/test_mcp/MANAGE.md)** - Protocol compliance and server testing
- **[Logs Management](logs/MANAGE.md)** - Centralized logging and monitoring

### 🛠️ **Development Resources**
- [example_usage.py](example_usage.py) - Usage examples
- [requirements.txt](requirements.txt) - Dependencies
- [.env.example](.env.example) - Environment setup

---

**For immediate assistance or questions, refer to the specific directory MANAGE.md files or the comprehensive IMPLEMENTATION_GUIDE.md.**
