"""
Inquiry Agent for initial greeting and slot collection.
"""

from google.adk.agents import Agent
from google.adk.tools.function_tool import FunctionTool

from .prompts import (
    INQUIRY_SYSTEM_PROMPT,
    INQUIRY_INSTRUCTION,
    SLOT_VALIDATION_PROMPTS,
    CONFIRMATION_TEMPLATE,
    ERROR_MESSAGES
)
from .tools import (
    validate_city,
    validate_dates,
    validate_guests,
    validate_budget,
    extract_slots_from_message,
    compile_session_slots
)


# Create the Inquiry Agent
inquiry_agent = Agent(
    name="inquiry_agent",
    model="gemini-2.0-flash",
    description="Handles initial greeting and collects booking requirements",
    global_instruction=INQUIRY_SYSTEM_PROMPT,
    instruction=INQUIRY_INSTRUCTION,
    tools=[
        FunctionTool(validate_city),
        FunctionTool(validate_dates),
        FunctionTool(validate_guests),
        FunctionTool(validate_budget),
        FunctionTool(extract_slots_from_message),
        FunctionTool(compile_session_slots),
    ]
)