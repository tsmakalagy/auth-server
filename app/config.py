# auth/config.py
import os
from datetime import timedelta
from supabase import create_client, Client

class Config:
    # Application Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # JWT Settings
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-jwt-secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Supabase Settings
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY')
    
    # Email Settings
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    SMTP_FROM_EMAIL = os.getenv('SMTP_FROM_EMAIL')
    
    # SMS Gateway Settings
    SMS_GATEWAY_URL = os.getenv('SMS_GATEWAY_URL', 'https://sms.godana.mg/send-sms')
    
    # OTP Settings
    OTP_LENGTH = 6
    OTP_EXPIRY_MINUTES = 15
    MAX_OTP_ATTEMPTS = 3
    
    # Rate Limiting
    RATE_LIMIT_WINDOW = 15 * 60  # 15 minutes
    MAX_LOGIN_ATTEMPTS = 5

# Initialize Supabase client
supabase_client: Client = create_client(
    Config.SUPABASE_URL,
    Config.SUPABASE_KEY
)