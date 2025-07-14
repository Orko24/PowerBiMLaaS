@echo off
echo 🚀 Starting AI Analytics System...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if PostgreSQL is running (port 5432)
netstat -an | find "5432" >nul
if errorlevel 1 (
    echo ❌ PostgreSQL is not running on port 5432
    echo Please start PostgreSQL first
    pause
    exit /b 1
)

echo ✅ PostgreSQL is running

REM Install FastAPI dependencies
echo 📦 Installing FastAPI dependencies...
cd fastapi_middleware
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)
cd ..

REM Start FastAPI backend
echo 🔧 Starting FastAPI AI Analytics Backend...
start "FastAPI Backend" cmd /k "cd fastapi_middleware && python api/main.py"

REM Wait a moment for FastAPI to start
timeout /t 3 /nobreak >nul

REM Start Prostgles frontend
echo 🌐 Starting Prostgles Frontend...
start "Prostgles Frontend" cmd /k "cd frontend/prostgles && start.sh"

echo ✅ AI Analytics System is starting...
echo 📊 Frontend: http://localhost:3004
echo 🔧 Backend API: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo 🎯 Navigate to http://localhost:3004/ai-analytics to use the AI Analytics Dashboard
echo.
echo Press any key to exit...
pause >nul 