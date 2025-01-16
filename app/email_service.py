# auth/email_service.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .config import Config
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.username = Config.SMTP_USERNAME
        self.password = Config.SMTP_PASSWORD
        self.from_email = Config.SMTP_FROM_EMAIL

    def send_verification(self, to_email: str, otp: str) -> bool:
        """Send verification email with OTP."""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = to_email
            msg['Subject'] = "Your Verification Code"

            body = f"""
            <html>
              <body>
                <h2>Verification Code</h2>
                <p>Your verification code is: <strong>{otp}</strong></p>
                <p>This code will expire in {Config.OTP_EXPIRY_MINUTES} minutes.</p>
                <p>If you didn't request this code, please ignore this email.</p>
              </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.send_message(msg)

            return True

        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            return False