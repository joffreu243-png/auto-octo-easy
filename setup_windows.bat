@echo off
REM OctoMaster Pro - Windows Setup Script
REM This script sets up the Python environment for Windows

echo ================================================
echo OctoMaster Pro - Windows Setup
echo ================================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11, 3.12, or 3.13 from python.org
    echo.
    pause
    exit /b 1
)

echo Checking Python version...
python -c "import sys; v=sys.version_info; exit(0 if (3,11)<=v<(3,14) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11-3.13 required
    echo Current version:
    python --version
    echo.
    echo Please install Python 3.11, 3.12, or 3.13
    echo WARNING: Python 3.14 is dev version and NOT supported!
    echo.
    pause
    exit /b 1
)

echo Python version OK
echo.

REM Upgrade pip, setuptools, and wheel first
echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
    echo ERROR: Failed to upgrade pip/setuptools/wheel
    pause
    exit /b 1
)
echo.

REM Install requirements with --prefer-binary to avoid compilation
echo Installing requirements...
echo Using --prefer-binary to avoid C++ compilation issues
pip install -r requirements.txt --prefer-binary
if errorlevel 1 (
    echo.
    echo ERROR: Installation failed!
    echo.
    echo Common fixes:
    echo 1. Install Microsoft C++ Build Tools if you see compilation errors
    echo 2. Try: pip install --prefer-binary greenlet
    echo 3. Check Python version (must be 3.11-3.13)
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo Installation Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Copy .env.example to .env and configure your settings
echo 2. Run: python main.py
echo.
echo For troubleshooting, see WINDOWS_INSTALL.md
echo.
pause
