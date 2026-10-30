@echo off
echo ========================================
echo PlanIt AI - Installation Script
echo ========================================
echo.

echo [1/3] Installing Python dependencies...
pip install -r backend/requirements.txt
if errorlevel 1 (
    echo [!] Failed to install Python dependencies
    pause
    exit /b 1
)
echo [✓] Python dependencies installed
echo.

echo [2/3] Installing Node.js dependencies...
cd frontend
call npm install
if errorlevel 1 (
    echo [!] Failed to install Node dependencies
    cd ..
    pause
    exit /b 1
)
cd ..
echo [✓] Node dependencies installed
echo.

echo [3/3] Setting up environment...
if not exist .env (
    copy .env.example .env
    echo [✓] Created .env file
    echo [!] Please edit .env and add your GOOGLE_API_KEY
) else (
    echo [✓] .env file already exists
)
echo.

echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env and add your GOOGLE_API_KEY
echo    Get it from: https://aistudio.google.com/
echo.
echo 2. Run the application:
echo    - Terminal 1: start.bat (backend)
echo    - Terminal 2: start-frontend.bat (frontend)
echo.
echo 3. Open http://localhost:5173 in your browser
echo.

pause
