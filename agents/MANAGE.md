# Agents Directory Management

## Purpose & Responsibilities

The `agents/` directory contains **7 specialized AI agents** that handle different phases of the hospitality booking lifecycle. Each agent is a self-contained module with its own prompts, tools, and business logic, orchestrated by the main system to provide a seamless booking experience.

## Directory Structure

```
agents/
├── __init__.py              # Agent exports for orchestrator
├── inquiry/                 # Phase 1: Initial greeting & slot collection
│   ├── agent.py            # InquiryAgent definition
│   ├── prompts.py          # System prompts & conversation templates
│   ├── tools.py            # Validation & slot extraction tools
│   └── __init__.py         # Package exports
├── availability/            # Phase 2: Property search & ranking
│   ├── agent.py            # AvailabilityAgent definition
│   ├── prompts.py          # Search & presentation prompts
│   ├── ranking.py          # Explainable ranking engine
│   └── __init__.py         # Package exports
├── booking/                 # Phase 3: Transaction processing
│   ├── agent.py            # BookingAgent definition
│   ├── prompts.py          # Booking confirmation prompts
│   ├── idempotency.py      # Natural key generation & duplicate prevention
│   └── __init__.py         # Package exports
├── upsell/                  # Phase 4: Add-on suggestions
│   ├── agent.py            # UpsellAgent definition
│   └── __init__.py         # Package exports
├── confirmation/            # Phase 5: Booking confirmation
│   ├── agent.py            # ConfirmationAgent definition
│   └── __init__.py         # Package exports
├── precheckin/              # Phase 6: Pre-arrival reminders (48hrs before)
│   ├── agent.py            # PreCheckinAgent definition
│   └── __init__.py         # Package exports
└── survey/                  # Phase 7: Post-stay feedback (24hrs after)
    ├── agent.py            # SurveyAgent definition
    └── __init__.py         # Package exports
```

## Agent Flow & Interactions

### Sequential Agent Orchestration

1. **InquiryAgent** → Collects: city, dates, guests, budget
2. **AvailabilityAgent** → Searches & ranks properties
3. **BookingAgent** → Processes transaction with idempotency
4. **UpsellAgent** → Suggests relevant add-ons
5. **ConfirmationAgent** → Finalizes booking & sends confirmation
6. **PreCheckinAgent** → Automated 48hr reminder (scheduled)
7. **SurveyAgent** → Post-stay feedback collection (scheduled)

### Agent Architecture Pattern

Each agent follows a consistent structure:
- **agent.py**: Google ADK Agent definition with tools
- **prompts.py**: System prompts, instructions, and templates
- **tools.py**: Business logic functions (where applicable)
- **__init__.py**: Package exports for orchestrator

## Key Components

### 1. InquiryAgent (`inquiry/`)
**Purpose**: Initial greeting and slot collection
- **Tools**: `validate_city()`, `validate_dates()`, `validate_guests()`, `validate_budget()`, `extract_slots_from_message()`, `compile_session_slots()`
- **Validation**: Supports 25+ cities, date ranges, guest limits (1-10), budget parsing
- **Flow**: Greets → Collects slots → Validates → Confirms → Transfers to availability

### 2. AvailabilityAgent (`availability/`)
**Purpose**: Property search and explainable ranking
- **Core Engine**: `PropertyRanker` class with configurable weights
- **Scoring Factors**: Price (30%), Distance (20%), Capacity fit (20%), Amenity match (20%), Recency (10%)
- **Tools**: `search_and_rank_properties()`, `calculate_total_price()`, `filter_by_amenities()`, `get_alternative_suggestions()`
- **Flow**: Searches → Ranks → Presents top 3-5 → Explains reasons → Gets selection

### 3. BookingAgent (`booking/`)
**Purpose**: Secure transaction processing with idempotency
- **Idempotency**: Natural key generation prevents duplicate bookings
- **Key Generation**: SHA256 hash of `guest_id:property_id:check_in:check_out`
- **Price Calculation**: Base + Service fee (10%) + Cleaning ($50) + Tax (8%) + Add-ons
- **Tools**: `process_booking()`, `validate_booking_capacity()`, `simulate_payment_authorization()`, `format_booking_confirmation()`
- **Flow**: Validates availability → Generates natural key → Checks duplicates → Creates booking → Authorizes payment

### 4. UpsellAgent (`upsell/`)
**Purpose**: Context-aware add-on suggestions
- **Add-ons**: Early check-in ($50), Late checkout ($50), Welcome basket ($75), Spa package ($200), Chef service ($300)
- **Flow**: Analyzes booking context → Suggests 2-3 relevant add-ons → Updates booking if accepted

### 5. ConfirmationAgent (`confirmation/`)
**Purpose**: Booking confirmation and communication
- **Flow**: Generates confirmation → Sends email → Explains next steps → Schedules follow-ups

### 6. PreCheckinAgent (`precheckin/`)
**Purpose**: Pre-arrival reminders and instructions
- **Trigger**: 48 hours before check-in (scheduled task)
- **Flow**: Sends reminder → Collects arrival info → Addresses special requests

### 7. SurveyAgent (`survey/`)
**Purpose**: Post-stay feedback collection
- **Trigger**: 24 hours after checkout (scheduled task)
- **Metrics**: CSAT/NPS collection and calculation
- **Flow**: Sends survey → Collects feedback → Calculates metrics → Thanks guest

## How to Use & Extend

### Adding a New Agent

