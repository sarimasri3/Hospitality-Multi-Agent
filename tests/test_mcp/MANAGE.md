# MCP Server Testing Management Guide

## Overview
The **MCP Server Testing** directory contains test suites specifically designed to validate Model Context Protocol (MCP) server implementations. These tests ensure proper MCP protocol compliance, tool registration, request/response handling, and server lifecycle management across all MCP servers in the hospitality booking system.

## Directory Structure
```
tests/test_mcp/
├── MANAGE.md           # This management guide
└── (implementation pending)
```

## Core Testing Responsibilities

### 1. **MCP Protocol Compliance**
- Protocol message format validation
- Request/response schema verification
- Tool registration and discovery testing
- Error handling and status code validation

### 2. **Server Lifecycle Testing**
- Server initialization and shutdown
- Connection establishment and management
- Resource cleanup and memory management
- Graceful degradation under load

### 3. **Tool Integration Testing**
- Tool registration and exposure
- Parameter validation and type checking
- Function execution and result handling
- Error propagation and recovery

## MCP Server Test Coverage

### **Firestore MCP Server Tests**
```python
class TestFirestoreMCPServer:
    """Test Firestore MCP server implementation."""
    
    async def test_server_initialization(self):
        """Test server startup and initialization."""
        
    async def test_tool_registration(self):
        """Test all tools are properly registered."""
        
    async def test_create_user_tool(self):
        """Test user creation through MCP protocol."""
        
    async def test_search_properties_tool(self):
        """Test property search through MCP protocol."""
        
    async def test_create_booking_tool(self):
        """Test booking creation through MCP protocol."""
        
    async def test_database_error_handling(self):
        """Test error handling for database failures."""
        
    async def test_concurrent_requests(self):
        """Test handling of concurrent MCP requests."""
```

### **Monitoring MCP Server Tests**
```python
class TestMonitoringMCPServer:
    """Test Monitoring MCP server implementation."""
    
    async def test_health_check_tool(self):
        """Test system health check tool."""
        
    async def test_metrics_collection_tool(self):
        """Test metrics collection and aggregation."""
        
    async def test_alert_creation_tool(self):
        """Test alert configuration and management."""
        
    async def test_performance_reporting(self):
        """Test performance report generation."""
```

### **Notification MCP Server Tests**
```python
class TestNotificationMCPServer:
    """Test Notification MCP server implementation."""
    
    async def test_send_email_tool(self):
        """Test email sending through MCP protocol."""
        
    async def test_send_sms_tool(self):
        """Test SMS sending through MCP protocol."""
        
    async def test_template_management(self):
        """Test notification template operations."""
        
    async def test_delivery_tracking(self):
        """Test message delivery status tracking."""
```

## MCP Protocol Testing Framework

### **Protocol Message Validation**
```python
import json
from mcp.types import Request, Response, Tool
from mcp.server.models import InitializationOptions

class MCPProtocolTester:
    """Base class for MCP protocol testing."""
    
    def validate_request_format(self, request_data: dict):
        """Validate MCP request message format."""
        required_fields = ["jsonrpc", "method", "id"]
        for field in required_fields:
            assert field in request_data
        
        assert request_data["jsonrpc"] == "2.0"
        assert isinstance(request_data["id"], (str, int))
    
    def validate_response_format(self, response_data: dict):
        """Validate MCP response message format."""
        required_fields = ["jsonrpc", "id"]
        for field in required_fields:
            assert field in response_data
        
        assert response_data["jsonrpc"] == "2.0"
        assert "result" in response_data or "error" in response_data
    
    def validate_tool_schema(self, tool: Tool):
        """Validate tool schema compliance."""
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")
        assert hasattr(tool, "inputSchema")
        
        # Validate JSON schema format
        schema = tool.inputSchema
        assert "type" in schema
        assert schema["type"] == "object"
```

