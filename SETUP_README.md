# Swing Analyzer Setup Guide

This guide explains how to set up and run the Swing Analyzer application, which consists of a Python Flask backend and a React frontend.

## Prerequisites

Before running the setup scripts, ensure you have the following installed:

- **Python 3.8+**: Download from [python.org](https://python.org)
- **Node.js 16+**: Download from [nodejs.org](https://nodejs.org)

## Quick Start

### Windows Users

1. **Setup**: Double-click `setup.bat` or run in Command Prompt:
   ```cmd
   setup.bat
   ```

2. **Start Application**: Double-click `start_all.bat` or run:
   ```cmd
   start_all.bat
   ```

### Cross-Platform (Windows/Mac/Linux)

1. **Setup**: Run the Python setup script:
   ```bash
   python setup.py
   ```

2. **Start Application**: Run the Python startup script:
   ```bash
   python start_all.py
   ```

## Available Scripts

### Setup Scripts

| Script | Platform | Description |
|--------|----------|-------------|
| `setup.bat` | Windows | Windows batch script for complete setup |
| `setup.py` | All | Cross-platform Python setup script |

**What the setup scripts do:**
- Check for Python and Node.js installations
- Create a Python virtual environment (`venv/`)
- Install Python dependencies from `requirements.txt`
- Install frontend dependencies with `npm install`

### Startup Scripts

#### Start Everything
| Script | Platform | Description |
|--------|----------|-------------|
| `start_all.bat` | Windows | Start both backend and frontend (separate windows) |
| `start_all.py` | All | Start both backend and frontend (single terminal) |

#### Start Individual Components
| Script | Platform | Description |
|--------|----------|-------------|
| `start_backend.bat` | Windows | Start only the Python Flask backend |
| `start_backend.py` | All | Start only the Python Flask backend |
| `start_frontend.bat` | Windows | Start only the React frontend |
| `start_frontend.py` | All | Start only the React frontend |

## Default Ports

- **Backend (Flask)**: http://localhost:5000
- **Frontend (Vite)**: http://localhost:5173

## Troubleshooting

### Common Issues

1. **"Python not found"**
   - Install Python 3.8+ and ensure it's in your PATH
   - On Windows, check "Add Python to PATH" during installation

2. **"Node.js not found"**
   - Install Node.js from nodejs.org
   - Restart your terminal after installation

3. **"Virtual environment not found"**
   - Run the setup script first: `setup.bat` or `python setup.py`

4. **"Frontend dependencies not installed"**
   - Run the setup script first
   - Or manually run: `cd frontend && npm install`

5. **Port already in use**
   - Stop any existing servers
   - The frontend (Vite) will automatically find an available port
   - For backend, check if another Flask app is running

### Manual Setup (if scripts fail)

If the automated scripts don't work, you can set up manually:

1. **Backend Setup:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   ```

3. **Start Backend:**
   ```bash
   # Make sure virtual environment is activated
   python swing_analysis_prototype.py
   ```

4. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

## Project Structure

```
Swing-Analyzer/
├── setup.bat                    # Windows setup script
├── setup.py                     # Cross-platform setup script
├── start_all.bat               # Windows: start both servers
├── start_all.py                # Cross-platform: start both servers
├── start_backend.bat           # Windows: start backend only
├── start_backend.py            # Cross-platform: start backend only
├── start_frontend.bat          # Windows: start frontend only
├── start_frontend.py           # Cross-platform: start frontend only
├── requirements.txt            # Python dependencies
├── swing_analysis_prototype.py # Main backend file
├── venv/                       # Python virtual environment (created by setup)
└── frontend/                   # React frontend
    ├── package.json
    ├── src/
    └── node_modules/           # Node.js dependencies (created by setup)
```

## Development Workflow

1. **Initial Setup** (once):
   ```bash
   python setup.py
   ```

2. **Daily Development**:
   ```bash
   python start_all.py
   ```

3. **Stop Servers**: Press `Ctrl+C` in the terminal

## Scripts Features

- **Error Checking**: All scripts check for prerequisites and dependencies
- **Cross-Platform**: Python scripts work on Windows, Mac, and Linux
- **User-Friendly**: Clear error messages and instructions
- **Robust**: Handle common failure scenarios gracefully
- **Flexible**: Can start components individually or together

## Need Help?

If you encounter issues not covered here:
1. Check that all prerequisites are installed
2. Try running the setup script again
3. Check the error messages for specific guidance
4. Try the manual setup steps as a fallback