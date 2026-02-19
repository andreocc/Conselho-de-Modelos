@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo      Local Model Council Launcher 🧠
echo ==========================================

:: 1. Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.9+ and add it to PATH.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 2. Check for Ollama
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] 'ollama' command not found in PATH.
    echo Please ensure Ollama is installed and running for the app to work.
    echo Download: https://ollama.com
    echo.
) else (
    echo [OK] Ollama found.
)

:: Ensure we are in the script's directory
cd /d "%~dp0"

:: 3. Setup Virtual Environment
if not exist "venv" (
    echo [INFO] Creating virtual environment 'venv'...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
) else (
    echo [INFO] Virtual environment 'venv' already exists.
)

:: 4. Activate Virtual Environment
call venv\Scripts\activate
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment.
    pause
    exit /b 1
)

:: 5. Install Dependencies
if exist "requirements.txt" (
    echo [INFO] Checking and installing dependencies...
    pip install -r requirements.txt
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
) else (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)

:: 6. Run Application
echo.
echo [INFO] Launching Local Model Council (Flask)...
echo [INFO] Opening browser...
start "" "http://127.0.0.1:8501"
python app.py

pause
