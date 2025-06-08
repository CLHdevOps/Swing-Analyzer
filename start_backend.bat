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

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if main Python file exists
if exist "swing_analysis_prototype.py" (
    echo Starting Flask backend server...
    python swing_analysis_prototype.py
) else if exist "app.py" (
    echo Starting Flask backend server...
    python app.py
) else if exist "main.py" (
    echo Starting Flask backend server...
    python main.py
) else (
    echo ERROR: No main Python file found (swing_analysis_prototype.py, app.py, or main.py)
    echo Please check your backend implementation
    pause
    exit /b 1
)