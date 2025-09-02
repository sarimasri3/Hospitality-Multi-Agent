# Survey Agent Management Guide

## Overview
The **Survey Agent** manages post-stay feedback collection and satisfaction metrics calculation. This agent schedules surveys, collects guest feedback, and calculates CSAT and NPS scores.

## Directory Structure
```
agents/survey/
├── MANAGE.md           # This management guide
├── __init__.py         # Package initialization
└── agent.py            # Survey agent implementation
```

## Core Responsibilities

### 1. **Survey Scheduling**
- Schedule surveys 24 hours after checkout
- Automated timing and delivery management
- Guest communication coordination

### 2. **Feedback Collection**
- Create standardized survey questions
- Collect ratings and comments
- Manage response processing

### 3. **Metrics Calculation**
- Calculate CSAT (Customer Satisfaction) scores
- Compute NPS (Net Promoter Score) metrics
- Generate satisfaction analytics

## Agent Implementation

### Core Agent Configuration
```python
survey_agent = Agent(
    name="survey_agent",
    model="gemini-2.0-flash",
    description="Collects post-stay feedback and calculates satisfaction metrics",
    tools=[
        FunctionTool(create_survey),
        FunctionTool(calculate_metrics),
        FunctionTool(schedule_survey_send)
    ]
)
```

### Available Tools

#### 1. **create_survey**
```python
async def create_survey(booking_id: str, property_id: str, guest_id: str) -> Dict[str, Any]
```
- Creates standardized post-stay survey
- Includes rating questions (1-5 scale)
- NPS recommendation question (1-10 scale)
- Open text feedback field

#### 2. **calculate_metrics**
```python
async def calculate_metrics(ratings: Dict[str, int], nps_score: int) -> Dict[str, Any]
```
- Calculates CSAT from rating averages
- Categorizes NPS (promoter/passive/detractor)
- Returns formatted metrics

#### 3. **schedule_survey_send**
```python
async def schedule_survey_send(booking_id: str, check_out_date: str, delay_hours: int = 24) -> Dict[str, Any]
```
- Schedules survey delivery timing
- Default 24-hour delay after checkout
- Configurable timing parameters

## Survey Questions

### Standard Question Set
1. **Overall Rating** (1-5): "How would you rate your overall stay?"
2. **Cleanliness** (1-5): "How clean was the property?"
3. **Accuracy** (1-5): "How accurate was the listing?"
4. **Check-in** (1-5): "How smooth was check-in?"
5. **Value** (1-5): "How was the value for money?"
6. **NPS** (1-10): "Would you recommend this property?"
7. **Comments** (text): "Any additional comments?"

## Metrics Calculation

### CSAT Calculation
- Average of all 1-5 ratings
- Converted to percentage (rating × 20)
- Rounded to 1 decimal place

### NPS Categories
- **Promoters**: Score 9-10
- **Passives**: Score 7-8
- **Detractors**: Score 1-6

## Usage Examples

### Basic Survey Flow
```python
# Schedule survey
schedule_result = await schedule_survey_send(
    booking_id="BK123456",
    check_out_date="2024-01-15T11:00:00"
)

# Create survey
survey = await create_survey(
    booking_id="BK123456",
    property_id="PROP789",
    guest_id="GUEST123"
)

# Calculate metrics from responses
metrics = await calculate_metrics(
    ratings={"overall": 5, "cleanliness": 4, "accuracy": 5},
    nps_score=9
)
```

## Integration Points

### **With Confirmation Agent**
- Receives checkout completion notifications
- Triggered after guest departure

### **With Analytics System**
- Feeds satisfaction metrics to reporting
- Provides trend analysis data

### **With Guest Support**
- Flags negative feedback for follow-up
- Escalates service issues

## Configuration

### **Environment Variables**
```bash
SURVEY_DELAY_HOURS=24
SURVEY_REMINDER_ENABLED=true
SURVEY_ANALYTICS_ENABLED=true
```

### **Feature Flags**
```yaml
survey:
  enabled: true
  auto_schedule: true
  metrics_calculation: true
  follow_up_alerts: true
```

## Troubleshooting

### **Common Commands**
```bash
# Test survey creation
python -c "from agents.survey.agent import create_survey; print('Survey creation available')"

# Check metrics calculation
python -c "from agents.survey.agent import calculate_metrics; print('Metrics calculation available')"
```

### **Log Analysis**
```bash
# Check survey logs
grep "survey" logs/hospitality.log | tail -10

# Monitor metrics calculation
grep "calculate_metrics" logs/hospitality.log
```

## Related Documentation
- [Root Management Guide](../../MANAGE.md) - System overview
- [Agents Overview](../MANAGE.md) - Agent system documentation
- [Confirmation Agent](../confirmation/MANAGE.md) - Booking confirmation
- [Configuration](../../config/MANAGE.md) - System settings
