@echo off
SETLOCAL EnableDelayedExpansion

REM ================================================================
REM OctoMaster Pro - One-Click Install and Run
REM ================================================================

title OctoMaster Pro - Installation

echo.
echo ============================================================
echo   OctoMaster Pro
echo   One-Click Installation and Launch
echo ============================================================
echo.

REM ================================================================
REM Step 1: Check Python
REM ================================================================

echo [1/7] Checking Python installation...

python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.11 or 3.12 from:
    echo   https://www.python.org/downloads/
    echo.
    echo IMPORTANT: Check "Add Python to PATH" during installation!
    echo.
    echo After installing Python, run this script again.
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%V in ('python --version 2^>^&1') do set PYTHON_VERSION=%%V
echo OK: Python %PYTHON_VERSION% detected

REM Warn if Python 3.14
echo %PYTHON_VERSION% | findstr /C:"3.14" >nul
if %ERRORLEVEL% EQU 0 (
    echo.
    echo WARNING: Python 3.14 detected!
    echo Python 3.14 is a development version and may have compatibility issues.
    echo Recommend using Python 3.12 instead.
    echo.
    echo Continue anyway? Press any key...
    pause >nul
)

REM ================================================================
REM Step 2: Create Virtual Environment
REM ================================================================

echo.
echo [2/7] Setting up virtual environment...

if exist "venv\" (
    echo Virtual environment already exists
) else (
    echo Creating new virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to create virtual environment!
        pause
        exit /b 1
    )
    echo OK: Virtual environment created
)

REM ================================================================
REM Step 3: Activate Virtual Environment
REM ================================================================

echo.
echo [3/7] Activating virtual environment...

call venv\Scripts\activate.bat
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate virtual environment!
    pause
    exit /b 1
)
echo OK: Virtual environment activated

REM ================================================================
REM Step 4: Update pip and tools
REM ================================================================

echo.
echo [4/7] Updating pip, setuptools, and wheel...

python -m pip install --upgrade pip setuptools wheel --quiet
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: pip update had issues, continuing anyway...
)
echo OK: Tools updated

REM ================================================================
REM Step 5: Install Dependencies
REM ================================================================

echo.
echo [5/7] Installing Python dependencies...
echo This may take 3-5 minutes on first run...
echo.

REM Use --prefer-binary to avoid compilation issues
pip install -r requirements.txt --prefer-binary

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Some packages failed to install!
    echo.
    echo Trying alternative method (binary packages only)...
    pip cache purge
    pip install --only-binary :all: greenlet sqlalchemy
    pip install -r requirements.txt --prefer-binary

    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo ERROR: Installation failed!
        echo.
        echo Please check the error messages above.
        echo You may need to install Visual C++ Build Tools:
        echo   https://aka.ms/vs/17/release/vs_BuildTools.exe
        echo.
        pause
        exit /b 1
    )
)

echo OK: Dependencies installed

REM ================================================================
REM Step 6: Install Playwright Chromium
REM ================================================================

echo.
echo [6/7] Installing Playwright Chromium browser...
echo This will download ~160 MB...
echo.

python -m playwright install chromium

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Playwright installation had issues
    echo The application may still work
)

echo OK: Playwright installed

REM ================================================================
REM Step 7: Apply Fixes
REM ================================================================

echo.
echo [7/7] Applying compatibility fixes...

REM Run fix scripts if they exist
if exist "fix_imports.py" (
    echo Fixing imports...
    python fix_imports.py >nul 2>&1
)

if exist "fix_pyqt6.py" (
    echo Fixing PyQt6 compatibility...
    python fix_pyqt6.py >nul 2>&1
)

echo OK: Fixes applied

REM ================================================================
REM Step 8: Create .env if needed
REM ================================================================

if not exist ".env" (
    if exist ".env.example" (
        echo.
        echo Creating .env configuration file...
        copy .env.example .env >nul
        echo OK: .env created from .env.example
        echo You can edit .env file to add your API keys
    )
)

REM ================================================================
REM Installation Complete
REM ================================================================

echo.
echo ============================================================
echo   INSTALLATION COMPLETE!
echo ============================================================
echo.
echo Starting OctoMaster Pro...
echo.

REM Run the application
python main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ============================================================
    echo   Application exited with errors
    echo   Check logs\ folder for details
    echo ============================================================
    echo.
)

pause
