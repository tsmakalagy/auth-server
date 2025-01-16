# auth/session_manager.py
from datetime import datetime, timezone
from typing import Dict, Optional, List
from .config import supabase_client
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self):
        self.supabase = supabase_client

    def create_session(self, user_id: str, device_info: Dict = None) -> Optional[str]:
        """Create new user session."""
        try:
            result = self.supabase.table('user_sessions').insert({
                'user_id': user_id,
                'device_info': device_info,
                'is_active': True,
                'last_activity': datetime.now(timezone.utc).isoformat()
            }).execute()

            if result.data:
                return result.data[0]['id']
            return None

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise

    def get_active_sessions(self, user_id: str) -> List[Dict]:
        """Get all active sessions for user."""
        try:
            result = self.supabase.table('user_sessions').select('*').match({
                'user_id': user_id,
                'is_active': True
            }).execute()

            return result.data or []

        except Exception as e:
            logger.error(f"Error getting sessions: {e}")
            return []

    def end_session(self, session_id: str):
        """End a specific session."""
        try:
            self.supabase.table('user_sessions').update({
                'is_active': False,
                'ended_at': datetime.now(timezone.utc).isoformat()
            }).match({'id': session_id}).execute()

        except Exception as e:
            logger.error(f"Error ending session: {e}")
            raise

    def update_session_activity(self, session_id: str):
        """Update last activity time for session."""
        try:
            self.supabase.table('user_sessions').update({
                'last_activity': datetime.now(timezone.utc).isoformat()
            }).match({'id': session_id}).execute()

        except Exception as e:
            logger.error(f"Error updating session: {e}")