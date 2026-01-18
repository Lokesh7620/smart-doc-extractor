#!/usr/bin/env python3
"""
Smart Document Extractor - Auto Run Script
This script activates the virtual environment and starts the Flask app
"""

import os
import sys
import subprocess
import platform

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(text)
    print("="*60 + "\n")

def check_venv():
    """Check if virtual environment exists"""
    venv_path = "venv"
    if not os.path.exists(venv_path):
        print("[ERROR] Virtual environment not found!")
        print("[INFO] Please run: python -m venv venv")
        sys.exit(1)
    return venv_path

def activate_venv(venv_path):
    """Activate virtual environment"""
    if platform.system() == "Windows":
        activate_script = os.path.join(venv_path, "Scripts", "activate.bat")
    else:
        activate_script = os.path.join(venv_path, "bin", "activate")
    
    return activate_script

def check_requirements():
    """Check if required packages are installed"""
    try:
        import flask
        return True
    except ImportError:
        print("[INFO] Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def main():
    """Main entry point"""
    print_header("[RUN] Smart Document Extractor - Auto Run")
    
    # Check virtual environment
    print("Checking virtual environment...")
    venv_path = check_venv()
    print("[OK] Virtual environment found!")
    
    # Check requirements
    print("\nChecking dependencies...")
    check_requirements()
    print("[OK] Dependencies installed!")
    
    # Print startup info
    print_header("Starting Flask Application")
    print("[INFO] The app will be available at: http://127.0.0.1:5000")
    print("[INFO] Press Ctrl+C to stop the server")
    print("="*60 + "\n")
    
    # Run the app
    try:
        subprocess.run([sys.executable, "app.py"], check=True)
    except KeyboardInterrupt:
        print("\n\n[INFO] Application stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
