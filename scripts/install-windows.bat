@echo off
setlocal

echo ==================================
echo Enhanced Voice Assistant Setup
echo ==================================

REM Check Python 3.11
echo Checking Python...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Please install Python 3.11 first.
    pause
    exit /b
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv .venv

REM Activate venv
call .venv\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt

REM Setup .env
if not exist ".env" (
    copy .env.example .env
)

REM Create assets folder
if not exist assets mkdir assets

echo.
echo Setup completed!
echo.
echo Next steps:
echo 1. Edit .env
echo 2. Activate environment:
echo    .venv\Scripts\activate
echo 3. Run:
echo    python main.py
echo.

pause