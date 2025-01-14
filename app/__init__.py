from flask import Flask
from flask_jwt_extended import JWTManager
from .config import Config
from .routes.email_auth import email_auth
from .routes.phone_auth import phone_auth

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize JWT
    jwt = JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(email_auth, url_prefix='/auth/email')
    app.register_blueprint(phone_auth, url_prefix='/auth/phone')
    
    return app

# Initialize Supabase client
from .config import supabase_client