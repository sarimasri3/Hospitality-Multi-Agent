# Firestore MCP Server Management Guide

## Overview
The **Firestore MCP Server** provides database operations for the hospitality booking system through the Model Context Protocol (MCP). This server handles all Firebase Firestore interactions including user management, property listings, bookings, and data persistence.

## Directory Structure
```
mcp_servers/firestore/
├── MANAGE.md           # This management guide
├── __init__.py         # Package initialization
├── server.py           # Main MCP server implementation
├── models.py           # Pydantic data models
└── transactions.py     # Database transaction logic
```

## Core Responsibilities

### 1. **Database Operations**
- User creation and management
- Property listing and search
- Booking creation with idempotency
- Status updates and data retrieval

### 2. **MCP Protocol Implementation**
- Tool registration and exposure
- Request/response handling
- Error management and logging
- Server lifecycle management

### 3. **Data Integrity**
- Transaction management for bookings
- Overlap checking for availability
- Natural key generation for idempotency
- Validation and constraint enforcement

## Server Implementation

### Core Server Configuration
```python
server = Server()
initialization_options = InitializationOptions(
    server_name="firestore-mcp-server",
    server_version="0.1.0"
)
```

### Firebase Initialization
```python
# Credential-based initialization
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
db = firestore.client()
```

## Available Tools

### **User Management**

#### 1. **create_user**
```python
async def create_user(
    name: str,
    email: str,
    role: str = "guest",
    phone: Optional[str] = None,
    preferences: Optional[Dict[str, Any]] = None
) -> Dict
```
- Creates new user with unique email validation
- Supports guest/host/admin roles
- Stores preferences and contact information

#### 2. **get_user**
```python
async def get_user(user_id: Optional[str] = None, email: Optional[str] = None) -> Dict
```
- Retrieves user by ID or email
- Returns complete user profile data
- Handles user not found scenarios

### **Property Management**

#### 3. **create_property**
```python
async def create_property(
    user_id: str, name: str, description: str,
    city: str, country: str, address: str,
    lat: float, lng: float, minimum_price: float,
    property_type: str, guest_space: int, amenities: List[str],
    images: Optional[List[str]] = None,
    check_in_time: str = "15:00",
    check_out_time: str = "11:00"
) -> Dict
```
- Creates property listings with location data
- Automatic weekend pricing (20% premium)
- Amenity and image management

#### 4. **search_properties**
```python
async def search_properties(
    city: Optional[str] = None,
    check_in_date: Optional[str] = None,
    check_out_date: Optional[str] = None,
    number_of_guests: Optional[int] = None,
    max_price: Optional[float] = None,
    amenities: Optional[List[str]] = None
) -> Dict
```
- Multi-criteria property search
- Availability checking with date overlap detection
- Amenity filtering and guest capacity validation
- Returns up to 10 matching properties

### **Booking Management**

#### 5. **create_booking**
```python
async def create_booking(
    property_id: str, guest_id: str, host_id: str,
    check_in_date: str, check_out_date: str,
    number_of_guests: int, total_price: float,
    add_ons: Optional[List[str]] = None
) -> Dict
```
- Transactional booking creation with idempotency
- Automatic overlap checking
- Natural key generation for duplicate prevention
- Add-on service support

#### 6. **get_booking**
```python
async def get_booking(booking_id: str) -> Dict
```
- Retrieves complete booking details
- Includes all booking metadata and status

#### 7. **update_booking_status_tool**
```python
async def update_booking_status_tool(
    booking_id: str,
    new_status: str,
    reason: Optional[str] = None
) -> Dict
```
- Updates booking status (pending/confirmed/cancelled/completed)
- Audit trail with reason tracking
- Status transition validation

#### 8. **get_user_bookings**
```python
async def get_user_bookings(
    user_id: str,
    role: str = "guest",
    status: Optional[str] = None
) -> Dict
```
- Retrieves all bookings for a user
- Supports both guest and host perspectives
- Optional status filtering

## Data Models

### **User Model**
```python
class User(BaseModel):
    uid: str
    name: str
    email: str  # unique
    role: UserRole  # guest/host/admin
    phone: Optional[str]
    preferences: Dict[str, Any]
    created_at: datetime
    last_login: Optional[datetime]
```

### **Property Model**
```python
class Property(BaseModel):
    property_id: str
    user_id: str  # host FK
    name: str
    description: str
    status: PropertyStatus  # active/inactive/maintenance
    location: Location
    minimum_price: float
    property_type: str
    guest_space: int
    amenities: List[str]
    prices: Dict[str, float]  # weekday/weekend
```

### **Booking Model**
```python
class Booking(BaseModel):
    booking_id: str
    property_id: str
    host_id: str
    guest_id: str
    check_in_date: datetime
    check_out_date: datetime
    number_of_guests: int
    total_price: float
    status: BookingStatus  # pending/confirmed/cancelled/completed
    add_ons: List[str]
```

## Transaction Management

### **Booking Creation Transaction**
- Idempotency key generation using natural keys
- Availability overlap checking
- Atomic booking creation with status tracking
- Rollback on conflicts or errors

### **Natural Key Generation**
```python
def generate_natural_key(property_id: str, guest_id: str, check_in: datetime) -> str:
    # Creates unique key for duplicate detection
    return f"{property_id}_{guest_id}_{check_in.strftime('%Y%m%d')}"
```

### **Overlap Detection**
```python
def check_booking_overlap(db, property_id: str, check_in: datetime, check_out: datetime) -> bool:
    # Checks for conflicting bookings in date range
    # Returns True if overlap exists
```

