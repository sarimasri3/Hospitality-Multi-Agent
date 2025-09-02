# Inquiry Agent Management

## Purpose & Responsibilities

The **Inquiry Agent** handles **initial guest greeting and booking requirement collection** through natural conversation. It serves as the entry point to the booking system, gathering essential information slots while maintaining a warm, professional interaction.

## Directory Structure

```
agents/inquiry/
├── __init__.py          # Package initialization
├── agent.py            # Main InquiryAgent implementation
├── prompts.py          # Agent prompts and conversation templates
└── tools.py            # Validation and slot extraction tools
```

## Core Components

### Inquiry Agent (`agent.py`)

**Purpose**: Main agent class for greeting guests and collecting booking requirements

**Key Tools**:
```python
async def validate_city(city: str) -> Dict[str, Any]
# Validates destination against supported cities
# Returns: Validation result with normalized city name

async def validate_dates(
    check_in_date: str,
    check_out_date: str
) -> Dict[str, Any]
# Validates booking dates and calculates nights
# Returns: Validation result with parsed dates

async def validate_guests(number_of_guests: int) -> Dict[str, Any]
# Validates guest count within acceptable range (1-10)
# Returns: Validation result with confirmation message

async def validate_budget(budget_string: str) -> Dict[str, Any]
# Parses and validates budget from user input
# Returns: Parsed budget range or single value

async def extract_slots_from_message(message: str) -> Dict[str, Any]
# Extracts booking information from natural language
# Returns: Dictionary of identified slots

async def compile_session_slots(
    existing_slots: Dict[str, Any],
    new_slots: Dict[str, Any]
) -> Dict[str, Any]
# Merges new slots with existing session data
# Returns: Complete slots dictionary with completeness status
```

**Agent Configuration**:
```python
inquiry_agent = Agent(
    name="inquiry_agent",
    model="gemini-2.0-flash",
    description="Handles initial greeting and collects booking requirements",
    global_instruction=INQUIRY_SYSTEM_PROMPT,
    instruction=INQUIRY_INSTRUCTION,
    tools=[validate_city, validate_dates, validate_guests, 
           validate_budget, extract_slots_from_message, compile_session_slots]
)
```

### Agent Prompts (`prompts.py`)

**System Prompt** (`INQUIRY_SYSTEM_PROMPT`):
- Defines agent as friendly hospitality booking assistant
- Emphasizes warm, professional personality
- Lists required information slots to collect
- Sets conversational guidelines and rapport-building approach

**Required Information Slots**:
1. **City/Location** - Where they want to stay
2. **Check-in Date** - When they want to arrive (YYYY-MM-DD)
3. **Check-out Date** - When they want to leave (YYYY-MM-DD)
4. **Number of Guests** - How many people will be staying
5. **Budget** (optional) - Their price range per night

**Instruction Prompt** (`INQUIRY_INSTRUCTION`):
- 7-step conversation process from greeting to confirmation
- Natural slot collection with validation
- Information summarization and guest confirmation
- Transfer preparation to availability agent

**Conversation Templates**:
```python
SLOT_VALIDATION_PROMPTS = {
    "city": "I'd be happy to help you find the perfect villa! Which city or area are you looking to stay in?",
    "check_in_date": "When are you planning to arrive? Please let me know the date (for example, 2025-03-15).",
    "check_out_date": "And when would you be checking out?",
    "number_of_guests": "How many guests will be joining you for this stay?",
    "budget": "Do you have a budget in mind per night? This will help me find the best options for you."
}

CONFIRMATION_TEMPLATE = """Perfect! Let me confirm your booking details:

📍 **Location**: {city}
📅 **Check-in**: {check_in_date}
📅 **Check-out**: {check_out_date}
👥 **Guests**: {number_of_guests}
💰 **Budget**: {budget}

Does everything look correct?"""

ERROR_MESSAGES = {
    "invalid_dates": "I notice the check-out date is before or the same as the check-in date. Could you please provide valid dates?",
    "past_dates": "The dates you've selected are in the past. Please provide future dates for your stay.",
    "too_many_guests": "Our villas can accommodate up to 10 guests. For larger groups, you might need to book multiple properties.",
    "invalid_city": "I couldn't find that destination in our system. Could you please provide another city or be more specific?"
}
```

### Validation Tools (`tools.py`)