1. **Create Directory Structure**:
   ```bash
   mkdir agents/new_agent
   touch agents/new_agent/__init__.py
   touch agents/new_agent/agent.py
   touch agents/new_agent/prompts.py
   ```

2. **Implement Agent** (`agent.py`):
   ```python
   from google.adk.agents import Agent
   from google.adk.tools.function_tool import FunctionTool
   from .prompts import SYSTEM_PROMPT, INSTRUCTION
   
   new_agent = Agent(
       name="new_agent",
       model="gemini-2.0-flash",
       description="Agent description",
       global_instruction=SYSTEM_PROMPT,
       instruction=INSTRUCTION,
       tools=[FunctionTool(your_tool_function)]
   )
   ```

3. **Add to Main Package** (`agents/__init__.py`):
   ```python
   from .new_agent import new_agent
   __all__ = [..., 'new_agent']
   ```

4. **Register in Orchestrator** (`orchestrator/main.py`):
   ```python
   agents=[..., new_agent]
   ```

### Modifying Existing Agents

- **Prompts**: Edit `prompts.py` files to adjust agent behavior
- **Tools**: Add/modify functions in `tools.py` or `agent.py`
- **Validation**: Update validation logic in tool functions
- **Templates**: Modify response templates in `prompts.py`

### Testing Agents

```python
# Test individual agent
from agents.inquiry import inquiry_agent
response = await inquiry_agent.run(messages=[...])

# Test agent tools
from agents.inquiry.tools import validate_city
result = await validate_city("Miami")
```

## Configuration & Environment

### Agent-Specific Settings
- **Model**: All agents use `gemini-2.0-flash` (configurable via `ADK_MODEL`)
- **Prompts**: Stored in individual `prompts.py` files
- **Validation Rules**: Embedded in tool functions

### Dependencies
- **Google ADK**: Agent framework and tool integration
- **Pydantic**: Data validation (where used)
- **Python 3.10+**: Async/await support

## Integration with Other Directories

### → `orchestrator/`
- Imports all agents via `agents/__init__.py`
- Coordinates agent execution flow
- Manages context between agent transfers

### → `memory/`
- Agents access session state via orchestrator
- Long-term preferences influence agent behavior
- Booking history affects recommendations

### → `mcp_servers/`
- Agents use MCP tools for database operations
- Firestore integration for property search and booking creation
- Transaction support for booking operations

### → `config/`
- Feature flags control agent availability (`ENABLE_UPSELL`, `ENABLE_SURVEY`, etc.)
- Business rules affect agent behavior (pricing, validation limits)

### → `utils/`
- Shared validation and formatting utilities
- Currency formatting, date validation
- Input sanitization

## Troubleshooting

### Common Issues

1. **Agent Import Errors**
   - Check `__init__.py` exports
   - Verify circular import issues
   - Ensure all dependencies installed

2. **Tool Function Failures**
   - Validate function signatures match FunctionTool requirements
   - Check async/await usage
   - Verify return type consistency

3. **Prompt Issues**
   - Test prompts in isolation
   - Check template variable substitution
   - Validate prompt length limits

### Debug Commands

```python
# Test agent initialization
from agents import inquiry_agent
print(inquiry_agent.name, inquiry_agent.tools)

# Test tool functions
from agents.inquiry.tools import validate_city
result = await validate_city("Invalid City")
print(result)

# Check agent exports
from agents import __all__
print("Available agents:", __all__)
```

## Performance Considerations

- **Agent Switching**: Sequential execution adds latency but ensures context preservation
- **Tool Execution**: Async tools improve responsiveness
- **Memory Usage**: Each agent loads independently, consider memory limits
- **Prompt Optimization**: Shorter prompts reduce token usage

## Testing

### Test Coverage
- **Test Files**: 
  - `tests/test_agents/test_inquiry_agent.py` - Inquiry agent validation tools
  - `tests/test_agents/test_availability_agent.py` - Property search and ranking
  - `tests/test_agents/test_booking_agent.py` - Booking processing and idempotency
  - `tests/test_agents/test_confirmation_agent.py` - Email generation and audit logs
- **Coverage**: Core agent functionality, tool validation, business logic
- **Test Types**: Unit tests, integration tests, async operation tests

### Running Tests
```bash
# Run all agent tests
pytest tests/test_agents/ -v

# Run specific agent tests
pytest tests/test_agents/test_inquiry_agent.py -v

# Run with coverage
pytest tests/test_agents/ --cov=agents --cov-report=html
```

### Test Scenarios Covered
- Input validation and slot extraction
- Property search, filtering, and ranking
- Booking creation with idempotency checks
- Price calculations and confirmations
- Email generation and audit logging

## Related Tasks

### High Priority
- **Production Deployment** (TASK_PLAN.md #1): Configure agent environment settings
- **Error Handling Enhancement** (TASK_PLAN.md #2): Add retry mechanisms for agent failures
- **Performance Optimization** (TASK_PLAN.md #3): Optimize agent switching and tool execution

### Medium Priority
- **Advanced Booking Features** (TASK_PLAN.md #4): Extend booking agent for complex scenarios
- **Enhanced Property Management** (TASK_PLAN.md #5): Improve availability agent search capabilities
- **User Experience Enhancement** (TASK_PLAN.md #6): Add personalization to agent responses

### Ongoing
- **Code Quality** (TASK_PLAN.md #10): Regular agent prompt and tool optimization
- **Testing QA** (TASK_PLAN.md #11): Expand agent test coverage and edge cases

---

**Next Steps**: See `orchestrator/MANAGE.md` for agent coordination details and `MANAGE.md` in the root for overall system flow.
