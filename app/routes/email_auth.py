# auth/routes/email_auth.py
from flask import Blueprint, request, jsonify
from ..auth_service import AuthService
from ..utils.validators import validate_email
from ..utils.rate_limiter import check_rate_limit

email_auth = Blueprint('email_auth', __name__)
auth_service = AuthService()

@email_auth.route('/register', methods=['POST'])
async def register():
    """Register with email."""
    data = request.json
    email = data.get('email')
    name = data.get('name', '')

    if not validate_email(email):
        return jsonify({
            'status': 'error',
            'message': 'Invalid email format'
        }), 400

    if not await check_rate_limit(email, request.remote_addr):
        return jsonify({
            'status': 'error',
            'message': 'Too many attempts, please try again later'
        }), 429

    success, message, result = await auth_service.register_with_email(email, name)
    return jsonify({
        'status': 'success' if success else 'error',
        'message': message,
        'data': result
    }), 200 if success else 400

@email_auth.route('/verify', methods=['POST'])
async def verify():
    """Verify email OTP."""
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    if not all([email, otp]):
        return jsonify({
            'status': 'error',
            'message': 'Email and OTP are required'
        }), 400

    success, message, result = await auth_service.verify_otp(email, otp, 'email')
    return jsonify({
        'status': 'success' if success else 'error',
        'message': message,
        'data': result
    }), 200 if success else 400

