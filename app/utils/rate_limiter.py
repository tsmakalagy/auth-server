# auth/utils/rate_limiter.py
from datetime import datetime, timedelta
from typing import Tuple
from ..config import Config, supabase_client
import logging

logger = logging.getLogger(__name__)

def check_rate_limit(identifier: str, ip_address: str) -> bool:
    """Check if the attempts exceed rate limit."""
    try:
        # Count attempts in the last window
        window_start = (datetime.utcnow() - timedelta(seconds=Config.RATE_LIMIT_WINDOW)).isoformat()
        
        result = supabase_client.table('login_attempts').select('*').filter(
            'created_at', 'gt', window_start
        ).filter('identifier', 'eq', identifier).execute()

        attempts = len(result.data)
        
        # Log the check for debugging
        logger.debug(f"Rate limit check - Identifier: {identifier}, "
                    f"Attempts: {attempts}, Limit: {Config.MAX_LOGIN_ATTEMPTS}")
        
        return attempts < Config.MAX_LOGIN_ATTEMPTS

    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        return True  # Allow on error to prevent blocking legitimate users

def log_attempt(identifier: str, ip_address: str, success: bool):
    """Log an authentication attempt."""
    try:
        # Clean up old records first (optional but recommended)
        cleanup_window = (datetime.utcnow() - timedelta(days=1)).isoformat()
        supabase_client.table('login_attempts').delete().filter(
            'created_at', 'lt', cleanup_window
        ).execute()

        # Log new attempt
        supabase_client.table('login_attempts').insert({
            'identifier': identifier,
            'ip_address': ip_address,
            'success': success,
            'created_at': datetime.utcnow().isoformat()
        }).execute()

    except Exception as e:
        logger.error(f"Error logging attempt: {e}")

def get_remaining_attempts(identifier: str) -> int:
    """Get remaining attempts for the identifier."""
    try:
        window_start = (datetime.utcnow() - timedelta(seconds=Config.RATE_LIMIT_WINDOW)).isoformat()
        
        result = supabase_client.table('login_attempts').select('*').filter(
            'created_at', 'gt', window_start
        ).filter('identifier', 'eq', identifier).execute()

        attempts = len(result.data)
        return max(0, Config.MAX_LOGIN_ATTEMPTS - attempts)

    except Exception as e:
        logger.error(f"Error getting remaining attempts: {e}")
        return Config.MAX_LOGIN_ATTEMPTS  # Return max on error