#!/usr/bin/env python3
"""
Cross-platform backend starter for Swing Analyzer
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def get_python_command():
    """Determine which Python command to use"""
    try:
        result = subprocess.run(["python", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return "python"
    except FileNotFoundError:
        pass
    
    try:
        result = subprocess.run(["py", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return "py"
    except FileNotFoundError:
        pass
    
    return sys.executable  # Fallback to current Python executable

def get_venv_python():
    """Get the path to the virtual environment Python executable"""
    system = platform.system().lower()
    if system == "windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")

def find_main_file():
    """Find the main Python file to run"""
    candidates = ["swing_analysis_prototype.py", "app.py", "main.py"]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None

def main():
    print("Starting Swing Analyzer Backend...")
    print()
    
    # Check if virtual environment exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("ERROR: Virtual environment not found")
        print("Please run setup.py first")
        return 1
    
    # Get Python command to use
    python_cmd = get_python_command()
    print(f"Using Python command: {python_cmd}")
    
    # Get Python executable path
    python_path = get_venv_python()
    if not python_path.exists():
        print("ERROR: Virtual environment Python not found")
        print("Please run setup.py first")
        return 1
    
    # Find main file
    main_file = find_main_file()
    if not main_file:
        print("ERROR: No main Python file found (swing_analysis_prototype.py, app.py, or main.py)")
        print("Please check your backend implementation")
        return 1
    
    print(f"Starting Flask backend server ({main_file})...")
    try:
        subprocess.run([str(python_path), main_file], check=True)
    except KeyboardInterrupt:
        print("\nBackend server stopped")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Backend server failed with exit code {e.returncode}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())