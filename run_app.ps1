# Smart Document Extractor - Auto Run Script (PowerShell)
# This script automatically activates the virtual environment and starts the Flask app

Write-Host ""
Write-Host "======================================================"
Write-Host "Smart Document Extractor - Auto Run"
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv venv" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Activate virtual environment
& "venv\Scripts\Activate.ps1"

# Check if pip packages are installed
$hasFlask = pip show flask 2>$null
if (-not $hasFlask) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Run the app
Write-Host ""
Write-Host "======================================================"
Write-Host "Starting Flask Application..." -ForegroundColor Green
Write-Host "======================================================"
Write-Host ""
Write-Host "The app will be available at: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server"
Write-Host ""

python app.py

Read-Host "Press Enter to exit"