**City Validation**:
```python
async def validate_city(city: str) -> Dict[str, Any]:
    # Supported cities list
    supported_cities = [
        "Miami", "Los Angeles", "New York", "San Francisco", "Chicago",
        "Austin", "Seattle", "Boston", "Denver", "Portland",
        "Las Vegas", "Orlando", "San Diego", "Phoenix", "Nashville",
        "Paris", "London", "Rome", "Barcelona", "Amsterdam",
        "Tokyo", "Sydney", "Dubai", "Singapore", "Bangkok"
    ]
    
    # Normalization and fuzzy matching
    normalized_city = city.strip().title()
    
    # Returns validation result with normalized city name
```

**Date Validation**:
```python
async def validate_dates(check_in_date: str, check_out_date: str) -> Dict[str, Any]:
    # Business rules validation:
    # - No past dates
    # - Check-out after check-in
    # - Maximum 365 days advance booking
    # - Minimum 1 night, maximum 30 nights
    
    # Returns parsed dates with nights calculation
```

**Guest Validation**:
```python
async def validate_guests(number_of_guests: int) -> Dict[str, Any]:
    # Range validation: 1-10 guests
    # Returns validation with personalized message
```

**Budget Parsing**:
```python
async def validate_budget(budget_string: str) -> Dict[str, Any]:
    # Handles multiple formats:
    # - Single value: "$500", "500"
    # - Range: "300-500", "$300-$500"
    # - Currency symbol removal and normalization
    
    # Returns min/max budget range
```

**Natural Language Processing**:
```python
async def extract_slots_from_message(message: str) -> Dict[str, Any]:
    # Regex patterns for slot extraction:
    # - Dates: YYYY-MM-DD format
    # - Guests: "2 people", "3 guests", "party of 4"
    # - Budget: Dollar amounts with various formats
    # - Cities: "in Miami", "to Paris", location patterns
    
    # Returns dictionary of extracted slots
```

**Session Management**:
```python
async def compile_session_slots(existing_slots: Dict, new_slots: Dict) -> Dict[str, Any]:
    # Merges new information with existing session data
    # Tracks completeness and missing slots
    # Returns updated session state with _complete and _missing flags
```

## How to Use & Extend

### Using the Inquiry Agent

**In Orchestrator**:
```python
from agents.inquiry.agent import inquiry_agent

# Process initial inquiry
response = await inquiry_agent.process_message(
    message="Hi, I need a villa in Miami for 4 people from March 15-18",
    session_data=session_data
)
```

**Direct Tool Usage**:
```python
# Extract slots from message
extracted_slots = await extract_slots_from_message(
    "Looking for a place in Miami for 4 guests from 2025-03-15 to 2025-03-18, budget around $500"
)

# Validate extracted information
city_validation = await validate_city(extracted_slots.get('city', ''))
date_validation = await validate_dates(
    extracted_slots.get('check_in_date', ''),
    extracted_slots.get('check_out_date', '')
)
guest_validation = await validate_guests(extracted_slots.get('number_of_guests', 0))

# Compile session slots
session_slots = await compile_session_slots(
    existing_slots={},
    new_slots=extracted_slots
)
```

### Extending Slot Collection

**Adding New Required Slots**:
```python
# In tools.py - extend compile_session_slots
async def compile_extended_session_slots(
    existing_slots: Dict[str, Any],
    new_slots: Dict[str, Any]
) -> Dict[str, Any]:
    """Extended slot compilation with additional requirements."""
    merged = existing_slots.copy()
    
    for key, value in new_slots.items():
        if value is not None and value != "":
            merged[key] = value
    
    # Extended required slots
    required_slots = [
        'city', 'check_in_date', 'check_out_date', 'number_of_guests',
        'property_type', 'special_requests'  # New requirements
    ]
    
    missing_slots = [slot for slot in required_slots if slot not in merged or merged[slot] is None]
    
    merged['_complete'] = len(missing_slots) == 0
    merged['_missing'] = missing_slots
    
    return merged

# Add validation for new slots
async def validate_property_type(property_type: str) -> Dict[str, Any]:
    """Validate property type preference."""
    valid_types = ["villa", "apartment", "house", "condo", "any"]
    normalized = property_type.lower().strip()
    
    if normalized in valid_types:
        return {
            "valid": True,
            "property_type": normalized,
            "message": f"I'll search for {normalized} properties for you."
        }
    
    return {
        "valid": False,
        "message": "Please specify: villa, apartment, house, condo, or any type."
    }
```

