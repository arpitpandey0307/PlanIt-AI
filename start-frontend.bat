@echo off
echo ========================================
echo PlanIt AI - Frontend Development Server
echo ========================================
echo.

cd frontend

REM Check if node_modules exists
if not exist node_modules (
    echo [*] Installing frontend dependencies...
    call npm install
    echo.
)

echo [*] Starting frontend development server...
echo [*] Open http://localhost:5173 in your browser
echo.

call npm run dev

pause
