@echo off
echo ========================================
echo 3D Swing Analyzer Setup Script
echo Advanced Biomechanical Analysis System
echo ========================================
echo.

REM Check if Python is installed - try python command first
set PYTHON_CMD=python
echo Checking for Python installation...
echo.

REM Test python command
echo Testing 'python' command...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 'python' command works
    set PYTHON_CMD=python
    python --version
    goto :python_found
) else (
    echo ✗ 'python' command not found
)

REM Test py command
echo Testing 'py' command...
py --version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 'py' command works
    set PYTHON_CMD=py
    py --version
    goto :python_found
) else (
    echo ✗ 'py' command not found
)

REM Try to find Python in common locations
echo Searching for Python in common locations...
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python" (
    echo Found Python installation at: C:\Users\%USERNAME%\AppData\Local\Programs\Python
    echo Please add this to your PATH or reinstall Python with "Add to PATH" option
) else if exist "C:\Python*" (
    echo Found Python installation in C:\ drive
    echo Please add this to your PATH or reinstall Python with "Add to PATH" option
) else (
    echo No Python installation found in common locations
)

echo.
echo ERROR: Python is not accessible from command line
echo.
echo SOLUTIONS:
echo.
echo 1. If Python is installed but not in PATH:
echo    - Reinstall Python from python.org
echo    - Check "Add Python to PATH" during installation
echo.
echo 2. Install Python using Microsoft Store:
echo    - Press Windows key + R, type: ms-windows-store:
echo    - Search for "Python 3.12" and install
echo.
echo 3. Manual PATH fix:
echo    - Find your Python installation folder
echo    - Add it to Windows PATH environment variable
echo.
echo 4. See detailed guide: INSTALL_PYTHON.md
echo.
echo Please fix Python installation and run this script again.
echo.
pause
exit /b 1

:python_found
echo ✓ Python is available via '%PYTHON_CMD%' command

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo.
    echo SOLUTION: Please install Node.js:
    echo.
    echo 1. Visit: https://nodejs.org
    echo 2. Download the LTS version ^(recommended^)
    echo 3. Run the installer with default settings
    echo 4. Restart this Command Prompt
    echo 5. Run this setup script again
    echo.
    pause
    exit /b 1
)

echo Python and Node.js detected successfully!
echo.

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    %PYTHON_CMD% -m venv venv
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
echo 3D Swing Analyzer Setup Complete!
echo ========================================
echo.
echo ✓ MediaPipe 3D pose estimation ready
echo ✓ Advanced biomechanical analysis enabled
echo ✓ Interactive 3D visualizations configured
echo ✓ Kinematic sequence analysis available
echo.
echo To start the application:
echo 1. Backend (3D Analysis): run "start_backend.bat"
echo 2. Frontend (Enhanced UI): run "start_frontend.bat"
echo 3. Or run both: "start_all.bat"
echo.
echo Features available:
echo - 3D pose estimation with MediaPipe
echo - Kinematic sequence analysis
echo - Spatial biomechanics evaluation
echo - Interactive 3D visualizations
echo - Professional swing recommendations
echo.
pause