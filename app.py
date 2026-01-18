#!/usr/bin/env python3
"""Smart Document Extractor - Flask Application"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from flask_login import LoginManager
from models import db, User
from auth import auth
from main import main
from config import Config
from database import init_db

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(Config)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Create application context and initialize database
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    app.register_blueprint(auth)
    app.register_blueprint(main)
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    # Print startup info
    print("\n" + "="*70)
    print("SMART DOCUMENT EXTRACTOR".center(70))
    print("="*70)
    print(f"\n✓ Server running at: http://127.0.0.1:5000")
    print(f"✓ Press Ctrl+C to stop\n")
    
    # Run the app
    try:
        app.run(
            host='127.0.0.1',
            port=5000,
            debug=True,
            use_reloader=True
        )
    except KeyboardInterrupt:
        print("\n\n✓ Application stopped\n")
        sys.exit(0)