**Enhanced NLP Extraction**:
```python
async def extract_enhanced_slots(message: str) -> Dict[str, Any]:
    """Enhanced slot extraction with more patterns."""
    slots = await extract_slots_from_message(message)  # Base extraction
    
    # Property type patterns
    property_patterns = {
        r'\b(villa|villas)\b': 'villa',
        r'\b(apartment|apt)\b': 'apartment',
        r'\b(house|home)\b': 'house',
        r'\b(condo|condominium)\b': 'condo'
    }
    
    for pattern, prop_type in property_patterns.items():
        if re.search(pattern, message, re.IGNORECASE):
            slots['property_type'] = prop_type
            break
    
    # Special requests extraction
    request_patterns = [
        r'(pet.friendly|pets? allowed)',
        r'(wheelchair accessible|accessible)',
        r'(pool|swimming pool)',
        r'(ocean view|sea view|beach view)',
        r'(parking|garage)'
    ]
    
    special_requests = []
    for pattern in request_patterns:
        if re.search(pattern, message, re.IGNORECASE):
            special_requests.append(re.search(pattern, message, re.IGNORECASE).group(1))
    
    if special_requests:
        slots['special_requests'] = special_requests
    
    return slots
```

### Multi-language Support

**Localized Prompts**:
```python
LOCALIZED_PROMPTS = {
    "en": {
        "greeting": "Hello! I'd be delighted to help you find the perfect villa for your stay.",
        "city_prompt": "Which city or area are you looking to stay in?",
        "date_prompt": "When are you planning to arrive?",
        "guest_prompt": "How many guests will be joining you?"
    },
    "es": {
        "greeting": "¡Hola! Estaré encantado de ayudarte a encontrar la villa perfecta para tu estadía.",
        "city_prompt": "¿En qué ciudad o área te gustaría hospedarte?",
        "date_prompt": "¿Cuándo planeas llegar?",
        "guest_prompt": "¿Cuántos huéspedes los acompañarán?"
    },
    "fr": {
        "greeting": "Bonjour! Je serais ravi de vous aider à trouver la villa parfaite pour votre séjour.",
        "city_prompt": "Dans quelle ville ou région souhaitez-vous séjourner?",
        "date_prompt": "Quand prévoyez-vous d'arriver?",
        "guest_prompt": "Combien d'invités vous accompagneront?"
    }
}

async def get_localized_prompt(prompt_key: str, language: str = "en") -> str:
    """Get localized prompt based on user's language preference."""
    return LOCALIZED_PROMPTS.get(language, LOCALIZED_PROMPTS["en"]).get(prompt_key, "")
```

## Integration with Other Components

### → `orchestrator/`
- **Entry Point**: First agent in the booking workflow
- **Session Initialization**: Creates initial session with collected slots
- **Workflow Trigger**: Transfers to availability agent when complete

### → `memory/`
- **Session Storage**: Stores collected slots in short-term memory
- **User Preferences**: Remembers past preferences and destinations
- **Conversation History**: Maintains interaction context

### → `utils/`
- **Input Validation**: Uses validators for data integrity
- **Date Formatting**: Formats dates for user-friendly display
- **Text Processing**: Sanitizes and normalizes user input

### → `config/`
- **Business Rules**: Booking constraints and validation limits
- **Supported Destinations**: List of available cities
- **Feature Flags**: Enable/disable advanced slot collection

### → `agents/availability/`
- **Data Handoff**: Passes validated slots to availability search
- **Requirement Consistency**: Ensures search criteria alignment
- **Workflow Continuation**: Seamless transition between agents

## Conversation Flow Patterns

### Initial Greeting Flow

1. **Welcome Message**
   ```
   "Hello! I'd be delighted to help you find the perfect villa for your stay. 
   Where are you looking to go, and when?"
   ```

2. **Information Collection**
   ```
   User: "I need a place in Miami for 4 people"
   Agent: "Miami is a wonderful choice! When are you planning to arrive?"
   ```

3. **Validation and Confirmation**
   ```
   Agent: "Perfect! Let me confirm:
   📍 Location: Miami
   📅 Check-in: 2025-03-15
   📅 Check-out: 2025-03-18
   👥 Guests: 4
   Does everything look correct?"
   ```

### Error Handling Flow

1. **Invalid Date Handling**
   ```
   User: "From March 18 to March 15"
   Agent: "I notice the check-out date is before the check-in date. 
   Could you please provide the correct dates?"
   ```

