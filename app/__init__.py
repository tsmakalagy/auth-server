# app/__init__.py
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from datetime import datetime
from .config import Config, supabase_client

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Register blueprints
    from .routes.email_auth import email_auth
    from .routes.phone_auth import phone_auth
    
    app.register_blueprint(email_auth, url_prefix='/auth/email')
    app.register_blueprint(phone_auth, url_prefix='/auth/phone')

    # Health check endpoint
    @app.route('/health')
    def health_check():
        try:
            # Test Supabase connection with a simple query
            supabase_status = False
            test_query = supabase_client.from_('users').select('*').limit(1).execute()
            if test_query:
                supabase_status = True
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'auth-server',
                'version': '1.0.0',
                'dependencies': {
                    'supabase': 'connected' if supabase_status else 'disconnected'
                }
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }), 500

    @app.route('/')
    def index():
        return jsonify({
            'service': 'Authentication API',
            'status': 'running',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'email_auth': '/auth/email',
                'phone_auth': '/auth/phone'
            }
        })

    return app

# Create the application instance
app = create_app()