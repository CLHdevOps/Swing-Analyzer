#!/usr/bin/env python3
"""
Cross-platform frontend starter for Swing Analyzer
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("Starting Swing Analyzer Frontend...")
    print()
    
    # Check if frontend directory exists
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("ERROR: Frontend directory not found")
        print("Please check your project structure")
        return 1
    
    # Check if node_modules exists
    node_modules = frontend_path / "node_modules"
    if not node_modules.exists():
        print("ERROR: Frontend dependencies not installed")
        print("Please run setup.py first")
        return 1
    
    print("Starting Vite development server...")
    try:
        subprocess.run(["npm", "run", "dev"], cwd=frontend_path, check=True)
    except KeyboardInterrupt:
        print("\nFrontend server stopped")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Frontend server failed with exit code {e.returncode}")
        return 1
    except FileNotFoundError:
        print("ERROR: npm not found. Please install Node.js")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())