# Agent Testing Management Guide

## Overview
The **Agent Testing** directory contains comprehensive test suites for all booking system agents. This testing framework validates agent functionality, tool integration, conversation flows, and error handling across the entire hospitality booking workflow.

## Directory Structure
```
tests/test_agents/
├── MANAGE.md           # This management guide
├── test_availability.py # Availability agent tests
└── test_booking.py     # Booking agent tests
```

## Core Testing Responsibilities

### 1. **Agent Functionality Testing**
- Individual agent tool validation
- Conversation flow testing
- Response quality assessment
- Error handling verification

### 2. **Integration Testing**
- Agent-to-agent handoff validation
- MCP server integration testing
- Database operation verification
- External service mocking

### 3. **Performance Testing**
- Response time measurement
- Concurrent request handling
- Memory usage monitoring
- Scalability validation

## Test Categories

### **Unit Tests**
- Individual tool function testing
- Input validation and sanitization
- Output format verification
- Edge case handling

### **Integration Tests**
- Agent workflow testing
- Database integration validation
- MCP protocol communication
- External API interaction

### **End-to-End Tests**
- Complete booking flow simulation
- Multi-agent conversation testing
- Real-world scenario validation
- User experience verification

## Agent Test Coverage

### **Availability Agent Tests** (`test_availability.py`)
```python
class TestAvailabilityAgent:
    def test_search_properties_basic(self):
        """Test basic property search functionality."""
        
    def test_property_ranking_algorithm(self):
        """Test property ranking with various criteria."""
        
    def test_pricing_calculation(self):
        """Test dynamic pricing calculations."""
        
    def test_amenity_filtering(self):
        """Test amenity-based property filtering."""
        
    def test_no_availability_handling(self):
        """Test handling when no properties are available."""
        
    def test_alternative_suggestions(self):
        """Test alternative property suggestions."""
```

### **Booking Agent Tests** (`test_booking.py`)
```python
class TestBookingAgent:
    def test_create_booking_success(self):
        """Test successful booking creation."""
        
    def test_idempotency_handling(self):
        """Test duplicate booking prevention."""
        
    def test_pricing_validation(self):
        """Test booking price calculation and validation."""
        
    def test_availability_checking(self):
        """Test final availability verification."""
        
    def test_payment_simulation(self):
        """Test payment processing simulation."""
        
    def test_booking_confirmation_format(self):
        """Test booking confirmation message format."""
```

## Testing Framework

### **Test Setup and Fixtures**
```python
import pytest
from unittest.mock import Mock, patch
from agents.availability.agent import availability_agent
from agents.booking.agent import booking_agent

@pytest.fixture
def mock_firestore():
    """Mock Firestore database for testing."""
    with patch('firebase_admin.firestore.client') as mock_db:
        yield mock_db

@pytest.fixture
def sample_property_data():
    """Sample property data for testing."""
    return {
        "property_id": "test_prop_123",
        "name": "Test Villa",
        "location": {"city": "Miami", "lat": 25.7617, "lng": -80.1918},
        "minimum_price": 300.0,
        "guest_space": 6,
        "amenities": ["pool", "wifi", "kitchen"]
    }

@pytest.fixture
def sample_booking_data():
    """Sample booking data for testing."""
    return {
        "property_id": "test_prop_123",
        "guest_id": "test_guest_456",
        "check_in_date": "2024-06-15",
        "check_out_date": "2024-06-20",
        "number_of_guests": 4,
        "total_price": 1500.0
    }
```

### **Mocking Strategies**
```python
# Mock MCP server responses
@patch('mcp_servers.firestore.server.search_properties')
async def test_property_search_with_mock(mock_search, sample_property_data):
    mock_search.return_value = {
        "success": True,
        "properties": [sample_property_data]
    }
    
    # Test agent functionality
    result = await availability_agent.search_properties(
        city="Miami",
        check_in_date="2024-06-15",
        check_out_date="2024-06-20",
        number_of_guests=4
    )
    
    assert result["success"] is True
    assert len(result["properties"]) == 1

# Mock external API calls
@patch('requests.post')
def test_payment_processing_mock(mock_post):
    mock_post.return_value.json.return_value = {
        "status": "success",
        "transaction_id": "txn_123456"
    }
    
    # Test payment simulation
    result = booking_agent.simulate_payment(1500.0, "credit_card")
    assert result["status"] == "success"
```

## Test Data Management

### **Test Database Setup**
```python
# Test database configuration
TEST_DB_CONFIG = {
    "project_id": "test-hospitality-booking",
    "emulator_host": "localhost:8080",
    "use_emulator": True
}

def setup_test_data():
    """Set up test data in Firestore emulator."""
    # Create test users
    # Create test properties
    # Create test bookings
    # Set up test sessions

def teardown_test_data():
    """Clean up test data after tests."""
    # Clear test collections
    # Reset emulator state
```

### **Sample Test Scenarios**
```python
# Successful booking flow
BOOKING_SUCCESS_SCENARIO = {
    "guest_preferences": {
        "city": "Miami",
        "dates": ["2024-06-15", "2024-06-20"],
        "guests": 4,
        "budget": 2000
    },
    "available_properties": [
        {"property_id": "prop1", "price": 300, "rating": 4.8},
        {"property_id": "prop2", "price": 450, "rating": 4.9}
    ],
    "expected_booking": {
        "property_id": "prop2",
        "total_price": 2250,
        "status": "confirmed"
    }
}

# No availability scenario
NO_AVAILABILITY_SCENARIO = {
    "guest_preferences": {
        "city": "Miami",
        "dates": ["2024-12-31", "2025-01-02"],
        "guests": 8,
        "budget": 500
    },
    "available_properties": [],
    "expected_response": {
        "message": "no_properties_available",
        "alternatives": True
    }
}
```

