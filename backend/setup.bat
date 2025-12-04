@echo off
REM OceanFront Backend Setup Script for Windows

echo.
echo ╔════════════════════════════════════════╗
echo ║  🌊 OceanFront Backend Setup Script   ║
echo ╚════════════════════════════════════════╝
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found! Please install Python 3.8+
    exit /b 1
)

echo ✅ Python detected

REM Create virtual environment
echo.
echo 📦 Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ℹ️  Virtual environment already exists
)

REM Activate virtual environment
echo.
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo.
echo 📥 Installing dependencies from requirements.txt...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    exit /b 1
)

echo ✅ Dependencies installed

REM Check .env file
echo.
if not exist ".env" (
    echo ⚠️  .env file not found! Creating template...
    (
        echo # Backend Configuration
        echo GROQ_API_KEY=sk-YOUR_GROQ_API_KEY_HERE
        echo PARQUET_DATA_PATH=d:\EDAI\OceanFront\oceanFrontData\Parquet
        echo DATABASE_URL=sqlite:///./oceanfront.db
        echo LOG_LEVEL=INFO
        echo PORT=8000
        echo HOST=0.0.0.0
    ) > .env
    echo ℹ️  Please edit .env and add your GROQ_API_KEY
) else (
    echo ✅ .env file found
)

echo.
echo ╔════════════════════════════════════════╗
echo ║  🚀 Setup Complete!                   ║
echo ╚════════════════════════════════════════╝
echo.
echo To start the backend, run:
echo   python main.py
echo.
echo Or for development with auto-reload:
echo   uvicorn main:app --reload
echo.
pause
