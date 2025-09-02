# Integration Testing Management Guide

## Overview
The **Integration Testing** directory contains end-to-end test suites that validate the complete hospitality booking system workflow. These tests ensure proper integration between agents, MCP servers, database operations, and external services across the entire booking lifecycle.

## Directory Structure
```
tests/test_integration/
├── MANAGE.md           # This management guide
└── test_full_flow.py   # Complete booking flow integration tests
```

## Core Testing Responsibilities

### 1. **End-to-End Workflow Testing**
- Complete booking journey from inquiry to survey
- Multi-agent conversation flow validation
- Cross-system integration verification
- Real-world scenario simulation

### 2. **System Integration Validation**
- Agent-to-agent handoff testing
- MCP server communication validation
- Database transaction integrity
- External service integration

### 3. **Performance Integration Testing**
- System-wide performance under load
- Resource utilization across components
- Scalability validation
- Bottleneck identification

## Integration Test Categories

### **Full Booking Flow Tests**
Complete end-to-end booking scenarios covering:
- Guest inquiry and slot collection
- Property search and availability checking
- Booking creation and confirmation
- Upsell opportunities and selection
- Pre-arrival communication
- Post-stay survey collection

### **Cross-Agent Integration Tests**
- Agent handoff mechanisms
- Context preservation between agents
- Session state management
- Error propagation and recovery

### **Database Integration Tests**
- Multi-table transaction validation
- Data consistency across operations
- Concurrent access handling
- Backup and recovery scenarios

### **External Service Integration Tests**
- Firebase Firestore operations
- Email/SMS notification delivery
- Payment processing simulation
- Third-party API interactions

## Test Implementation

### **Full Flow Test Structure** (`test_full_flow.py`)
```python
import pytest
import asyncio
from datetime import datetime, timedelta
from orchestrator.main import HospitalityOrchestrator
from mcp_servers.firestore.server import FirestoreServer
from agents.inquiry.agent import inquiry_agent
from agents.availability.agent import availability_agent
from agents.booking.agent import booking_agent

class TestFullBookingFlow:
    """Test complete booking workflow integration."""
    
    @pytest.fixture
    async def orchestrator(self):
        """Set up orchestrator with all components."""
        orchestrator = HospitalityOrchestrator()
        await orchestrator.initialize()
        return orchestrator
    
    @pytest.fixture
    def guest_scenario(self):
        """Sample guest booking scenario."""
        return {
            "guest_name": "John Doe",
            "guest_email": "john@example.com",
            "destination": "Miami",
            "check_in": "2024-06-15",
            "check_out": "2024-06-20",
            "guests": 4,
            "budget": 2000,
            "preferences": ["pool", "wifi", "kitchen"]
        }
    
    async def test_successful_booking_journey(self, orchestrator, guest_scenario):
        """Test complete successful booking flow."""
        
        # Step 1: Initial inquiry
        inquiry_response = await orchestrator.process_message(
            message="Hi, I'm looking for a villa in Miami for 4 people",
            session_id="test_session_001"
        )
        
        assert inquiry_response["agent"] == "inquiry"
        assert "welcome" in inquiry_response["message"].lower()
        
        # Step 2: Provide booking details
        details_response = await orchestrator.process_message(
            message=f"I need accommodation from {guest_scenario['check_in']} to {guest_scenario['check_out']} for {guest_scenario['guests']} guests",
            session_id="test_session_001"
        )
        
        # Should transition to availability agent
        assert details_response["agent"] == "availability"
        
        # Step 3: Property search and selection
        search_response = await orchestrator.process_message(
            message="Show me available properties",
            session_id="test_session_001"
        )
        
        assert "properties" in search_response
        assert len(search_response["properties"]) > 0
        
        # Step 4: Select property and proceed to booking
        booking_response = await orchestrator.process_message(
            message="I'd like to book the first property",
            session_id="test_session_001"
        )
        
        assert booking_response["agent"] == "booking"
        
        # Step 5: Complete booking
        confirmation_response = await orchestrator.process_message(
            message="Yes, please confirm the booking",
            session_id="test_session_001"
        )
        
        assert confirmation_response["booking_confirmed"] is True
        assert "booking_id" in confirmation_response
        
        # Verify booking in database
        booking_id = confirmation_response["booking_id"]
        booking_data = await orchestrator.get_booking(booking_id)
        
        assert booking_data["success"] is True
        assert booking_data["booking"]["status"] == "confirmed"
    
    async def test_booking_with_upsells(self, orchestrator, guest_scenario):
        """Test booking flow with upsell selection."""
        
        # Complete initial booking flow (abbreviated)
        session_id = "test_session_upsell"
        
        # ... (initial steps similar to above)
        
        # Upsell presentation
        upsell_response = await orchestrator.process_message(
            message="What add-on services are available?",
            session_id=session_id
        )
        
        assert upsell_response["agent"] == "upsell"
        assert "add_ons" in upsell_response
        
        # Select upsells
        upsell_selection = await orchestrator.process_message(
            message="I'd like early check-in and the welcome basket",
            session_id=session_id
        )
        
        # Verify upsells added to booking
        assert "early_checkin" in upsell_selection["selected_add_ons"]
        assert "welcome_basket" in upsell_selection["selected_add_ons"]
    
    async def test_no_availability_scenario(self, orchestrator):
        """Test handling when no properties are available."""
        
        session_id = "test_session_no_availability"
        
        # Request unavailable dates/location
        response = await orchestrator.process_message(
            message="I need a 10-bedroom villa in Antarctica for tomorrow",
            session_id=session_id
        )
        
        assert response["agent"] == "availability"
        assert response["properties_found"] == 0
        assert "alternatives" in response
    
    async def test_booking_conflict_handling(self, orchestrator, guest_scenario):
        """Test handling of booking conflicts and overlaps."""
        
        # Create initial booking
        session_id_1 = "test_session_conflict_1"
        # ... complete booking flow
        
        # Attempt conflicting booking
        session_id_2 = "test_session_conflict_2"
        conflict_response = await orchestrator.process_message(
            message="Book the same property for the same dates",
            session_id=session_id_2
        )
        
        assert conflict_response["success"] is False
        assert "conflict" in conflict_response["message"].lower()
    
    async def test_error_recovery_flow(self, orchestrator):
        """Test system recovery from various error conditions."""
        
        session_id = "test_session_error_recovery"
        
        # Simulate database error
        with patch('mcp_servers.firestore.server.db') as mock_db:
            mock_db.side_effect = Exception("Database connection failed")
            
            error_response = await orchestrator.process_message(
                message="Search for properties in Miami",
                session_id=session_id
            )
            
            assert error_response["success"] is False
            assert "error" in error_response["message"].lower()
        
        # Verify system recovery after error
        recovery_response = await orchestrator.process_message(
            message="Try searching again",
            session_id=session_id
        )
        
        assert recovery_response["success"] is True
```

