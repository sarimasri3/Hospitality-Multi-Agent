"""
Main Orchestrator for Hospitality Booking System.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from typing import Dict, Optional, Any, List
import asyncio
from pathlib import Path
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import all agents
from agents import (
    inquiry_agent,
    availability_agent,
    booking_agent,
    upsell_agent,
    confirmation_agent,
    precheckin_agent,
    survey_agent
)

# Import memory management
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HospitalityOrchestrator:
    """Main orchestrator for hospitality booking flow."""
    
    def __init__(self):
        """Initialize the orchestrator with all components."""
        # Initialize memory systems
        self.stm = ShortTermMemory()
        self.ltm = LongTermMemory()
        
        # Initialize MCP connection for Firestore
        firestore_mcp_path = Path(__file__).parent.parent / "mcp_servers" / "firestore" / "server.py"
        
        try:
            self.firestore_mcp = MCPToolset(
                connection_params=StdioServerParameters(
                    command="python",
                    args=[str(firestore_mcp_path.resolve())]
                )
            )
            logger.info("Firestore MCP connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Firestore MCP: {e}")
            self.firestore_mcp = None
        
        # Initialize root orchestrator agent
        self.root_agent = LlmAgent(
            name="hospitality_orchestrator",
            model="gemini-2.0-flash",
            global_instruction="""You are the main orchestrator for a luxury villa booking system.
            Your role is to guide guests through the complete booking journey while ensuring
            a smooth, personalized experience. You coordinate between specialized agents,
            maintain conversation context, and ensure all steps are completed successfully.
            
            Core responsibilities:
            - Route conversations to appropriate specialized agents
            - Maintain session state and context between agent transfers
            - Ensure smooth handoffs between agents
            - Handle errors gracefully
            - Track the booking flow progress
            - Provide a cohesive experience despite using multiple agents""",
            
            instruction="""Orchestration flow for booking:
            
            1. **Initial Inquiry** (InquiryAgent):
               - Greet the guest warmly
               - Collect: city, check-in/out dates, number of guests, budget
               - Validate all inputs
               - Once complete, transfer to availability
            
            2. **Property Search** (AvailabilityAgent):
               - Search available properties based on criteria
               - Rank properties by suitability
               - Present top 3-5 options with explanations
               - Once guest selects, transfer to booking
            
            3. **Booking Creation** (BookingAgent):
               - Validate final availability
               - Calculate total price with all fees
               - Process booking with idempotency
               - Authorize payment
               - Once confirmed, transfer to upsell
            
            4. **Upsell Opportunities** (UpsellAgent):
               - Suggest relevant add-ons based on context
               - Present 2-3 most relevant options
               - Update booking if add-ons selected
               - Transfer to confirmation
            
            5. **Booking Confirmation** (ConfirmationAgent):
               - Provide comprehensive confirmation
               - Send confirmation email
               - Explain house rules and next steps
               - Schedule pre-checkin reminder
            
            6. **Pre-Checkin** (PreCheckinAgent) - Triggered 48hrs before:
               - Send reminder with check-in instructions
               - Collect arrival information
               - Address special requests
            
            7. **Post-Stay Survey** (SurveyAgent) - Triggered 24hrs after checkout:
               - Send feedback survey
               - Calculate CSAT/NPS metrics
               - Thank guest for feedback
            
            CRITICAL Rules:
            - Maintain context throughout the entire flow
            - If any step fails, handle gracefully and provide alternatives
            - Track metrics for each interaction
            - Ensure idempotent operations for bookings
            - Save session state after each major step""",
            
            agents=[
                inquiry_agent,
                availability_agent,
                booking_agent,
                upsell_agent,
                confirmation_agent,
                precheckin_agent,
                survey_agent
            ],
            tools=[self.firestore_mcp] if self.firestore_mcp else []
        )
    
    async def handle_request(
        self,
        user_input: str,
        session_id: str,
        user_id: Optional[str] = None
    ) -> str:
        """
        Handle a user request with session management.
        
        Args:
            user_input: User's message
            session_id: Unique session identifier
            user_id: Optional user ID for authenticated users
        
        Returns:
            Agent's response
        """
        try:
            # Load or create session
            session = await self.stm.get_session(session_id)
            if not session:
                session = await self.stm.create_session(session_id, user_id)
                logger.info(f"Created new session: {session_id}")
            
            # Load user preferences if user_id provided
            user_preferences = {}
            if user_id:
                user_preferences = await self.ltm.get_user_preferences(user_id)
            
            # Add user input to conversation history
            session['messages'].append({
                "role": "user",
                "content": user_input
            })
            
            # Prepare context for agent
            context = {
                "session_id": session_id,
                "user_id": user_id,
                "slots": session.get('slots', {}),
                "current_agent": session.get('current_agent', 'inquiry'),
                "user_preferences": user_preferences,
                "booking_data": session.get('booking_data', {})
            }
            
            # Process through root agent
            response = await self.root_agent.run(
                messages=session['messages'],
                context=context
            )
            
            # Add response to conversation history
            session['messages'].append({
                "role": "assistant",
                "content": response
            })
            
            # Update session
            await self.stm.update_session(session_id, session)
            
            # Save long-term preferences if booking completed
            if session.get('booking_data', {}).get('status') == 'confirmed' and user_id:
                await self.ltm.update_user_preferences(
                    user_id,
                    session.get('slots', {})
                )
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return "I apologize, but I encountered an error processing your request. Please try again."
    
    async def process_scheduled_tasks(self):
        """
        Process scheduled tasks like pre-checkin reminders and surveys.
        This would run as a background task in production.
        """
        while True:
            try:
                # Check for pre-checkin reminders
                reminders = await self.get_pending_reminders()
                for reminder in reminders:
                    await self.send_precheckin_reminder(reminder)
                
                # Check for post-stay surveys
                surveys = await self.get_pending_surveys()
                for survey in surveys:
                    await self.send_survey(survey)
                
                # Sleep for 1 hour
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in scheduled tasks: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute on error
    
    async def get_pending_reminders(self) -> List[Dict]:
        """Get bookings that need pre-checkin reminders."""
        # In production, query Firestore for bookings with check-in in 48 hours
        return []
    
    async def send_precheckin_reminder(self, booking: Dict):
        """Send pre-checkin reminder for a booking."""
        # Trigger PreCheckinAgent for the booking
        pass
    
    async def get_pending_surveys(self) -> List[Dict]:
        """Get bookings that need post-stay surveys."""
        # In production, query Firestore for completed bookings
        return []
    
    async def send_survey(self, booking: Dict):
        """Send post-stay survey for a booking."""
        # Trigger SurveyAgent for the booking
        pass


async def main():
    """Main entry point for the orchestrator."""
    orchestrator = HospitalityOrchestrator()
    
    # Example usage
    session_id = "test_session_123"
    
    # Simulate a booking flow
    responses = []
    
    # Initial inquiry
    response = await orchestrator.handle_request(
        "Hi, I'm looking for a villa in Miami for next weekend, March 15-17, for 4 people",
        session_id
    )
    responses.append(response)
    print(f"Agent: {response}\n")
    
    # Continue conversation
    response = await orchestrator.handle_request(
        "My budget is around $500 per night",
        session_id
    )
    responses.append(response)
    print(f"Agent: {response}\n")
    
    return responses


if __name__ == "__main__":
    asyncio.run(main())