## Usage Examples

### Basic User and Property Setup
```python
# Create a host user
user_result = await create_user(
    name="John Host",
    email="john@example.com",
    role="host",
    phone="+1234567890"
)

# Create a property
property_result = await create_property(
    user_id=user_result["user_id"],
    name="Luxury Beach Villa",
    description="Beautiful oceanfront villa",
    city="Miami",
    country="USA",
    address="123 Ocean Drive",
    lat=25.7617,
    lng=-80.1918,
    minimum_price=300.0,
    property_type="villa",
    guest_space=8,
    amenities=["pool", "wifi", "kitchen", "parking"]
)
```

### Property Search and Booking
```python
# Search for properties
search_result = await search_properties(
    city="Miami",
    check_in_date="2024-06-15",
    check_out_date="2024-06-20",
    number_of_guests=4,
    max_price=500.0,
    amenities=["pool", "wifi"]
)

# Create booking
booking_result = await create_booking(
    property_id="prop123",
    guest_id="guest456",
    host_id="host789",
    check_in_date="2024-06-15",
    check_out_date="2024-06-20",
    number_of_guests=4,
    total_price=1500.0,
    add_ons=["early_checkin", "welcome_basket"]
)
```

## Integration Points

### **With Agents**
- Provides database operations for all booking agents
- Handles data persistence for agent workflows
- Supports session state management

### **With Orchestrator**
- Receives database requests through MCP protocol
- Returns structured responses for agent processing
- Manages transaction coordination

### **With External Systems**
- Firebase Firestore for data storage
- Google Cloud authentication
- MCP protocol for tool exposure

## Configuration

### **Environment Variables**
```bash
# Firebase configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
FIREBASE_PROJECT_ID=your-project-id

# MCP server settings
MCP_SERVER_NAME=firestore-mcp-server
MCP_SERVER_VERSION=0.1.0

# Logging configuration
LOG_LEVEL=INFO
LOG_FILE_PATH=firestore_mcp.log
```

### **Firebase Setup**
```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login and initialize project
firebase login
firebase init firestore

# Deploy Firestore rules and indexes
firebase deploy --only firestore
```

## Error Handling

### **Common Error Scenarios**
- **Authentication Failures**: Invalid credentials or permissions
- **Booking Conflicts**: Overlapping date ranges
- **Validation Errors**: Invalid data formats or constraints
- **Network Issues**: Firebase connection problems

### **Error Response Format**
```python
{
    "success": False,
    "message": "Detailed error description",
    "error_code": "BOOKING_OVERLAP",  # Optional
    "details": {}  # Optional additional context
}
```

### **Retry Logic**
- Automatic retry for transient network errors
- Exponential backoff for rate limiting
- Circuit breaker for persistent failures

## Performance Considerations

### **Query Optimization**
- Composite indexes for multi-field queries
- Pagination for large result sets
- Caching for frequently accessed data

### **Transaction Efficiency**
- Minimize transaction scope and duration
- Batch operations where possible
- Use subcollections for related data

### **Monitoring Metrics**
- Request latency and throughput
- Error rates by operation type
- Database read/write costs
- Connection pool utilization

## Security

### **Authentication**
- Service account credentials for server access
- User authentication through Firebase Auth
- Role-based access control (RBAC)

### **Data Validation**
- Pydantic models for input validation
- SQL injection prevention through parameterized queries
- Input sanitization and constraint checking

### **Privacy Protection**
- PII encryption for sensitive data
- Audit logging for data access
- GDPR compliance for user data

## Troubleshooting

### **Common Commands**
```bash
# Test MCP server connection
python -m mcp_servers.firestore.server

# Validate Firebase credentials
firebase auth:list

# Check Firestore rules
firebase firestore:rules:get

# Monitor server logs
tail -f firestore_mcp.log
```

### **Debug Information**
- Check Firebase project configuration
- Verify service account permissions
- Validate Firestore security rules
- Monitor network connectivity

### **Log Analysis**
```bash
# Check server startup
grep "Firebase Admin SDK initialized" firestore_mcp.log

# Monitor tool registration
grep "Registered.*tools" firestore_mcp.log

# Track booking operations
grep "create_booking" firestore_mcp.log | grep ERROR
```

## Development Setup

### **Local Development**
```bash
# Install dependencies
pip install firebase-admin mcp pydantic python-dotenv

# Set up environment
cp .env.example .env
# Edit .env with your Firebase credentials

# Run server
python -m mcp_servers.firestore.server
```

### **Testing**
```bash
# Run unit tests
python -m pytest tests/test_mcp/test_firestore.py

# Integration tests
python -m pytest tests/test_integration/test_firestore_integration.py

# Load testing
python scripts/load_test_firestore.py
```

## Related Documentation
- [Root Management Guide](../../MANAGE.md) - System overview and architecture
- [MCP Servers Overview](../MANAGE.md) - MCP server system documentation
- [Orchestrator](../../orchestrator/MANAGE.md) - Request coordination and routing
- [Agents Overview](../../agents/MANAGE.md) - Agent system integration
- [Configuration](../../config/MANAGE.md) - System configuration and settings

## Development Notes
- Server implements MCP protocol for tool exposure to agents
- Uses Firebase Firestore for scalable NoSQL data storage
- Implements transactional booking creation with idempotency
- Supports real-time queries and complex filtering
- Designed for high availability and horizontal scaling
- Integrates with Google Cloud ecosystem for authentication and monitoring
