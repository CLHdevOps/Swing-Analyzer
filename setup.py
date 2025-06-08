#!/usr/bin/env python3
"""
Cross-platform setup script for Swing Analyzer
Works on Windows, macOS, and Linux
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(command, cwd=None, shell=True):
    """Run a command and handle errors"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=shell, cwd=cwd, check=True, 
                              capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Command failed with exit code {e.returncode}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def check_python():
    """Check if Python is available and determine command to use"""
    try:
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print("ERROR: Python 3.8+ is required")
            return False, None
        print(f"Python {version.major}.{version.minor}.{version.micro} detected")
        
        # Test which command works
        try:
            result = subprocess.run(["python", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                return True, "python"
        except FileNotFoundError:
            pass
        
        try:
            result = subprocess.run(["py", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                return True, "py"
        except FileNotFoundError:
            pass
        
        # If we're here, we're running Python but neither command works (shouldn't happen)
        return True, sys.executable
        
    except Exception:
        print("ERROR: Python not found")
        return False, None

def check_node():
    """Check if Node.js is available"""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Node.js {result.stdout.strip()} detected")
            return True
        else:
            print("ERROR: Node.js not found")
            return False
    except FileNotFoundError:
        print("ERROR: Node.js not found")
        return False

def create_venv(python_cmd):
    """Create Python virtual environment"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("Virtual environment already exists")
        return True
    
    print("Creating Python virtual environment...")
    return run_command(f"{python_cmd} -m venv venv")

def get_venv_python():
    """Get the path to the virtual environment Python executable"""
    system = platform.system().lower()
    if system == "windows":
        return Path("venv/Scripts/python.exe")
    else:
        return Path("venv/bin/python")

def get_venv_pip():
    """Get the path to the virtual environment pip executable"""
    system = platform.system().lower()
    if system == "windows":
        return Path("venv/Scripts/pip.exe")
    else:
        return Path("venv/bin/pip")

def install_python_deps():
    """Install Python dependencies"""
    print("Installing Python dependencies...")
    pip_path = get_venv_pip()
    
    # Upgrade pip first
    if not run_command(f"{pip_path} install --upgrade pip"):
        return False
    
    # Install requirements
    return run_command(f"{pip_path} install -r requirements.txt")

def install_frontend_deps():
    """Install frontend dependencies"""
    print("Installing frontend dependencies...")
    frontend_path = Path("frontend")
    
    if not frontend_path.exists():
        print("ERROR: Frontend directory not found")
        return False
    
    node_modules = frontend_path / "node_modules"
    if node_modules.exists():
        print("Frontend dependencies already installed")
        print("Running npm install to ensure they're up to date...")
    
    return run_command("npm install", cwd=frontend_path)

def main():
    print("=" * 50)
    print("Swing Analyzer Setup Script")
    print("=" * 50)
    print()
    
    # Check prerequisites
    python_available, python_cmd = check_python()
    if not python_available:
        print("Please install Python 3.8+ from https://python.org")
        return 1
    
    print(f"Using Python command: {python_cmd}")
    
    if not check_node():
        print("Please install Node.js from https://nodejs.org")
        return 1
    
    print("Prerequisites check passed!")
    print()
    
    # Create virtual environment
    if not create_venv(python_cmd):
        print("Failed to create virtual environment")
        return 1
    
    # Install Python dependencies
    if not install_python_deps():
        print("Failed to install Python dependencies")
        return 1
    
    # Install frontend dependencies
    if not install_frontend_deps():
        print("Failed to install frontend dependencies")
        return 1
    
    print()
    print("=" * 50)
    print("Setup completed successfully!")
    print("=" * 50)
    print()
    print("To start the application:")
    print(f"1. Backend: {python_cmd} start_backend.py")
    print(f"2. Frontend: {python_cmd} start_frontend.py")
    print(f"3. Or run both: {python_cmd} start_all.py")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())