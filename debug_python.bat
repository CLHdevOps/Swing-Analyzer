@echo off
echo ============================================
echo Python Installation Debug Script
echo ============================================
echo.

echo Current Environment:
echo USERNAME: %USERNAME%
echo COMPUTERNAME: %COMPUTERNAME%
echo PATH: %PATH%
echo.

echo Testing Python commands:
echo.

echo 1. Testing 'python --version':
python --version
echo Exit code: %errorlevel%
echo.

echo 2. Testing 'py --version':
py --version
echo Exit code: %errorlevel%
echo.

echo 3. Testing 'where python':
where python
echo Exit code: %errorlevel%
echo.

echo 4. Testing 'where py':
where py
echo Exit code: %errorlevel%
echo.

echo 5. Checking common Python locations:
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python" (
    echo Found: C:\Users\%USERNAME%\AppData\Local\Programs\Python
    dir "C:\Users\%USERNAME%\AppData\Local\Programs\Python" /B
) else (
    echo Not found: C:\Users\%USERNAME%\AppData\Local\Programs\Python
)

if exist "C:\Users\%USERNAME%\AppData\Local\Microsoft\WindowsApps\python.exe" (
    echo Found: C:\Users\%USERNAME%\AppData\Local\Microsoft\WindowsApps\python.exe
) else (
    echo Not found: C:\Users\%USERNAME%\AppData\Local\Microsoft\WindowsApps\python.exe
)

echo.
echo 6. Testing direct Python execution:
if exist "C:\Users\%USERNAME%\AppData\Local\Microsoft\WindowsApps\python.exe" (
    "C:\Users\%USERNAME%\AppData\Local\Microsoft\WindowsApps\python.exe" --version
    echo Direct execution exit code: %errorlevel%
)

echo.
echo Debug complete. Please share this output.
pause