@echo off
echo Testing Python installation and commands...
echo.

echo Testing 'python' command:
python --version 2>nul
if %errorlevel% equ 0 (
    echo ✓ 'python' command works
    set PYTHON_WORKS=1
) else (
    echo ✗ 'python' command not found
    set PYTHON_WORKS=0
)

echo.
echo Testing 'py' command:
py --version 2>nul
if %errorlevel% equ 0 (
    echo ✓ 'py' command works
    set PY_WORKS=1
) else (
    echo ✗ 'py' command not found
    set PY_WORKS=0
)

echo.
if %PYTHON_WORKS% equ 1 (
    echo RECOMMENDATION: Use 'python' command
    echo Run: setup.bat
) else if %PY_WORKS% equ 1 (
    echo RECOMMENDATION: Use 'py' command
    echo Run: py setup.py
) else (
    echo ERROR: Neither 'python' nor 'py' commands work
    echo Please install Python from:
    echo - Microsoft Store: Search "Python 3.12"
    echo - Or visit: https://python.org/downloads
    echo.
    echo See INSTALL_PYTHON.md for detailed instructions
)

echo.
pause