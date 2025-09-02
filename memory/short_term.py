"""
Short-term memory management for session state.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import hashlib


class ShortTermMemory:
    """
    Manages short-term memory for active sessions.
    In production, this would use Redis or similar.
    """
    
    def __init__(self, ttl_minutes: int = 30):
        """
        Initialize STM with TTL configuration.
        
        Args:
            ttl_minutes: Time-to-live for sessions in minutes
        """
        self.ttl_minutes = ttl_minutes
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._max_size_mb = 100  # Maximum memory size
    
    async def create_session(
        self,
        session_id: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new session.
        
        Args:
            session_id: Unique session identifier
            user_id: Optional user ID
        
        Returns:
            New session dictionary
        """
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=self.ttl_minutes)).isoformat(),
            "current_agent": "inquiry",
            "slots": {},
            "context": {},
            "messages": [],
            "booking_data": {}
        }
        
        self._sessions[session_id] = session
        await self._cleanup_expired()
        
        return session
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Session dictionary or None if not found/expired
        """
        if session_id not in self._sessions:
            return None
        
        session = self._sessions[session_id]
        
        # Check if expired
        expires_at = datetime.fromisoformat(session['expires_at'])
        if datetime.now() > expires_at:
            del self._sessions[session_id]
            return None
        
        # Extend TTL on access
        session['expires_at'] = (datetime.now() + timedelta(minutes=self.ttl_minutes)).isoformat()
        session['updated_at'] = datetime.now().isoformat()
        
        return session
    
    async def update_session(
        self,
        session_id: str,
        session_data: Dict[str, Any]
    ) -> bool:
        """
        Update session data.
        
        Args:
            session_id: Session identifier
            session_data: Updated session data
        
        Returns:
            True if updated, False if session not found
        """
        if session_id not in self._sessions:
            return False
        
        session_data['updated_at'] = datetime.now().isoformat()
        session_data['expires_at'] = (datetime.now() + timedelta(minutes=self.ttl_minutes)).isoformat()
        
        self._sessions[session_id] = session_data
        return True
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if deleted, False if not found
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    async def update_slots(
        self,
        session_id: str,
        slots: Dict[str, Any]
    ) -> bool:
        """
        Update session slots.
        
        Args:
            session_id: Session identifier
            slots: Slot updates
        
        Returns:
            True if updated
        """
        session = await self.get_session(session_id)
        if not session:
            return False
        
        session['slots'].update(slots)
        return await self.update_session(session_id, session)
    
    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> bool:
        """
        Add a message to session history.
        
        Args:
            session_id: Session identifier
            role: Message role (user/assistant)
            content: Message content
        
        Returns:
            True if added
        """
        session = await self.get_session(session_id)
        if not session:
            return False
        
        session['messages'].append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Limit message history to last 50 messages
        if len(session['messages']) > 50:
            session['messages'] = session['messages'][-50:]
        
        return await self.update_session(session_id, session)
    
    async def _cleanup_expired(self):
        """Remove expired sessions."""
        now = datetime.now()
        expired = []
        
        for session_id, session in self._sessions.items():
            expires_at = datetime.fromisoformat(session['expires_at'])
            if now > expires_at:
                expired.append(session_id)
        
        for session_id in expired:
            del self._sessions[session_id]
    
    async def get_memory_usage(self) -> Dict[str, Any]:
        """
        Get current memory usage statistics.
        
        Returns:
            Memory usage information
        """
        # Estimate memory size
        total_size = len(json.dumps(self._sessions))
        size_mb = total_size / (1024 * 1024)
        
        return {
            "sessions_count": len(self._sessions),
            "size_mb": round(size_mb, 2),
            "max_size_mb": self._max_size_mb,
            "usage_percentage": round((size_mb / self._max_size_mb) * 100, 1)
        }