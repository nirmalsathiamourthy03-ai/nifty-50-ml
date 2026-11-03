@echo off
title NIFTY 50 Prediction Dashboard
echo ===================================================
echo   NIFTY 50 AI Prediction Dashboard Launcher
echo ===================================================

cd /d "%~dp0"

echo [1/3] Ensuring port 8501 is free...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"

echo [2/3] Verifying frontend build...
if not exist "frontend\dist\index.html" (
    echo Building frontend assets...
    cd frontend
    call npm run build
    cd ..
)

echo [3/3] Launching NIFTY 50 ML Dashboard on http://localhost:8501...
echo Dashboard will automatically open in your browser.
echo (Keep this terminal window open while using the dashboard)
echo ===================================================

start "" http://localhost:8501
python api.py

pause
