# Production deployment script for Windows (PowerShell)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Smart Document Extractor - Production Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python is not installed" -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "`nCreating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install production dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.production.txt

# Run deployment script
Write-Host "Running deployment setup..." -ForegroundColor Yellow
python deploy.py

Write-Host "`n✅ Setup complete! Run with:" -ForegroundColor Green
Write-Host "   waitress-serve --host=0.0.0.0 --port=8000 --threads=4 wsgi:app" -ForegroundColor Cyan
