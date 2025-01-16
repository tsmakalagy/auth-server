# auth/auth_service.py
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional
import logging
from .config import supabase_client, Config
from .email_service import EmailService
from .token_manager import TokenManager
from .session_manager import SessionManager
import requests
import pytz

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.supabase = supabase_client
        self.email_service = EmailService()
        self.token_manager = TokenManager()
        self.session_manager = SessionManager()

    def register_with_email(self, email: str, name: str) -> Tuple[bool, str, Optional[Dict]]:
        """Handle email registration."""
        try:
            # Check if email exists
            user = self.supabase.table('users').select('*').eq('email', email).execute()
            if user.data:
                return False, "Email already registered", None

            # Generate OTP
            otp = self._generate_otp()
            
            # Send verification email
            if not self.email_service.send_verification(email, otp):
                return False, "Failed to send verification email", None

            # Store verification code
            try:
                self.supabase.table('verification_codes').insert({
                    'email': email,
                    'code': otp,
                    'name': name,  # Store name for later user creation
                    'type': 'email',
                    'expires_at': (datetime.now(pytz.UTC) + timedelta(minutes=Config.OTP_EXPIRY_MINUTES)).isoformat()
                }).execute()
            except Exception as e:
                logger.error(f"Failed to store verification code: {e}")
                return False, "Failed to create verification code", None

            if not self.email_service.send_verification(email, otp):
                # Cleanup the stored code if email fails
                self.supabase.table('verification_codes').delete().match({
                    'email': email,
                    'code': otp
                }).execute()
                return False, "Failed to send verification email", None

            return True, "Verification email sent", {'email': email}

        except Exception as e:
            logger.error(f"Email registration error: {e}")
            return False, str(e), None

    def register_with_phone(self, phone: str, name: str) -> Tuple[bool, str, Optional[Dict]]:
        """Handle phone registration."""
        try:
            # Check if phone exists
            user = self.supabase.table('users').select('*').eq('phone_number', phone).execute()
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
            self.supabase.table('verification_codes').insert({
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

    def verify_otp(self, email: str, otp: str) -> Tuple[bool, str, Optional[Dict]]:
        """Verify email OTP."""
        try:
            now = datetime.now(pytz.UTC)
            logger.info(f"Verifying OTP for email: {email}")

            # Get verification code
            result = self.supabase.table('verification_codes').select('*').match({
                'email': email,
                'code': otp,
                'verified': False
            }).execute()

            if not result.data:
                logger.warning(f"No verification code found for email: {email}")
                return False, "Invalid verification code", None

            code_data = result.data[0]
            
            # Parse expiry time
            expires_at = datetime.fromisoformat(code_data['expires_at'])
            if not expires_at.tzinfo:
                expires_at = pytz.UTC.localize(expires_at)
            
            if expires_at < now:
                logger.warning(f"Expired code for email: {email}")
                return False, "Verification code expired", None

            # Update verification status
            try:
                self.supabase.table('verification_codes').update({
                    'verified': True,
                    'verified_at': now.isoformat()
                }).match({
                    'id': code_data['id']
                }).execute()
            except Exception as e:
                logger.error(f"Failed to update verification status: {e}")
                return False, "Error updating verification status", None

            # Create or update user
            try:
                user_data = {
                    'email': email,
                    'email_verified': True,
                    'name': code_data.get('name'),
                    'updated_at': now.isoformat()
                }

                user_response = self.supabase.table('users').upsert(user_data).execute()
                if not user_response.data:
                    raise Exception("Failed to create/update user")
                user = user_response.data[0]

                # Generate access token
                tokens = self.token_manager.create_tokens(user['id'])
                
                # Create session
                session = self.session_manager.create_session(user['id'])

                return True, "Verification successful", {
                    'user': user,
                    'tokens': tokens,
                    'session': session
                }

            except Exception as e:
                logger.error(f"User creation/update error: {e}")
                return False, "Error creating user account", None

        except Exception as e:
            logger.error(f"OTP verification error: {e}")
            return False, str(e), None

    def _get_or_create_user(self, user_data: Dict) -> Dict:
        """Get existing user or create new one."""
        # Implementation details would go here
        pass