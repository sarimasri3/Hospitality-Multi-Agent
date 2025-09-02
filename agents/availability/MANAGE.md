# Availability Agent Management

## Purpose & Responsibilities

The **Availability Agent** is responsible for **property search, ranking, and presentation** in the hospitality booking system. It finds available properties based on guest criteria, ranks them using an intelligent scoring system, and presents the best options with clear explanations and value propositions.

## Directory Structure

```
agents/availability/
├── __init__.py          # Package initialization
├── agent.py            # Main AvailabilityAgent implementation
├── ranking.py          # PropertyRanker with explainable scoring
└── prompts.py          # Agent prompts and templates
```

## Core Components

### Availability Agent (`agent.py`)

**Purpose**: Main agent class with property search and pricing tools

**Key Tools**:
```python
async def search_and_rank_properties(
    city: str,
    check_in_date: str,
    check_out_date: str,
    number_of_guests: int,
    max_price: Optional[float] = None,
    amenities: Optional[List[str]] = None,
    user_preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]
# Searches properties via MCP and ranks by suitability
# Returns: Ranked property results with recommendations

async def calculate_total_price(
    base_price: float,
    nights: int,
    add_ons: Optional[List[str]] = None,
    service_fee_percentage: float = 0.1,
    tax_percentage: float = 0.08,
    cleaning_fee: float = 50.0
) -> Dict[str, Any]
# Calculates comprehensive price breakdown
# Returns: Detailed pricing with fees, taxes, and add-ons

async def filter_by_amenities(
    properties: List[Dict],
    required_amenities: List[str]
) -> List[Dict]
# Filters properties by required amenities
# Returns: Properties matching amenity requirements

async def get_alternative_suggestions(
    city: str,
    check_in_date: str,
    check_out_date: str,
    number_of_guests: int
) -> Dict[str, Any]
# Generates alternatives when no properties found
# Returns: Nearby cities, date flexibility, split booking suggestions
```

**Agent Configuration**:
```python
availability_agent = Agent(
    name="availability_agent",
    model="gemini-2.0-flash",
    description="Searches for available properties and ranks them by suitability",
    global_instruction=AVAILABILITY_SYSTEM_PROMPT,
    instruction=AVAILABILITY_INSTRUCTION,
    tools=[search_and_rank_properties, calculate_total_price, 
           filter_by_amenities, get_alternative_suggestions]
)
```

### Property Ranker (`ranking.py`)

**Purpose**: Intelligent property ranking with explainable scoring

**Core Class**:
```python
class PropertyRanker:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        # Default weights:
        # price: 0.3, distance: 0.2, capacity_fit: 0.2, 
        # amenity_match: 0.2, recency: 0.1
        
    def rank_properties(
        self,
        properties: List[Dict],
        user_preferences: Dict[str, Any],
        search_criteria: Dict[str, Any]
    ) -> List[Tuple[Dict, float, List[str]]]
        # Returns: (property, score, reason_codes) tuples
```

**Scoring Factors**:

1. **Price Scoring** (`_score_price`)
   - Exceptional value: ≤50% of budget (full weight)
   - Great value: ≤75% of budget (0.8x weight)
   - Within budget: ≤100% of budget (0.5x weight)
   - Over budget: negative scoring

2. **Distance Scoring** (`_score_distance`)
   - Walking distance: <1km (full weight)
   - Close: <5km (0.8x weight)
   - Nearby: <10km (0.5x weight)
   - Uses Haversine formula for accuracy

3. **Capacity Scoring** (`_score_capacity`)
   - Perfect fit: exact guest count (full weight)
   - Comfortable: 1-2 extra spaces (0.8x weight)
   - Too large: >2 extra spaces (0.3x weight)
   - Insufficient: negative scoring

4. **Amenity Matching** (`_score_amenities`)
   - High match: ≥80% amenities (full weight)
   - Good match: ≥50% amenities (proportional)
   - Poor match: <50% amenities (minimal weight)

5. **Recency Bonus** (`_score_recency`)
   - New listings: <30 days (full weight)
   - Recent: <90 days (0.5x weight)
   - Older: no bonus

**Recommendation Formatting**:
```python
def format_recommendations(
    self,
    ranked_properties: List[Tuple[Dict, float, List[str]]],
    max_results: int = 3
) -> str
    # Formats top properties with reasons and amenities
    # Returns: User-friendly recommendation text
```

### Agent Prompts (`prompts.py`)

**System Prompt** (`AVAILABILITY_SYSTEM_PROMPT`):
- Defines agent as luxury property specialist
- Emphasizes value proposition and transparency
- Sets professional yet friendly communication style

