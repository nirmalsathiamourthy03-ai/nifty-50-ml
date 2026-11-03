@echo off
title Remove NIFTY 50 Post-Market Auto-Update Task
cd /d "%~dp0"
echo =========================================================================
echo   Removing Windows Scheduled Task: NIFTY 50 Post-Market Auto-Update
echo =========================================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0remove_task.ps1"

echo.
pause
