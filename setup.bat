@echo off
REM TDW Cuts Automation Tool - Setup Script
REM For Windows users

echo ==========================================
echo TDW Cuts Automation Tool - Setup
echo ==========================================
echo.

REM Check if Python is installed
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed!
    echo Please download and install Python from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Install dependencies
echo Installing required packages...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ✅ Setup complete!
    echo.
    echo To start the application, run:
    echo   run.bat
    echo.
    echo Or manually:
    echo   python app.py
    echo.
) else (
    echo.
    echo ❌ Installation failed. Please check the error messages above.
    echo.
    pause
    exit /b 1
)

pause