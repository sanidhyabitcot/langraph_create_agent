"""
Session Service
Manages conversation sessions and history
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

from data.models import Session, Message


class SessionService:
    """Service for managing conversation sessions"""
    
    def __init__(self):
        """Initialize session storage"""
        self.sessions: Dict[str, Session] = {}
    
    def create_session(self, user_id: Optional[str] = None) -> Session:
        """
        Create a new conversation session
        
        Args:
            user_id: Optional user identifier
            
        Returns:
            Created session
        """
        session = Session(
            session_id=str(uuid.uuid4()),
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            messages=[]
        )
        
        self.sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get session by ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session if found, None otherwise
        """
        return self.sessions.get(session_id)
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str
    ) -> bool:
        """
        Add message to session
        
        Args:
            session_id: Session identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            
        Returns:
            Success status
        """
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.utcnow()
        )
        
        session.messages.append(message)
        session.updated_at = datetime.utcnow()
        return True
    
    def get_conversation_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get conversation history in LangGraph format
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of messages
        """
        session = self.sessions.get(session_id)
        if not session:
            return []
        
        return [
            {"role": msg.role, "content": msg.content}
            for msg in session.messages
        ]
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            Success status
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def list_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all sessions with optional user filter
        
        Args:
            user_id: Optional user ID filter
            
        Returns:
            List of session summaries
        """
        sessions = []
        for session in self.sessions.values():
            if user_id is None or session.user_id == user_id:
                sessions.append({
                    "session_id": session.session_id,
                    "user_id": session.user_id,
                    "created_at": session.created_at.isoformat(),
                    "updated_at": session.updated_at.isoformat(),
                    "message_count": len(session.messages)
                })
        
        sessions.sort(key=lambda x: x["updated_at"], reverse=True)
        return sessions


# Global instance
session_service = SessionService()
