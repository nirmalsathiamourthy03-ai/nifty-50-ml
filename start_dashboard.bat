@echo off
title NIFTY 50 Prediction Dashboard
echo ===================================================
echo   NIFTY 50 AI Prediction Dashboard Launcher
echo ===================================================

cd /d "%~dp0"

echo [1/2] Ensuring port 8501 is free...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8501 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"

echo [2/2] Launching Streamlit Dashboard...
echo Dashboard will automatically open in your browser at http://localhost:8501
echo (Keep this terminal window open while using the dashboard)
echo ===================================================

python -m streamlit run app.py --server.port 8501

pause
