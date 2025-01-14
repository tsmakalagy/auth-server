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
            # Test Supabase connection
            supabase_status = bool(supabase_client.auth.get_url())
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'service': 'auth-server',
                'version': '1.0.0',
                'supabase_connected': supabase_status,
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
            'documentation': '/docs'  # If you add API documentation later
        })

    return app

# Create the application instance
app = create_app()