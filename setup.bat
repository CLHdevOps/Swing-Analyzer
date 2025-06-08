@echo off
echo ========================================
echo Swing Analyzer Setup Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org
    pause
    exit /b 1
)

echo Python and Node.js detected successfully!
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully!
) else (
    echo Virtual environment already exists.
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install Python dependencies
echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies
    pause
    exit /b 1
)
echo Python dependencies installed successfully!
echo.

REM Install frontend dependencies
echo Installing frontend dependencies...
cd frontend
if not exist "node_modules" (
    npm install
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install frontend dependencies
        cd ..
        pause
        exit /b 1
    )
    echo Frontend dependencies installed successfully!
) else (
    echo Frontend dependencies already installed.
    echo Running npm install to ensure they're up to date...
    npm install
)
cd ..
echo.

echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo To start the application:
echo 1. Backend: run "start_backend.bat"
echo 2. Frontend: run "start_frontend.bat"
echo 3. Or run both: "start_all.bat"
echo.
pause