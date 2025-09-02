# Hospitality Multi-Agent Booking System - Implementation Guide

## Overview

This is a **production-ready multi-agent booking system** for luxury villa and property rentals, built using **Google ADK (Agent Development Kit)** with **Firebase/Firestore** integration via **MCP (Model Context Protocol)**. The system orchestrates 7 specialized AI agents to handle the complete guest booking lifecycle from initial inquiry to post-stay feedback.

### Key Features
- **Multi-agent architecture** with specialized roles
- **Idempotent booking creation** preventing duplicates
- **Explainable AI recommendations** with ranking engine
- **Dual memory systems** (short-term sessions + long-term user profiles)
- **Transaction support** with overlap detection
- **Comprehensive testing** suite
- **Feature flags** for flexible deployment

## Technologies & Frameworks

### Core Technologies
- **Python 3.10+** - Primary language
- **Google ADK** - Agent Development Kit for AI agents
- **Firebase Admin SDK** - Firestore database operations
- **MCP (Model Context Protocol)** - Tool integration standard
- **Pydantic 2.0+** - Data validation and serialization
- **Gemini 2.0 Flash** - LLM model for agents

### Development Tools
- **pytest** - Testing framework with async support
- **ruff** - Fast Python linter
- **mypy** - Static type checking
- **black** - Code formatting
- **python-dotenv** - Environment variable management

### Infrastructure
- **Firestore** - NoSQL document database
- **Google Cloud** - Hosting and credentials
- **Redis** (production) - Session storage and caching

## Project Structure

```
hospitality_booking/
├── agents/                    # 7 Specialized AI Agents
│   ├── inquiry/              # Initial greeting & slot collection
│   │   ├── agent.py         # Agent definition
│   │   ├── prompts.py       # System prompts & templates
│   │   └── tools.py         # Validation tools
│   ├── availability/         # Property search & ranking
│   │   ├── agent.py
│   │   ├── ranking.py       # Explainable ranking engine
│   │   └── prompts.py
│   ├── booking/             # Transaction processing
│   │   ├── agent.py
│   │   ├── idempotency.py   # Natural key generation
│   │   └── prompts.py
│   ├── upsell/              # Add-on suggestions
│   ├── confirmation/        # Booking confirmation
│   ├── precheckin/          # Pre-arrival reminders
│   ├── survey/              # Post-stay feedback
│   └── __init__.py          # Agent exports
│
├── orchestrator/             # Main Coordination System
│   └── main.py              # HospitalityOrchestrator class
│
├── mcp_servers/             # MCP Server Implementations
│   ├── firestore/           # Firestore MCP server
│   │   ├── server.py        # Main MCP server
│   │   ├── models.py        # Data models
│   │   └── transactions.py  # Transaction logic
│   ├── monitoring/          # Metrics & monitoring
│   └── notify/              # Notification services
│
├── memory/                  # Memory Management
│   ├── short_term.py        # Session state (STM)
│   └── long_term.py         # User profiles (LTM)
│
├── utils/                   # Shared Utilities
│   ├── validators.py        # Input validation
│   └── formatters.py        # Response formatting
│
├── config/                  # Configuration
│   ├── settings.py          # Environment settings
│   ├── feature_flags.yaml   # Feature toggles
│   └── firestore_indexes.json # Database indexes
│
├── tests/                   # Test Suite
│   ├── test_agents/         # Agent unit tests
│   ├── test_integration/    # End-to-end tests
│   └── test_mcp/           # MCP server tests
│
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Project configuration
└── example_usage.py       # Usage examples
```

## Environment Setup

### 1. Prerequisites
- **Python 3.10+**
- **Firebase project** with Firestore enabled
- **Google Cloud service account** with Firestore permissions

### 2. Installation

```bash
# Clone the repository
cd hospitality_booking

# Install dependencies
pip install -r requirements.txt

# Or using pip-tools for development
pip install -e .
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# Google Cloud / Firebase Configuration
FIRESTORE_PROJECT_ID=your-firebase-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# ADK Configuration
ADK_MODEL=gemini-2.0-flash

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60

# Session Configuration
SESSION_TTL_MINUTES=30
STM_MAX_SIZE_MB=100

# Feature Flags
ENABLE_UPSELL=true
ENABLE_SURVEY=true
ENABLE_PRECHECKIN=true

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=logs/hospitality.log
```

### 4. Firebase Setup

```bash
# Deploy Firestore indexes
firebase deploy --only firestore:indexes

# Verify connection
python test_firestore.py
```

