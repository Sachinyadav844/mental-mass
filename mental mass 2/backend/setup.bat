@echo off
REM MentalMass Backend Setup Script for Windows

echo ==========================================
echo MentalMass Backend Setup (Windows)
echo ==========================================
echo.

REM Check if we're in the backend directory
if not exist "app.py" (
    echo [X] Error: Please run this script from the backend directory
    pause
    exit /b 1
)

REM Create .env if it doesn't exist
if not exist ".env" (
    echo [*] Creating .env file...
    (
        echo FLASK_ENV=development
        echo DEBUG=False
        echo FLASK_HOST=0.0.0.0
        echo FLASK_PORT=5000
        echo JWT_SECRET_KEY=mentalmass_secret_key_2024_production
    ) > .env
    echo [+] .env created
)

REM Create directories
if not exist "data" mkdir data
if not exist "logs" mkdir logs

REM Install dependencies
echo [*] Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% equ 0 (
    echo [+] Dependencies installed
) else (
    echo [X] Failed to install dependencies
    pause
    exit /b 1
)

REM Initialize database
echo [*] Initializing database...
python -c "from database import init_db; init_db(); print('[+] Database initialized successfully')"
if %errorlevel% neq 0 (
    echo [X] Database initialization error
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [+] Setup Complete!
echo ==========================================
echo.
echo To start the backend server, run:
echo   python app.py
echo.
echo Server will be available at:
echo   http://localhost:5000
echo.
echo API Documentation:
echo   See BACKEND_COMPLETE.md for full API reference
echo.
pause
