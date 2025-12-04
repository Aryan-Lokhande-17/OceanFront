@echo off
REM ============================================
REM OceanFront Frontend Starter Script
REM ============================================

echo.
echo ╔════════════════════════════════════════╗
echo ║   OceanFront Frontend - Starting...    ║
echo ╚════════════════════════════════════════╝
echo.

cd /d D:\EDAI\OceanFront\frontend

echo Checking dependencies...
npm --version >nul 2>&1
if errorlevel 1 (
    echo ❌ npm is not installed
    echo Install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ npm found

echo.
echo Starting development server...
echo.
echo 🌐 Frontend will be available at: http://localhost:3000
echo 🤖 Chat interface: http://localhost:3000/ai-agent
echo.
echo Press CTRL+C to stop the server
echo.

npm run dev

pause