### **Performance Integration Tests**
```python
class TestSystemPerformance:
    """Test system-wide performance characteristics."""
    
    async def test_concurrent_booking_load(self):
        """Test system under concurrent booking load."""
        
        orchestrator = HospitalityOrchestrator()
        await orchestrator.initialize()
        
        async def simulate_booking_session(session_id):
            """Simulate a complete booking session."""
            start_time = time.time()
            
            # Complete booking flow
            responses = []
            messages = [
                "Hi, I need a villa in Miami",
                "For June 15-20, 4 guests",
                "Show me available properties",
                "Book the first property",
                "Confirm the booking"
            ]
            
            for message in messages:
                response = await orchestrator.process_message(
                    message=message,
                    session_id=session_id
                )
                responses.append(response)
            
            end_time = time.time()
            return responses, end_time - start_time
        
        # Run concurrent sessions
        tasks = []
        for i in range(20):
            session_id = f"perf_test_session_{i}"
            tasks.append(simulate_booking_session(session_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Analyze results
        successful_sessions = [r for r in results if not isinstance(r, Exception)]
        success_rate = len(successful_sessions) / len(results)
        avg_duration = sum(duration for _, duration in successful_sessions) / len(successful_sessions)
        
        assert success_rate >= 0.95  # 95% success rate
        assert avg_duration < 10.0   # Average session under 10 seconds
    
    async def test_memory_usage_under_load(self):
        """Test memory usage during high-load scenarios."""
        
        import psutil
        process = psutil.Process()
        
        # Baseline memory
        baseline_memory = process.memory_info().rss
        
        # Simulate high load
        orchestrator = HospitalityOrchestrator()
        await orchestrator.initialize()
        
        for i in range(100):
            session_id = f"memory_test_session_{i}"
            await orchestrator.process_message(
                message="Search for properties in Miami",
                session_id=session_id
            )
        
        # Check memory usage
        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - baseline_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 200 * 1024 * 1024  # Less than 200MB increase
```

### **Database Integration Tests**
```python
class TestDatabaseIntegration:
    """Test database operations and consistency."""
    
    async def test_transaction_integrity(self):
        """Test database transaction consistency."""
        
        # Test booking creation transaction
        booking_data = {
            "property_id": "test_prop_123",
            "guest_id": "test_guest_456",
            "check_in_date": "2024-06-15",
            "check_out_date": "2024-06-20",
            "number_of_guests": 4,
            "total_price": 1500.0
        }
        
        # Create booking
        result = await create_booking(**booking_data)
        assert result["success"] is True
        
        booking_id = result["booking_id"]
        
        # Verify all related data was created
        booking = await get_booking(booking_id)
        assert booking["success"] is True
        
        # Verify idempotency key was stored
        # Verify availability was updated
        # Verify audit log was created
    
    async def test_concurrent_database_access(self):
        """Test handling of concurrent database operations."""
        
        property_id = "test_concurrent_prop"
        
        # Create multiple concurrent booking attempts
        tasks = []
        for i in range(5):
            booking_data = {
                "property_id": property_id,
                "guest_id": f"guest_{i}",
                "check_in_date": "2024-06-15",
                "check_out_date": "2024-06-20",
                "number_of_guests": 2,
                "total_price": 1000.0
            }
            tasks.append(create_booking(**booking_data))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Only one booking should succeed due to availability constraints
        successful_bookings = [r for r in results if isinstance(r, dict) and r.get("success")]
        assert len(successful_bookings) == 1
```

