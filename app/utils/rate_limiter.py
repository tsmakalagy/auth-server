# auth/utils/rate_limiter.py
from datetime import datetime, timedelta
from typing import Tuple
from ..config import Config, supabase_client
import logging

logger = logging.getLogger(__name__)

async def check_rate_limit(identifier: str, ip_address: str) -> bool:
    """Check if the attempts exceed rate limit."""
    try:
        # Count attempts in the last window
        window_start = (datetime.utcnow() - timedelta(seconds=Config.RATE_LIMIT_WINDOW)).isoformat()
        
        result = await supabase_client.table('login_attempts').select('*').filter(
            'created_at', 'gt', window_start
        ).filter('identifier', 'eq', identifier).execute()

        attempts = len(result.data)
        return attempts < Config.MAX_LOGIN_ATTEMPTS

    except Exception as e:
        logger.error(f"Rate limit check error: {e}")
        return True  # Allow on error

async def log_attempt(identifier: str, ip_address: str, success: bool):
    """Log an authentication attempt."""
    try:
        await supabase_client.table('login_attempts').insert({
            'identifier': identifier,
            'ip_address': ip_address,
            'success': success,
            'created_at': datetime.utcnow().isoformat()
        }).execute()

    except Exception as e:
        logger.error(f"Error logging attempt: {e}")