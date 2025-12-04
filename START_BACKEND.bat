@echo off
REM ============================================
REM OceanFront Backend Starter Script
REM ============================================

echo.
echo ╔════════════════════════════════════════╗
echo ║   OceanFront Backend - Starting...     ║
echo ╚════════════════════════════════════════╝
echo.

cd /d D:\EDAI\OceanFront\backend

echo Checking Python environment...
if not exist ".venv\Scripts\python.exe" (
    echo ❌ Virtual environment not found
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Checking dependencies...
pip show fastapi >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo ✅ All dependencies ready
echo.

echo Starting FastAPI server...
echo.
echo 🌐 Backend will be available at: http://localhost:8000
echo 📊 API Docs: http://localhost:8000/docs
echo ✅ Health Check: http://localhost:8000/api/health
echo.
echo Press CTRL+C to stop the server
echo.

python main.py

pause
