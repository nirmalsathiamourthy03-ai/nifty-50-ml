@echo off
title Push NIFTY 50 ML Project to GitHub
cd /d "%~dp0"
echo =========================================================================
echo       NIFTY 50 ML Movement Prediction - Push to GitHub
echo =========================================================================
echo.

set /p REPO_URL="Enter your GitHub Repository URL (e.g., https://github.com/username/nifty50.git): "

if "%REPO_URL%"=="" (
    echo [ERROR] No URL provided. Exiting.
    pause
    exit /b
)

echo.
echo [1/4] Setting main branch...
git branch -M main

echo [2/4] Setting Remote Origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo [3/4] Staging and Committing all project files...
git add .
git commit -m "feat: NIFTY 50 Dual Movement Prediction System with GitHub Actions EOD Engine"

echo [4/4] Pushing to GitHub (main branch)...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo =========================================================================
    echo  [SUCCESS] Code successfully pushed to GitHub!
    echo  GitHub Actions is now active at: %REPO_URL%/actions
    echo  It will automatically collect data and predict every weekday at 16:30 IST
    echo  even if your computer is completely powered off!
    echo =========================================================================
) else (
    echo.
    echo [ERROR] Git push failed. Please verify your repository URL and GitHub credentials.
)

echo.
pause
