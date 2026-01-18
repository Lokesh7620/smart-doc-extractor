#!/usr/bin/env python3
"""
Production deployment script for Smart Document Extractor
Run with: python deploy.py
"""
import os
import sys
import subprocess
import secrets
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(f" {text}")
    print("="*70)

def check_python_version():
    """Ensure Python 3.8+ is installed"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")

def create_env_file():
    """Create .env file from template if it doesn't exist"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if env_file.exists():
        print("✓ .env file already exists")
        return
    
    if env_example.exists():
        print("Creating .env file from template...")
        # Read template
        with open(env_example, 'r') as f:
            content = f.read()
        
        # Generate secure secret key
        secret_key = secrets.token_hex(32)
        content = content.replace('your-secret-key-here-change-in-production', secret_key)
        
        # Write .env file
        with open(env_file, 'w') as f:
            f.write(content)
        
        print(f"✓ Created .env file with secure SECRET_KEY")
        print("⚠️  Please edit .env file to configure your database and other settings")
    else:
        print("❌ .env.example not found")

def install_dependencies():
    """Install production dependencies"""
    print_header("Installing Dependencies")
    
    # Check if virtual environment is active
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not activated")
        response = input("Continue without virtual environment? (y/n): ")
        if response.lower() != 'y':
            print("Please activate virtual environment and run again")
            sys.exit(0)
    
    print("Installing production requirements...")
    subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.production.txt'], check=True)
    print("✓ Dependencies installed")

def initialize_database():
    """Initialize the database"""
    print_header("Initializing Database")
    
    from app import create_app
    from models import db
    
    # Set environment to production
    os.environ['FLASK_ENV'] = 'production'
    
    app = create_app()
    
    with app.app_context():
        db.create_all()
        print("✓ Database initialized")

def create_upload_directory():
    """Create uploads directory if it doesn't exist"""
    upload_dir = Path('static/uploads')
    upload_dir.mkdir(parents=True, exist_ok=True)
    print(f"✓ Upload directory created: {upload_dir}")

def print_deployment_instructions():
    """Print instructions for different deployment methods"""
    print_header("Deployment Options")
    
    print("\n🎯 Option 1: Deploy with Gunicorn (Linux/Mac)")
    print("   gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 wsgi:app")
    
    print("\n🎯 Option 2: Deploy with Waitress (Windows)")
    print("   waitress-serve --host=0.0.0.0 --port=8000 --threads=4 wsgi:app")
    
    print("\n🎯 Option 3: Deploy with systemd (Linux Service)")
    print("   See DEPLOYMENT.md for detailed instructions")
    
    print("\n🎯 Option 4: Deploy with Docker")
    print("   docker build -t document-extractor .")
    print("   docker run -p 8000:8000 document-extractor")
    
    print("\n📝 Important Notes:")
    print("   - Update .env file with production database credentials")
    print("   - Set up reverse proxy (Nginx/Apache) for HTTPS")
    print("   - Configure firewall rules")
    print("   - Set up monitoring and logging")
    print("   - Enable automated backups")

def main():
    """Main deployment process"""
    try:
        print_header("Smart Document Extractor - Deployment Setup")
        
        # Step 1: Check Python version
        print("\n📋 Step 1: Checking Python version...")
        check_python_version()
        
        # Step 2: Create .env file
        print("\n📋 Step 2: Setting up environment configuration...")
        create_env_file()
        
        # Step 3: Install dependencies
        print("\n📋 Step 3: Installing dependencies...")
        install_dependencies()
        
        # Step 4: Create upload directory
        print("\n📋 Step 4: Creating upload directory...")
        create_upload_directory()
        
        # Step 5: Initialize database
        print("\n📋 Step 5: Initializing database...")
        initialize_database()
        
        # Step 6: Show deployment instructions
        print_deployment_instructions()
        
        print_header("✅ Deployment Setup Complete!")
        print("\nNext steps:")
        print("1. Edit .env file with your production settings")
        print("2. Choose a deployment method from the options above")
        print("3. Set up reverse proxy and SSL certificate")
        print("4. Configure monitoring and backups")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during deployment: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