**Instruction Prompt** (`AVAILABILITY_INSTRUCTION`):
- 6-step search and presentation process
- Focus on ranking, explanation, and decision support
- Handles no-availability scenarios

**Templates**:
```python
NO_AVAILABILITY_TEMPLATE = """
I've searched our properties in {city} for your dates ({check_in} to {check_out}), 
but unfortunately, I don't have any exact matches available.

Here are some alternatives that might work for you:
- Adjust Your Dates
- Nearby Locations  
- Adjust Guest Count
"""

PROPERTY_PRESENTATION_TEMPLATE = """
Based on your requirements, I've found {count} excellent properties in {city} 
for your stay from {check_in} to {check_out}:

{properties}

Which property interests you most?
"""

SINGLE_PROPERTY_DETAIL_TEMPLATE = """
**{name}**
📍 Location: {location}
💰 Price: ${price}/night (Total: ${total} for {nights} nights)
👥 Capacity: Up to {capacity} guests
🏠 Type: {property_type}

**Why We Recommend This:**
{reasons}

**Key Amenities:**
{amenities}
"""
```

## How to Use & Extend

### Using the Availability Agent

**In Orchestrator**:
```python
from agents.availability.agent import availability_agent

# Process availability request
response = await availability_agent.process_message(
    message="Find villas in Miami for 4 guests from March 15-18, budget $500/night",
    session_data=session_data
)
```

**Tool Integration**:
```python
# Search properties (connects to Firestore MCP)
search_result = await search_and_rank_properties(
    city="Miami",
    check_in_date="2025-03-15",
    check_out_date="2025-03-18", 
    number_of_guests=4,
    max_price=500.0,
    amenities=["pool", "wifi"],
    user_preferences={"preferred_type": "villa"}
)

# Calculate pricing
pricing = await calculate_total_price(
    base_price=400.0,
    nights=3,
    add_ons=["early_checkin"],
    service_fee_percentage=0.1,
    tax_percentage=0.08,
    cleaning_fee=50.0
)
```

### Extending Ranking Logic

**Custom Scoring Weights**:
```python
from agents.availability.ranking import PropertyRanker

# Create ranker with custom weights
custom_ranker = PropertyRanker(weights={
    "price": 0.4,        # Emphasize price more
    "distance": 0.3,     # Location very important
    "capacity_fit": 0.15,
    "amenity_match": 0.1,
    "recency": 0.05
})

# Use in ranking
ranked = custom_ranker.rank_properties(properties, preferences, criteria)
```

**Adding New Scoring Factors**:
```python
class ExtendedPropertyRanker(PropertyRanker):
    def __init__(self, weights=None):
        super().__init__(weights)
        self.weights['rating'] = 0.15  # Add rating factor
    
    def rank_properties(self, properties, preferences, criteria):
        # Call parent method
        scored = super().rank_properties(properties, preferences, criteria)
        
        # Add rating scoring
        for prop, score, reasons in scored:
            rating_score, rating_reason = self._score_rating(prop)
            score += rating_score
            if rating_reason:
                reasons.append(rating_reason)
        
        return scored
    
    def _score_rating(self, prop):
        """Score based on property rating."""
        rating = prop.get('rating', 0)
        if rating >= 4.5:
            return self.weights['rating'], f"Excellent {rating}★ rating"
        elif rating >= 4.0:
            return self.weights['rating'] * 0.8, f"Great {rating}★ rating"
        else:
            return 0, None
```

### Adding New Tools

**New Search Tool**:
```python
async def search_by_property_type(
    property_type: str,
    city: str,
    check_in_date: str,
    check_out_date: str
) -> Dict[str, Any]:
    """Search properties by specific type (villa, apartment, etc.)."""
    # Implementation
    return {"properties": [], "count": 0}

# Add to agent tools
availability_agent.tools.append(FunctionTool(search_by_property_type))
```

**Price Comparison Tool**:
```python
async def compare_property_prices(
    property_ids: List[str],
    nights: int
) -> Dict[str, Any]:
    """Compare pricing across multiple properties."""
    comparisons = []
    for prop_id in property_ids:
        # Get property details and calculate pricing
        pricing = await calculate_total_price(base_price, nights)
        comparisons.append({
            "property_id": prop_id,
            "pricing": pricing
        })
    
    return {"comparisons": comparisons}
```

## Integration with Other Components

### → `orchestrator/`
- **Request Routing**: Handles availability phase requests
- **Session Management**: Maintains search criteria and preferences
- **MCP Integration**: Connects tools to Firestore MCP server

