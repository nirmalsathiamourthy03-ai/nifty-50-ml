@echo off
title Setup NIFTY 50 Post-Market Auto-Update Task
cd /d "%~dp0"
echo =========================================================================
echo   Registering Windows Scheduled Task: NIFTY 50 Post-Market Auto-Update
echo   - Triggers strictly after market close at 4:00 PM IST (Mon-Fri)
echo   - No live market polling during trading hours
echo   - Computes features only from official finalized closing prices
echo   - If your computer was OFF at 4:00 PM, runs as soon as you turn it on!
echo =========================================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup_task.ps1"

echo.
pause
