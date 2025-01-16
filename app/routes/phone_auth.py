# auth/routes/phone_auth.py
from flask import Blueprint, request, jsonify
from ..auth_service import AuthService
from ..config import Config
from ..utils.rate_limiter import check_rate_limit, log_attempt, get_remaining_attempts
from ..utils.validators import validate_phone

phone_auth = Blueprint('phone_auth', __name__)
auth_service = AuthService()

@phone_auth.route('/register', methods=['POST'])
def register():
    """Register with phone number."""
    data = request.json
    phone = data.get('phone')
    name = data.get('name', '')

    if not validate_phone(phone):
        return jsonify({
            'status': 'error',
            'message': 'Invalid phone number format'
        }), 400

    if not check_rate_limit(phone, request.remote_addr):
        remaining_time = Config.RATE_LIMIT_WINDOW
        return jsonify({
            'status': 'error',
            'message': f'Too many attempts. Please try again in {remaining_time} seconds',
            'remaining_attempts': 0,
            'wait_time': remaining_time
        }), 429

    success, message, result = auth_service.register_with_phone(phone, name)
    
    # Log the attempt
    log_attempt(phone, request.remote_addr, success)
    
    return jsonify({
        'status': 'success' if success else 'error',
        'message': message,
        'data': result,
        'remaining_attempts': get_remaining_attempts(phone) if not success else None
    }), 200 if success else 400

@phone_auth.route('/verify', methods=['POST'])
def verify():
    """Verify phone OTP."""
    data = request.json
    phone = data.get('phone')
    otp = data.get('otp')

    if not phone or not otp:
        return jsonify({
            'status': 'error',
            'message': 'Phone number and OTP are required'
        }), 400

    if not validate_phone(phone):
        return jsonify({
            'status': 'error',
            'message': 'Invalid phone number format'
        }), 400

    try:
        success, message, result = auth_service.verify_phone_otp(phone, otp)
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message': message,
            'data': result
        }), 200 if success else 400

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500