### **Server Communication Testing**
```python
import asyncio
import json
from mcp.server.stdio import stdio_server

class MCPServerTester:
    """Test MCP server communication."""
    
    async def test_server_handshake(self, server_process):
        """Test MCP server initialization handshake."""
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self.send_request(server_process, init_request)
        
        assert response["jsonrpc"] == "2.0"
        assert response["id"] == 1
        assert "result" in response
        assert "capabilities" in response["result"]
    
    async def test_tool_discovery(self, server_process):
        """Test tool discovery through MCP protocol."""
        
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = await self.send_request(server_process, tools_request)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response
        assert "tools" in response["result"]
        assert len(response["result"]["tools"]) > 0
    
    async def test_tool_execution(self, server_process, tool_name: str, params: dict):
        """Test tool execution through MCP protocol."""
        
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": params
            }
        }
        
        response = await self.send_request(server_process, call_request)
        
        assert response["jsonrpc"] == "2.0"
        assert "result" in response or "error" in response
        
        if "result" in response:
            assert "content" in response["result"]
```

## Test Implementation Examples

### **Firestore Server MCP Tests**
```python
import pytest
from mcp_servers.firestore.server import main as firestore_main

class TestFirestoreMCPProtocol:
    """Test Firestore server MCP protocol implementation."""
    
    @pytest.fixture
    async def firestore_server(self):
        """Start Firestore MCP server for testing."""
        # Start server process
        server_process = await start_mcp_server(firestore_main)
        yield server_process
        # Cleanup
        await stop_mcp_server(server_process)
    
    async def test_create_user_mcp_call(self, firestore_server):
        """Test user creation through MCP protocol."""
        
        tester = MCPServerTester()
        
        # Test tool execution
        params = {
            "name": "Test User",
            "email": "test@example.com",
            "role": "guest"
        }
        
        response = await tester.test_tool_execution(
            firestore_server,
            "create_user",
            params
        )
        
        # Validate response
        assert "result" in response
        result = json.loads(response["result"]["content"][0]["text"])
        assert result["success"] is True
        assert "user_id" in result
    
    async def test_search_properties_mcp_call(self, firestore_server):
        """Test property search through MCP protocol."""
        
        tester = MCPServerTester()
        
        params = {
            "city": "Miami",
            "check_in_date": "2024-06-15",
            "check_out_date": "2024-06-20",
            "number_of_guests": 4
        }
        
        response = await tester.test_tool_execution(
            firestore_server,
            "search_properties",
            params
        )
        
        # Validate response
        assert "result" in response
        result = json.loads(response["result"]["content"][0]["text"])
        assert result["success"] is True
        assert "properties" in result
    
    async def test_invalid_tool_call(self, firestore_server):
        """Test handling of invalid tool calls."""
        
        tester = MCPServerTester()
        
        # Call non-existent tool
        call_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "non_existent_tool",
                "arguments": {}
            }
        }
        
        response = await tester.send_request(firestore_server, call_request)
        
        assert "error" in response
        assert response["error"]["code"] == -32601  # Method not found
```

### **Server Performance Testing**
```python
class TestMCPServerPerformance:
    """Test MCP server performance characteristics."""
    
    async def test_concurrent_tool_calls(self, server_process):
        """Test server performance under concurrent load."""
        
        tester = MCPServerTester()
        
        async def make_tool_call(call_id):
            """Make a single tool call."""
            params = {"city": "Miami", "number_of_guests": 4}
            return await tester.test_tool_execution(
                server_process,
                "search_properties",
                params
            )
        
        # Make concurrent calls
        tasks = [make_tool_call(i) for i in range(50)]
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Analyze results
        successful_calls = [r for r in results if not isinstance(r, Exception)]
        success_rate = len(successful_calls) / len(results)
        avg_response_time = (end_time - start_time) / len(results)
        
        assert success_rate >= 0.95  # 95% success rate
        assert avg_response_time < 0.5  # Average response under 500ms
    
    async def test_memory_usage_stability(self, server_process):
        """Test server memory usage stability."""
        
        import psutil
        
        # Get server process
        server_pid = server_process.pid
        process = psutil.Process(server_pid)
        
        # Baseline memory
        baseline_memory = process.memory_info().rss
        
        # Make many tool calls
        tester = MCPServerTester()
        for i in range(1000):
            await tester.test_tool_execution(
                server_process,
                "search_properties",
                {"city": "Miami"}
            )
        
        # Check memory usage
        final_memory = process.memory_info().rss
        memory_increase = final_memory - baseline_memory
        
        # Memory should not increase significantly
        assert memory_increase < 100 * 1024 * 1024  # Less than 100MB increase
```

## Error Handling Tests

