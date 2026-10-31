@echo off
echo ========================================
echo PlanIt AI - Vercel Deployment
echo ========================================
echo.

echo [1/5] Checking Vercel CLI...
where vercel >nul 2>&1
if errorlevel 1 (
    echo Installing Vercel CLI...
    npm install -g vercel
) else (
    echo ✓ Vercel CLI found
)
echo.

echo [2/5] Building frontend...
cd frontend
call npm run build
if errorlevel 1 (
    echo ✗ Build failed
    pause
    exit /b 1
)
cd ..
echo ✓ Frontend built successfully
echo.

echo [3/5] Deploying to Vercel...
echo You'll need to:
echo   - Login to Vercel (if not already)
echo   - Add GOOGLE_API_KEY environment variable
echo.
pause

vercel
echo.

echo [4/5] Setting environment variables...
echo Run this command and paste your API key:
echo   vercel env add GOOGLE_API_KEY production
echo.
pause

echo [5/5] Deploying to production...
vercel --prod
echo.

echo ========================================
echo Deployment Complete!
echo ========================================
echo.
echo Your app is now live!
echo Check the URL provided above.
echo.

pause
