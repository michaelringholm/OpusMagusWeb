@echo off
REM OpusMagus CDK Developer Environment Setup Script (Windows)
REM This script sets up a local Python virtual environment and installs dependencies

setlocal enabledelayedexpansion

echo ==========================================
echo OpusMagus CDK Environment Setup
echo ==========================================

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [X] Python is not installed or not in PATH. Please install Python 3.10 or later.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python version: %PYTHON_VERSION%

REM Create virtual environment
echo.
echo Creating virtual environment...
if exist ".venv" (
    echo Virtual environment already exists at .venv
    set /p RECREATE="Do you want to delete and recreate it? (y/n): "
    if /i "!RECREATE!"=="y" (
        rmdir /s /q .venv
        python -m venv .venv
        echo [OK] Virtual environment recreated
    )
) else (
    python -m venv .venv
    echo [OK] Virtual environment created
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [X] Failed to activate virtual environment
    pause
    exit /b 1
)
echo [OK] Virtual environment activated

REM Upgrade pip
echo.
echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
if errorlevel 1 (
    echo [X] Failed to upgrade pip
    pause
    exit /b 1
)
echo [OK] pip upgraded

REM Install requirements
echo.
echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo [X] Failed to install dependencies
    pause
    exit /b 1
)
echo [OK] Dependencies installed

REM Create .env file if it doesn't exist
echo.
if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env >nul
    echo [OK] .env file created (please review and update values as needed)
) else (
    echo [OK] .env file already exists
)

echo.
echo ==========================================
echo [OK] Setup completed successfully!
echo ==========================================
echo.
echo Next steps:
echo 1. Activate the virtual environment:
echo    .venv\Scripts\activate.bat
echo 2. Review and update .env with your configuration
echo 3. List available stacks:
echo    cdk list
echo.
pause
