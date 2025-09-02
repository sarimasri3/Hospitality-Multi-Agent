# Hospitality Multi-Agent Booking System

A production-ready multi-agent booking system using Google ADK with Firebase/Firestore MCP integration for hospitality management.

## Overview

This system implements a complete guest booking lifecycle with orchestrated agents handling:
- Guest inquiry and slot collection
- Property availability search and ranking
- Transactional booking creation with idempotency
- Upsell opportunities
- Booking confirmation
- Pre-check-in reminders
- Post-stay surveys

## Architecture

### Agents

1. **InquiryAgent**: Handles initial greeting and collects booking requirements (city, dates, guests, budget)
2. **AvailabilityAgent**: Searches and ranks properties based on guest preferences
3. **BookingAgent**: Creates bookings with transaction support and idempotency
4. **UpsellAgent**: Suggests relevant add-on services
5. **ConfirmationAgent**: Provides booking confirmation and sends emails
6. **PreCheckinAgent**: Manages pre-arrival communication
7. **SurveyAgent**: Collects post-stay feedback and metrics

### Core Components

- **Orchestrator**: Coordinates agent interactions and maintains flow state
- **Memory Management**:
  - Short-term Memory (STM): Session state with TTL
  - Long-term Memory (LTM): User profiles and preferences
- **Firestore MCP Server**: Handles all database operations
- **Ranking Engine**: Explainable property scoring and recommendations

## Installation

1. Clone the repository:
```bash
cd hospitality_booking
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Set up Firebase:
- Create a Firebase project
- Download service account credentials
- Set `GOOGLE_APPLICATION_CREDENTIALS` in .env

## Usage

### Running the Orchestrator

```python
import asyncio
from orchestrator import HospitalityOrchestrator

async def main():
    orchestrator = HospitalityOrchestrator()
    
    # Handle a user request
    response = await orchestrator.handle_request(
        "I need a villa in Miami for 4 people",
        session_id="unique_session_id",
        user_id="optional_user_id"
    )
    print(response)

asyncio.run(main())
```

### Starting the MCP Server

```bash
python mcp_servers/firestore/server.py
```

## Configuration

Edit `config/settings.py` to customize:
- Session TTL
- Rate limits
- Pricing rules
- Feature flags
- Upsell packages

## Testing

Run unit tests:
```bash
pytest tests/test_agents/ -v
```

Run integration tests:
```bash
pytest tests/test_integration/ -v
```

Run all tests:
```bash
pytest tests/ -v
```

## Performance Metrics

Target SLOs:
- p95 latency: < 800ms
- Zero double bookings
- Conversion rate: > 40%
- CSAT/NPS: > 4.5/5.0

## Project Structure

```
hospitality_booking/
├── agents/              # Specialized agents
├── orchestrator/        # Main orchestration logic
├── mcp_servers/         # MCP server implementations
├── memory/              # STM/LTM management
├── config/              # Configuration files
├── tests/               # Test suites
└── utils/               # Utility functions
```

## Features

- **Idempotent Bookings**: Natural key generation prevents duplicates
- **Transaction Support**: Atomic booking creation with overlap detection
- **Explainable Ranking**: Clear reasons for property recommendations
- **Personalization**: Learning from user preferences and history
- **Comprehensive Testing**: Unit and integration test coverage
- **Observability**: Structured logging and metrics

## Contributing

1. Follow PEP8 style guidelines
2. Add tests for new features
3. Update documentation
4. Run validation before submitting

## License

Copyright 2025 - All rights reserved