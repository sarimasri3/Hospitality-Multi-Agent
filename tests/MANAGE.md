# Tests Directory Management

## Purpose & Responsibilities

The `tests/` directory provides **comprehensive test coverage** for the hospitality booking system, ensuring code quality, reliability, and correctness across all components. It includes unit tests, integration tests, and end-to-end testing scenarios.

## Directory Structure

```
tests/
├── __init__.py                    # Test package initialization
├── test_agents/                   # Agent-specific tests
│   ├── test_availability.py       # AvailabilityAgent tests
│   └── test_booking.py           # BookingAgent tests
├── test_integration/              # Integration & E2E tests
│   └── test_full_flow.py         # Complete booking flow tests
└── test_mcp/                     # MCP server tests (placeholder)
```

## Core Test Components

### Agent Tests (`test_agents/`)

**Purpose**: Unit testing for individual agents and their components

#### **Availability Agent Tests** (`test_availability.py`)
```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from agents.availability.agent import AvailabilityAgent
from agents.availability.ranking import PropertyRanker

class TestAvailabilityAgent:
    """Test suite for AvailabilityAgent functionality."""
    
    @pytest.fixture
    def mock_mcp_client(self):
        """Mock MCP client for testing."""
        return AsyncMock()
    
    @pytest.fixture
    def availability_agent(self, mock_mcp_client):
        """Create AvailabilityAgent instance for testing."""
        return AvailabilityAgent(mcp_client=mock_mcp_client)
    
    async def test_search_properties_success(self, availability_agent):
        """Test successful property search."""
        # Test implementation
        pass
    
    async def test_search_properties_no_results(self, availability_agent):
        """Test property search with no results."""
        # Test implementation
        pass
    
    async def test_calculate_pricing(self, availability_agent):
        """Test pricing calculation logic."""
        # Test implementation
        pass

class TestPropertyRanker:
    """Test suite for PropertyRanker functionality."""
    
    def test_rank_properties_basic(self):
        """Test basic property ranking."""
        # Test implementation
        pass
    
    def test_rank_properties_with_preferences(self):
        """Test ranking with user preferences."""
        # Test implementation
        pass
```

#### **Booking Agent Tests** (`test_booking.py`)
```python
import pytest
from unittest.mock import AsyncMock
from agents.booking.agent import BookingAgent
from agents.booking.idempotency import IdempotencyManager

class TestBookingAgent:
    """Test suite for BookingAgent functionality."""
    
    @pytest.fixture
    def mock_mcp_client(self):
        return AsyncMock()
    
    @pytest.fixture
    def booking_agent(self, mock_mcp_client):
        return BookingAgent(mcp_client=mock_mcp_client)
    
    async def test_create_booking_success(self, booking_agent):
        """Test successful booking creation."""
        # Test implementation
        pass
    
    async def test_create_booking_duplicate(self, booking_agent):
        """Test duplicate booking prevention."""
        # Test implementation
        pass

class TestIdempotencyManager:
    """Test suite for IdempotencyManager."""
    
    def test_generate_natural_key(self):
        """Test natural key generation."""
        # Test implementation
        pass
    
    def test_check_existing_booking(self):
        """Test existing booking detection."""
        # Test implementation
        pass
```

### Integration Tests (`test_integration/`)

**Purpose**: End-to-end testing of complete booking workflows

