#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the Flask application
from app import create_app

# Get configuration class from environment
config_name = os.environ.get('FLASK_CONFIG', 'config.Config')

# Create the application instance
try:
    if 'production' in config_name.lower():
        from config_production import ProductionConfig
        print("[INFO] Using production configuration")
        ProductionConfig.validate_production_config()
        application = create_app()
        application.config.from_object(ProductionConfig)
        print("[INFO] Production app initialized successfully")
    else:
        print("[INFO] Using development configuration")
        application = create_app()
except Exception as e:
    print(f"[ERROR] Failed to initialize app with production config: {e}")
    print("[INFO] Falling back to default configuration")
    application = create_app()

# This is the WSGI application object that servers will use
app = application

if __name__ == '__main__':
    # For testing the WSGI file directly
    print("[INFO] Starting WSGI app in debug mode")
    app.run(host='0.0.0.0', port=8000)