## Test Environment Setup

### **Integration Test Configuration**
```python
# Integration test settings
INTEGRATION_TEST_CONFIG = {
    "use_test_database": True,
    "firestore_emulator": "localhost:8080",
    "test_data_cleanup": True,
    "mock_external_services": True,
    "enable_logging": True,
    "log_level": "DEBUG"
}

@pytest.fixture(scope="session")
async def test_environment():
    """Set up integration test environment."""
    
    # Start Firestore emulator
    emulator_process = start_firestore_emulator()
    
    # Initialize test data
    await setup_integration_test_data()
    
    yield
    
    # Cleanup
    await cleanup_integration_test_data()
    emulator_process.terminate()
```

### **Test Data Management**
```python
async def setup_integration_test_data():
    """Set up comprehensive test data for integration tests."""
    
    # Create test users
    test_users = [
        {"name": "Test Guest", "email": "guest@test.com", "role": "guest"},
        {"name": "Test Host", "email": "host@test.com", "role": "host"}
    ]
    
    for user_data in test_users:
        await create_user(**user_data)
    
    # Create test properties
    test_properties = [
        {
            "name": "Test Villa Miami",
            "city": "Miami",
            "minimum_price": 300.0,
            "guest_space": 6,
            "amenities": ["pool", "wifi", "kitchen"]
        },
        {
            "name": "Test Apartment NYC",
            "city": "New York",
            "minimum_price": 200.0,
            "guest_space": 4,
            "amenities": ["wifi", "kitchen"]
        }
    ]
    
    for property_data in test_properties:
        await create_property(**property_data)
```

## Test Execution and Reporting

### **Running Integration Tests**
```bash
# Run all integration tests
pytest tests/test_integration/ -v

# Run with detailed output
pytest tests/test_integration/ -v -s

# Run performance tests only
pytest tests/test_integration/ -m performance

# Run with coverage
pytest tests/test_integration/ --cov=. --cov-report=html

# Generate integration test report
pytest tests/test_integration/ --html=integration_report.html
```

### **CI/CD Integration**
```yaml
name: Integration Tests
on: [push, pull_request]

jobs:
  integration-test:
    runs-on: ubuntu-latest
    services:
      firestore:
        image: google/cloud-sdk:latest
        ports:
          - 8080:8080
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio pytest-html
      
      - name: Start services
        run: |
          gcloud emulators firestore start --host-port=localhost:8080 &
          sleep 10
      
      - name: Run integration tests
        run: |
          pytest tests/test_integration/ -v --html=integration_report.html
      
      - name: Upload test results
        uses: actions/upload-artifact@v2
        with:
          name: integration-test-results
          path: integration_report.html
```

## Monitoring and Metrics

### **Integration Test Metrics**
- End-to-end flow completion rates
- Cross-system integration success rates
- Performance benchmarks and trends
- Error recovery effectiveness

### **Quality Gates**
- Minimum 95% integration test pass rate
- Maximum 10-second end-to-end flow duration
- Zero data consistency violations
- 100% critical path coverage

## Troubleshooting

### **Common Integration Issues**
```bash
# Firestore emulator connection issues
export FIRESTORE_EMULATOR_HOST=localhost:8080
pytest tests/test_integration/ -v

# Agent communication problems
pytest tests/test_integration/ -s --tb=long

# Performance test failures
pytest tests/test_integration/ -m performance --durations=10

# Database consistency issues
pytest tests/test_integration/ --setup-show
```

### **Debug Commands**
```bash
# Run single integration test with full output
pytest tests/test_integration/test_full_flow.py::TestFullBookingFlow::test_successful_booking_journey -v -s

# Check system resource usage during tests
pytest tests/test_integration/ --profile-svg

# Validate test environment setup
python scripts/validate_integration_environment.py
```

## Related Documentation
- [Root Management Guide](../../MANAGE.md) - System overview and architecture
- [Tests Overview](../MANAGE.md) - Testing system documentation
- [Agent Tests](../test_agents/MANAGE.md) - Individual agent testing
- [MCP Tests](../test_mcp/MANAGE.md) - MCP server testing
- [Orchestrator](../../orchestrator/MANAGE.md) - System coordination

## Development Notes
- Integration tests validate complete system workflows
- Uses Firestore emulator for isolated testing environment
- Comprehensive performance and load testing capabilities
- Automated CI/CD integration for continuous validation
- Real-world scenario simulation for user experience validation
- Cross-component integration verification and monitoring
