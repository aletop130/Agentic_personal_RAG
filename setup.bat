@echo off
REM Agentic RAG - Quick Start Setup for Windows

echo ==========================================
echo    Agentic RAG - Quick Start
echo ==========================================
echo.

echo Checking prerequisites...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.12+ first.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% detected

REM Check Python version (need 3.12+)
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% lss 3 (
    echo [ERROR] Python 3.12+ is required for Regolo AI. Found: %PYTHON_VERSION%
    pause
    exit /b 1
)

if %MAJOR% equ 3 (
    if %MINOR% lss 12 (
        echo [ERROR] Python 3.12+ is required for Regolo AI. Found: %PYTHON_VERSION%
        pause
        exit /b 1
    )
)

where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker first.
    pause
    exit /b 1
)

echo [OK] All prerequisites found!
echo.

echo Setting up backend...
cd backend

if not exist .env (
    echo [WARNING] .env file not found. Creating from .env.example...
    copy .env.example .env
    echo [WARNING] IMPORTANT: Edit backend\.env and add your REGOLO_API_KEY!
    echo            Get your API key from: https://dashboard.regolo.ai
    echo.
    echo Then run: setup.bat again
    pause
    exit /b 0
)

echo Installing Python dependencies...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install Python dependencies.
    pause
    exit /b 1
)

echo [OK] Backend dependencies installed!
echo.

echo Starting Qdrant...
cd ..\docker\qdrant
docker-compose up -d

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start Qdrant.
    pause
    exit /b 1
)

echo [OK] Qdrant started on ports 7333 (HTTP) and 7334 (gRPC)
echo.

cd ..\..

echo Setup complete!
echo.
echo Next steps:
echo    1. Edit backend\.env and add your REGOLO_API_KEY
echo    2. Start the backend:
echo       cd backend
echo       python -m app.main
echo    3. Open frontend\index.html in your browser
echo.
echo API Documentation: http://localhost:8000/docs
echo.

pause
