@echo off
echo ========================================
echo PlanIt AI - Event Planner
echo ========================================
echo.

REM Check if .env exists
if not exist .env (
    echo [!] .env file not found!
    echo [*] Copying .env.example to .env...
    copy .env.example .env
    echo.
    echo [!] Please edit .env and add your GOOGLE_API_KEY
    echo [!] Get your API key from: https://aistudio.google.com/
    echo.
    pause
    exit /b 1
)

echo [*] Starting backend server...
echo.

REM Start backend in current window
cd backend
python app/main.py

pause
