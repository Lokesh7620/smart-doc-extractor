@echo off
REM Smart Document Extractor - Auto Run Script
REM This script automatically activates the virtual environment and starts the Flask app

echo.
echo ======================================================
echo Smart Document Extractor - Auto Run
echo ======================================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if pip packages are installed
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)
REM Run the app
echo.
echo Starting Document Extractor on http://127.0.0.1:5000
echo Press CTRL+C to stop
echo.
python app.py

REM Keep window open on error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit.
    pause
)
echo Starting Flask Application...
echo ======================================================
echo.
echo The app will be available at: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