#### **Full Flow Tests** (`test_full_flow.py`)
```python
import pytest
import asyncio
from unittest.mock import AsyncMock
from orchestrator.main import HospitalityOrchestrator

class TestFullBookingFlow:
    """Integration tests for complete booking workflows."""
    
    @pytest.fixture
    async def orchestrator(self):
        """Create orchestrator instance for testing."""
        return HospitalityOrchestrator()
    
    async def test_complete_booking_flow(self, orchestrator):
        """Test complete booking from inquiry to confirmation."""
        # Simulate user inquiry
        inquiry_response = await orchestrator.process_message(
            user_id="test_user",
            message="I need a villa in Miami for 4 guests from March 15-18"
        )
        
        # Verify inquiry processing
        assert "inquiry" in inquiry_response
        
        # Continue with availability search
        availability_response = await orchestrator.process_message(
            user_id="test_user", 
            message="Show me available properties"
        )
        
        # Verify availability results
        assert "properties" in availability_response
        
        # Complete booking
        booking_response = await orchestrator.process_message(
            user_id="test_user",
            message="Book property 1 with john@example.com"
        )
        
        # Verify booking confirmation
        assert "booking_confirmed" in booking_response
    
    async def test_booking_flow_with_upsells(self, orchestrator):
        """Test booking flow including upsell suggestions."""
        # Test implementation
        pass
    
    async def test_booking_flow_error_handling(self, orchestrator):
        """Test error handling in booking flow."""
        # Test implementation
        pass
```

### MCP Server Tests (`test_mcp/`)

**Purpose**: Testing MCP server functionality and database operations

```python
import pytest
from unittest.mock import AsyncMock, patch
from mcp_servers.firestore.server import FirestoreMCPServer

class TestFirestoreMCPServer:
    """Test suite for Firestore MCP server."""
    
    @pytest.fixture
    def mock_firestore_client(self):
        return AsyncMock()
    
    @pytest.fixture
    def mcp_server(self, mock_firestore_client):
        with patch('firebase_admin.firestore.client', return_value=mock_firestore_client):
            return FirestoreMCPServer()
    
    async def test_create_user(self, mcp_server):
        """Test user creation via MCP."""
        # Test implementation
        pass
    
    async def test_search_properties(self, mcp_server):
        """Test property search via MCP."""
        # Test implementation
        pass
    
    async def test_create_booking_transaction(self, mcp_server):
        """Test transactional booking creation."""
        # Test implementation
        pass
```

## Testing Patterns & Best Practices

### Test Structure

**AAA Pattern** (Arrange, Act, Assert):
```python
async def test_property_search(self, availability_agent):
    # Arrange
    search_criteria = {
        "city": "Miami",
        "check_in": "2025-03-15",
        "check_out": "2025-03-18",
        "guests": 4
    }
    
    # Act
    results = await availability_agent.search_properties(search_criteria)
    
    # Assert
    assert len(results) > 0
    assert all("price" in prop for prop in results)
```

### Mocking Strategies

**MCP Client Mocking**:
```python
@pytest.fixture
def mock_mcp_client():
    client = AsyncMock()
    
    # Mock property search
    client.call_tool.return_value = {
        "properties": [
            {
                "id": "prop_1",
                "name": "Luxury Villa",
                "price": 500.0,
                "location": {"city": "Miami"}
            }
        ]
    }
    
    return client
```

**Database Mocking**:
```python
@patch('firebase_admin.firestore.client')
def test_database_operation(mock_firestore):
    mock_collection = AsyncMock()
    mock_firestore.return_value.collection.return_value = mock_collection
    
    # Test database operations
    pass
```

### Test Data Management

**Test Fixtures**:
```python
@pytest.fixture
def sample_property():
    return {
        "id": "test_property_1",
        "name": "Test Villa",
        "location": {
            "city": "Miami",
            "coordinates": {"lat": 25.7617, "lng": -80.1918}
        },
        "capacity": 8,
        "minimum_price": 300.0,
        "amenities": ["pool", "wifi", "kitchen"]
    }

@pytest.fixture
def sample_booking_request():
    return {
        "property_id": "test_property_1",
        "user_email": "test@example.com",
        "check_in_date": "2025-03-15",
        "check_out_date": "2025-03-18",
        "guests": 4
    }
```

## How to Run Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_agents/test_availability.py

# Run specific test class
pytest tests/test_agents/test_availability.py::TestAvailabilityAgent