## Starting the System

### Entry Point
The main entry point is `orchestrator/main.py`:

```bash
# Start the orchestrator
python orchestrator/main.py
```

### Alternative: Example Usage
For testing without full ADK setup:

```bash
# Run component examples
python example_usage.py
```

## Execution Flow

### 1. System Initialization
```python
# orchestrator/main.py
orchestrator = HospitalityOrchestrator()
```

**What happens:**
- Initializes **Short-Term Memory** (STM) and **Long-Term Memory** (LTM)
- Establishes **Firestore MCP connection**
- Creates **root orchestrator agent** with all 7 specialized agents
- Sets up **logging** and **error handling**

### 2. Request Processing Flow

```
User Input → Orchestrator → Agent Router → Specialized Agent → MCP Tools → Response
```

**Detailed Flow:**

#### Phase 1: Session Management
```python
session = await stm.get_session(session_id) or await stm.create_session(session_id, user_id)
user_preferences = await ltm.get_user_preferences(user_id) if user_id else {}
```

#### Phase 2: Agent Orchestration
The **HospitalityOrchestrator** routes requests through agents sequentially:

1. **InquiryAgent** - Collects booking requirements
   - City, dates, guests, budget
   - Validates all inputs
   - Updates session slots

2. **AvailabilityAgent** - Searches and ranks properties
   - Queries Firestore via MCP
   - Applies explainable ranking algorithm
   - Presents top 3-5 options

3. **BookingAgent** - Processes transactions
   - Generates natural key for idempotency
   - Validates final availability
   - Calculates pricing with fees/taxes
   - Creates booking atomically

4. **UpsellAgent** - Suggests add-ons
   - Context-aware recommendations
   - Updates booking if accepted

5. **ConfirmationAgent** - Finalizes booking
   - Sends confirmation email
   - Schedules follow-up tasks

6. **PreCheckinAgent** - Pre-arrival (48hrs before)
   - Automated reminder system
   - Collects arrival details

7. **SurveyAgent** - Post-stay (24hrs after checkout)
   - CSAT/NPS feedback collection

### 3. Data Flow Between Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Input    │───▶│   Orchestrator  │───▶│ Specialized     │
│                 │    │                 │    │ Agent           │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   STM Session   │◀───│   Memory Mgmt   │───▶│   LTM Profile   │
│   (30min TTL)   │    │                 │    │   (Persistent)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Firestore     │◀───│   MCP Server    │◀───│   Agent Tools   │
│   Database      │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 4. Key Algorithms

#### Idempotent Booking Creation
```python
natural_key = generate_natural_key(guest_id, property_id, check_in, check_out)
existing = idempotency_manager.check_idempotency(natural_key)
if existing:
    return existing  # Return existing booking
# Create new booking...
```

#### Property Ranking Engine
```python
# agents/availability/ranking.py
def rank_properties(properties, user_preferences, search_criteria):
    scores = []
    for prop in properties:
        score = calculate_base_score(prop, search_criteria)
        score += apply_preference_boost(prop, user_preferences)
        score += apply_recency_boost(prop)
        scores.append((prop, score, generate_reasons(prop)))
    return sorted(scores, key=lambda x: x[1], reverse=True)
```

## Usage Instructions

### Basic Usage

```python
from orchestrator.main import HospitalityOrchestrator

async def main():
    orchestrator = HospitalityOrchestrator()
    
    # Handle user request
    response = await orchestrator.handle_request(
        user_input="I need a villa in Miami for 4 people next weekend",
        session_id="user_session_123",
        user_id="guest_001"  # Optional for personalization
    )
    
    print(response)
```

### Testing Individual Components

