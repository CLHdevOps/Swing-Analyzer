#!/usr/bin/env python3
"""
Cross-platform full-stack starter for Swing Analyzer
Starts both backend and frontend servers
"""

import os
import sys
import subprocess
import threading
import time
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

def start_backend():
    """Start the backend server"""
    print("Starting backend server...")
    
    # Get Python executable path
    python_path = get_venv_python()
    if not python_path.exists():
        print("ERROR: Virtual environment Python not found")
        return False
    
    # Find main file
    main_file = find_main_file()
    if not main_file:
        print("ERROR: No main Python file found")
        return False
    
    try:
        # Start backend in a separate process
        backend_process = subprocess.Popen(
            [str(python_path), main_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        print(f"Backend server started with PID {backend_process.pid}")
        print("Backend logs:")
        
        # Print backend output
        for line in iter(backend_process.stdout.readline, ''):
            print(f"[Backend] {line.rstrip()}")
            if backend_process.poll() is not None:
                break
                
    except Exception as e:
        print(f"ERROR starting backend: {e}")
        return False
    
    return True

def start_frontend():
    """Start the frontend server"""
    print("Starting frontend server...")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("ERROR: Frontend directory not found")
        return False
    
    node_modules = frontend_path / "node_modules"
    if not node_modules.exists():
        print("ERROR: Frontend dependencies not installed")
        return False
    
    try:
        # Start frontend in a separate process
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev"],
            cwd=frontend_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True
        )
        
        print(f"Frontend server started with PID {frontend_process.pid}")
        print("Frontend logs:")
        
        # Print frontend output
        for line in iter(frontend_process.stdout.readline, ''):
            print(f"[Frontend] {line.rstrip()}")
            if frontend_process.poll() is not None:
                break
                
    except FileNotFoundError:
        print("ERROR: npm not found. Please install Node.js")
        return False
    except Exception as e:
        print(f"ERROR starting frontend: {e}")
        return False
    
    return True

def start_backend_thread():
    """Thread function to start backend"""
    start_backend()

def start_frontend_thread():
    """Thread function to start frontend"""
    # Wait a bit for backend to start
    time.sleep(3)
    start_frontend()

def main():
    print("=" * 50)
    print("Starting Swing Analyzer - Full Stack Application")
    print("=" * 50)
    print()
    
    # Check prerequisites
    python_cmd = get_python_command()
    print(f"Using Python command: {python_cmd}")
    
    venv_path = Path("venv")
    if not venv_path.exists():
        print("ERROR: Virtual environment not found")
        print("Please run setup.py first")
        return 1
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("ERROR: Frontend directory not found")
        print("Please check your project structure")
        return 1
    
    node_modules = frontend_path / "node_modules"
    if not node_modules.exists():
        print("ERROR: Frontend dependencies not installed")
        print("Please run setup.py first")
        return 1
    
    print("Starting both servers...")
    print("Use Ctrl+C to stop both servers")
    print()
    
    try:
        # Start backend in a thread
        backend_thread = threading.Thread(target=start_backend_thread, daemon=True)
        backend_thread.start()
        
        # Start frontend in a thread
        frontend_thread = threading.Thread(target=start_frontend_thread, daemon=True)
        frontend_thread.start()
        
        print()
        print("=" * 50)
        print("Both servers are starting!")
        print("=" * 50)
        print("Backend: Usually runs on http://localhost:5000")
        print("Frontend: Usually runs on http://localhost:5173")
        print()
        print("Press Ctrl+C to stop both servers...")
        
        # Keep main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping servers...")
        return 0
    except Exception as e:
        print(f"ERROR: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())