# auth/token_manager.py
from datetime import datetime, timezone
from typing import Dict, Optional
from .config import Config, supabase_client
import jwt
import logging

logger = logging.getLogger(__name__)

class TokenManager:
    def __init__(self):
        self.supabase = supabase_client

    def create_tokens(self, user_id: str) -> Dict[str, str]:
        """Create access and refresh tokens."""
        try:
            # Create access token
            access_token = jwt.encode(
                {
                    'user_id': user_id,
                    'type': 'access',
                    'exp': datetime.now(timezone.utc) + Config.JWT_ACCESS_TOKEN_EXPIRES
                },
                Config.JWT_SECRET_KEY,
                algorithm='HS256'
            )

            # Create refresh token
            refresh_token = jwt.encode(
                {
                    'user_id': user_id,
                    'type': 'refresh',
                    'exp': datetime.now(timezone.utc) + Config.JWT_REFRESH_TOKEN_EXPIRES
                },
                Config.JWT_SECRET_KEY,
                algorithm='HS256'
            )

            # Store refresh token
            self.supabase.table('refresh_tokens').insert({
                'user_id': user_id,
                'token': refresh_token,
                'expires_at': (datetime.now(timezone.utc) + Config.JWT_REFRESH_TOKEN_EXPIRES).isoformat()
            }).execute()

            return {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

        except Exception as e:
            logger.error(f"Error creating tokens: {e}")
            raise

    def verify_token(self, token: str, token_type: str = 'access') -> Optional[Dict]:
        """Verify token and return payload if valid."""
        try:
            payload = jwt.decode(
                token,
                Config.JWT_SECRET_KEY,
                algorithms=['HS256']
            )

            if payload.get('type') != token_type:
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            return None

    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Create new access token using refresh token."""
        payload = self.verify_token(refresh_token, 'refresh')
        if not payload:
            return None

        # Check if refresh token is valid in database
        result = self.supabase.table('refresh_tokens').select('*').match({
            'token': refresh_token,
            'is_revoked': False
        }).execute()

        if not result.data:
            return None

        return self.create_tokens(payload['user_id'])