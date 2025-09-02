"""
Tests for the main orchestrator.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from orchestrator.main import HospitalityOrchestrator


class TestHospitalityOrchestrator:
    """Test cases for HospitalityOrchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing."""
        with patch('orchestrator.main.MCPToolset'):
            return HospitalityOrchestrator()
    
    @pytest.fixture
    def mock_session(self):
        """Mock session data."""
        return {
            'session_id': 'test_session',
            'user_id': 'test_user',
            'messages': [],
            'slots': {},
            'current_agent': 'inquiry',
            'booking_data': {}
        }
    
    def test_orchestrator_initialization(self, orchestrator):
        """Test orchestrator initializes correctly."""
        assert orchestrator.stm is not None
        assert orchestrator.ltm is not None
        assert orchestrator.root_agent is not None
    
    @pytest.mark.asyncio
    async def test_handle_request_new_session(self, orchestrator, mock_session):
        """Test handling request with new session."""
        with patch.object(orchestrator.stm, 'get_session', return_value=None), \
             patch.object(orchestrator.stm, 'create_session', return_value=mock_session), \
             patch.object(orchestrator.stm, 'update_session', return_value=True), \
             patch.object(orchestrator.ltm, 'get_user_preferences', return_value={}), \
             patch.object(orchestrator.root_agent, 'run', return_value="Hello! How can I help you?"):
            
            response = await orchestrator.handle_request(
                "Hi, I need a villa",
                "test_session",
                "test_user"
            )
            
            assert response == "Hello! How can I help you?"
    
    @pytest.mark.asyncio
    async def test_handle_request_existing_session(self, orchestrator, mock_session):
        """Test handling request with existing session."""
        with patch.object(orchestrator.stm, 'get_session', return_value=mock_session), \
             patch.object(orchestrator.stm, 'update_session', return_value=True), \
             patch.object(orchestrator.ltm, 'get_user_preferences', return_value={}), \
             patch.object(orchestrator.root_agent, 'run', return_value="I can help with that!"):
            
            response = await orchestrator.handle_request(
                "I need a place in Miami",
                "test_session",
                "test_user"
            )
            
            assert response == "I can help with that!"
    
    @pytest.mark.asyncio
    async def test_handle_request_error_handling(self, orchestrator):
        """Test error handling in request processing."""
        with patch.object(orchestrator.stm, 'get_session', side_effect=Exception("Database error")):
            
            response = await orchestrator.handle_request(
                "Test message",
                "test_session"
            )
            
            assert "encountered an error" in response
    
    @pytest.mark.asyncio
    async def test_get_pending_reminders(self, orchestrator):
        """Test getting pending reminders."""
        reminders = await orchestrator.get_pending_reminders()
        assert isinstance(reminders, list)
    
    @pytest.mark.asyncio
    async def test_get_pending_surveys(self, orchestrator):
        """Test getting pending surveys."""
        surveys = await orchestrator.get_pending_surveys()
        assert isinstance(surveys, list)
    
    @pytest.mark.asyncio
    async def test_send_precheckin_reminder(self, orchestrator):
        """Test sending pre-checkin reminder."""
        booking = {'booking_id': 'test_booking'}
        # Should not raise exception
        await orchestrator.send_precheckin_reminder(booking)
    
    @pytest.mark.asyncio
    async def test_send_survey(self, orchestrator):
        """Test sending survey."""
        booking = {'booking_id': 'test_booking'}
        # Should not raise exception
        await orchestrator.send_survey(booking)
    
    def test_orchestrator_agent_configuration(self, orchestrator):
        """Test that orchestrator agent is properly configured."""
        agent = orchestrator.root_agent
        assert agent.name == "hospitality_orchestrator"
        assert agent.model == "gemini-2.0-flash"
        assert "orchestrator" in agent.global_instruction.lower()
        assert "booking journey" in agent.global_instruction.lower()
    
    @pytest.mark.asyncio
    async def test_user_preferences_update_on_booking_completion(self, orchestrator, mock_session):
        """Test that user preferences are updated when booking is confirmed."""
        confirmed_session = mock_session.copy()
        confirmed_session['booking_data'] = {'status': 'confirmed'}
        confirmed_session['slots'] = {'city': 'Miami', 'budget': 500}
        
        with patch.object(orchestrator.stm, 'get_session', return_value=None), \
             patch.object(orchestrator.stm, 'create_session', return_value=confirmed_session), \
             patch.object(orchestrator.stm, 'update_session', return_value=True), \
             patch.object(orchestrator.ltm, 'get_user_preferences', return_value={}), \
             patch.object(orchestrator.ltm, 'update_user_preferences', return_value=True) as mock_update, \
             patch.object(orchestrator.root_agent, 'run', return_value="Booking confirmed!"):
            
            await orchestrator.handle_request(
                "Confirm booking",
                "test_session",
                "test_user"
            )
            
            mock_update.assert_called_once_with("test_user", confirmed_session['slots'])


@pytest.mark.asyncio
async def test_main_function():
    """Test the main function runs without error."""
    with patch('orchestrator.main.HospitalityOrchestrator') as mock_orchestrator:
        mock_instance = Mock()
        mock_instance.handle_request = AsyncMock(return_value="Test response")
        mock_orchestrator.return_value = mock_instance
        
        from orchestrator.main import main
        responses = await main()
        
        assert len(responses) == 2
        assert all(response == "Test response" for response in responses)


if __name__ == "__main__":
    pytest.main([__file__])
