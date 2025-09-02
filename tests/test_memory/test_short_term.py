"""
Tests for Short-term Memory management.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from memory.short_term import ShortTermMemory


class TestShortTermMemory:
    """Test cases for ShortTermMemory."""
    
    @pytest.fixture
    def stm(self):
        """Create STM instance for testing."""
        return ShortTermMemory(ttl_minutes=30)
    
    @pytest.mark.asyncio
    async def test_create_session(self, stm):
        """Test session creation."""
        session_id = "test_session_001"
        user_id = "user_123"
        
        session = await stm.create_session(session_id, user_id)
        
        assert session['session_id'] == session_id
        assert session['user_id'] == user_id
        assert session['current_agent'] == 'inquiry'
        assert session['slots'] == {}
        assert session['context'] == {}
        assert session['messages'] == []
        assert session['booking_data'] == {}
        assert 'created_at' in session
        assert 'updated_at' in session
        assert 'expires_at' in session
    
    @pytest.mark.asyncio
    async def test_create_session_without_user_id(self, stm):
        """Test session creation without user ID."""
        session_id = "test_session_002"
        
        session = await stm.create_session(session_id)
        
        assert session['session_id'] == session_id
        assert session['user_id'] is None
    
    @pytest.mark.asyncio
    async def test_get_session_existing(self, stm):
        """Test retrieving existing session."""
        session_id = "test_session_003"
        created_session = await stm.create_session(session_id, "user_123")
        
        retrieved_session = await stm.get_session(session_id)
        
        assert retrieved_session is not None
        assert retrieved_session['session_id'] == session_id
        assert retrieved_session['user_id'] == "user_123"
    
    @pytest.mark.asyncio
    async def test_get_session_nonexistent(self, stm):
        """Test retrieving non-existent session."""
        result = await stm.get_session("nonexistent_session")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_session_extends_ttl(self, stm):
        """Test that getting a session extends its TTL."""
        session_id = "test_session_004"
        await stm.create_session(session_id)
        
        # Get the session
        session1 = await stm.get_session(session_id)
        original_expires = session1['expires_at']
        
        # Wait a moment and get again
        import asyncio
        await asyncio.sleep(0.1)
        session2 = await stm.get_session(session_id)
        new_expires = session2['expires_at']
        
        assert new_expires > original_expires
    
    @pytest.mark.asyncio
    async def test_get_session_expired(self, stm):
        """Test retrieving expired session."""
        # Create STM with very short TTL
        short_stm = ShortTermMemory(ttl_minutes=0.001)  # ~0.06 seconds
        session_id = "test_session_005"
        
        await short_stm.create_session(session_id)
        
        # Wait for expiration
        import asyncio
        await asyncio.sleep(0.1)
        
        result = await short_stm.get_session(session_id)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_session(self, stm):
        """Test session update."""
        session_id = "test_session_006"
        session = await stm.create_session(session_id)
        
        # Modify session data
        session['slots'] = {'city': 'Miami', 'guests': 4}
        session['current_agent'] = 'availability'
        
        success = await stm.update_session(session_id, session)
        assert success is True
        
        # Verify update
        updated_session = await stm.get_session(session_id)
        assert updated_session['slots']['city'] == 'Miami'
        assert updated_session['current_agent'] == 'availability'
    
    @pytest.mark.asyncio
    async def test_update_session_nonexistent(self, stm):
        """Test updating non-existent session."""
        success = await stm.update_session("nonexistent", {'test': 'data'})
        assert success is False
    
    @pytest.mark.asyncio
    async def test_delete_session(self, stm):
        """Test session deletion."""
        session_id = "test_session_007"
        await stm.create_session(session_id)
        
        # Verify session exists
        session = await stm.get_session(session_id)
        assert session is not None
        
        # Delete session
        success = await stm.delete_session(session_id)
        assert success is True
        
        # Verify session is gone
        session = await stm.get_session(session_id)
        assert session is None
    
    @pytest.mark.asyncio
    async def test_delete_session_nonexistent(self, stm):
        """Test deleting non-existent session."""
        success = await stm.delete_session("nonexistent")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_update_slots(self, stm):
        """Test slot updates."""
        session_id = "test_session_008"
        await stm.create_session(session_id)
        
        # Update slots
        slots = {'city': 'Miami', 'guests': 4, 'budget': 500}
        success = await stm.update_slots(session_id, slots)
        assert success is True
        
        # Verify slots
        session = await stm.get_session(session_id)
        assert session['slots'] == slots
    
    @pytest.mark.asyncio
    async def test_update_slots_merge(self, stm):
        """Test slot updates merge with existing slots."""
        session_id = "test_session_009"
        await stm.create_session(session_id)
        
        # Set initial slots
        await stm.update_slots(session_id, {'city': 'Miami', 'guests': 2})
        
        # Update with new slots
        await stm.update_slots(session_id, {'guests': 4, 'budget': 500})
        
        # Verify merge
        session = await stm.get_session(session_id)
        assert session['slots']['city'] == 'Miami'  # Preserved
        assert session['slots']['guests'] == 4      # Updated
        assert session['slots']['budget'] == 500    # Added
    
    @pytest.mark.asyncio
    async def test_update_slots_nonexistent_session(self, stm):
        """Test updating slots for non-existent session."""
        success = await stm.update_slots("nonexistent", {'city': 'Miami'})
        assert success is False
    
    @pytest.mark.asyncio
    async def test_add_message(self, stm):
        """Test adding messages to session."""
        session_id = "test_session_010"
        await stm.create_session(session_id)
        
        # Add user message
        success = await stm.add_message(session_id, "user", "Hello, I need a villa")
        assert success is True
        
        # Add assistant message
        success = await stm.add_message(session_id, "assistant", "I can help you with that!")
        assert success is True
        
        # Verify messages
        session = await stm.get_session(session_id)
        assert len(session['messages']) == 2
        assert session['messages'][0]['role'] == 'user'
        assert session['messages'][0]['content'] == "Hello, I need a villa"
        assert session['messages'][1]['role'] == 'assistant'
        assert session['messages'][1]['content'] == "I can help you with that!"
        assert 'timestamp' in session['messages'][0]
        assert 'timestamp' in session['messages'][1]
    
    @pytest.mark.asyncio
    async def test_add_message_limit(self, stm):
        """Test message limit enforcement."""
        session_id = "test_session_011"
        await stm.create_session(session_id)
        
        # Add 55 messages (more than the 50 limit)
        for i in range(55):
            await stm.add_message(session_id, "user", f"Message {i}")
        
        # Verify only last 50 are kept
        session = await stm.get_session(session_id)
        assert len(session['messages']) == 50
        assert session['messages'][0]['content'] == "Message 5"  # First 5 should be dropped
        assert session['messages'][-1]['content'] == "Message 54"
    
    @pytest.mark.asyncio
    async def test_add_message_nonexistent_session(self, stm):
        """Test adding message to non-existent session."""
        success = await stm.add_message("nonexistent", "user", "Hello")
        assert success is False
    
    @pytest.mark.asyncio
    async def test_cleanup_expired(self, stm):
        """Test cleanup of expired sessions."""
        # Create sessions with different expiration times
        session1_id = "session_1"
        session2_id = "session_2"
        
        await stm.create_session(session1_id)
        await stm.create_session(session2_id)
        
        # Manually expire session1
        session1 = await stm.get_session(session1_id)
        session1['expires_at'] = (datetime.now() - timedelta(minutes=1)).isoformat()
        stm._sessions[session1_id] = session1
        
        # Trigger cleanup
        await stm._cleanup_expired()
        
        # Verify expired session is gone, active session remains
        assert await stm.get_session(session1_id) is None
        assert await stm.get_session(session2_id) is not None
    
    @pytest.mark.asyncio
    async def test_get_memory_usage(self, stm):
        """Test memory usage statistics."""
        # Create some sessions
        for i in range(5):
            await stm.create_session(f"session_{i}", f"user_{i}")
            await stm.update_slots(f"session_{i}", {
                'city': f'City_{i}',
                'guests': i + 1,
                'budget': (i + 1) * 100
            })
        
        usage = await stm.get_memory_usage()
        
        assert usage['sessions_count'] == 5
        assert usage['size_mb'] > 0
        assert usage['max_size_mb'] == 100
        assert 0 <= usage['usage_percentage'] <= 100
    
    @pytest.mark.asyncio
    async def test_session_ttl_configuration(self):
        """Test STM with custom TTL configuration."""
        custom_stm = ShortTermMemory(ttl_minutes=60)
        assert custom_stm.ttl_minutes == 60
        
        session = await custom_stm.create_session("test_session")
        created_at = datetime.fromisoformat(session['created_at'])
        expires_at = datetime.fromisoformat(session['expires_at'])
        
        # Should expire in approximately 60 minutes
        time_diff = (expires_at - created_at).total_seconds()
        assert 3590 <= time_diff <= 3610  # Allow small variance
    
    @pytest.mark.asyncio
    async def test_session_data_persistence(self, stm):
        """Test that session data persists across operations."""
        session_id = "persistence_test"
        
        # Create session with initial data
        await stm.create_session(session_id, "user_123")
        await stm.update_slots(session_id, {'city': 'Miami'})
        await stm.add_message(session_id, "user", "Hello")
        
        # Perform multiple operations
        await stm.update_slots(session_id, {'guests': 4})
        await stm.add_message(session_id, "assistant", "Hi there!")
        
        # Verify all data is preserved
        session = await stm.get_session(session_id)
        assert session['user_id'] == "user_123"
        assert session['slots']['city'] == 'Miami'
        assert session['slots']['guests'] == 4
        assert len(session['messages']) == 2
        assert session['messages'][0]['content'] == "Hello"
        assert session['messages'][1]['content'] == "Hi there!"


if __name__ == "__main__":
    pytest.main([__file__])