```python
# Test memory systems
from memory.short_term import ShortTermMemory
stm = ShortTermMemory()
session = await stm.create_session("test_session", "user_001")

# Test ranking engine
from agents.availability.ranking import PropertyRanker
ranker = PropertyRanker()
ranked = ranker.rank_properties(properties, preferences, criteria)

# Test idempotency
from agents.booking.idempotency import generate_natural_key
key = generate_natural_key("user1", "prop1", "2025-03-15", "2025-03-18")
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_agents/ -v          # Agent tests
pytest tests/test_integration/ -v     # Integration tests
pytest tests/test_mcp/ -v            # MCP server tests

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

### Extending the System

#### Adding a New Agent
1. Create agent directory: `agents/new_agent/`
2. Implement `agent.py`, `prompts.py`, `tools.py`
3. Add to `agents/__init__.py`
4. Register in `orchestrator/main.py`

#### Adding MCP Tools
1. Create tool function in appropriate MCP server
2. Register with `FunctionTool(your_function)`
3. Add to server's tool list

## Configuration & Environment Variables

### Critical Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `FIRESTORE_PROJECT_ID` | ✅ | Firebase project ID | - |
| `GOOGLE_APPLICATION_CREDENTIALS` | ✅ | Path to service account JSON | - |
| `ADK_MODEL` | ❌ | LLM model name | `gemini-2.0-flash` |
| `SESSION_TTL_MINUTES` | ❌ | Session expiration | `30` |
| `LOG_LEVEL` | ❌ | Logging level | `INFO` |

### Feature Flags

Configure in `.env` or `config/feature_flags.yaml`:

```yaml
# Feature toggles
ENABLE_UPSELL: true        # Show add-on suggestions
ENABLE_SURVEY: true        # Post-stay surveys
ENABLE_PRECHECKIN: true    # Pre-arrival reminders
ENABLE_MONITORING: false   # Metrics collection
```

### Business Rules Configuration

```python
# config/settings.py
MIN_BOOKING_DAYS = 1           # Minimum stay
MAX_BOOKING_DAYS = 30          # Maximum stay
MAX_GUESTS_PER_BOOKING = 10    # Guest limit
SERVICE_FEE_PERCENTAGE = 0.1   # 10% service fee
TAX_PERCENTAGE = 0.08          # 8% tax
```

## Gotchas & Important Notes

### 🚨 Critical Requirements

1. **Service Account Permissions**
   - Firestore read/write access required
   - Cloud Storage access for images (if used)
   - Proper IAM roles configured

2. **Firestore Indexes**
   - Must deploy indexes before first run
   - Check `config/firestore_indexes.json`
   - Run: `firebase deploy --only firestore:indexes`

3. **Memory Management**
   - STM has 30-minute TTL by default
   - Sessions auto-expire and cleanup
   - Monitor memory usage in production

### ⚠️ Development Gotchas

1. **MCP Server Connection**
   - Firestore MCP runs as subprocess
   - Check logs if connection fails
   - Ensure Python path is correct

2. **Idempotency Keys**
   - Natural keys prevent duplicate bookings
   - Based on: guest_id + property_id + dates
   - Keys are deterministic and collision-resistant

3. **Agent Orchestration**
   - Agents run sequentially, not parallel
   - Context preserved between agent transfers
   - Session state critical for flow continuity

4. **Date Handling**
   - All dates in ISO format (YYYY-MM-DD)
   - Timezone handling in production deployment
   - Validate date ranges and booking windows

### 🔧 Production Considerations

1. **Scaling**
   - Use Redis for STM in production
   - Implement proper connection pooling
   - Consider agent load balancing

2. **Monitoring**
   - Enable comprehensive logging
   - Set up metrics collection
   - Monitor booking success rates

3. **Security**
   - Validate all user inputs
   - Implement rate limiting
   - Secure service account credentials

## Performance Targets

The system is designed to meet:
- **p95 latency** ≤ 800ms per request
- **Zero double bookings** (idempotency guarantee)
- **Conversion rate** > 40% (inquiry to booking)
- **CSAT/NPS** > 4.5/5.0 (user satisfaction)

## Troubleshooting

### Common Issues

1. **"Firebase not initialized"**
   - Check `GOOGLE_APPLICATION_CREDENTIALS` path
   - Verify service account permissions
   - Ensure Firebase project exists

2. **"MCP connection failed"**
   - Check Python path in MCP server startup
   - Verify firestore server.py is executable
   - Check logs in `logs/` directory

3. **"Session not found"**
   - Sessions expire after TTL (default 30min)
   - Check session ID consistency
   - Verify STM configuration

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python orchestrator/main.py

# Run validation script
python validate_structure.py
```

---

## Quick Start Checklist

- [ ] Python 3.10+ installed
- [ ] Firebase project created
- [ ] Service account downloaded
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured
- [ ] Firestore indexes deployed
- [ ] Test connection (`python test_firestore.py`)
- [ ] Run example (`python example_usage.py`)
- [ ] Start orchestrator (`python orchestrator/main.py`)

**The system is now ready for booking requests!**

---

*This implementation provides a complete, production-ready multi-agent booking system with strong guarantees around consistency, idempotency, and user experience.*
