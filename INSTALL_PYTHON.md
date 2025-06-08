# Python Installation Guide for Windows

Since Python is not currently installed on your system, here's a step-by-step guide to install it:

## Option 1: Install from Microsoft Store (Recommended for Windows 10/11)

1. **Open Microsoft Store**
   - Press `Windows key + R`
   - Type `ms-windows-store:` and press Enter

2. **Search for Python**
   - Search for "Python 3.12" or "Python 3.11"
   - Click on the official Python app (published by Python Software Foundation)

3. **Install**
   - Click "Install" or "Get"
   - Wait for installation to complete

4. **Verify Installation**
   - Open Command Prompt (`Windows key + R`, type `cmd`, press Enter)
   - Type `python --version`
   - You should see something like "Python 3.12.x"

## Option 2: Install from Python.org

1. **Download Python**
   - Go to [https://python.org/downloads](https://python.org/downloads)
   - Click "Download Python 3.12.x" (latest version)

2. **Run the Installer**
   - **IMPORTANT**: Check "Add Python to PATH" before clicking Install
   - Choose "Install Now" for default installation
   - If prompted, allow the installer to make changes

3. **Verify Installation**
   - Open a **new** Command Prompt window
   - Type `python --version`
   - You should see the Python version

## Option 3: Install using Chocolatey (for advanced users)

If you have Chocolatey installed:
```cmd
choco install python
```

## After Python Installation

1. **Close all Command Prompt/PowerShell windows**
2. **Open a new Command Prompt or PowerShell**
3. **Navigate to your project directory**:
   ```cmd
   cd "C:\Users\ogDevOps\source\source\Swing-Analyzer"
   ```
4. **Run the setup script**:
   ```cmd
   setup.bat
   ```

## Troubleshooting

### "Python was not found" error after installation

1. **Restart your computer** - This ensures PATH changes take effect
2. **Check if Python is in PATH**:
   ```cmd
   echo %PATH%
   ```
   Look for a Python path in the output

3. **Try using the Python Launcher**:
   ```cmd
   py --version
   ```

### Manual PATH addition (if needed)

If Python still isn't found:

1. **Find Python installation**:
   - Microsoft Store: `C:\Users\{username}\AppData\Local\Microsoft\WindowsApps`
   - Python.org: `C:\Python312` or `C:\Users\{username}\AppData\Local\Programs\Python\Python312`

2. **Add to PATH**:
   - Press `Windows key + X`, select "System"
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "User variables", find "Path" and click "Edit"
   - Click "New" and add the Python installation path
   - Click "OK" on all dialogs

3. **Restart Command Prompt** and try again

## What You Need

The Swing Analyzer requires:
- **Python 3.8 or newer** (3.12 recommended)
- **pip** (included with Python)
- **Node.js** (separate installation needed)

After installing Python, you'll also need Node.js from [https://nodejs.org](https://nodejs.org).

## Quick Test

After installation, run these commands to verify everything works:

```cmd
python --version
pip --version
node --version
npm --version
```

If all commands work, you're ready to run the setup script!