# Run specific test method
pytest tests/test_agents/test_availability.py::TestAvailabilityAgent::test_search_properties_success
```

### Test Configuration

**pytest.ini** (in project root):
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --strict-markers
    --disable-warnings
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

### Coverage Analysis

```bash
# Run tests with coverage
pytest --cov=agents --cov=orchestrator --cov=memory --cov=mcp_servers --cov=utils

# Generate coverage report
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

## Test Categories & Markers

### Test Markers

```python
import pytest

@pytest.mark.unit
def test_unit_functionality():
    """Fast unit test."""
    pass

@pytest.mark.integration
async def test_integration_flow():
    """Integration test requiring external services."""
    pass

@pytest.mark.slow
async def test_full_system():
    """Slow end-to-end test."""
    pass
```

### Running Specific Test Categories

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests  
pytest -m integration

# Skip slow tests
pytest -m "not slow"
```

## Test Environment Setup

### Test Configuration

**conftest.py** (test configuration):
```python
import pytest
import asyncio
from unittest.mock import AsyncMock

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_database():
    """Setup test database."""
    # Setup test data
    yield
    # Cleanup test data

@pytest.fixture
def mock_environment(monkeypatch):
    """Mock environment variables for testing."""
    monkeypatch.setenv("FIRESTORE_PROJECT_ID", "test-project")
    monkeypatch.setenv("ENVIRONMENT", "testing")
```

### Test Data Seeding

```python
async def seed_test_data():
    """Seed database with test data."""
    test_properties = [
        {
            "id": "test_prop_1",
            "name": "Test Villa 1",
            "location": {"city": "Miami"},
            "price": 300.0
        }
    ]
    
    # Insert test data
    for prop in test_properties:
        await create_test_property(prop)
```

## Integration with Other Directories

### → `agents/`
- **Unit Tests**: Test individual agent functionality
- **Mock Integration**: Test agent interactions with MCP
- **Validation Tests**: Test input/output validation

### → `orchestrator/`
- **Flow Tests**: Test complete orchestration workflows
- **Memory Tests**: Test session and memory management
- **Error Handling**: Test error propagation and recovery

### → `mcp_servers/`
- **Database Tests**: Test CRUD operations
- **Transaction Tests**: Test transactional integrity
- **Connection Tests**: Test MCP protocol compliance

### → `memory/`
- **STM Tests**: Test short-term memory operations
- **LTM Tests**: Test long-term memory persistence
- **Cleanup Tests**: Test memory cleanup and expiration

### → `utils/`
- **Validation Tests**: Test input validation functions
- **Formatting Tests**: Test output formatting
- **Helper Tests**: Test utility function correctness

### → `config/`
- **Configuration Tests**: Test setting loading and validation
- **Feature Flag Tests**: Test feature toggle functionality
- **Environment Tests**: Test environment-specific configurations

## Continuous Integration

### GitHub Actions Workflow

```yaml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## Troubleshooting

### Common Test Issues

1. **Async Test Failures**
   ```python
   # Ensure proper async test setup
   @pytest.mark.asyncio
   async def test_async_function():
       result = await async_function()
       assert result is not None
   ```

2. **Mock Configuration Issues**
   ```python
   # Debug mock setup
   mock_client = AsyncMock()
   mock_client.call_tool.assert_called_with("search_properties", {...})
   ```

3. **Test Data Isolation**
   ```python
   # Use unique test data per test
   @pytest.fixture
   def unique_test_id():
       return f"test_{uuid.uuid4().hex[:8]}"
   ```

### Debug Commands

```bash
# Run tests with verbose output
pytest -v -s

# Run single test with debugging
pytest tests/test_agents/test_availability.py::test_search_properties -v -s

# Check test discovery
pytest --collect-only

# Run tests with pdb on failure
pytest --pdb
```

---

**Next Steps**: See root `MANAGE.md` for complete system overview and testing integration details.