### **Protocol Error Testing**
```python
class TestMCPErrorHandling:
    """Test MCP protocol error handling."""
    
    async def test_malformed_request(self, server_process):
        """Test handling of malformed JSON-RPC requests."""
        
        # Send invalid JSON
        invalid_requests = [
            '{"invalid": "json"',  # Malformed JSON
            '{"jsonrpc": "1.0"}',  # Wrong protocol version
            '{"jsonrpc": "2.0"}',  # Missing required fields
        ]
        
        for invalid_request in invalid_requests:
            response = await send_raw_request(server_process, invalid_request)
            
            # Should return parse error or invalid request error
            assert "error" in response
            assert response["error"]["code"] in [-32700, -32600]
    
    async def test_tool_parameter_validation(self, server_process):
        """Test tool parameter validation."""
        
        tester = MCPServerTester()
        
        # Test missing required parameters
        invalid_params = [
            {},  # Missing all parameters
            {"name": "Test"},  # Missing email
            {"email": "invalid-email"},  # Invalid email format
        ]
        
        for params in invalid_params:
            response = await tester.test_tool_execution(
                server_process,
                "create_user",
                params
            )
            
            assert "error" in response or (
                "result" in response and 
                "success" in json.loads(response["result"]["content"][0]["text"]) and
                not json.loads(response["result"]["content"][0]["text"])["success"]
            )
```

## Test Utilities

### **MCP Server Test Helpers**
```python
import subprocess
import asyncio
import json

async def start_mcp_server(server_main_func):
    """Start an MCP server for testing."""
    
    # Create subprocess for server
    process = await asyncio.create_subprocess_exec(
        "python", "-m", server_main_func.__module__,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Wait for server to initialize
    await asyncio.sleep(1)
    
    return process

async def stop_mcp_server(server_process):
    """Stop MCP server process."""
    server_process.terminate()
    await server_process.wait()

async def send_mcp_request(server_process, request_data: dict):
    """Send MCP request to server."""
    
    request_json = json.dumps(request_data) + "\n"
    server_process.stdin.write(request_json.encode())
    await server_process.stdin.drain()
    
    # Read response
    response_line = await server_process.stdout.readline()
    return json.loads(response_line.decode())
```

## Test Configuration

### **MCP Test Settings**
```python
# MCP test configuration
MCP_TEST_CONFIG = {
    "protocol_version": "2024-11-05",
    "test_timeout": 30,
    "server_startup_timeout": 5,
    "max_concurrent_requests": 100,
    "enable_debug_logging": True
}

@pytest.fixture(scope="session")
def mcp_test_environment():
    """Set up MCP testing environment."""
    
    # Configure test environment
    os.environ["MCP_TEST_MODE"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    
    yield
    
    # Cleanup
    if "MCP_TEST_MODE" in os.environ:
        del os.environ["MCP_TEST_MODE"]
```

## Test Execution

### **Running MCP Tests**
```bash
# Run all MCP server tests
pytest tests/test_mcp/ -v

# Run specific server tests
pytest tests/test_mcp/test_firestore_mcp.py -v

# Run with protocol debugging
pytest tests/test_mcp/ -v -s --log-cli-level=DEBUG

# Run performance tests
pytest tests/test_mcp/ -m performance

# Generate MCP test report
pytest tests/test_mcp/ --html=mcp_test_report.html
```

## Related Documentation
- [Root Management Guide](../../MANAGE.md) - System overview and architecture
- [Tests Overview](../MANAGE.md) - Testing system documentation
- [MCP Servers Overview](../../mcp_servers/MANAGE.md) - MCP server implementations
- [Firestore MCP Server](../../mcp_servers/firestore/MANAGE.md) - Database server testing
- [Integration Tests](../test_integration/MANAGE.md) - End-to-end testing

## Implementation Status
**Current Status**: Planning phase - directory structure created, implementation pending

**Next Steps**:
1. Implement MCP protocol testing framework
2. Create Firestore MCP server test suite
3. Develop monitoring and notification server tests
4. Set up performance and load testing
5. Integrate with CI/CD pipeline
6. Create comprehensive test documentation

## Development Notes
- Tests validate MCP protocol compliance and server implementations
- Uses subprocess communication for isolated server testing
- Comprehensive error handling and edge case validation
- Performance testing for concurrent request handling
- Integration with existing test infrastructure
- Automated validation of tool registration and execution
