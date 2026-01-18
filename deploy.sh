#!/bin/bash
# Production deployment script for Linux/Unix systems

echo "============================================"
echo "Smart Document Extractor - Production Setup"
echo "============================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install production dependencies
echo "Installing dependencies..."
pip install -r requirements.production.txt

# Run deployment script
echo "Running deployment setup..."
python deploy.py

echo ""
echo "✅ Setup complete! Run with:"
echo "   gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 wsgi:app"
