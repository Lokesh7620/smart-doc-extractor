@echo off
setlocal enabledelayedexpansion
cd /d d:\1
title Smart Document Extractor - Auto Fix and Run
color 0A

echo.
echo ================================================================================
echo    SMART DOCUMENT EXTRACTOR - AUTO FIX ^& RUN
echo    Fixing all errors and improving handwriting recognition
echo ================================================================================
echo.

REM Step 1: Create/check venv
if not exist venv (
    echo [1/7] Creating virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment exists
)
echo.

REM Step 2: Activate venv
echo [2/7] Activating environment...
call venv\Scripts\activate.bat
echo [OK] Environment activated
echo.

REM Step 3: Upgrade pip
echo [3/7] Upgrading pip...
python -m pip install --quiet --upgrade pip
echo [OK] Pip upgraded
echo.

REM Step 4: Install/upgrade all packages
echo [4/7] Installing dependencies (may take 5-10 minutes first time)...
pip install --quiet --upgrade -r requirements.txt
echo [OK] Dependencies installed
echo.

REM Step 5: Create directories
echo [5/7] Creating directories...
if not exist "static\uploads" mkdir static\uploads
if not exist "instance" mkdir instance
echo [OK] Directories created
echo.

REM Step 6: Setup .env
echo [6/7] Setting up configuration...
if not exist .env (
    (
        echo SECRET_KEY=sk-dev-secure-key
        echo GROQ_API_KEY=org_01kew89rgkfn9vj1mj2a28van6
        echo FLASK_ENV=development
    ) > .env
    echo [OK] Configuration created
) else (
    echo [OK] Configuration exists
)
echo.

REM Step 7: Launch app
echo [7/7] Starting Flask application...
echo.
echo ================================================================================
echo    SMART DOCUMENT EXTRACTOR IS RUNNING
echo ================================================================================
echo.
echo    Website URL: http://127.0.0.1:5000
echo    Status: Active
echo    
echo    Features:
echo    - Advanced AI-powered OCR
echo    - TrOCR for handwriting
echo    - PaddleOCR support
echo    - EasyOCR integration
echo    - Tesseract fallback
echo.
echo    Press Ctrl+C to stop the server
echo.
echo ================================================================================
echo.

python app.py

if errorlevel 1 (
    echo.
    echo ================================================================================
    echo    ERROR OCCURRED
    echo ================================================================================
    echo.
    echo Check the error messages above for details.
    pause
    exit /b 1
)

echo.
echo Application stopped normally.
pause