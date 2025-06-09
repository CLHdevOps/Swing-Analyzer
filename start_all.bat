@echo off
echo Starting 3D Swing Analyzer - Advanced Biomechanical Analysis
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Check if frontend directory exists
if not exist "frontend" (
    echo ERROR: Frontend directory not found
    echo Please check your project structure
    pause
    exit /b 1
)

REM Check if node_modules exists
if not exist "frontend\node_modules" (
    echo ERROR: Frontend dependencies not installed
    echo Please run setup.bat first
    pause
    exit /b 1
)

REM Determine Python command to use
set PYTHON_CMD=python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo ERROR: Python not found. Please install Python first.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
)

echo Starting backend server in background...
start "Backend Server" cmd /k "call venv\Scripts\activate.bat && %PYTHON_CMD% swing_analysis_prototype.py"

echo Waiting 3 seconds for backend to initialize...
timeout /t 3 /nobreak >nul

echo Starting frontend development server...
cd frontend
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ========================================
echo 3D Swing Analyzer Servers Starting!
echo ========================================
echo Backend (3D Analysis): http://localhost:5001
echo Frontend (Enhanced UI): http://localhost:5173
echo.
echo Features Available:
echo ✓ MediaPipe 3D pose estimation
echo ✓ Kinematic sequence analysis
echo ✓ Interactive 3D visualizations
echo ✓ Advanced biomechanical feedback
echo.
echo Press any key to close this window...
echo (Note: Servers will continue running in separate windows)
pause >nul