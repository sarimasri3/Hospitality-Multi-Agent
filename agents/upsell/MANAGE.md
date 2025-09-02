# Upsell Agent Management Guide

## Overview
The **Upsell Agent** suggests relevant add-on services to enhance guest experiences and increase booking value. This agent analyzes booking context to recommend personalized services that align with guest preferences and trip characteristics.

## Directory Structure
```
agents/upsell/
├── MANAGE.md           # This management guide
├── __init__.py         # Package initialization
└── agent.py            # Upsell agent implementation
```

## Core Responsibilities

### 1. **Add-on Service Suggestions**
- Analyze booking context for relevant recommendations
- Present personalized service options
- Calculate pricing and value propositions

### 2. **Context-Aware Recommendations**
- Consider property type and guest count
- Factor in trip purpose (honeymoon, family, business)
- Adapt to user preferences and booking history

### 3. **Revenue Optimization**
- Maximize booking value through strategic upselling
- Balance guest satisfaction with revenue goals
- Track conversion rates and service popularity

## Agent Implementation

### Core Agent Configuration
```python
upsell_agent = Agent(
    name="upsell_agent",
    model="gemini-2.0-flash",
    description="Suggests relevant add-on services to enhance the guest experience",
    instruction="Present add-on services that would enhance the guest's stay...",
    tools=[FunctionTool(suggest_add_ons)]
)
```

### Available Tools

#### **suggest_add_ons**
```python
async def suggest_add_ons(
    property_type: str,
    number_of_guests: int,
    trip_purpose: Optional[str] = None,
    user_preferences: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]
```
- **Purpose**: Generate contextual add-on recommendations
- **Returns**: Top 3 most relevant services with pricing and descriptions
- **Sorting**: By relevance score (0.0-1.0)

## Available Add-on Services

### **Standard Services**
1. **Early Check-in (12 PM)** - $50
   - Start vacation earlier with noon arrival
   - High relevance (0.8) for most bookings

2. **Late Check-out (2 PM)** - $50
   - Extended departure time for leisurely mornings
   - High relevance (0.8) for most bookings

3. **Welcome Basket** - $75
   - Local treats, wine, and artisanal snacks
   - Higher relevance for larger groups (>2 guests)

4. **In-Villa Spa Treatment** - $200
   - Professional 90-minute couples massage
   - Maximum relevance for honeymoon trips

5. **Private Chef Experience** - $300
   - Personal chef for gourmet dinner preparation
   - Optimal for groups of 4+ guests

### **Relevance Scoring Logic**
- **Base relevance**: Standard appeal for service type
- **Guest count multiplier**: Larger groups favor group services
- **Trip purpose boost**: Honeymoon trips prioritize romantic services
- **Property type consideration**: Villa amenities influence suggestions

## Usage Examples

### Basic Upsell Flow
```python
# Generate suggestions for family trip
suggestions = await suggest_add_ons(
    property_type="villa",
    number_of_guests=6,
    trip_purpose="family_vacation",
    user_preferences={"dining": "important", "relaxation": "high"}
)

# Expected top suggestions:
# 1. Private Chef Experience (relevance: 0.9)
# 2. Early Check-in (relevance: 0.8)
# 3. Welcome Basket (relevance: 0.7)
```

### Honeymoon Optimization
```python
# Romantic trip suggestions
suggestions = await suggest_add_ons(
    property_type="luxury_villa",
    number_of_guests=2,
    trip_purpose="honeymoon"
)

# Expected prioritization:
# 1. In-Villa Spa Treatment (relevance: 0.9)
# 2. Early Check-in (relevance: 0.8)
# 3. Late Check-out (relevance: 0.8)
```

## Integration Points

### **With Booking Agent**
- Receives booking context and guest information
- Triggered during booking confirmation process
- Updates total pricing with selected add-ons

### **With Confirmation Agent**
- Passes selected services for inclusion in confirmation
- Provides service details for guest communication

### **With Revenue Analytics**
- Reports conversion rates by service type
- Tracks revenue impact and guest satisfaction
- Feeds optimization algorithms

### **With Property Management**
- Coordinates service delivery scheduling
- Manages vendor relationships and availability
- Handles special request fulfillment

## Workflow Process

### 1. **Trigger Points**
- After successful booking creation
- During booking modification requests
- Pre-arrival communication (24-48 hours before)

### 2. **Recommendation Flow**
```
Booking Context → Analyze Preferences → Score Services → 
Rank by Relevance → Present Top 3 → Process Selection → Update Booking
```

### 3. **Selection Processing**
- Calculate updated total with selected services
- Schedule service delivery coordination
- Update booking confirmation details

## Extension Points

