@echo off
echo Starting Swing Analyzer Backend...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ERROR: Virtual environment not found
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

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if main Python file exists and start server
if exist "swing_analysis_prototype.py" (
    echo Starting Flask backend server...
    %PYTHON_CMD% swing_analysis_prototype.py
) else if exist "app.py" (
    echo Starting Flask backend server...
    %PYTHON_CMD% app.py
) else if exist "main.py" (
    echo Starting Flask backend server...
    %PYTHON_CMD% main.py
) else (
    echo ERROR: No main Python file found (swing_analysis_prototype.py, app.py, or main.py)
    echo Please check your backend implementation
    pause
    exit /b 1
)