### → `mcp_servers/firestore/`
- **Property Search**: `search_properties` tool via MCP
- **Availability Check**: Real-time availability queries
- **Property Details**: Detailed property information retrieval

### → `memory/`
- **User Preferences**: Stores search preferences and history
- **Session State**: Maintains current search criteria
- **Ranking Preferences**: Learns from user selections

### → `utils/`
- **Date Validation**: Validates check-in/check-out dates
- **Price Formatting**: Formats currency displays
- **Input Sanitization**: Cleans search parameters

### → `config/`
- **Business Rules**: Max guests, booking windows, pricing rules
- **Feature Flags**: Enable/disable ranking features
- **Pricing Configuration**: Service fees, tax rates, cleaning fees

## Alternative Suggestions Logic

### Nearby Cities Mapping
```python
nearby_cities = {
    "Miami": ["Fort Lauderdale", "Miami Beach", "Coral Gables"],
    "Los Angeles": ["Santa Monica", "Beverly Hills", "Malibu"],
    "New York": ["Brooklyn", "Queens", "Jersey City"],
    "San Francisco": ["Oakland", "Berkeley", "San Jose"],
    "Paris": ["Versailles", "Saint-Denis", "Boulogne-Billancourt"],
    "London": ["Westminster", "Camden", "Greenwich"]
}
```

### Suggestion Types
1. **Nearby Locations**: Alternative cities/neighborhoods
2. **Date Flexibility**: Suggest adjusting dates by few days
3. **Split Booking**: For large groups, suggest multiple properties
4. **Property Type**: Suggest alternative property types
5. **Budget Adjustment**: Suggest slightly higher budget ranges

## Performance Optimization

### Ranking Efficiency
```python
# Limit property set before ranking
def pre_filter_properties(properties, criteria):
    """Pre-filter properties before expensive ranking."""
    filtered = []
    for prop in properties:
        # Basic filters
        if prop['guest_space'] >= criteria['number_of_guests']:
            if criteria.get('max_price', float('inf')) >= prop['minimum_price']:
                filtered.append(prop)
    return filtered

# Use in ranking
pre_filtered = pre_filter_properties(properties, search_criteria)
ranked = ranker.rank_properties(pre_filtered, preferences, criteria)
```

### Caching Strategies
```python
# Cache expensive calculations
from functools import lru_cache

@lru_cache(maxsize=1000)
def calculate_distance_cached(lat1, lng1, lat2, lng2):
    """Cached distance calculation."""
    return calculate_distance(
        {'lat': lat1, 'lng': lng1},
        {'lat': lat2, 'lng': lng2}
    )
```

## Troubleshooting

### Common Issues

1. **No Properties Found**
   ```python
   # Debug search criteria
   print(f"Search: {city}, {check_in_date}-{check_out_date}, {guests} guests")
   print(f"Budget: ${max_price}, Amenities: {amenities}")
   
   # Check alternative suggestions
   alternatives = await get_alternative_suggestions(city, check_in, check_out, guests)
   print(f"Alternatives: {alternatives}")
   ```

2. **Ranking Issues**
   ```python
   # Debug ranking scores
   ranker = PropertyRanker()
   ranked = ranker.rank_properties(properties, preferences, criteria)
   
   for prop, score, reasons in ranked:
       print(f"{prop['name']}: {score:.3f} - {reasons}")
   ```

3. **Price Calculation Errors**
   ```python
   # Test pricing calculation
   try:
       pricing = await calculate_total_price(
           base_price=400.0,
           nights=3,
           add_ons=["early_checkin"]
       )
       print(f"Pricing: {pricing}")
   except Exception as e:
       print(f"Pricing error: {e}")
   ```

### Debug Commands

```python
# Test agent tools
from agents.availability.agent import availability_agent

# Test search
search_result = await availability_agent.tools[0].function(
    city="Miami",
    check_in_date="2025-03-15", 
    check_out_date="2025-03-18",
    number_of_guests=4
)

# Test ranking
from agents.availability.ranking import PropertyRanker
ranker = PropertyRanker()
print(f"Ranker weights: {ranker.weights}")

# Test prompts
from agents.availability.prompts import AVAILABILITY_SYSTEM_PROMPT
print(f"System prompt length: {len(AVAILABILITY_SYSTEM_PROMPT)}")
```

---

**Next Steps**: See [agents/MANAGE.md](../MANAGE.md) for agent coordination and [mcp_servers/firestore/MANAGE.md](../../mcp_servers/firestore/MANAGE.md) for database integration.
