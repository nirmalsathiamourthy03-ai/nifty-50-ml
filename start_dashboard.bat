@echo off
title NIFTY 50 Prediction Dashboard
echo ===================================================
echo   NIFTY 50 AI Prediction Dashboard Launcher
echo ===================================================

cd /d "%~dp0"

echo [1/2] Verifying frontend build...
if not exist "frontend\dist\index.html" (
    echo Building frontend assets...
    cd frontend
    call npm run build
    cd ..
)

echo [2/2] Launching NIFTY 50 ML Dashboard...
echo Server starting up on http://127.0.0.1:8501...
echo The dashboard will automatically open in your browser as soon as ready.
echo (Keep this terminal window open while using the dashboard)
echo ===================================================

python api.py

pause