## Performance Testing

### **Load Testing**
```python
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

async def test_concurrent_bookings():
    """Test handling of concurrent booking requests."""
    
    async def create_booking(booking_data):
        start_time = time.time()
        result = await booking_agent.create_booking(**booking_data)
        end_time = time.time()
        return result, end_time - start_time
    
    # Create multiple concurrent booking requests
    tasks = []
    for i in range(10):
        booking_data = generate_test_booking_data(i)
        tasks.append(create_booking(booking_data))
    
    results = await asyncio.gather(*tasks)
    
    # Validate results
    success_count = sum(1 for result, _ in results if result["success"])
    avg_response_time = sum(time for _, time in results) / len(results)
    
    assert success_count >= 8  # Allow for some conflicts
    assert avg_response_time < 2.0  # Response time under 2 seconds
```

### **Memory Usage Testing**
```python
import psutil
import gc

def test_memory_usage():
    """Test agent memory usage during operations."""
    
    # Measure baseline memory
    process = psutil.Process()
    baseline_memory = process.memory_info().rss
    
    # Perform multiple agent operations
    for i in range(100):
        result = availability_agent.search_properties(
            city="Miami",
            number_of_guests=4
        )
    
    # Force garbage collection
    gc.collect()
    
    # Measure final memory
    final_memory = process.memory_info().rss
    memory_increase = final_memory - baseline_memory
    
    # Memory increase should be reasonable
    assert memory_increase < 50 * 1024 * 1024  # Less than 50MB increase
```

## Error Handling Tests

### **Exception Testing**
```python
def test_database_connection_failure():
    """Test agent behavior when database is unavailable."""
    
    with patch('firebase_admin.firestore.client') as mock_db:
        mock_db.side_effect = Exception("Database connection failed")
        
        result = availability_agent.search_properties(city="Miami")
        
        assert result["success"] is False
        assert "database" in result["message"].lower()

def test_invalid_input_handling():
    """Test agent response to invalid inputs."""
    
    # Test invalid date format
    result = booking_agent.create_booking(
        property_id="prop123",
        check_in_date="invalid-date",
        check_out_date="2024-06-20"
    )
    
    assert result["success"] is False
    assert "invalid date" in result["message"].lower()

def test_timeout_handling():
    """Test agent behavior with slow external services."""
    
    with patch('asyncio.wait_for') as mock_wait:
        mock_wait.side_effect = asyncio.TimeoutError()
        
        result = booking_agent.create_booking(
            property_id="prop123",
            guest_id="guest456"
        )
        
        assert result["success"] is False
        assert "timeout" in result["message"].lower()
```

## Test Execution

### **Running Tests**
```bash
# Run all agent tests
pytest tests/test_agents/ -v

# Run specific agent tests
pytest tests/test_agents/test_availability.py -v
pytest tests/test_agents/test_booking.py -v

# Run with coverage
pytest tests/test_agents/ --cov=agents --cov-report=html

# Run performance tests
pytest tests/test_agents/ -m performance

# Run integration tests
pytest tests/test_agents/ -m integration
```

### **Test Configuration**
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    unit: Unit tests
    integration: Integration tests
    performance: Performance tests
    slow: Slow running tests
addopts = 
    --strict-markers
    --disable-warnings
    --tb=short
```

## Continuous Integration

### **GitHub Actions Workflow**
```yaml
name: Agent Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio
      
      - name: Start Firestore Emulator
        run: |
          firebase emulators:start --only firestore &
          sleep 10
      
      - name: Run tests
        run: |
          pytest tests/test_agents/ --cov=agents --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v1
```

## Test Reporting

### **Coverage Reports**
- Line coverage for all agent modules
- Branch coverage for decision points
- Function coverage for tool implementations
- Integration coverage for agent workflows

### **Performance Metrics**
- Response time percentiles (P50, P95, P99)
- Throughput measurements (requests/second)
- Memory usage patterns
- Error rate tracking

### **Quality Metrics**
- Test pass/fail rates
- Code coverage percentages
- Performance regression detection
- Integration test success rates

## Troubleshooting

### **Common Test Issues**
```bash
# Firestore emulator not running
firebase emulators:start --only firestore

# Test data cleanup issues
pytest tests/test_agents/ --setup-show

# Mock configuration problems
pytest tests/test_agents/ -s -v --tb=long

# Performance test failures
pytest tests/test_agents/ -m performance --durations=10
```

### **Debug Commands**
```bash
# Run single test with debugging
pytest tests/test_agents/test_availability.py::test_search_properties -s -v

# Check test coverage
pytest tests/test_agents/ --cov=agents --cov-report=term-missing

# Profile test performance
pytest tests/test_agents/ --profile

# Generate test report
pytest tests/test_agents/ --html=report.html
```

## Related Documentation
- [Root Management Guide](../../MANAGE.md) - System overview and architecture
- [Tests Overview](../MANAGE.md) - Testing system documentation
- [Agents Overview](../../agents/MANAGE.md) - Agent system documentation
- [Integration Tests](../test_integration/MANAGE.md) - End-to-end testing
- [MCP Tests](../test_mcp/MANAGE.md) - MCP server testing

## Development Notes
- Tests use pytest framework with async support
- Firestore emulator for isolated database testing
- Comprehensive mocking for external dependencies
- Performance benchmarks for scalability validation
- CI/CD integration for automated testing
- Coverage reporting for code quality assurance
