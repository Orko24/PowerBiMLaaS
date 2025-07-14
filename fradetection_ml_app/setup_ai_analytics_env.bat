@echo off
setlocal enabledelayedexpansion

REM === 1. Prompt for API URL ===
set "DEFAULT_API_URL=http://localhost:8000"
set /p API_URL="Enter your AI Analytics backend API URL [default: %DEFAULT_API_URL%]: "
if "%API_URL%"=="" set "API_URL=%DEFAULT_API_URL%"
echo Using API URL: %API_URL%

REM === 2. Write .env files for Vite and CRA ===
cd frontend\prostgles\client

REM Write for Vite
(echo VITE_AI_API_URL=%API_URL%) > .env
REM Write for CRA
(echo REACT_APP_AI_API_URL=%API_URL%) >> .env

cd ..\..\..

REM === 3. Install frontend dependencies ===
echo Installing frontend dependencies...
cd frontend\prostgles\client
if exist yarn.lock (
  yarn install
) else (
  npm install
)

REM === 4. Build the frontend ===
echo Building frontend...
if exist yarn.lock (
  yarn build
) else (
  npm run build
)

cd ..\..\..

REM === 5. Start backend and frontend ===
echo Starting FastAPI backend...
start "FastAPI Backend" cmd /k "cd fastapi_middleware && pip install -r requirements.txt && python api/main.py"

echo Starting Prostgles frontend...
start "Prostgles Frontend" cmd /k "cd frontend\prostgles && start.sh"

REM === 6. Instructions ===
echo.
echo =====================================
echo AI Analytics system is starting!
echo Backend: %API_URL%
echo Frontend: http://localhost:3004
echo Open http://localhost:3004/ai-analytics in your browser
echo =====================================
echo.
pause 