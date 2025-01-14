# auth/auth_service.py
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import logging
from .config import supabase_client, Config
from .email_service import EmailService
from .token_manager import TokenManager
from .session_manager import SessionManager
import requests

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.supabase = supabase_client
        self.email_service = EmailService()
        self.token_manager = TokenManager()
        self.session_manager = SessionManager()

    async def register_with_email(self, email: str, name: str) -> Tuple[bool, str, Optional[Dict]]:
        """Handle email registration."""
        try:
            # Check if email exists
            user = await self.supabase.table('users').select('*').eq('email', email).execute()
            if user.data:
                return False, "Email already registered", None

            # Generate OTP
            otp = self._generate_otp()
            
            # Send verification email
            if not await self.email_service.send_verification(email, otp):
                return False, "Failed to send verification email", None

            # Store verification code
            await self.supabase.table('verification_codes').insert({
                'email': email,
                'code': otp,
                'type': 'email',
                'expires_at': (datetime.utcnow() + timedelta(minutes=Config.OTP_EXPIRY_MINUTES)).isoformat()
            }).execute()

            return True, "Verification email sent", {'email': email}

        except Exception as e:
            logger.error(f"Email registration error: {e}")
            return False, str(e), None

    async def register_with_phone(self, phone: str, name: str) -> Tuple[bool, str, Optional[Dict]]:
        """Handle phone registration."""
        try:
            # Check if phone exists
            user = await self.supabase.table('users').select('*').eq('phone_number', phone).execute()
            if user.data:
                return False, "Phone number already registered", None

            # Generate OTP
            otp = self._generate_otp()

            # Send SMS via gateway
            response = requests.post(Config.SMS_GATEWAY_URL, json={
                'phone_number': phone,
                'message': f'Your verification code is: {otp}'
            })

            if response.status_code != 200:
                return False, "Failed to send SMS", None

            # Store verification code
            await self.supabase.table('verification_codes').insert({
                'phone': phone,
                'code': otp,
                'type': 'phone',
                'expires_at': (datetime.utcnow() + timedelta(minutes=Config.OTP_EXPIRY_MINUTES)).isoformat()
            }).execute()

            return True, "Verification SMS sent", {'phone': phone}

        except Exception as e:
            logger.error(f"Phone registration error: {e}")
            return False, str(e), None

    def _generate_otp(self) -> str:
        """Generate OTP code."""
        import random
        return ''.join(random.choices('0123456789', k=Config.OTP_LENGTH))

    async def verify_otp(self, identifier: str, otp: str, auth_type: str) -> Tuple[bool, str, Optional[Dict]]:
        """Verify OTP for both email and phone."""
        try:
            # Get verification code
            result = await self.supabase.table('verification_codes').select('*').match({
                auth_type: identifier,
                'code': otp,
                'verified': False
            }).execute()

            if not result.data:
                return False, "Invalid verification code", None

            code_data = result.data[0]
            
            # Check expiry
            if datetime.fromisoformat(code_data['expires_at']) < datetime.utcnow():
                return False, "Verification code expired", None

            # Create or update user
            user_data = {
                auth_type: identifier,
                f'{auth_type}_verified': True
            }

            user = await self._get_or_create_user(user_data)
            
            # Generate tokens
            tokens = await self.token_manager.create_tokens(user['id'])
            
            # Create session
            session = await self.session_manager.create_session(user['id'])

            return True, "Verification successful", {
                'user': user,
                'tokens': tokens,
                'session': session
            }

        except Exception as e:
            logger.error(f"OTP verification error: {e}")
            return False, str(e), None

    async def _get_or_create_user(self, user_data: Dict) -> Dict:
        """Get existing user or create new one."""
        # Implementation details would go here
        pass