2. **Unsupported City**
   ```
   User: "I want to stay in Atlantis"
   Agent: "I couldn't find Atlantis in our destinations. 
   Could you try another city or be more specific about the location?"
   ```

3. **Capacity Issues**
   ```
   User: "For 15 people"
   Agent: "Our villas accommodate up to 10 guests. For larger groups, 
   you might need to book multiple properties. Would you like me to help with that?"
   ```

## Performance Optimization

### Slot Extraction Efficiency

```python
import re
from functools import lru_cache

@lru_cache(maxsize=1000)
def compile_regex_patterns():
    """Cache compiled regex patterns for better performance."""
    return {
        'dates': re.compile(r'\b(\d{4}-\d{2}-\d{2})\b'),
        'guests': re.compile(r'(\d+)\s*(?:people|guests|persons|adults)', re.IGNORECASE),
        'budget': re.compile(r'\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)'),
        'cities': re.compile(r'(?:in|to|at|near)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)')
    }

async def optimized_slot_extraction(message: str) -> Dict[str, Any]:
    """Optimized slot extraction using cached patterns."""
    patterns = compile_regex_patterns()
    slots = {}
    
    # Use pre-compiled patterns
    date_matches = patterns['dates'].findall(message)
    if len(date_matches) >= 2:
        slots['check_in_date'] = date_matches[0]
        slots['check_out_date'] = date_matches[1]
    
    guest_match = patterns['guests'].search(message)
    if guest_match:
        slots['number_of_guests'] = int(guest_match.group(1))
    
    return slots
```

### Validation Caching

```python
from functools import lru_cache

@lru_cache(maxsize=500)
def cached_city_validation(city: str) -> bool:
    """Cache city validation results."""
    supported_cities = get_supported_cities()
    return city.strip().title() in supported_cities

async def fast_validate_city(city: str) -> Dict[str, Any]:
    """Fast city validation using cache."""
    if cached_city_validation(city):
        return {
            "valid": True,
            "normalized_city": city.strip().title(),
            "message": f"Great choice! {city.strip().title()} is a wonderful destination."
        }
    
    return {
        "valid": False,
        "message": f"I couldn't find {city} in our destinations."
    }
```

## Troubleshooting

### Common Issues

1. **Slot Extraction Failures**
   ```python
   # Debug slot extraction
   message = "I need a villa in Miami for 4 people from March 15-18"
   extracted = await extract_slots_from_message(message)
   print(f"Extracted slots: {extracted}")
   
   # Check individual patterns
   import re
   dates = re.findall(r'\b(\d{4}-\d{2}-\d{2})\b', message)
   print(f"Date matches: {dates}")
   ```

2. **Validation Errors**
   ```python
   # Test validation functions
   city_result = await validate_city("Miami")
   print(f"City validation: {city_result}")
   
   date_result = await validate_dates("2025-03-15", "2025-03-18")
   print(f"Date validation: {date_result}")
   
   guest_result = await validate_guests(4)
   print(f"Guest validation: {guest_result}")
   ```

3. **Session Slot Issues**
   ```python
   # Debug session compilation
   existing = {"city": "Miami"}
   new = {"check_in_date": "2025-03-15", "number_of_guests": 4}
   
   compiled = await compile_session_slots(existing, new)
   print(f"Compiled slots: {compiled}")
   print(f"Complete: {compiled.get('_complete', False)}")
   print(f"Missing: {compiled.get('_missing', [])}")
   ```

### Debug Commands

```python
# Test inquiry agent tools
from agents.inquiry.agent import inquiry_agent
from agents.inquiry.tools import *

# Test slot extraction
message = "Looking for a villa in Miami for 4 guests from 2025-03-15 to 2025-03-18, budget $500"
slots = await extract_slots_from_message(message)
print(f"Extracted: {slots}")

# Test validations
city_val = await validate_city("Miami")
date_val = await validate_dates("2025-03-15", "2025-03-18")
guest_val = await validate_guests(4)
budget_val = await validate_budget("$500")

print(f"Validations: city={city_val['valid']}, dates={date_val['valid']}, guests={guest_val['valid']}, budget={budget_val['valid']}")

# Test session compilation
session = await compile_session_slots({}, slots)
print(f"Session complete: {session.get('_complete', False)}")
```

---

**Next Steps**: See [agents/MANAGE.md](../MANAGE.md) for agent coordination and [agents/availability/MANAGE.md](../availability/MANAGE.md) for the next workflow step.
