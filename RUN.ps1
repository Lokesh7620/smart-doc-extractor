cd d:\1

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  SMART DOCUMENT EXTRACTOR" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

# Create venv
if (!(Test-Path venv)) {
    Write-Host "[1/7] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "[OK] Created`n" -ForegroundColor Green
}

# Activate
Write-Host "[2/7] Activating..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "[3/7] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install packages
Write-Host "[4/7] Installing packages (5-10 min)..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create dirs
Write-Host "[5/7] Creating directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "static\uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "instance" | Out-Null

# Setup .env
Write-Host "[6/7] Configuration..." -ForegroundColor Yellow
if (!(Test-Path .env)) {
    @"
SECRET_KEY=sk-dev-secure-key
GROQ_API_KEY=org_01kew89rgkfn9vj1mj2a28van6
FLASK_ENV=development
"@ | Out-File -FilePath .env
}

# Run app
Write-Host "`n[7/7] Starting Flask..." -ForegroundColor Yellow
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  URL: http://127.0.0.1:5000" -ForegroundColor Green
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

python app.py