### **Additional Services**
```python
# Transportation services
{
    "id": "airport_transfer",
    "name": "Private Airport Transfer",
    "price": 150,
    "description": "Luxury vehicle pickup and drop-off"
}

# Experience packages
{
    "id": "wine_tour",
    "name": "Local Wine Tour",
    "price": 250,
    "description": "Guided tour of nearby vineyards with tastings"
}

# Convenience services
{
    "id": "grocery_stocking",
    "name": "Pre-Arrival Grocery Service",
    "price": 100,
    "description": "Villa stocked with essentials before arrival"
}
```

### **Dynamic Pricing**
```python
# Seasonal pricing adjustments
async def calculate_dynamic_pricing(base_price: float, season: str, demand: str) -> float:
    multipliers = {
        "peak": 1.3,
        "high": 1.15,
        "standard": 1.0,
        "low": 0.85
    }
    return base_price * multipliers.get(demand, 1.0)
```

### **Personalization Engine**
```python
# ML-based recommendations
async def get_personalized_suggestions(guest_history: dict, preferences: dict) -> List[dict]:
    # Implement machine learning model for personalized recommendations
    pass
```

## Configuration

### **Environment Variables**
```bash
# Upsell settings
UPSELL_ENABLED=true
UPSELL_MAX_SUGGESTIONS=3
UPSELL_MIN_RELEVANCE=0.5

# Pricing configuration
UPSELL_DYNAMIC_PRICING=true
UPSELL_SEASONAL_ADJUSTMENTS=true

# Integration settings
UPSELL_BOOKING_INTEGRATION=true
UPSELL_ANALYTICS_TRACKING=true
```

### **Feature Flags**
```yaml
upsell:
  enabled: true
  suggestions: true
  dynamic_pricing: false
  personalization: false
  analytics: true
```

## Performance Considerations

### **Recommendation Speed**
- Cache frequently accessed service data
- Pre-calculate relevance scores for common scenarios
- Optimize sorting algorithms for real-time responses

### **Conversion Optimization**
- A/B test different presentation formats
- Track which services convert best by context
- Adjust relevance scoring based on historical data

### **Revenue Analytics**
- Monitor average order value impact
- Track service adoption rates
- Measure guest satisfaction correlation

## Error Handling

### **Common Issues**
- **Service Unavailability**: Check availability before suggesting
- **Pricing Errors**: Validate pricing data integrity
- **Integration Failures**: Graceful degradation when booking updates fail

### **Fallback Strategies**
```python
# Default suggestions when context analysis fails
async def get_default_suggestions() -> List[dict]:
    return [
        {"id": "early_checkin", "relevance": 0.8},
        {"id": "late_checkout", "relevance": 0.8},
        {"id": "welcome_basket", "relevance": 0.6}
    ]
```

## Troubleshooting

### **Common Commands**
```bash
# Test suggestion generation
python -c "from agents.upsell.agent import suggest_add_ons; print('Upsell suggestions available')"

# Validate service data
python -c "import asyncio; from agents.upsell.agent import suggest_add_ons; print(asyncio.run(suggest_add_ons('villa', 4)))"
```

### **Debug Information**
- Check service availability and pricing data
- Verify relevance scoring logic
- Monitor conversion rates and guest feedback
- Validate integration with booking system

### **Log Analysis**
```bash
# Check upsell logs
grep "upsell" logs/hospitality.log | tail -20

# Monitor suggestion generation
grep "suggest_add_ons" logs/hospitality.log | grep ERROR

# Track conversion rates
grep "upsell_conversion" logs/hospitality.log
```

## Analytics and Metrics

### **Key Performance Indicators**
- **Conversion Rate**: Percentage of guests who select add-ons
- **Average Order Value**: Revenue impact per booking
- **Service Popularity**: Most frequently selected services
- **Guest Satisfaction**: Feedback on upsold services

### **Reporting Queries**
```python
# Conversion rate by service type
SELECT service_id, COUNT(*) as suggestions, 
       SUM(CASE WHEN selected THEN 1 ELSE 0 END) as conversions,
       (SUM(CASE WHEN selected THEN 1 ELSE 0 END) * 100.0 / COUNT(*)) as conversion_rate
FROM upsell_suggestions 
GROUP BY service_id;

# Revenue impact analysis
SELECT DATE(created_at) as date,
       SUM(service_price) as upsell_revenue,
       COUNT(DISTINCT booking_id) as bookings_with_upsells
FROM selected_upsells 
GROUP BY DATE(created_at);
```

## Related Documentation
- [Root Management Guide](../../MANAGE.md) - System overview and architecture
- [Agents Overview](../MANAGE.md) - Agent system documentation
- [Booking Agent](../booking/MANAGE.md) - Booking creation and management
- [Confirmation Agent](../confirmation/MANAGE.md) - Booking confirmation process
- [Configuration](../../config/MANAGE.md) - System configuration and settings

## Development Notes
- Agent uses Google ADK framework with Gemini 2.0 Flash model
- Implements context-aware recommendation algorithms
- Designed for real-time suggestion generation during booking flow
- Supports A/B testing and conversion optimization
- Integrates with revenue analytics and guest satisfaction tracking
