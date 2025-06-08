@echo off
echo Starting Swing Analyzer Frontend...
echo.

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

REM Start the frontend development server
cd frontend
echo Starting Vite development server...
npm run dev