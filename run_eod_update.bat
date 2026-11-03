@echo off
cd /d "%~dp0"
echo =========================================================
echo   Executing NIFTY 50 Post-Market EOD Observation Check
echo   Time: %date% %time%
echo =========================================================
python auto_watch.py --once
