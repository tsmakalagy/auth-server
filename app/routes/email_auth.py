# auth/routes/email_auth.py
from flask import Blueprint, request, jsonify
from ..auth.auth_service import AuthService
from ..auth.utils.rate_limiter import check_rate_limit, log_attempt, get_remaining_attempts
from ..auth.utils.validators import validate_email
from ..config import Config

email_auth = Blueprint('email_auth', __name__)
auth_service = AuthService()

@email_auth.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    name = data.get('name', '')

    if not validate_email(email):
        return jsonify({
            'status': 'error',
            'message': 'Invalid email format'
        }), 400

    if not check_rate_limit(email, request.remote_addr):
        remaining_time = Config.RATE_LIMIT_WINDOW
        return jsonify({
            'status': 'error',
            'message': f'Too many attempts. Please try again in {remaining_time} seconds',
            'remaining_attempts': 0,
            'wait_time': remaining_time
        }), 429

    success, message, result = auth_service.register_with_email(email, name)
    
    # Log the attempt
    log_attempt(email, request.remote_addr, success)
    
    return jsonify({
        'status': 'success' if success else 'error',
        'message': message,
        'data': result,
        'remaining_attempts': get_remaining_attempts(email) if not success else None
    }), 200 if success else 400

@email_auth.route('/verify', methods=['POST'])
def verify():
    """Verify email OTP."""
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    if not all([email, otp]):
        return jsonify({
            'status': 'error',
            'message': 'Email and OTP are required'
        }), 400

    success, message, result = auth_service.verify_otp(email, otp, 'email')
    return jsonify({
        'status': 'success' if success else 'error',
        'message': message,
        'data': result
    }), 200 if success else 400

