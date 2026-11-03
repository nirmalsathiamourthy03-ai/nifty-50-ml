@echo off
title NIFTY 50 Post-Market EOD Watcher
echo =========================================================================
echo   NIFTY 50 Post-Market End-of-Day (EOD) Observation Watcher
echo   - Ignores live market ticks during market hours (09:15 - 15:30 IST)
echo   - Automatically triggers post-market (~15:45 IST) once daily candle closes
echo   - Recalculates 16 technical features based on the new closing price
echo =========================================================================
cd /d "%~dp0"
python auto_watch.py
pause
